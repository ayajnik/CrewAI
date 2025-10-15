import numpy as np
import pandas as pd
import cv2
from pathlib import Path
from src.plant_detection.entity.config_entity import DataTransformationConfig
from src.plant_detection import logger
from typing import Tuple, Optional
import os

class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config
        
    def _get_preprocessing_function(self):
        """Get the appropriate preprocessing function based on model"""
        # Use NumPy-based preprocessing to avoid TensorFlow loading issues
        
        if self.config.model_name in ['ResNet50', 'ResNet101', 'VGG16', 'VGG19']:
            logger.info(f"Using Caffe-style preprocessing for {self.config.model_name}")
            return self._caffe_preprocess
        elif self.config.model_name in ['MobileNetV2', 'EfficientNetB0']:
            logger.info(f"Using TensorFlow-style preprocessing for {self.config.model_name}")
            return self._tf_style_preprocess
        elif self.config.model_name == 'InceptionV3':
            logger.info("Using Inception-style preprocessing")
            return self._inception_preprocess
        else:
            logger.warning(f"Model {self.config.model_name} not found, using standard normalization")
            return self._standard_normalize
    
    def _caffe_preprocess(self, image):
        """Caffe-style preprocessing (ResNet, VGG) - RGB to BGR + mean subtraction"""
        # image is already RGB from cv2.cvtColor
        # Convert RGB to BGR
        image_bgr = image[:, :, ::-1].astype(np.float32)
        
        # Subtract ImageNet mean (in BGR order)
        mean_bgr = np.array([103.939, 116.779, 123.68])
        image_bgr -= mean_bgr
        
        return image_bgr
    
    def _tf_style_preprocess(self, image):
        """TensorFlow-style preprocessing (MobileNet, EfficientNet) - scale to [-1, 1]"""
        image = image.astype(np.float32)
        return (image / 127.5) - 1.0
    
    def _inception_preprocess(self, image):
        """Inception-style preprocessing - scale to [-1, 1]"""
        image = image.astype(np.float32)
        image /= 255.0
        image -= 0.5
        image *= 2.0
        return image
    
    def _standard_normalize(self, image):
        """Standard ImageNet normalization"""
        image = image.astype(np.float32)
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        return (image / 255.0 - mean) / std
    
    def _load_and_preprocess_image(self, image_path: Path) -> np.ndarray:
        """Load and preprocess a single image"""
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, self.config.image_size)
        
        preprocess_fn = self._get_preprocessing_function()
        image = preprocess_fn(image)
        return image
    
    def _read_annotations(self, data_dir: Path) -> pd.DataFrame:
        """Read CSV annotations from directory"""
        csv_files = list(Path(data_dir).glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV file found in {data_dir}")
        
        annotations = pd.read_csv(csv_files[0])
        logger.info(f"Loaded annotations from {csv_files[0]}")
        return annotations
    
    def transform_data(self, source_dir: Path, target_dir: Path):
        """Transform images and save to target directory"""
        os.makedirs(target_dir, exist_ok=True)
        annotations = self._read_annotations(source_dir)
        
        image_files = list(Path(source_dir).glob("*.jpg"))
        logger.info(f"Found {len(image_files)} images in {source_dir}")
        
        transformed_images = []
        
        for idx, img_path in enumerate(image_files):
            try:
                transformed_img = self._load_and_preprocess_image(img_path)
                output_path = Path(target_dir) / f"{img_path.stem}.npy"
                np.save(output_path, transformed_img)
                transformed_images.append(str(output_path))
                
                if idx % 100 == 0:
                    logger.info(f"Transformed {idx}/{len(image_files)} images")
                    
            except Exception as e:
                logger.error(f"Error processing {img_path}: {e}")
                continue
        
        annotations.to_csv(Path(target_dir) / "annotations.csv", index=False)
        logger.info(f"Saved annotations to {target_dir}/annotations.csv")
        
        return len(transformed_images)
    
    def transform_all_datasets(self):
        """Transform train, test, and validation datasets"""
        logger.info("Starting data transformation...")
        
        train_count = self.transform_data(
            self.config.train_data, 
            self.config.transformed_train_data
        )
        logger.info(f"Transformed {train_count} training images")
        
        test_count = self.transform_data(
            self.config.test_data, 
            self.config.transformed_test_data
        )
        logger.info(f"Transformed {test_count} test images")
        
        val_count = self.transform_data(
            self.config.val_data, 
            self.config.transformed_val_data
        )
        logger.info(f"Transformed {val_count} validation images")
        
        logger.info("Data transformation completed successfully!")
        
        return {
            'train_count': train_count,
            'test_count': test_count,
            'val_count': val_count
        }