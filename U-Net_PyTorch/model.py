import torch
import torch.nn as nn
import lightning as L

import segmentation_models_pytorch as smp

from torchmetrics.classification import (BinaryAccuracy,
                                         BinaryRecall,
                                         BinaryPrecision,
                                         BinaryF1Score,
                                         BinaryMatthewsCorrCoef,
                                         BinaryStatScores)

from torch.optim.lr_scheduler import ReduceLROnPlateau

L.seed_everything(14, workers=True)


class DitchNet(L.LightningModule):
    def __init__(self, encoder_name="efficientnet-b4", pos_weight=3.0, lr=1e-4, in_channels=2):
        super().__init__()
        self.save_hyperparameters("encoder_name", "pos_weight", "lr", "in_channels")

        # U-Net segmentation model from segmentation_models_pytorch
        self.model = smp.Unet(
            encoder_name=encoder_name,
            encoder_weights=None,
            in_channels=in_channels,
            classes=1
        )

        # Weighted BCE loss to compensate for severe class imbalance (few ditch pixels vs large background)
        self.register_buffer("pos_weight", torch.tensor(pos_weight))
        self.bce_loss = nn.BCEWithLogitsLoss(pos_weight=self.pos_weight)

        # Define evaluation metrics for binary classification
        self.accuracy = BinaryAccuracy()
        self.recall = BinaryRecall()
        self.precision = BinaryPrecision()
        self.f1_score = BinaryF1Score()
        self.mcc = BinaryMatthewsCorrCoef()
        self.stats = BinaryStatScores()

    def forward(self, x):
        # Forward pass through the segmentation model
        return self.model(x)

    def _shared_step(self, batch, stage):
        # Common step for training, validation, and testing phases
        x, y = batch
        logits = self(x)
        predictions = torch.sigmoid(logits)
        loss = self.bce_loss(logits, y)

        # Compute performance metrics
        metrics = {
            "loss": loss,
            "acc": self.accuracy(predictions, y),
            "recall": self.recall(predictions, y),
            "prec": self.precision(predictions, y),
            "f1": self.f1_score(predictions, y),
            "mcc": self.mcc(predictions, y)
        }

        # Log key metrics for the current phase (averaged over the epoch)
        for name, value in metrics.items():
            self.log(f"{stage}_{name}", value, prog_bar=(name == "loss"), on_step=False, on_epoch=True, sync_dist=True)

        # Log confusion matrix elements for validation and test only
        if stage in ("val", "test"):
            tp, fp, tn, fn, _ = self.stats(predictions, y)
            for name, value in zip(("tp", "fp", "tn", "fn"), (tp, fp, tn, fn)):
                self.log(f"{stage}_{name}", value.float(), on_step=False, on_epoch=True,
                         reduce_fx="sum", sync_dist=True)

        return loss

    # Lightning calls these once per phase,
    # each receives a batch (features, labels) from the DataLoader
    # and an index (batch_idx) assigned by the training loop
    def training_step(self, batch, batch_idx):
        return self._shared_step(batch, "train")

    def validation_step(self, batch, batch_idx):
        self._shared_step(batch, "val")

    def test_step(self, batch, batch_idx):
        self._shared_step(batch, "test")

    def configure_optimizers(self):
        # AdamW optimizer with mild weight decay for stability
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.hparams.lr, weight_decay=1e-4)

        # Reduce learning rate when validation loss plateaus
        scheduler = ReduceLROnPlateau(optimizer,
                                      mode="min",
                                      factor=0.5,
                                      patience=5,
                                      cooldown=2,
                                      min_lr=1e-7,
                                      threshold=1e-3,
                                      threshold_mode="rel")

        # Return both optimizer and scheduler to Lightning
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val_loss"
            }
        }
