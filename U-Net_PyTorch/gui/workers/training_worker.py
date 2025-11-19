import subprocess
import os

from PySide6.QtCore import QThread, Signal


class TrainingWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal(bool)

    def __init__(self, feature_dir, label_dir, max_epochs, encoder_name,
                 pos_weight, batch_size, num_workers, compute_precision, conda_python):
        super().__init__()

        self.feature_dir = feature_dir
        self.label_dir = label_dir
        self.max_epochs = max_epochs
        self.encoder_name = encoder_name
        self.pos_weight = pos_weight
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.compute_precision = compute_precision
        self.conda_python = conda_python

        # path to train.py
        script_path = os.path.join(os.path.dirname(__file__), "..", "..", "train.py")
        self.train_script = os.path.abspath(script_path)

    def run(self):
        try:
            cmd = [
                self.conda_python,
                self.train_script,
                self.feature_dir,
                self.label_dir,
                str(self.max_epochs),
                "--encoder_name", self.encoder_name,
                "--pos_weight", str(self.pos_weight),
                "--batch_size", str(self.batch_size),
                "--num_workers", str(self.num_workers),
                "--compute_precision", self.compute_precision,
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            for line in process.stdout:
                self.log_signal.emit(line.rstrip())

            success = process.wait() == 0
            self.done_signal.emit(success)

        except Exception as e:
            self.log_signal.emit(str(e))
            self.done_signal.emit(False)
