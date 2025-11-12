import argparse

import lightning as L
from torch.utils.data import DataLoader
from pytorch_lightning.loggers import CSVLogger

import os
from pathlib import Path

import albumentations as A
from albumentations.pytorch import ToTensorV2

from model import DitchNet
from train import DitchDataset


class Test:
    def __init__(self, model_path, feature_dir, label_dir,
                 batch_size=4, num_workers=0, compute_precision="32-true"):

        self.model = DitchNet.load_from_checkpoint(model_path)
        self.X_test, self.y_test = self._construct_test_set(feature_dir, label_dir)

        self.test_transform = A.Compose([ToTensorV2()],
                                        additional_targets={"label": "mask"})

        self.test_dataloader = self._construct_dataloader(batch_size, num_workers)

        self.logger = CSVLogger(save_dir=Path.cwd() / "lightning_logs", name="test_logs")

        self.compute_precision = compute_precision

    @staticmethod
    def _construct_test_set(feature_dir, label_dir):
        # Resolve and sort all feature and label paths
        X = sorted(Path(feature_dir).resolve().iterdir())
        y = sorted(Path(label_dir).resolve().iterdir())

        if len(X) != len(y):
            raise ValueError("Feature and label directories must contain the same number of files.")

        return X, y

    def _construct_dataloader(self, batch_size, num_workers):
        # Dataset and DataLoader construction
        test_dataset = DitchDataset(X=self.X_test, y=self.y_test, transform=self.test_transform)

        test_dataloader = DataLoader(test_dataset,
                                     batch_size=batch_size,
                                     num_workers=num_workers,
                                     persistent_workers=(num_workers > 0),
                                     pin_memory=True)

        return test_dataloader

    def run(self):
        trainer = L.Trainer(accelerator="auto",
                            devices="auto",
                            strategy="auto",
                            logger=self.logger,
                            precision=self.compute_precision)

        trainer.test(self.model, self.test_dataloader)


class Main:
    def __init__(self):
        self.args = self._parse_arguments()
        self.tester = Test(self.args.model_path,
                           self.args.feature_dir,
                           self.args.label_dir,
                           batch_size=self.args.batch_size,
                           num_workers=self.args.num_workers,
                           compute_precision=self.args.compute_precision)
        self.run()

    @staticmethod
    def _parse_arguments():
        parser = argparse.ArgumentParser(description="Test the trained DitchNet segmentation model.")

        parser.add_argument("model_path", help="Path to the trained DitchNet model (.ckpt file).")

        parser.add_argument("feature_dir", help="Path to directory containing input feature images.")
        parser.add_argument("label_dir", help="Path to directory containing label (mask) images.")

        parser.add_argument("--batch_size", type=int, default=4, help="Batch size for testing.")

        parser.add_argument("--num_workers", type=int, default=0,
                            help="Number of parallel CPU workers used for loading batches from disk.")

        parser.add_argument("--compute_precision",
                            choices=["16-true", "16-mixed",
                                     "bf16-true", "bf16-mixed",
                                     "32-true", "64-true",
                                     "64", "32", "16", "bf16"],

                            default="32-true",
                            help="Computation precision for testing. More information: "
                                 "https://lightning.ai/docs/pytorch/stable/common/precision_basic.html")

        return parser.parse_args()

    def run(self):
        self.tester.run()


if __name__ == "__main__":
    Main()
