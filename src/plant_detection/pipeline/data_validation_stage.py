from src.plant_detection.config.configuration import ConfigurationManager
from src.plant_detection.components.data_validation import DataValidation
from src.plant_detection import logger


class DataValidationTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        data_validation_config = config.get_data_validation_config()
        data_validation = DataValidation(config=data_validation_config)
        data_validation.validate_files_present()