import subprocess
from PySide6.QtCore import QThread, Signal

class TrainingWorker(QThread):
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
                self.config["feature_dir"],
                self.config["label_dir"],
                str(self.config["max_epochs"]),
                "--batch_size", str(self.config["batch_size"]),
                "--num_workers", str(self.config["num_workers"]),
                "--compute_precision", self.config["compute_precision"],
                "--encoder_name", self.config["encoder_name"],
                "--pos_weight", str(self.config["pos_weight"]),
                "--learning_rate", str(self.config["learning_rate"]),
                "--weight_decay", str(self.config["weight_decay"]),
                "--in_channels", str(self.config["in_channels"]),
            ]

            if self.config["ckpt_path"] and self.config["ckpt_path"].strip():
                cmd.extend(["--ckpt_path", self.config["ckpt_path"]])

            if not self.config["use_scheduler"]:
                cmd.append("--no_scheduler")
            else:
                cmd.extend(["--scheduler_monitor", self.config["scheduler_monitor"]])
                cmd.extend(["--scheduler_mode", self.config["scheduler_mode"]])
                cmd.extend(["--scheduler_patience", str(self.config["scheduler_patience"])])
                cmd.extend(["--scheduler_factor", str(self.config["scheduler_factor"])])
                cmd.extend(["--scheduler_cooldown", str(self.config["scheduler_cooldown"])])
                cmd.extend(["--scheduler_min_lr", str(self.config["scheduler_min_lr"])])
                cmd.extend(["--scheduler_threshold", str(self.config["scheduler_threshold"])])
                cmd.extend(["--scheduler_threshold_mode", self.config["scheduler_threshold_mode"]])

            cmd.extend(["--val_size", str(self.config["val_size"])])
            cmd.extend(["--save_top_k", str(self.config["save_top_k"])])
            cmd.extend(["--checkpoint_monitor", self.config["checkpoint_monitor"]])
            cmd.extend(["--checkpoint_mode", self.config["checkpoint_mode"]])

            if self.config["save_full_checkpoint"]:
                cmd.append("--full_checkpoint")

            if not self.config["use_early_stop"]:
                cmd.append("--no_early_stop")
            else:
                cmd.extend(["--early_stop_patience", str(self.config["early_stop_patience"])])
                cmd.extend(["--early_stop_monitor", self.config["early_stop_monitor"]])
                cmd.extend(["--early_stop_mode", self.config["early_stop_mode"]])

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