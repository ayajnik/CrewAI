from src.plant_detection.config.configuration import ConfigurationManager
from src.plant_detection.components.object_detection import main_yolo_pipeline
from src.plant_detection import logger

class ObjectDetectionStage:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        model_training_config = config.get_model_training_config()
        
        logger.info(f"Starting YOLOv8 Object Detection Pipeline")
        detector, results, metrics = main_yolo_pipeline(model_training_config)
        logger.info(f"YOLOv8 Pipeline completed successfully")