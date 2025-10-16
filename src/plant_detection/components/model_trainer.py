import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.utils.class_weight import compute_class_weight
from src.plant_detection.entity.config_entity import ModelTrainingConfig
from src.plant_detection import logger
import json
import os


class ModelTrainer:
    def __init__(self, config: ModelTrainingConfig):
        self.config = config
        self.model = None
        self.class_names = None
        self._tf_loaded = False
    
    def _load_tensorflow(self):
        """Lazy load TensorFlow only when needed"""
        if self._tf_loaded:
            return
            
        logger.info("Loading TensorFlow - please wait (30-90 seconds on macOS)...")
        
        try:
            import tensorflow as tf
            
            # Configure TensorFlow for memory efficiency
            tf.config.threading.set_intra_op_parallelism_threads(2)
            tf.config.threading.set_inter_op_parallelism_threads(2)
            tf.config.set_visible_devices([], 'GPU')

            from tensorflow import keras
            from tensorflow.keras import layers, models, optimizers, callbacks
            from tensorflow.keras.applications import (
                ResNet50, ResNet101, VGG16, VGG19, 
                MobileNetV2, EfficientNetB0
            )

            self.tf = tf
            self.keras = keras
            self.layers = layers
            self.models = models
            self.optimizers = optimizers
            self.callbacks = callbacks
            self.models_dict = {
                "ResNet50": ResNet50,
                "ResNet101": ResNet101,
                "VGG16": VGG16,
                "VGG19": VGG19,
                "MobileNetV2": MobileNetV2,
                "EfficientNetB0": EfficientNetB0
            }

            self._tf_loaded = True
            logger.info("TensorFlow loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load TensorFlow: {e}")
            raise

    def _create_tf_dataset(self, data_dir, annotations, class_to_idx, batch_size, shuffle):
        """Create optimized tf.data.Dataset pipeline"""
        
        # Prepare file paths and labels
        file_paths = []
        labels = []
        
        unique_files = annotations['filename'].unique()
        for filename in unique_files:
            npy_filename = Path(filename).stem + '.npy'
            img_path = Path(data_dir) / npy_filename
            
            if img_path.exists():
                label = annotations[annotations['filename'] == filename]['class'].iloc[0]
                label_idx = class_to_idx[label]
                
                file_paths.append(str(img_path))
                labels.append(label_idx)
        
        logger.info(f"Creating dataset with {len(file_paths)} samples")
        
        # Create dataset from file paths
        def load_npy(path, label):
            """Load numpy array using TensorFlow"""
            def _load_fn(path_tensor, label_tensor):
                # Load numpy file
                data = np.load(path_tensor.numpy())
                return data.astype(np.float32), label_tensor.numpy().astype(np.int32)
            
            image, label = self.tf.py_function(
                _load_fn,
                [path, label],
                [self.tf.float32, self.tf.int32]
            )
            
            # Set shapes explicitly
            image.set_shape([*self.config.image_size, 3])
            label.set_shape([])
            
            return image, label
        
        # Create dataset
        dataset = self.tf.data.Dataset.from_tensor_slices((file_paths, labels))
        
        if shuffle:
            dataset = dataset.shuffle(buffer_size=min(1000, len(file_paths)))
        
        # Load images in parallel
        dataset = dataset.map(
            load_npy,
            num_parallel_calls=self.tf.data.AUTOTUNE
        )
        
        # Batch and prefetch
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(self.tf.data.AUTOTUNE)
        
        return dataset

    def _prepare_datasets(self, data_dir: Path, shuffle=True):
        """Prepare optimized tf.data.Dataset"""
        logger.info(f"Preparing dataset for {data_dir}")
        
        # Load annotations
        annotations_path = Path(data_dir) / "_annotations.csv"
        annotations = pd.read_csv(annotations_path)
        
        # Get unique classes
        if self.class_names is None:
            self.class_names = sorted(annotations['class'].unique())
            logger.info(f"Found {len(self.class_names)} classes: {self.class_names}")
        
        # Create class to index mapping
        class_to_idx = {cls: idx for idx, cls in enumerate(self.class_names)}
        
        # Create dataset
        dataset = self._create_tf_dataset(
            data_dir=data_dir,
            annotations=annotations,
            class_to_idx=class_to_idx,
            batch_size=self.config.batch_size,
            shuffle=shuffle
        )
        
        # Count total samples
        num_samples = len(annotations['filename'].unique())
        steps = int(np.ceil(num_samples / self.config.batch_size))
        logger.info(f"Dataset ready with {num_samples} samples, {steps} steps per epoch")
        
        return dataset, annotations, steps
    
    def _get_base_model(self):
        """Get pre-trained base model"""
        if not self._tf_loaded:
            self._load_tensorflow()
            
        input_shape = (*self.config.image_size, 3)
        
        if self.config.model_name not in self.models_dict:
            raise ValueError(f"Model {self.config.model_name} not supported. Available: {list(self.models_dict.keys())}")
        
        base_model = self.models_dict[self.config.model_name](
            include_top=False,
            weights='imagenet',
            input_shape=input_shape
        )
        
        if self.config.freeze_base_layers:
            base_model.trainable = False
            logger.info(f"Frozen all base model layers")
        
        return base_model
    
    def _build_model(self):
        """Build complete model with transfer learning"""
        if not self._tf_loaded:
            self._load_tensorflow()
            
        logger.info(f"Building {self.config.model_name} model...")
        
        # Get base model
        base_model = self._get_base_model()
        
        # Build classification head
        inputs = self.keras.Input(shape=(*self.config.image_size, 3))
        x = base_model(inputs, training=False)
        x = self.layers.GlobalAveragePooling2D()(x)
        x = self.layers.Dropout(0.5)(x)
        x = self.layers.Dense(512, activation='relu')(x)
        x = self.layers.Dropout(0.3)(x)
        outputs = self.layers.Dense(self.config.num_classes, activation='softmax')(x)
        
        model = self.keras.Model(inputs, outputs)
        
        # Compile model with mixed precision for speed
        model.compile(
            optimizer=self.optimizers.Adam(learning_rate=self.config.learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info(f"Model built successfully")
        logger.info(f"Total parameters: {model.count_params():,}")
        
        return model
    
    def _compute_class_weights(self, annotations):
        """Compute class weights for imbalanced datasets"""
        if not self.config.use_class_weights:
            return None
        
        # Get labels from annotations
        labels = []
        for filename in annotations['filename'].unique():
            label = annotations[annotations['filename'] == filename]['class'].iloc[0]
            label_idx = self.class_names.index(label)
            labels.append(label_idx)
        
        labels = np.array(labels)
        
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(labels),
            y=labels
        )
        
        class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
        logger.info(f"Class weights: {class_weight_dict}")
        
        return class_weight_dict
    
    def _get_callbacks(self):
        """Get training callbacks"""
        if not self._tf_loaded:
            self._load_tensorflow()
            
        os.makedirs(self.config.root_dir, exist_ok=True)
        
        callback_list = [
            # Early stopping
            self.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config.early_stopping_patience,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Model checkpoint
            self.callbacks.ModelCheckpoint(
                filepath=str(self.config.trained_model_weights),
                monitor='val_accuracy',
                save_best_only=True,
                save_weights_only=True,
                verbose=1
            ),
            
            # Reduce learning rate
            self.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=self.config.reduce_lr_patience,
                min_lr=1e-7,
                verbose=1
            ),
            
            # TensorBoard
            self.callbacks.TensorBoard(
                log_dir=str(Path(self.config.root_dir) / 'logs'),
                histogram_freq=1
            )
        ]
        
        return callback_list
    
    def train(self):
        """Main training function with optimized data loading"""
        self._load_tensorflow()
        logger.info("Starting model training...")
        
        # Prepare datasets
        train_dataset, train_annotations, train_steps = self._prepare_datasets(
            self.config.transformed_train_data, shuffle=True
        )
        val_dataset, val_annotations, val_steps = self._prepare_datasets(
            self.config.transformed_val_data, shuffle=False
        )
        
        logger.info(f"Training steps: {train_steps}, Validation steps: {val_steps}")
        
        # Build model
        self.model = self._build_model()
        
        # Compute class weights
        class_weights = self._compute_class_weights(train_annotations)
        
        # Get callbacks
        callback_list = self._get_callbacks()
        
        # Train model using datasets
        logger.info("Starting training with optimized data pipeline...")
        history = self.model.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=self.config.epochs,
            steps_per_epoch=train_steps,
            validation_steps=val_steps,
            class_weight=class_weights,
            callbacks=callback_list,
            verbose=1
        )
        
        # Save final model
        self.model.save(self.config.trained_model_path)
        logger.info(f"Model saved to {self.config.trained_model_path}")
        
        # Save class names
        class_names_path = Path(self.config.root_dir) / 'class_names.json'
        with open(class_names_path, 'w') as f:
            json.dump(self.class_names, f)
        logger.info(f"Class names saved to {class_names_path}")
        
        # Save training history
        history_path = Path(self.config.root_dir) / 'training_history.json'
        history_dict = {k: [float(v) for v in vals] for k, vals in history.history.items()}
        with open(history_path, 'w') as f:
            json.dump(history_dict, f)
        logger.info(f"Training history saved to {history_path}")
        
        return history
    
    def evaluate(self):
        """Evaluate model on test set"""
        if not self._tf_loaded:
            self._load_tensorflow()
            
        logger.info("Evaluating model on test set...")
        
        # Prepare test dataset
        test_dataset, _, test_steps = self._prepare_datasets(
            self.config.transformed_test_data, shuffle=False
        )
        
        if self.model is None:
            logger.info("Loading trained model...")
            self.model = self.keras.models.load_model(self.config.trained_model_path)
        
        # Evaluate using dataset
        results = self.model.evaluate(test_dataset, steps=test_steps, verbose=1)
        test_loss = results[0]
        test_acc = results[1]
        
        logger.info(f"Test Loss: {test_loss:.4f}")
        logger.info(f"Test Accuracy: {test_acc:.4f}")
        
        # Save evaluation results
        eval_results = {
            'test_loss': float(test_loss),
            'test_accuracy': float(test_acc)
        }
        
        eval_path = Path(self.config.root_dir) / 'evaluation_results.json'
        with open(eval_path, 'w') as f:
            json.dump(eval_results, f, indent=4)
        logger.info(f"Evaluation results saved to {eval_path}")
        
        return test_loss, test_acc