import numpy as np
import pandas as pd
from pathlib import Path
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras import layers, models, optimizers, callbacks
# from tensorflow.keras.applications import ResNet50, VGG16, MobileNetV2, EfficientNetB0
from sklearn.utils.class_weight import compute_class_weight
from src.plant_detection.entity.config_entity import ModelTrainingConfig
from src.plant_detection import logger
import json

import os
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"


class ModelTrainer:
    def __init__(self, config: ModelTrainingConfig):
        self.config = config
        self.model = None
        self.class_names = None
        self._tf_loaded = False
    
    import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.utils.class_weight import compute_class_weight
from src.plant_detection.entity.config_entity import ModelTrainingConfig
from src.plant_detection import logger
import json

# REMOVE THIS LINE - IT'S TOO LATE HERE
# os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"


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
        
        # Add a timeout mechanism
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("TensorFlow import timed out after 120 seconds")
        
        # Set a 120 second timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(120)
        
        try:
            import tensorflow as tf
            signal.alarm(0)  # Cancel the alarm
            
            # Configure TensorFlow
            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)
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
            
        except TimeoutError as e:
            logger.error("TensorFlow import timed out - this is a known macOS issue")
            logger.error("Try running with: OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES python main.py")
            raise

        
    def _load_data(self, data_dir: Path):
        """Load preprocessed numpy arrays and annotations"""
        logger.info(f"Loading data from {data_dir}")
        
        # Load annotations
        annotations_path = Path(data_dir) / "_annotations.csv"
        annotations = pd.read_csv(annotations_path)
        
        # Get unique classes
        if self.class_names is None:
            self.class_names = sorted(annotations['class'].unique())
            logger.info(f"Found {len(self.class_names)} classes: {self.class_names}")
        
        # Create class to index mapping
        class_to_idx = {cls: idx for idx, cls in enumerate(self.class_names)}
        
        # Load images and labels
        images = []
        labels = []
        
        # Get unique filenames (to avoid duplicates from multiple bounding boxes)
        unique_files = annotations['filename'].unique()
        
        for filename in unique_files:
            # Load preprocessed image
            npy_filename = Path(filename).stem + '.npy'
            img_path = Path(data_dir) / npy_filename
            
            if not img_path.exists():
                logger.warning(f"Preprocessed image not found: {img_path}")
                continue
            
            image = np.load(img_path)
            
            # Get label (using first occurrence if multiple boxes)
            label = annotations[annotations['filename'] == filename]['class'].iloc[0]
            label_idx = class_to_idx[label]
            
            images.append(image)
            labels.append(label_idx)
        
        images = np.array(images)
        labels = np.array(labels)
        
        logger.info(f"Loaded {len(images)} images with shape {images.shape}")
        
        return images, labels
    
    def _get_base_model(self):
        """Get pre-trained base model"""
        if not self._tf_loaded:
            self._load_tensorflow()
            
        input_shape = (*self.config.image_size, 3)
        
        # Use models from instance variables
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
        
        # Compile model
        model.compile(
            optimizer=self.optimizers.Adam(learning_rate=self.config.learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', self.keras.metrics.SparseCategoricalAccuracy(name='acc')]
        )
        
        logger.info(f"Model built successfully")
        logger.info(f"Total parameters: {model.count_params():,}")
        
        return model
    
    def _compute_class_weights(self, labels):
        """Compute class weights for imbalanced datasets"""
        if not self.config.use_class_weights:
            return None
        
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
        """Main training function"""
        self._load_tensorflow()
        logger.info("Starting model training...")
        
        # Load data
        X_train, y_train = self._load_data(self.config.transformed_train_data)
        X_val, y_val = self._load_data(self.config.transformed_val_data)
        
        logger.info(f"Training set: {X_train.shape}, Validation set: {X_val.shape}")
        
        # Build model
        self.model = self._build_model()
        
        # Compute class weights
        class_weights = self._compute_class_weights(y_train)
        
        # Get callbacks
        callback_list = self._get_callbacks()
        
        # Train model
        logger.info("Starting training...")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
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
        with open(history_path, 'w') as f:
            json.dump(history.history, f)
        logger.info(f"Training history saved to {history_path}")
        
        return history
    
    def evaluate(self):
        """Evaluate model on test set"""
        if not self._tf_loaded:
            self._load_tensorflow()
            
        logger.info("Evaluating model on test set...")
        
        X_test, y_test = self._load_data(self.config.transformed_test_data)
        
        if self.model is None:
            logger.info("Loading trained model...")
            self.model = self.keras.models.load_model(self.config.trained_model_path)
        
        test_loss, test_acc = self.model.evaluate(X_test, y_test, verbose=1)
        
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