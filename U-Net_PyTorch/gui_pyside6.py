import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit, QDoubleSpinBox
)
from PySide6.QtCore import QThread, Signal


class BackendWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal()

    def __init__(self, python_exec, backend_script,
                 model_path, input_dir, output_dir,
                 threshold, prob_map, class_map, depth_map):
        super().__init__()
        self.python_exec = python_exec
        self.backend_script = backend_script
        self.model_path = model_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.threshold = threshold
        self.prob_map = prob_map
        self.class_map = class_map
        self.depth_map = depth_map

    def run(self):
        try:
            args = [
                self.python_exec,
                self.backend_script,
                self.model_path,
                self.input_dir,
                self.output_dir,
                "--threshold", str(self.threshold)
            ]

            if not self.prob_map:
                args.append("--no_prob_map")
            if not self.class_map:
                args.append("--no_class_map")
            if not self.depth_map:
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


class GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DitchNet – GUI")
        self.setFixedWidth(600)

        layout = QVBoxLayout()

        # path to python in conda env (backend env)
        layout.addWidget(QLabel("Backend python interpreter (conda env):"))
        self.python_exec = QLineEdit()
        layout.addWidget(self.python_exec)
        btn = QPushButton("Browse python interpreter (python.exe)")
        btn.clicked.connect(self.select_python)
        layout.addWidget(btn)

        # backend script path
        layout.addWidget(QLabel("Backend script (inference.py):"))
        self.backend_script = QLineEdit()
        layout.addWidget(self.backend_script)
        btn = QPushButton("Browse script")
        btn.clicked.connect(self.select_script)
        layout.addWidget(btn)

        # model
        layout.addWidget(QLabel("Model (.ckpt):"))
        self.model_path = QLineEdit()
        layout.addWidget(self.model_path)
        btn = QPushButton("Browse model")
        btn.clicked.connect(self.select_model)
        layout.addWidget(btn)

        # input dir
        layout.addWidget(QLabel("Input DEM directory:"))
        self.dem_path = QLineEdit()
        layout.addWidget(self.dem_path)
        btn = QPushButton("Browse input directory")
        btn.clicked.connect(self.select_dem)
        layout.addWidget(btn)

        # output dir
        layout.addWidget(QLabel("Output directory:"))
        self.out_path = QLineEdit()
        layout.addWidget(self.out_path)
        btn = QPushButton("Browse output directory")
        btn.clicked.connect(self.select_output)
        layout.addWidget(btn)

        # threshold
        box = QHBoxLayout()
        box.addWidget(QLabel("Threshold:"))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.0, 1.0)
        self.threshold.setValue(0.3)
        box.addWidget(self.threshold)
        layout.addLayout(box)

        # checkboxes
        self.cb_prob = QCheckBox("Generate probability map")
        self.cb_prob.setChecked(True)
        layout.addWidget(self.cb_prob)

        self.cb_class = QCheckBox("Generate classified map")
        self.cb_class.setChecked(True)
        layout.addWidget(self.cb_class)

        self.cb_depth = QCheckBox("Generate depth map")
        self.cb_depth.setChecked(True)
        layout.addWidget(self.cb_depth)

        # run buttom
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_prediction)
        layout.addWidget(self.run_btn)

        # log window
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        layout.addWidget(self.log)

        self.setLayout(layout)

    def log_write(self, text):
        self.log.append(text)
        self.log.ensureCursorVisible()

    # file dialogs
    def select_python(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select python interpreter (python.exe)", "", "Python (python.exe)")
        if file:
            self.python_exec.setText(file)

    def select_script(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select backend script", "", "Python (*.py)")
        if file:
            self.backend_script.setText(file)

    def select_model(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select model", "", "Checkpoint (*.ckpt)")
        if file:
            self.model_path.setText(file)

    def select_dem(self):
        folder = QFileDialog.getExistingDirectory(self)
        if folder:
            self.dem_path.setText(folder)

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self)
        if folder:
            self.out_path.setText(folder)

    def run_prediction(self):
        if not (
            os.path.isfile(self.python_exec.text()) and
            os.path.isfile(self.backend_script.text()) and
            os.path.isfile(self.model_path.text()) and
            os.path.isdir(self.dem_path.text()) and
            os.path.isdir(self.out_path.text())
        ):
            self.log_write(" Missing required paths!")
            return

        self.run_btn.setEnabled(False)
        self.log_write(" Running backend...\n")

        self.worker = BackendWorker(
            python_exec=self.python_exec.text(),
            backend_script=self.backend_script.text(),
            model_path=self.model_path.text(),
            input_dir=self.dem_path.text(),
            output_dir=self.out_path.text(),
            threshold=self.threshold.value(),
            prob_map=self.cb_prob.isChecked(),
            class_map=self.cb_class.isChecked(),
            depth_map=self.cb_depth.isChecked()
        )

        self.worker.log_signal.connect(self.log_write)
        self.worker.done_signal.connect(lambda: self.run_btn.setEnabled(True))
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())
