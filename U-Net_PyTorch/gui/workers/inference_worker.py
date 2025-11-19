import subprocess
from PySide6.QtCore import QThread, Signal

class InferenceWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal()

    def __init__(self, python_exec, script, model, inp, out,
                 thr, prob, cls, depth):
        super().__init__()
        self.python_exec = python_exec
        self.script = script
        self.model = model
        self.inp = inp
        self.out = out
        self.thr = thr
        self.prob = prob
        self.cls = cls
        self.depth = depth

    def run(self):
        try:
            args = [
                self.python_exec,
                self.script,
                self.model,
                self.inp,
                self.out,
                "--threshold", str(self.thr)
            ]

            if not self.prob:
                args.append("--no_prob_map")
            if not self.cls:
                args.append("--no_binary_map")
            if not self.depth:
                args.append("--no_depth_map")

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
                self.log_signal.emit(" Done")
            else:
                self.log_signal.emit(f" Backend exited with code {process.returncode}")

        except Exception as e:
            self.log_signal.emit(f" ERROR: {str(e)}")

        self.done_signal.emit()
