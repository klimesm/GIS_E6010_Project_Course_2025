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


class DitchNet(L.LightningModule):
    def __init__(self, encoder_name="efficientnet-b4", pos_weight=5.0, lr=1e-4, in_channels=2):
        super().__init__()
        self.save_hyperparameters("encoder_name", "pos_weight", "lr", "in_channels")

        self.model = smp.Unet(
            encoder_name=encoder_name,
            encoder_weights=None,
            in_channels=in_channels,
            classes=1
        )

        self.register_buffer("pos_weight", torch.tensor(pos_weight))
        self.bce_loss = nn.BCEWithLogitsLoss(pos_weight=self.pos_weight)

        self.accuracy = BinaryAccuracy()
        self.recall = BinaryRecall()
        self.precision = BinaryPrecision()
        self.f1_score = BinaryF1Score()
        self.mcc = BinaryMatthewsCorrCoef()
        self.stats = BinaryStatScores()

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)

        loss = self.bce_loss(logits, y)

        preds = torch.sigmoid(logits)

        acc = self.accuracy(preds, y)
        rec = self.recall(preds, y)
        prec = self.precision(preds, y)
        f1 = self.f1_score(preds, y)
        mcc = self.mcc(preds, y)

        self.log("train_loss", loss, on_step=False, on_epoch=True, sync_dist=True)
        self.log("train_acc", acc, on_step=False, on_epoch=True, sync_dist=True)
        self.log("train_recall", rec, on_step=False, on_epoch=True, sync_dist=True)
        self.log("train_prec", prec, on_step=False, on_epoch=True, sync_dist=True)
        self.log("train_f1", f1, on_step=False, on_epoch=True, sync_dist=True)
        self.log("train_mcc", mcc, on_step=False, on_epoch=True, sync_dist=True)

        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)

        loss = self.bce_loss(logits, y)

        preds = torch.sigmoid(logits)

        acc = self.accuracy(preds, y)
        rec = self.recall(preds, y)
        prec = self.precision(preds, y)
        f1 = self.f1_score(preds, y)
        mcc = self.mcc(preds, y)

        self.log("val_loss", loss, on_step=False, on_epoch=True, sync_dist=True)
        self.log("val_acc", acc, on_step=False, on_epoch=True, sync_dist=True)
        self.log("val_recall", rec, on_step=False, on_epoch=True, sync_dist=True)
        self.log("val_prec", prec, on_step=False, on_epoch=True, sync_dist=True)
        self.log("val_f1", f1, on_step=False, on_epoch=True, sync_dist=True)
        self.log("val_mcc", mcc, on_step=False, on_epoch=True, sync_dist=True)

        tp, fp, tn, fn, _ = self.stats(preds, y)

        self.log("val_tp", tp.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)
        self.log("val_fp", fp.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)
        self.log("val_tn", tn.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)
        self.log("val_fn", fn.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)

    def test_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)

        loss = self.bce_loss(logits, y)

        preds = torch.sigmoid(logits)

        acc = self.accuracy(preds, y)
        rec = self.recall(preds, y)
        prec = self.precision(preds, y)
        f1 = self.f1_score(preds, y)
        mcc = self.mcc(preds, y)

        self.log("test_loss", loss, on_step=False, on_epoch=True, sync_dist=True)
        self.log("test_acc", acc, on_step=False, on_epoch=True, sync_dist=True)
        self.log("test_recall", rec, on_step=False, on_epoch=True, sync_dist=True)
        self.log("test_prec", prec, on_step=False, on_epoch=True, sync_dist=True)
        self.log("test_f1", f1, on_step=False, on_epoch=True, sync_dist=True)
        self.log("test_mcc", mcc, on_step=False, on_epoch=True, sync_dist=True)

        tp, fp, tn, fn, _ = self.stats(preds, y)

        self.log("test_tp", tp.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)
        self.log("test_fp", fp.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)
        self.log("test_tn", tn.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)
        self.log("test_fn", fn.float(), on_step=False, on_epoch=True, reduce_fx="sum", sync_dist=True)

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.hparams.lr, weight_decay=1e-4)

        scheduler = ReduceLROnPlateau(optimizer,
                                      mode="min",
                                      factor=0.5,
                                      patience=5,
                                      cooldown=2,
                                      min_lr=1e-7,
                                      threshold=1e-3,
                                      threshold_mode="rel")

        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val_loss"
            }
        }
