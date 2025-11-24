import subprocess
from PySide6.QtCore import QThread, Signal


class InferenceWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal()

    def __init__(self,
                 python_exec,
                 script,
                 model_dir,
                 input_dem_dir,
                 output_dir,
                 threshold,
                 output_prob_map,
                 output_binary_map,
                 output_depth_map,
                 device):

        super().__init__()

        self.python_exec = python_exec
        self.script = script

        # GUI inputs
        self.model_dir = model_dir
        self.input_dem_dir = input_dem_dir
        self.output_dir = output_dir

        self.threshold = threshold
        self.output_prob_map = output_prob_map
        self.output_binary_map = output_binary_map
        self.output_depth_map = output_depth_map
        self.device = device

    def run(self):
        try:

            # DUMMY VALUES – backend si reálné načte sám z YAML
            encoder_name = "auto"
            in_channels = "2"

            args = [
                self.python_exec,
                self.script,
                encoder_name,
                in_channels,
                self.model_dir,
                self.input_dem_dir,
                self.output_dir,
                "--threshold", str(self.threshold),
                "--device", self.device
            ]

            if not self.output_prob_map:
                args.append("--no_prob_map")
            if not self.output_binary_map:
                args.append("--no_binary_map")
            if not self.output_depth_map:
                args.append("--no_depth_map")

            # Debug print
            self.log_signal.emit("ARGS: " + " ".join(args))

            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                self.log_signal.emit(line.rstrip())

            process.wait()

            if process.returncode == 0:
                self.log_signal.emit("Done")
            else:
                self.log_signal.emit(f"Backend exited with code {process.returncode}")

        except Exception as e:
            self.log_signal.emit(f"ERROR: {str(e)}")

        self.done_signal.emit()
