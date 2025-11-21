from dataclasses import dataclass
from typing import Literal
from pathlib import Path


@dataclass
class PreprocessingConfig:
    input_dem_dir: Path
    label_vector_data: Path
    output_dir: Path
    mode: Literal["train", "test"] = "train"
    label_hpmf_threshold: float = -0.075


@dataclass
class ModelConfig:
    encoder_name: str = "efficientnet-b4"
    pos_weight: float = 3.0
    lr: float = 1e-7
    in_channels: int = 2
    weight_decay: float = 1e-4

    use_scheduler: bool = True
    scheduler_monitor: str = "val_loss"
    scheduler_mode: Literal["min", "max"] = "min"
    scheduler_factor: float = 0.5
    scheduler_patience: int = 5
    scheduler_cooldown: int = 5
    scheduler_min_lr: float = 1e-7
    scheduler_threshold: float = 1e-3
    scheduler_threshold_mode: Literal["rel", "abs"] = "rel"


@dataclass
class TrainConfig:
    feature_dir: Path
    label_dir: Path
    max_epochs: int
    model_seed: int = 14
    encoder_name: str = "efficientnet-b4"
    pos_weight: float = 3.0
    val_size: float = 0.2
    batch_size: int = 4
    num_workers: int = 0
    compute_precision: str = "32-true"
    model_config: ModelConfig = ModelConfig()


@dataclass
class TestConfig:
    model_path: Path
    feature_dir: Path
    label_dir: Path
    batch_size: int = 4
    num_workers: int = 0
    compute_precision: str = "32-true"


@dataclass
class InferenceConfig:
    model_dir: Path
    input_dem_dir: Path
    output_dir: Path
    threshold: float = 0.3
    output_prob_map: bool = True
    output_binary_map: bool = True
    output_depth_map: bool = True
    device: str = "auto"
