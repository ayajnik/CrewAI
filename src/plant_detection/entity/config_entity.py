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

@dataclass(frozen=True)
class ModelTrainingConfig:
    root_dir: Path
    trained_model_path: Path
    trained_model_weights: Path
    transformed_train_data: Path  # Source of preprocessed data
    transformed_test_data: Path
    transformed_val_data: Path
    model_name: str
    image_size: tuple
    num_classes: int
    epochs: int
    batch_size: int
    learning_rate: float
    early_stopping_patience: int
    reduce_lr_patience: int
    validation_split: float
    use_class_weights: bool
    freeze_base_layers: bool
    fine_tune_from_layer: int
