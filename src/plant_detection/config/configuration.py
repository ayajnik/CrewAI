from src.plant_detection.constants import CONFIG_FILE_PATH
from src.plant_detection.utils.main_utils import read_yaml, create_directories
from src.plant_detection.entity.config_entity import DataValidationConfig
from src.plant_detection.entity.config_entity import DataTransformationConfig
from src.plant_detection.entity.config_entity import ModelTrainingConfig
from pathlib import Path

class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH):

        self.config = read_yaml(config_filepath)
        #self.params = read_yaml(params_filepath)
        #create_directories([self.config.artifacts_root])
 
    

    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=config.root_dir,
            STATUS_FILE=config.STATUS_FILE,
            train_data=config.train_data,
            test_data=config.test_data,
            val_data=config.val_data
        )

        return data_validation_config


    # def get_data_transformation_config(self) -> DataTransformationConfig:
    #     config = self.config.data_transformation

    #     data_transformation_config = DataTransformationConfig(
    #         root_dir=config.root_dir,
    #         transformed_train_data=config.transformed_train_data,
    #         transformed_test_data=config.transformed_test_data,
    #         transformed_val_data=config.transformed_val_data
    #     )
    
    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation
        
        # Get source data paths from data_validation config
        data_val_config = self.config.data_validation
        
        create_directories([config.root_dir])
        
        data_transformation_config = DataTransformationConfig(
            root_dir=Path(config.root_dir),
            transformed_train_data=Path(config.transformed_train_data),
            transformed_test_data=Path(config.transformed_test_data),
            transformed_val_data=Path(config.transformed_val_data),
            train_data=Path(data_val_config.train_data),
            test_data=Path(data_val_config.test_data),
            val_data=Path(data_val_config.val_data),
            image_size=tuple(config.image_size),
            normalization_method=config.normalization_method,
            model_name=config.model_name,
            color_mode=config.color_mode,
            data_format=config.data_format
        )
        
        return data_transformation_config

    from src.plant_detection.entity.config_entity import ModelTrainingConfig

# Add this method to ConfigurationManager class:

    def get_model_training_config(self) -> ModelTrainingConfig:
        config = self.config.model_training
        data_transform_config = self.config.data_transformation
        
        create_directories([config.root_dir])
        
        model_training_config = ModelTrainingConfig(
            root_dir=Path(config.root_dir),
            trained_model_path=Path(config.trained_model_path),
            trained_model_weights=Path(config.trained_model_weights),
            transformed_train_data=Path(data_transform_config.transformed_train_data),
            transformed_test_data=Path(data_transform_config.transformed_test_data),
            transformed_val_data=Path(data_transform_config.transformed_val_data),
            trained_model_yolo_path=Path(config.trained_model_yolo_path),
            train_data=Path(config.train_data),
            test_data=Path(config.test_data),
            val_data=Path(config.val_data),
            model_name=config.model_name,
            image_size=tuple(config.image_size),
            num_classes=config.num_classes,
            epochs=config.epochs,
            batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            early_stopping_patience=config.early_stopping_patience,
            reduce_lr_patience=config.reduce_lr_patience,
            validation_split=config.validation_split,
            use_class_weights=config.use_class_weights,
            freeze_base_layers=config.freeze_base_layers,
            fine_tune_from_layer=config.fine_tune_from_layer
        )
        
        return model_training_config