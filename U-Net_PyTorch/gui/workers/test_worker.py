import subprocess
from PySide6.QtCore import QThread, Signal

class TestWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            cmd = [
                self.config["python_exec"],
                self.config["script"],
                
                self.config["model_path"],
                
                self.config["hparams_path"],
                
                self.config["feature_dir"],
                
                self.config["label_dir"],
                
                "--batch_size", str(self.config["batch_size"]),
                "--num_workers", str(self.config["num_workers"]),
                "--compute_precision", self.config["precision"]
            ]

            self.log_signal.emit(f"CMD: {' '.join(cmd)}\n")

            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True, 
                bufsize=1
            )

            for line in process.stdout:
                self.log_signal.emit(line.rstrip())

            success = process.wait() == 0
            self.done_signal.emit(success)

        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.done_signal.emit(False)