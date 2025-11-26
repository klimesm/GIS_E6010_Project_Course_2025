# workers/age_worker.py
import subprocess
from PySide6.QtCore import QThread, Signal


class AgeWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal()

    def __init__(self, python_exec: str, method: str, script_path: str, args: dict):
        """
        python_exec: path to python executable
        method: "vectors" or "rasters"
        script_path: path to the script to run
        args: dictionary with method-specific arguments
        """
        super().__init__()
        self.python_exec = python_exec or "python"
        self.method = method
        self.script_path = script_path
        self.args = args or {}

    def run(self):
        try:
            if self.method == "vectors":
                # Required keys:
                #  probability_map, vector_layers_str, output_vector
                cmd = [
                    self.python_exec,
                    self.script_path,
                    self.args["probability_map"],
                    self.args["vector_layers_str"],
                    self.args["output_vector"],
                    "--prob_threshold", str(self.args.get("prob_threshold", 0.5)),
                    "--min_overlap_length", str(self.args.get("min_overlap_length", 10.0)),
                ]
            elif self.method == "rasters":
                # Required keys:
                #  new_layer_dir, old_layer_dir, output_dir
                cmd = [
                    self.python_exec,
                    self.script_path,
                    self.args["new_layer_dir"],
                    self.args["old_layer_dir"],
                    self.args["output_dir"],
                    "--threshold", str(self.args.get("threshold", 0.5)),
                    "--tolerance", str(self.args.get("tolerance", 2)),
                    "--buffer", str(self.args.get("buffer", 3)),
                ]
            else:
                self.log_signal.emit(f"ERROR: Unknown method '{self.method}'")
                self.done_signal.emit()
                return

            # Emit command for debug (helpful, safe)
            self.log_signal.emit("Running: " + " ".join(cmd))

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Stream output line by line
            for line in process.stdout:
                self.log_signal.emit(line.rstrip())

            process.wait()
            if process.returncode == 0:
                self.log_signal.emit("Done")
            else:
                self.log_signal.emit(f"Backend exited with code {process.returncode}")

        except Exception as e:
            self.log_signal.emit(f"ERROR: {e}")

        self.done_signal.emit()
