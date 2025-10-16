from src.plant_detection.config.configuration import ConfigurationManager
from src.plant_detection.components.model_trainer import ModelTrainer
from src.plant_detection import logger

class ModelTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        model_training_config = config.get_model_training_config()
        model_trainer = ModelTrainer(config=model_training_config)
        
        # Train model
        history = model_trainer.train()
        
        # Evaluate model
        test_loss, test_acc = model_trainer.evaluate()
        
        logger.info(f"Training completed! Test Accuracy: {test_acc:.4f}")