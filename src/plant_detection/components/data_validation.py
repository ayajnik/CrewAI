import os
from src.plant_detection import logger
from src.plant_detection.entity.config_entity import DataValidationConfig

class DataValidation:
    def __init__(self, config:DataValidationConfig):
        self.config = config

    def validate_files_present(self):

        validating_counts = None

        image_count = []
        annotations_count = []

        print(self.config.STATUS_FILE)

        os.makedirs(os.path.dirname(self.config.STATUS_FILE), exist_ok=True)


        all_files = os.listdir(os.path.join('data','train'))
        ##print(all_files)
        for files in all_files:
            if files not in self.config.train_data:
                validating_counts = False
            elif files.endswith('.jpg'):
                image_count.append(len(files))
                with open(self.config.STATUS_FILE, 'w') as f:
                    f.write(f'''>>>>>>>>>>>>>>>Training Image Data Counts<<<<<<<<<<<<<<<<
                            : {image_count}''')
                validating_counts = True

            elif files.endswith('.csv'):
                annotations_count.append(len(files))
                with open(self.config.STATUS_FILE, 'w') as f:
                    f.write(f'''>>>>>>>>>>>>>>>Training Image Data Annotations<<<<<<<<<<<<<<<<
                            : {annotations_count}''')
                validating_counts = True
            #logger.info("Validating the files and the files are there or not")
        return validating_counts



