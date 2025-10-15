from src.plant_detection.config.configuration import ConfigurationManager
from src.plant_detection.components.data_transformation import DataTransformation
from src.plant_detection import logger

class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        data_transformation_config = config.get_data_transformation_config()
        data_transformation = DataTransformation(config=data_transformation_config)
        results = data_transformation.transform_all_datasets()
        logger.info(f"Transformation results: {results}")