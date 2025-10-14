from src.plant_detection.constants import CONFIG_FILE_PATH
from src.plant_detection.utils.main_utils import read_yaml, create_directories
from src.plant_detection.entity.config_entity import DataValidationConfig

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
