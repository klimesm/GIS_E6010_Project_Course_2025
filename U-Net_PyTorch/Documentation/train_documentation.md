# `train.py` — Model Training for DitchNet

## Overview
`train.py` handles the **training process** for the DitchNet segmentation model. It loads the preprocessed 
feature and label chips produced by `preprocessing.py`, builds the dataset, defines augmentations, 
and trains the model using PyTorch Lightning.

---

## Class: `Train`
Encapsulates all functionality required to train the DitchNet model end-to-end.

### Initialization
```python
Train(
    feature_dir,             # directory containing feature chips (.tif)
    label_dir,               # directory containing label chips (.tif)
    max_epochs,              # number of training epochs
    encoder_name="efficientnet-b4",
    pos_weight=3,
    batch_size=4,
    num_workers=0,
    compute_precision="32-true"
)
```

### Main Responsibilities
- Initializes the DitchNet segmentation model with a selected encoder backbone.  
- Loads the dataset from disk using `DitchDataset` from `preprocessing.py`.  
- Splits the dataset into **training** and **validation** subsets (80/20).  
- Defines augmentation pipelines for both sets using **Albumentations**.  
- Creates PyTorch **DataLoaders** for efficient batch loading.  
- Configures callbacks for **checkpoint saving** and **early stopping**.  
- Launches the Lightning `Trainer` to perform the full training process.

---

### Methods

#### `_construct_train_val_sets(feature_dir, label_dir)`
- Resolves and sorts all feature and label chip paths.  
- Validates that both directories contain the same number of `.tif` files.  
- Splits data into 80% training and 20% validation sets using a fixed random seed (`random_state=14`) for reproducibility.

#### `_construct_transforms()`
- Defines two Albumentations transformation pipelines:
  - **Training transform:** includes random flips, rotations, and transpositions to increase dataset diversity.  
  - **Validation transform:** applies only conversion to tensor for consistent evaluation.

#### `_construct_dataloaders(batch_size, num_workers)`
- Wraps both datasets (`training` and `validation`) into `DataLoader` objects.  
- Enables shuffling for training data, memory pinning, and persistent workers for parallel loading.

#### `_set_callbacks()`
- Creates a **ModelCheckpoint** callback to save the 10 best models based on validation MCC score (`val_mcc`).  
- Adds **EarlyStopping** to stop the training if the validation loss does not improve for 15 epochs.

#### `run()`
- Builds a PyTorch Lightning `Trainer` with automatic device selection (CPU/GPU).  
- Launches training with:
  - Defined epoch count  
  - Configured precision (e.g., `"16-mixed"` or `"32-true"`)  
  - Logging to CSV via `CSVLogger` under `lightning_logs/train_logs`  
- Trains until the stopping conditions are met.

---

## Class: `Main`
Provides a **command-line interface (CLI)** for running training directly from the terminal.

### Arguments
| Argument | Type | Description                                                                            |
|-----------|------|----------------------------------------------------------------------------------------|
| `feature_dir` | Path | Directory containing input feature chips.                                              |
| `label_dir` | Path | Directory containing label (mask) chips.                                               |
| `max_epochs` | int | Maximum number of training epochs.                                                     |
| `--encoder_name` | str | Encoder backbone for DitchNet. Default: `efficientnet-b4`.                  |
| `--pos_weight` | int | Weight for the positive (ditch) class to handle class imbalance. Default: `3`.         |
| `--batch_size` | int | Batch size for training. Default: `4`.                                                 |
| `--num_workers` | int | Number of parallel CPU workers for data loading. Default: `0`.                         |
| `--compute_precision` | str | Computation precision for training (`16-mixed`, `32-true`, etc.). Default: `"32-true"`. |

---

## Output
Training produces:
- A `lightning_logs/train_logs/` directory containing CSV logs of metrics and losses.  
- `hparams.yaml` file storing the hyperparameters and configuration used during training.
- A set of model checkpoint files (`.ckpt`) in the working directory corresponding to the top 10 validation MCC scores.

Example structure:
```
script_root\
└── lightning_logs\
    └── train_logs\
        └── version_0\
            ├── metrics.csv
            ├── hparams.yaml
            └── checkpoints\
                ├── epoch=0-step=10.ckpt
                ├── epoch=1-step=20.ckpt
                └── ...

```

---

## Example Usage
```bash
python train.py   ./dataset_output/training_data/feature_chips   ./dataset_output/training_data/label_chips   50   --encoder_name efficientnet-b4   --pos_weight 3   --batch_size 8   --compute_precision 16-mixed
```

Both **relative** and **absolute** paths are supported for all inputs.  

---

## Dependencies
- **PyTorch Lightning**: for structured training, validation, logging, and checkpointing.  
- **Albumentations**: for data augmentation and preprocessing.  
- **Segmentation Models PyTorch (smp)**: defines the model architecture and encoder. 
- **scikit-learn**: used for dataset splitting (`train_test_split`).  
- **preprocessing.py**: provides `DitchDataset`, which handles feature–label loading.  
- **model.py**: defines the DitchNet architecture used for training.  

The trained model checkpoints are later used by **`test.py`** and **`inference.py`** for evaluation and prediction.
