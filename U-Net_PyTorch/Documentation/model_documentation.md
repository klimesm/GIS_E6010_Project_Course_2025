# `model.py` — DitchNet Segmentation Model

`model.py` defines **DitchNet**, a PyTorch Lightning–based U-Net segmentation model used to predict ditch probability maps from 2-channel input features (HPMF + ISI).  
The module includes the model architecture, loss function, evaluation metrics, and optimizer/scheduler configuration.

---

## Class: `DitchNet`

### Overview  
A LightningModule wrapping a **U-Net** architecture from `segmentation_models_pytorch`.  
Designed for binary semantic segmentation with strong class imbalance.

### Initialization  
`__init__(encoder_name="efficientnet-b4", pos_weight=3.0, lr=1e-4, in_channels=2)`

The constructor:

- Builds a U-Net with the specified encoder. 
- Sets the number of input channels.
- Configures **weighted BCEWithLogitsLoss** to handle the highly imbalanced ditch vs. background classes.  
- Registers common binary classification metrics:  
  - Accuracy 
  - Recall 
  - Precision 
  - F1-score 
  - Matthews Correlation Coefficient (MCC) 
  - Confusion-matrix stats  
- Stores hyperparameters for checkpointing and reproducibility.

---

### Methods

### `forward(x)`
Runs a forward pass through the U-Net model and returns raw logits.  
Used during training, validation, testing, and inference.

---

### `_shared_step(batch, stage)`
Shared computation used by all training phases. The method:

- receives a batch `(features, labels)`  
- computes logits and sigmoid probabilities  
- calculates weighted BCE loss  
- computes accuracy, recall, precision, F1-score, and MCC  
- logs loss and metrics under phase-prefixed names (`train_*`, `val_*`, `test_*`)  
- logs confusion-matrix components (TP, FP, TN, FN) for validation and test  
- Returns the loss value.

---

### `training_step(batch, batch_idx)`
Runs the shared step in **training** mode.

### `validation_step(batch, batch_idx)`
Runs the shared step in **validation** mode and logs validation metrics.

### `test_step(batch, batch_idx)`
Runs the shared step in **test** mode and logs test metrics.

---

### `configure_optimizers()`
Defines optimization strategy:

- **AdamW** optimizer with weight decay.  
- **ReduceLROnPlateau** scheduler that halves the learning rate when validation loss stops improving. 

Lightning receives both optimizer and scheduler in the expected dictionary format.

---

## Dependencies
- **PyTorch** – model architecture, autograd, optimization  
- **PyTorch Lightning** – handles the training loop, checkpointing, and logging
- **segmentation_models_pytorch** – U-Net implementation with configurable encoders  
- **torchmetrics** – binary evaluation metrics  
- **PyTorch scheduler** – ReduceLROnPlateau for LR control
