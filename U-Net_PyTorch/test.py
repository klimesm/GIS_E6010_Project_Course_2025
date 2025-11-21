import argparse

import lightning as L
from torch.utils.data import DataLoader
from pytorch_lightning.loggers import CSVLogger

from pathlib import Path

import albumentations as A
from albumentations.pytorch import ToTensorV2

from preprocessing import DitchDataset
from model import DitchNet
from utils.config import TestConfig
from utils.cli_args.test_args import add_test_args


class Test:
    def __init__(self, config: TestConfig):
        self.config = config

        self.model = DitchNet.load_from_checkpoint(config.model_path)
        self.X_test, self.y_test = self._construct_test_set(config.feature_dir, config.label_dir)

        self.test_transform = A.Compose([ToTensorV2()],
                                        additional_targets={"label": "mask"})

        self.test_dataloader = self._construct_dataloader(config.batch_size, config.num_workers)

        self.logger = CSVLogger(save_dir=Path.cwd() / "lightning_logs", name="test_logs")

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
                            precision=self.config.compute_precision)

        trainer.test(self.model, self.test_dataloader)


class Main:
    def __init__(self):
        args = self._parse_arguments()
        config = TestConfig(args.model_path,
                            args.feature_dir,
                            args.label_dir,
                            batch_size=args.batch_size,
                            num_workers=args.num_workers,
                            compute_precision=args.compute_precision)

        self.tester = Test(config)
        self.run()

    @staticmethod
    def _parse_arguments():
        parser = argparse.ArgumentParser(description="Test the trained DitchNet segmentation model.")
        add_test_args(parser)

        return parser.parse_args()

    def run(self):
        self.tester.run()


if __name__ == "__main__":
    Main()
