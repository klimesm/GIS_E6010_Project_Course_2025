# `test.py` — Model Evaluation for DitchNet

## Overview
`test.py` handles the **evaluation process** for the DitchNet segmentation model. It loads a trained model 
checkpoint from `train.py`, prepares the test dataset using the same preprocessing and dataset pipeline, 
and computes validation metrics.

---

## Class: `Test`
Encapsulates all functionality required to evaluate the trained DitchNet model.

### Initialization
```python
Test(
    feature_dir,             # directory containing test feature chips (.tif)
    label_dir,               # directory containing test label chips (.tif)
    checkpoint_path,         # path to trained model checkpoint (.ckpt)
    batch_size=4,
    num_workers=0,
    compute_precision="32-true"
)
```

### Main Responsibilities
- Loads the test dataset using `DitchDataset` for consistent preprocessing.  
- Loads the trained model checkpoint from disk.  
- Creates a DataLoader for evaluation.  
- Runs model evaluation using PyTorch Lightning’s `Trainer`.  
- Logs final metrics and results.

---

### Methods

#### `_construct_test_set(feature_dir, label_dir)`
- Resolves and sorts all feature and label chip paths.  
- Validates that both directories contain the same number of `.tif` files.

#### `_construct_dataloader(batch_size, num_workers)`
- Loads the feature and label chip pairs into a PyTorch `DataLoader`.  
- Maintains deterministic order and disables augmentations.  
- Supports pinned memory and parallel workers for faster loading.

#### `run()`
- Builds a PyTorch Lightning `Trainer` with automatic device selection (CPU/GPU). 
- Runs evaluation. 
- Logs metrics to CSV via `CSVLogger` in `lightning_logs/test_logs`.  
- Prints final metrics (loss, MCC, etc.) to console.

---

## Class: `Main`
Provides a **command-line interface (CLI)** for running model evaluation directly from the terminal.

### Arguments
| Argument | Type | Description |
|-----------|------|-------------|
| `feature_dir` | Path | Directory containing test feature chips. |
| `label_dir` | Path | Directory containing test label chips. |
| `checkpoint_path` | Path | Path to trained model checkpoint (.ckpt) produced by `train.py`. |
| `--batch_size` | int | Batch size for evaluation. Default: `4`. |
| `--num_workers` | int | Number of CPU workers for data loading. Default: `0`. |
| `--compute_precision` | str | Computation precision (`16-mixed`, `32-true`, etc.). Default: `"32-true"`. |

---

## Output
Test produces:
- A `lightning_logs/test_logs/` directory containing CSV logs of metrics and losses.
- `hparams.yaml` file storing the hyperparameters and configuration used during evaluation.

Example structure:
```
script_root\
└── lightning_logs\
    └── test_logs\
        └── version_0\
            ├── metrics.csv
            ├── hparams.yaml

```

---

## Example Usage
```bash
python test.py   ./dataset_output/test_data/feature_chips   ./dataset_output/test_data/label_chips   ./lightning_logs/train_logs/version_0/checkpoints/epoch=005-val_mcc=0.74.ckpt   --batch_size 4   --compute_precision 16-mixed
```

Both **relative** and **absolute** paths are supported for all arguments.  
The script evaluates the model using the given checkpoint and logs results automatically.

---

## Dependencies
- **PyTorch Lightning**: provides the structured evaluation workflow and logging.  
- **Albumentations**: ensures consistent preprocessing during testing.  
- **Segmentation Models PyTorch (smp)**: defines the model architecture and encoder.  
- **preprocessing.py**: provides `DitchDataset`, which handles feature–label loading.
- **model.py**: defines the DitchNet architecture used for evaluation.
