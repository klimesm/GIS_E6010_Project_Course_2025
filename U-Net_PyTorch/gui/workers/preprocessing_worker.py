import subprocess
import os
from PySide6.QtCore import QThread, Signal

class PreprocessingWorker(QThread):
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
                
                self.config["input_dem_dir"],
                self.config["label_vector_data"],
                self.config["output_dir"],

                "--mode", self.config["mode"],
                "--ditch_width", str(self.config["ditch_width"]),
                "--label_hpmf_threshold", str(self.config["label_hpmf_threshold"])
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
            self.log_signal.emit(f"ERROR: {str(e)}")
            self.done_signal.emit(False)