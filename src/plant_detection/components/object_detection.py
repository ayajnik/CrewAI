import numpy as np
import pandas as pd
from pathlib import Path
from src.plant_detection.entity.config_entity import ModelTrainingConfig
from src.plant_detection import logger
import json
import os
import pandas as pd
import yaml
import shutil
from ultralytics import YOLO
import cv2
from typing import List, Dict

class YOLODataConverter:
    """Convert CSV annotations to YOLO format"""
    
    def __init__(self,config_modelTrain:ModelTrainingConfig ,class_names: List[str] = None):
        self.class_names = class_names
        self.class_to_idx = None
        self.config_modelTrain = config_modelTrain

    def convert_dataset(self, split: str):
        """
        Convert one dataset split (train/valid/test) to YOLO format
        
        Args:
            input_dir: Directory containing images and _annotations.csv
            output_dir: Output directory for YOLO format
            split: 'train', 'valid', or 'test'
        """
        print(f"\nConverting {split} dataset...")
        
        # Determine which data directory to use based on split
        if split == 'train':
            input_path = Path(self.config_modelTrain.train_data)
        elif split == 'val' or split == 'valid':
            input_path = Path(self.config_modelTrain.val_data)
        else:  # test
            input_path = Path(self.config_modelTrain.test_data)
        
        print(f"Using input path: {input_path}")
        annotations_csv = input_path / '_annotations.csv'
        
        if not annotations_csv.exists():
            print(f"Warning: {annotations_csv} not found. Skipping {split}.")
            return
        
        # Read annotations
        df = pd.read_csv(annotations_csv)
        
        # Get unique classes
        if self.class_names is None:
            self.class_names = sorted(df['class'].unique())
            self.class_to_idx = {cls: idx for idx, cls in enumerate(self.class_names)}
            print(f"Found {len(self.class_names)} classes: {self.class_names}")
        
        # Create output directories
        output_path = Path(self.config_modelTrain.trained_model_yolo_path) / split
        images_dir = output_path / 'images'
        labels_dir = output_path / 'labels'
        
        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each unique image
        unique_files = df['filename'].unique()
        print(f"Processing {len(unique_files)} images...")
        
        converted_count = 0
        for filename in unique_files:
            # Get all annotations for this image
            image_annotations = df[df['filename'] == filename]
            
            # Find source image (try different extensions)
            source_image = None
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                potential_path = input_path / filename.replace(Path(filename).suffix, ext)
                if potential_path.exists():
                    source_image = potential_path
                    break
            
            if source_image is None:
                print(f"Warning: Image not found: {filename}")
                continue
            
            # Copy image to YOLO images directory
            dest_image = images_dir / source_image.name
            shutil.copy2(source_image, dest_image)
            
            # Create YOLO label file
            label_file = labels_dir / f"{source_image.stem}.txt"
            
            with open(label_file, 'w') as f:
                for _, row in image_annotations.iterrows():
                    # Get image dimensions
                    img_width = row['width']
                    img_height = row['height']
                    
                    # Get bounding box coordinates
                    xmin = row['xmin']
                    ymin = row['ymin']
                    xmax = row['xmax']
                    ymax = row['ymax']
                    
                    # Convert to YOLO format (normalized center coordinates + width/height)
                    x_center = ((xmin + xmax) / 2) / img_width
                    y_center = ((ymin + ymax) / 2) / img_height
                    bbox_width = (xmax - xmin) / img_width
                    bbox_height = (ymax - ymin) / img_height
                    
                    # Get class index
                    class_idx = self.class_to_idx[row['class']]
                    
                    # Write YOLO format: class x_center y_center width height
                    f.write(f"{class_idx} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
            
            converted_count += 1
            
            if converted_count % 100 == 0:
                print(f"  Converted {converted_count}/{len(unique_files)} images")
        
        print(f"Converted {converted_count} images for {split}")
        return converted_count
    
    def create_yaml_config(self, yaml_path: str):
        """Create YOLO data configuration YAML file"""
        
        data_config = {
            'path': str(Path(self.config_modelTrain.trained_model_yolo_path).absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': len(self.class_names),  # Number of classes
            'names': self.class_names  # Class names list
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"\nYOLO config saved to: {yaml_path}")
        print(f"  Number of classes: {len(self.class_names)}")
        print(f"  Classes: {self.class_names}")

class PlantDiseaseYOLO:
    """YOLO-based plant disease detector"""
    
    def __init__(self, config_modelTrain:ModelTrainingConfig):
        self.config_modelTrain = config_modelTrain
        self.model = None
        self.class_names = None
    
    def prepare_data(self):
        """
        Convert all data splits to YOLO format
        """
        print("=" * 60)
        print("PREPARING DATA FOR YOLO")
        print("=" * 60)
        
        converter = YOLODataConverter(self.config_modelTrain)
        
        # Convert each split
        for split in ['train', 'val', 'test']:
            converter.convert_dataset(split)
        
        # Create YAML config
        yaml_path = Path(self.config_modelTrain.trained_model_yolo_path) / 'plant_disease.yaml'
        converter.create_yaml_config(str(yaml_path))
        
        self.class_names = converter.class_names
        
        print("\n" + "=" * 60)
        print("DATA PREPARATION COMPLETE!")
        print("=" * 60)
        
        return str(yaml_path)
    
    def train(
        self,
        data_yaml: str,
        model_size: str = 'n',
        project: str = 'artifacts/yolo_detection',
        name: str = 'plant_disease_detector'
    ):
        
        print("\n" + "=" * 60)
        print(f"TRAINING YOLOv8{model_size.upper()} MODEL")
        print("=" * 60)
        
        # Load pre-trained YOLO model
        model_name = f'yolov8{model_size}.pt'
        print(f"Loading {model_name}...")
        self.model = YOLO(model_name)
        
        # Train
        print(f"\nStarting training for {self.config_modelTrain.epochs} epochs...")
        results = self.model.train(
            data=data_yaml,
            epochs=self.config_modelTrain.epochs,
            imgsz=self.config_modelTrain.image_size[0],  # YOLO expects single int, not tuple
            batch=self.config_modelTrain.batch_size,
            device='cpu',  # Change to 'cuda' if GPU available
            
            # Early stopping
            patience=self.config_modelTrain.early_stopping_patience,
            
            # Save settings
            save=True,
            save_period=10,  # Save checkpoint every 10 epochs
            project=project,
            name=name,
            exist_ok=True,
            
            # Data augmentation
            hsv_h=0.015,      # Hue augmentation
            hsv_s=0.7,        # Saturation
            hsv_v=0.4,        # Value
            degrees=10.0,     # Rotation
            translate=0.1,    # Translation
            scale=0.5,        # Scale
            flipud=0.0,       # Vertical flip
            fliplr=0.5,       # Horizontal flip (50% chance)
            mosaic=1.0,       # Mosaic augmentation
            mixup=0.1,        # Mixup augmentation
            
            # Training hyperparameters
            lr0=self.config_modelTrain.learning_rate,  # Use config learning rate
            lrf=0.01,         # Final learning rate
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3.0,
            warmup_momentum=0.8,
            
            # Validation
            val=True,
            plots=True,       # Save training plots
            verbose=True
        )
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print(f"Best model saved to: {Path(project) / name / 'weights' / 'best.pt'}")
        print("=" * 60)
        
        return results
    
    def evaluate(self, data_yaml: str, model_path: str = None):
        """
        Evaluate model on test set
        
        Args:
            data_yaml: Path to YOLO data config
            model_path: Path to trained model (if None, uses current model)
        """
        print("\n" + "=" * 60)
        print("EVALUATING MODEL")
        print("=" * 60)
        
        if model_path:
            self.model = YOLO(model_path)
        
        if self.model is None:
            raise ValueError("No model loaded. Train or load a model first.")
        
        # Run validation on test set
        metrics = self.model.val(
            data=data_yaml,
            split='test',
            plots=True
        )
        
        # Print results
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"mAP50:        {metrics.box.map50:.4f}  (IoU=0.5)")
        print(f"mAP50-95:     {metrics.box.map:.4f}  (IoU=0.5:0.95)")
        print(f"Precision:    {metrics.box.mp:.4f}")
        print(f"Recall:       {metrics.box.mr:.4f}")
        print("=" * 60)
        
        # Save results
        results_dict = {
            'mAP50': float(metrics.box.map50),
            'mAP50-95': float(metrics.box.map),
            'precision': float(metrics.box.mp),
            'recall': float(metrics.box.mr)
        }
        
        results_path = Path('artifacts/yolo_detection/evaluation_results.json')
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(results_dict, f, indent=4)
        
        print(f"Results saved to: {results_path}")
        
        return metrics
    
    def predict(
        self,
        image_path: str,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        save: bool = True,
        output_dir: str = 'artifacts/yolo_detection/predictions'
    ):
        """
        Predict on a single image
        
        Args:
            image_path: Path to image
            conf_threshold: Confidence threshold (0-1)
            iou_threshold: IoU threshold for NMS
            save: Whether to save annotated image
            output_dir: Directory to save predictions
        
        Returns:
            List of detections
        """
        if self.model is None:
            raise ValueError("No model loaded. Train or load a model first.")
        
        # Run prediction
        results = self.model.predict(
            source=image_path,
            conf=conf_threshold,
            iou=iou_threshold,
            save=save,
            project=output_dir,
            name='results',
            exist_ok=True
        )
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            
            for i in range(len(boxes)):
                detection = {
                    'class': result.names[int(boxes.cls[i])],
                    'class_id': int(boxes.cls[i]),
                    'confidence': float(boxes.conf[i]),
                    'bbox_xyxy': boxes.xyxy[i].tolist(),  # [x1, y1, x2, y2]
                    'bbox_xywh': boxes.xywh[i].tolist(),  # [x_center, y_center, width, height]
                }
                detections.append(detection)
        
        return detections
    
    def predict_batch(
        self,
        image_dir: str,
        conf_threshold: float = 0.25,
        save: bool = True,
        output_dir: str = 'artifacts/yolo_detection/batch_predictions'
    ):
        """Predict on multiple images in a directory"""
        if self.model is None:
            raise ValueError("No model loaded. Train or load a model first.")
        
        print(f"\nRunning batch prediction on: {image_dir}")
        
        results = self.model.predict(
            source=image_dir,
            conf=conf_threshold,
            save=save,
            project=output_dir,
            name='results',
            exist_ok=True,
            stream=True  # Process one image at a time (memory efficient)
        )
        
        all_detections = {}
        for result in results:
            filename = Path(result.path).name
            
            detections = []
            boxes = result.boxes
            
            for i in range(len(boxes)):
                detection = {
                    'class': result.names[int(boxes.cls[i])],
                    'confidence': float(boxes.conf[i]),
                    'bbox': boxes.xyxy[i].tolist()
                }
                detections.append(detection)
            
            all_detections[filename] = detections
        
        print(f"✓ Processed {len(all_detections)} images")
        return all_detections
    
    def load_model(self, model_path: str):
        """Load a trained model"""
        print(f"Loading model from: {model_path}")
        self.model = YOLO(model_path)
        print("✓ Model loaded successfully!")
    
    def export_model(self, format: str = 'onnx', output_dir: str = 'artifacts/yolo_detection/export'):
        """
        Export model to different formats for deployment
        
        Args:
            format: Export format - 'onnx', 'torchscript', 'coreml', 'tflite', 'pb', etc.
            output_dir: Output directory
        """
        if self.model is None:
            raise ValueError("No model loaded")
        
        print(f"\nExporting model to {format} format...")
        
        export_path = self.model.export(
            format=format,
            imgsz=640
        )
        
        print(f"✓ Model exported to: {export_path}")
        return export_path
    
    def visualize_predictions(
        self,
        image_path: str,
        output_path: str = None,
        conf_threshold: float = 0.25
    ):
        """Visualize predictions on an image with custom styling"""
        detections = self.predict(image_path, conf_threshold=conf_threshold, save=False)
        
        # Load image
        img = cv2.imread(str(image_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = [int(coord) for coord in det['bbox_xyxy']]
            
            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label background
            label = f"{det['class']}: {det['confidence']:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(img, (x1, y1 - label_h - 10), (x1 + label_w, y1), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Save or show
        if output_path:
            cv2.imwrite(output_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            print(f"✓ Visualization saved to: {output_path}")
        
        return img, detections


# Main execution script
def main_yolo_pipeline(config: ModelTrainingConfig):
    """Complete YOLO training pipeline using configuration"""
    
    print("\n" + "=" * 60)
    print("YOLO PLANT DISEASE DETECTION")
    print("=" * 60)
    
    # Initialize detector
    detector = PlantDiseaseYOLO(config)
    
    # Step 1: Prepare data
    print("\nStep 1: Converting data to YOLO format...")
    data_yaml = detector.prepare_data()
    
    # Step 2: Train model
    print("\nStep 2: Training YOLO model...")
    results = detector.train(
        data_yaml=data_yaml,
        model_size='n',            # Start with nano (fastest)
        project='artifacts/yolo_detection',
        name='plant_disease_run1'
    )
    
    # Step 3: Evaluate
    print("\nStep 3: Evaluating model...")
    best_model = 'artifacts/yolo_detection/plant_disease_run1/weights/best.pt'
    metrics = detector.evaluate(data_yaml, model_path=best_model)
    
    # Step 4: Test predictions
    print("\nStep 4: Testing predictions...")
    # Find first image in test directory
    test_dir = Path(config.test_data)
    test_images = list(test_dir.glob('*.jpg')) + list(test_dir.glob('*.png'))
    
    if test_images:
        test_image = str(test_images[0])
        detections = detector.predict(test_image, conf_threshold=0.5)
        
        print(f"\nFound {len(detections)} detections:")
        for i, det in enumerate(detections, 1):
            print(f"  {i}. {det['class']}: {det['confidence']:.2%}")
        
        # Visualize
        detector.visualize_predictions(
            test_image,
            output_path='artifacts/yolo_detection/test_prediction.jpg'
        )
    else:
        print("No test images found in test directory")
    
    # Step 5: Export for deployment
    print("\nStep 5: Exporting model...")
    detector.export_model(format='onnx')
    
    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("Check artifacts/yolo_detection/ for all outputs")
    print("=" * 60)
    
    return detector, results, metrics