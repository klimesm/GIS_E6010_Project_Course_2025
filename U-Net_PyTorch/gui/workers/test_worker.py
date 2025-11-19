import subprocess
import os

from PySide6.QtCore import QThread, Signal


class TestWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal()

    def __init__(self, model_path, feature_dir, label_dir,
                 batch_size, num_workers, compute_precision,
                 conda_python):
        super().__init__()

        self.model_path = model_path
        self.feature_dir = feature_dir
        self.label_dir = label_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.compute_precision = compute_precision
        self.conda_python = conda_python

        # Relative path to test.py
        script_path = os.path.join(os.path.dirname(__file__), "..", "..", "test.py")
        self.test_script = os.path.abspath(script_path)

    def run(self):
        try:
            cmd = [
                self.conda_python,
                self.test_script,
                self.model_path,
                self.feature_dir,
                self.label_dir,
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
