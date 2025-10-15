from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataValidationConfig:
    root_dir: Path
    STATUS_FILE: str
    train_data: Path
    test_data: Path
    val_data: Path

@dataclass(frozen=True)
class DataTransformationConfig:
    root_dir: Path
    transformed_train_data: Path
    transformed_test_data: Path
    transformed_val_data: Path
    train_data: Path  # source
    test_data: Path   # source
    val_data: Path    # source
    image_size: tuple
    normalization_method: str
    model_name: str
    color_mode: str
    data_format: str
