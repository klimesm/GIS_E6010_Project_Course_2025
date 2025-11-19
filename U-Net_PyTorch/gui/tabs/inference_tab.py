import os
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit, QDoubleSpinBox, QComboBox
)
from PySide6.QtCore import QSettings

from workers.inference_worker import InferenceWorker
from utils.conda_scanner import find_conda_pythons

class InferenceTab(QWidget):
    def __init__(self):
        super().__init__()
        # path to inference.py relative to this file
        self.backend_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..","..", "inference.py")
        )
        self.settings = QSettings("DitchNet", "GUI")
        layout = QVBoxLayout()

        # Python interpreter selection
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

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.select_python)
        row.addWidget(browse_btn)
        layout.addLayout(row)

        # --- backend script ---
        # layout.addWidget(QLabel("Backend script (inference.py):"))
        # row = QHBoxLayout()
        # self.backend_script = QLineEdit()
        # self.backend_script.setText(self.settings.value("backend_script", ""))
        # btn = QPushButton("Browse")
        # btn.clicked.connect(self.select_script)
        # row.addWidget(self.backend_script)
        # row.addWidget(btn)
        # layout.addLayout(row)

        # model/models dir path
        layout.addWidget(QLabel("Model directory:"))
        row = QHBoxLayout()
        self.model_path = QLineEdit()
        self.model_path.setText(self.settings.value("model_path", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_model)
        row.addWidget(self.model_path)
        row.addWidget(btn)
        layout.addLayout(row)

        # DEM input dir
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

        # binary map threshold
        box = QHBoxLayout()
        box.addWidget(QLabel("Binary map threshold:"))
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

        # run button
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_prediction)
        layout.addWidget(self.run_btn)

        # log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        layout.addWidget(self.log)

        self.setLayout(layout)

        # tooltips
        self.python_exec.setToolTip("Path to python.exe from the backend conda environment (containing necessary ML libraries).")
        # self.backend_script.setToolTip("Select inference.py or train (maybe we will addd)")
        self.model_path.setToolTip("Folder containing one or more trained .ckpt model files.")
        self.dem_path.setToolTip("Folder containing input DEM files.")
        self.out_path.setToolTip("Folder where results will be saved.")
        self.threshold.setToolTip("Probability threshold (0–1).")
        self.cb_prob.setToolTip("Generate probability map.")
        self.cb_class.setToolTip("Generate binary map.")
        self.cb_depth.setToolTip("Generate depth map.")

    #  save previous choices/paths
    def save(self):
        self.settings.setValue("python_exec", self.python_exec.currentText())
        # self.settings.setValue("backend_script", self.backend_script.text())
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

    def select_python(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select python interpreter (python.exe)", "", "Python (python.exe)")
        if file:
            self.python_exec.setEditText(file)
            self.save()

    # def select_script(self):
    #     file, _ = QFileDialog.getOpenFileName(self, "Select backend script", "", "Python (*.py)")
    #     if file:
    #         self.backend_script.setText(file)
    #         self.save()

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

    # run
    def run_prediction(self):
        self.save()
        if not (
            os.path.isfile(self.python_exec.currentText()) and
            # os.path.isfile(self.backend_script.text()) and
            os.path.isdir(self.model_path.text()) and
            os.path.isdir(self.dem_path.text()) and
            os.path.isdir(self.out_path.text())
        ):
            self.log_write(" Missing required paths!")
            return

        self.run_btn.setEnabled(False)
        self.set_enabled(False)
        self.log_write(" Running backend...\n")

        self.worker = InferenceWorker(
            python_exec=self.python_exec.currentText(),
            script=self.backend_script_path,
            model=self.model_path.text(),
            inp=self.dem_path.text(),
            out=self.out_path.text(),
            thr=self.threshold.value(),
            prob=self.cb_prob.isChecked(),
            cls=self.cb_class.isChecked(),
            depth=self.cb_depth.isChecked()
        )

        self.worker.log_signal.connect(self.log_write)
        self.worker.done_signal.connect(self.on_worker_done)
        self.worker.start()

    def on_worker_done(self):
        self.log_write("\nWorker finished")
        self.run_btn.setEnabled(True)
        self.set_enabled(True)

    def set_enabled(self, state: bool):
        widgets = [
            self.python_exec, self.model_path,
            self.dem_path, self.out_path, self.threshold,
            self.cb_prob, self.cb_class, self.cb_depth
        ]
        for w in widgets:
            w.setEnabled(state)

    # conda scan
    def find_conda_pythons(self):
        return find_conda_pythons()