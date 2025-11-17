import argparse

import lightning as L
from torch.utils.data import DataLoader
from pytorch_lightning.loggers import CSVLogger
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping
import segmentation_models_pytorch as smp

from pathlib import Path

import albumentations as A
from albumentations.pytorch import ToTensorV2

from sklearn.model_selection import train_test_split

from preprocessing import DitchDataset
from model import DitchNet

L.seed_everything(14, workers=True)


class Train:
    def __init__(self, feature_dir, label_dir, max_epochs,
                 encoder_name="efficientnet-b4",
                 pos_weight=3, batch_size=4,
                 num_workers=0, compute_precision="32-true"):

        # Initialize the segmentation model
        self.model = DitchNet(encoder_name=encoder_name, pos_weight=pos_weight)
        self.max_epochs = max_epochs

        # Split dataset into training and validation sets
        self.X_train, self.X_val, self.y_train, self.y_val = self._construct_train_val_sets(feature_dir, label_dir)

        # Define augmentation and preprocessing pipelines
        self.train_transform, self.val_transform = self._construct_transforms()

        # Create PyTorch DataLoaders for training and validation
        self.train_dataloader, self.validation_dataloader = self._construct_dataloaders(batch_size, num_workers)

        # Initialize logger and callbacks for model tracking and checkpointing
        self.logger = CSVLogger(save_dir=Path.cwd() / "lightning_logs", name="train_logs")
        self.callbacks = self._set_callbacks()

        # Defines the computation precision used by the Trainer
        # (e.g., '16-mixed' for faster mixed precision or '32-true' for full precision)
        self.compute_precision = compute_precision

    @staticmethod
    def _construct_train_val_sets(feature_dir, label_dir):
        # Resolve and sort all feature and label paths
        X = sorted(Path(feature_dir).resolve().iterdir())
        y = sorted(Path(label_dir).resolve().iterdir())

        if len(X) != len(y):
            raise ValueError("Feature and label directories must contain the same number of files.")

        # Split into training and validation sets (80/20)
        return train_test_split(X, y, test_size=0.20, random_state=14)

    @staticmethod
    def _construct_transforms():
        train_transform = A.Compose([A.HorizontalFlip(p=0.5),
                                     A.VerticalFlip(p=0.5),
                                     A.RandomRotate90(p=0.5),
                                     A.Transpose(p=0.2),
                                     ToTensorV2()],
                                    additional_targets={"label": "mask"})

        val_transform = A.Compose([ToTensorV2()],
                                  additional_targets={"label": "mask"})

        return train_transform, val_transform

    def _construct_dataloaders(self, batch_size, num_workers):
        # Dataset and DataLoader construction
        training_dataset = DitchDataset(X=self.X_train, y=self.y_train, transform=self.train_transform)
        validation_dataset = DitchDataset(X=self.X_val, y=self.y_val, transform=self.val_transform)

        training_dataloader = DataLoader(training_dataset,
                                         batch_size=batch_size,
                                         num_workers=num_workers,
                                         persistent_workers=(num_workers > 0),
                                         shuffle=True,
                                         pin_memory=True)

        validation_dataloader = DataLoader(validation_dataset,
                                           batch_size=batch_size,
                                           num_workers=num_workers,
                                           persistent_workers=(num_workers > 0),
                                           pin_memory=True)

        return training_dataloader, validation_dataloader

    @staticmethod
    def _set_callbacks():
        # Save top-performing checkpoints and enable early stopping
        checkpoint = ModelCheckpoint(save_weights_only=True, save_top_k=10, monitor="val_mcc", mode="max")
        early_stop = EarlyStopping(patience=50, monitor="val_loss", mode="min")

        return [checkpoint, early_stop]

    def run(self):
        # Configure the Lightning trainer and launch training
        trainer = L.Trainer(max_epochs=self.max_epochs,
                            accelerator="auto",
                            devices="auto",
                            strategy="auto",
                            callbacks=self.callbacks,
                            logger=self.logger,
                            precision=self.compute_precision)

        trainer.fit(self.model,
                    train_dataloaders=self.train_dataloader,
                    val_dataloaders=self.validation_dataloader)


class Main:
    def __init__(self):
        self.args = self._parse_arguments()
        self.trainer = Train(self.args.feature_dir,
                             self.args.label_dir,
                             self.args.max_epochs,
                             encoder_name=self.args.encoder_name,
                             pos_weight=self.args.pos_weight,
                             batch_size=self.args.batch_size,
                             num_workers=self.args.num_workers,
                             compute_precision=self.args.compute_precision)
        self.run()

    @staticmethod
    def _parse_arguments():
        parser = argparse.ArgumentParser(description="Train the DitchNet segmentation model.")

        parser.add_argument("feature_dir", help="Path to directory containing input feature images.")
        parser.add_argument("label_dir", help="Path to directory containing label (mask) images.")

        parser.add_argument("max_epochs", type=int, help="Maximum number of training epochs to run.")

        parser.add_argument("--encoder_name",
                            default="efficientnet-b4",
                            choices=smp.encoders.get_encoder_names(),
                            help="Encoder backbone for DitchNet. "
                                 "Choices: https://smp.readthedocs.io/en/latest/encoders.html")

        parser.add_argument("--pos_weight",
                            type=float, default=3,
                            help="Weighting factor for positive (ditch) class in the BCE loss to handle imbalance.")

        parser.add_argument("--batch_size", type=int, default=4, help="Batch size for training.")
        parser.add_argument("--num_workers", type=int, default=0,
                            help="Number of parallel CPU workers used for loading batches from disk.")

        parser.add_argument("--compute_precision",
                            choices=["16-true", "16-mixed",
                                     "bf16-true", "bf16-mixed",
                                     "32-true", "64-true",
                                     "64", "32", "16", "bf16"],

                            default="32-true",
                            help="Computation precision for training. More information: "
                                 "https://lightning.ai/docs/pytorch/stable/common/precision_basic.html")

        return parser.parse_args()

    def run(self):
        self.trainer.run()


if __name__ == "__main__":
    Main()
