from src.plant_detection.entity.config_entity import DataValidationConfig
from pathlib import Path
from src.plant_detection import logger

class DataValidation:
    def __init__(self, config: DataValidationConfig):
        self.config = config

    def _count_files(self, data_dir):
        data_path = Path(data_dir)
        image_count = 0
        annotation_count = 0

        for file in data_path.iterdir():
            if file.suffix == '.jpg':
                image_count += 1
            elif file.suffix == '.csv':
                annotation_count += 1
        return image_count, annotation_count

    def validate_files_present(self):
        train_image_count, train_annotation_count = self._count_files(self.config.train_data)
        test_image_count, test_annotation_count = self._count_files(self.config.test_data)
        val_image_count, val_annotation_count = self._count_files(self.config.val_data)

        # Ensure directory exists for status file
        status_path = Path(self.config.STATUS_FILE)
        status_path.parent.mkdir(parents=True, exist_ok=True)

        # Write only counts to status file, not actual file names
        with open(status_path, 'w') as f:
            f.write(f">>>>>>>>>>>>>>> Training Image Data Counts <<<<<<<<<<<<<<<<\n")
            f.write(f"Total train images: {train_image_count}\n")
            f.write(f"Total train annotations: {train_annotation_count}\n\n")

            f.write(f">>>>>>>>>>>>>>> Test Image Data Counts <<<<<<<<<<<<<<<<\n")
            f.write(f"Total test images: {test_image_count}\n")
            f.write(f"Total test annotations: {test_annotation_count}\n\n")

            f.write(f">>>>>>>>>>>>>>> Validation Image Data Counts <<<<<<<<<<<<<<<<\n")
            f.write(f"Total validation images: {val_image_count}\n")
            f.write(f"Total validation annotations: {val_annotation_count}\n")

        logger.info(f"Data validation status written to {status_path.resolve()}")
        return any([train_image_count, train_annotation_count, test_image_count, test_annotation_count, val_image_count, val_annotation_count])
