import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit, QDoubleSpinBox, QComboBox
)
from PySide6.QtCore import QThread, Signal, QSettings


class BackendWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal()

    def __init__(self, python_exec, backend_script,
                 model_path, input_dir, output_dir,
                 threshold, prob_map, binary_map, depth_map):
        super().__init__()
        self.python_exec = python_exec
        self.backend_script = backend_script
        self.model_path = model_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.threshold = threshold
        self.prob_map = prob_map
        self.binary_map = binary_map
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
            if not self.binary_map:
                args.append("--no_binary_map")
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
        self.settings = QSettings("DitchNet", "GUI")
        layout = QVBoxLayout()

        # path to python in conda env (backend env)
        layout.addWidget(QLabel("Backend python interpreter (conda env):"))
        row = QHBoxLayout()

        self.python_exec = QComboBox()
        self.python_exec.setEditable(True)
        self.python_exec.setMinimumWidth(350)
        row.addWidget(self.python_exec)
        row.addStretch()

        # Fill from conda envs
        for exe in self.find_conda_pythons():
            self.python_exec.addItem(exe)
        # Load saved value
        saved = self.settings.value("python_exec", "")
        if saved:
            self.python_exec.setCurrentText(saved)

        # Browse button
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.select_python)
        row.addWidget(browse_btn)

        layout.addLayout(row)

        # backend script path
        layout.addWidget(QLabel("Backend script (inference.py):"))
        row = QHBoxLayout()
        self.backend_script = QLineEdit()
        self.backend_script.setText(self.settings.value("backend_script", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_script)
        row.addWidget(self.backend_script)
        row.addWidget(btn)
        layout.addLayout(row)

        # model dir
        layout.addWidget(QLabel("Model directory:"))
        row = QHBoxLayout()
        self.model_path = QLineEdit()
        self.model_path.setText(self.settings.value("model_path", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_model)
        row.addWidget(self.model_path)
        row.addWidget(btn)
        layout.addLayout(row)

        # input dir
        layout.addWidget(QLabel("Input DEM directory:"))
        row = QHBoxLayout()
        self.dem_path = QLineEdit()
        self.dem_path.setText(self.settings.value("dem_path", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_dem)
        row.addWidget(self.dem_path)
        row.addWidget(btn)
        layout.addLayout(row)

        # output dir
        layout.addWidget(QLabel("Output directory:"))
        row = QHBoxLayout()
        self.out_path = QLineEdit()
        self.out_path.setText(self.settings.value("out_path", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_output)
        row.addWidget(self.out_path)
        row.addWidget(btn)
        layout.addLayout(row)

        # threshold
        box = QHBoxLayout()
        box.addWidget(QLabel("Threshold:"))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.0, 1.0)
        self.threshold.setValue(float(self.settings.value("threshold", 0.3)))
        self.threshold.setSingleStep(0.05)
        box.addWidget(self.threshold)
        layout.addLayout(box)

        # checkboxes
        self.cb_prob = QCheckBox("Generate probability map")
        self.cb_prob.setChecked(self.settings.value("prob_map", "true") == "true")
        layout.addWidget(self.cb_prob)

        self.cb_class = QCheckBox("Generate binary map")
        self.cb_class.setChecked(self.settings.value("binary_map", "true") == "true")
        layout.addWidget(self.cb_class)

        self.cb_depth = QCheckBox("Generate depth map")
        self.cb_depth.setChecked(self.settings.value("depth_map", "true") == "true")
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

        # add tooltips and help
        self.python_exec.setToolTip("Path to python.exe from the backend conda environment (containing necessary ML libraries).")
        self.backend_script.setToolTip("Select inference.py or train (maybe we will addd)")
        self.model_path.setToolTip("Folder containing one or more trained .ckpt model files.")
        self.dem_path.setToolTip("Folder containing input DEM files.")
        self.out_path.setToolTip("Folder where results will be saved.")
        self.threshold.setToolTip("Probability threshold (0–1).")
        self.cb_prob.setToolTip("Generate probability map.")
        self.cb_class.setToolTip("Generate binary map.")
        self.cb_depth.setToolTip("Generate depth map.")

    def save(self):
        self.settings.setValue("python_exec", self.python_exec.currentText())
        self.settings.setValue("backend_script", self.backend_script.text())
        self.settings.setValue("model_path", self.model_path.text())
        self.settings.setValue("dem_path", self.dem_path.text())
        self.settings.setValue("out_path", self.out_path.text())
        self.settings.setValue("threshold", self.threshold.value())
        self.settings.setValue("prob_map", "true" if self.cb_prob.isChecked() else "false")
        self.settings.setValue("binary_map", "true" if self.cb_class.isChecked() else "false")
        self.settings.setValue("depth_map", "true" if self.cb_depth.isChecked() else "false")

    def log_write(self, text):
        self.log.append(text)
        self.log.ensureCursorVisible()

    # file dialogs
    def select_python(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select python interpreter (python.exe)", "", "Python (python.exe)")
        if file:
            self.python_exec.setEditText(file)
            self.save()

    def select_script(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select backend script", "", "Python (*.py)")
        if file:
            self.backend_script.setText(file)
            self.save()

    def select_model(self):
        folder = QFileDialog.getExistingDirectory(self)
        if folder:
            self.model_path.setText(folder)
            self.save()

    def select_dem(self):
        folder = QFileDialog.getExistingDirectory(self)
        if folder:
            self.dem_path.setText(folder)
            self.save()

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self)
        if folder:
            self.out_path.setText(folder)
            self.save()

    def run_prediction(self):
        self.save()
        if not (
            os.path.isfile(self.python_exec.currentText()) and
            os.path.isfile(self.backend_script.text()) and
            os.path.isdir(self.model_path.text()) and
            os.path.isdir(self.dem_path.text()) and
            os.path.isdir(self.out_path.text())
        ):
            self.log_write(" Missing required paths!")
            return

        self.run_btn.setEnabled(False)
        self.log_write(" Running backend...\n")

        self.worker = BackendWorker(
            python_exec=self.python_exec.currentText(),
            backend_script=self.backend_script.text(),
            model_path=self.model_path.text(),
            input_dir=self.dem_path.text(),
            output_dir=self.out_path.text(),
            threshold=self.threshold.value(),
            prob_map=self.cb_prob.isChecked(),
            binary_map=self.cb_class.isChecked(),
            depth_map=self.cb_depth.isChecked()
        )

        self.worker.log_signal.connect(self.log_write)
        self.worker.done_signal.connect(lambda: self.run_btn.setEnabled(True))
        self.worker.start()

    def find_conda_pythons(self):
        python_paths = []

        user = os.getenv("USERNAME") or ""
        user_dirs = [
            rf"C:\Users\{user}\anaconda3\envs",
            rf"C:\Users\{user}\miniconda3\envs"
        ]

        programdata_dirs = [
            r"C:\ProgramData\Anaconda3\envs",
            r"C:\ProgramData\Miniconda3\envs"
        ]

        custom_dirs = [
            r"C:\conda\envs"
        ]

        search_dirs = user_dirs + programdata_dirs + custom_dirs

        for root in search_dirs:
            if not os.path.isdir(root):
                continue

            for env_name in os.listdir(root):
                python_exe = os.path.join(root, env_name, "python.exe")
                if os.path.isfile(python_exe):
                    python_paths.append(python_exe)

        # Remove duplicates while preserving order
        return list(dict.fromkeys(python_paths))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())
