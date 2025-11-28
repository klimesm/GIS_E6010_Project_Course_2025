import os

from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit,
    QDoubleSpinBox, QComboBox, QGroupBox, QTabWidget, QFormLayout
)
from PySide6.QtCore import QSettings

from workers.inference_worker import InferenceWorker
from utils.conda_scanner import find_conda_pythons


class InferenceTab(QWidget):
    def __init__(self):
        super().__init__()

        # path to inference backend
        self.backend_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "inference.py")
        )

        self.settings = QSettings("DEM2Ditch", "GUI")

        main = QVBoxLayout()

        # create Tabs
        tabs = QTabWidget()
        main.addWidget(tabs)

        # Define basic settings tab
        basic_tab = QWidget()
        basic = QVBoxLayout()
        basic_tab.setLayout(basic)

        # Python executable
        self.env_container = QGroupBox("Environment")
        env = QHBoxLayout()
        self.env_container.setLayout(env)
        env.addWidget(QLabel("Python executable:"))
        row = QHBoxLayout()
        self.python_exec = QComboBox()
        self.python_exec.setEditable(True)
        self.python_exec.setToolTip("Path to python executable in conda environment containing all necessary libraries")
        self.python_exec.setMinimumWidth(350)
        row.addWidget(self.python_exec)
        row.addStretch()

        for exe in find_conda_pythons():
            self.python_exec.addItem(exe)

        saved = self.settings.value("python_exec", "")
        if saved:
            self.python_exec.setCurrentText(saved)

        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_python)
        row.addWidget(btn)
        env.addLayout(row)
        basic.addWidget(self.env_container)

        # groupbox for model and data
        data_group = QGroupBox("Model and Data")
        form = QFormLayout()

        # Model dir
        row = QHBoxLayout()
        self.model_path = QLineEdit(self.settings.value("model_path", ""))
        self.model_path.setToolTip("Directory containing one or more LightningDitchNet model checkpoints (*.ckpt) and "
                                   "corresponding hyperparameter files (*.yaml)")
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_model)
        row.addWidget(self.model_path)
        row.addWidget(btn)
        form.addRow("Model directory:",row)

        # DEM input dir
        row = QHBoxLayout()
        self.dem_path = QLineEdit(self.settings.value("dem_path", ""))
        self.dem_path.setToolTip("Directory containing DEM files (*.tif) to process.")
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_dem)
        row.addWidget(self.dem_path)
        row.addWidget(btn)
        form.addRow("Input DEM directory:",row)

        # Output dir
        row = QHBoxLayout()
        self.out_path = QLineEdit(self.settings.value("out_path", ""))
        self.out_path.setToolTip("Directory where output maps will be saved.")
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_output)
        row.addWidget(self.out_path)
        row.addWidget(btn)
        form.addRow("Output directory:", row)

        # Add groupbox
        data_group.setLayout(form)
        basic.addWidget(data_group)

        # Add Basic Tab
        tabs.addTab(basic_tab, "Basic settings")

        # Create advanced settings tab
        advanced_tab = QWidget()
        adv = QVBoxLayout()
        advanced_tab.setLayout(adv)

        # groupbox for maps and threshold
        maps_group = QGroupBox("Threshold and Output Maps")
        maps_layout = QFormLayout()

        # Threshold
        row = QHBoxLayout()
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.0, 1.0)
        self.threshold.setSingleStep(0.05)
        self.threshold.setValue(float(self.settings.value("threshold", 0.3)))
        self.threshold.setToolTip("Binarization threshold for the output binary map.")
        row.addWidget(self.threshold)
        maps_layout.addRow("Binary map threshold:",row)

        # probability map
        self.cb_prob = QCheckBox()
        self.cb_prob.setChecked(self.settings.value("prob_map", "true") == "true")
        maps_layout.addRow("Generate probability map",self.cb_prob)

        # binary map
        self.cb_class = QCheckBox()
        self.cb_class.setChecked(self.settings.value("binary_map", "true") == "true")
        maps_layout.addRow("Generate binary map",self.cb_class)

        # depth map
        self.cb_depth = QCheckBox()
        self.cb_depth.setChecked(self.settings.value("depth_map", "true") == "true")
        maps_layout.addRow("Generate depth map",self.cb_depth)

        # Add maps groupbox
        maps_group.setLayout(maps_layout)
        adv.addWidget(maps_group)

        # groupbox for device
        device_group = QGroupBox("Computation device")
        device_layout = QFormLayout()

        # Device selection
        row = QHBoxLayout()
        self.device_box = QComboBox()
        self.device_box.addItems(["auto", "cpu", "cuda"])
        self.device_box.setCurrentText(self.settings.value("device", "auto"))
        self.device_box.setToolTip('Computation device: "cpu", "cuda", or "auto" (automatically detect GPU if available).')
        row.addWidget(self.device_box)
        device_layout.addRow("Device:",row)

        # Add device groupbox
        device_group.setLayout(device_layout)
        adv.addWidget(device_group)

        # Add advanced tab
        tabs.addTab(advanced_tab, "Advanced settings")

        # Run button
        self.run_btn = QPushButton("Run inference")
        self.run_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.run_btn.clicked.connect(self.run_prediction)
        main.addWidget(self.run_btn)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        main.addWidget(self.log)

        self.setLayout(main)

    # Save settings
    def save(self):
        # basic
        self.settings.setValue("python_exec", self.python_exec.currentText())
        self.settings.setValue("model_path", self.model_path.text())
        self.settings.setValue("dem_path", self.dem_path.text())
        self.settings.setValue("out_path", self.out_path.text())

        # advanced
        self.settings.setValue("threshold", self.threshold.value())
        self.settings.setValue("prob_map", "true" if self.cb_prob.isChecked() else "false")
        self.settings.setValue("binary_map", "true" if self.cb_class.isChecked() else "false")
        self.settings.setValue("depth_map", "true" if self.cb_depth.isChecked() else "false")
        self.settings.setValue("device", self.device_box.currentText())

    # File selection
    def select_python(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select python executable", "", "Python (python*)")
        if file:
            self.python_exec.setEditText(file)
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

    # Logging
    def log_write(self, text):
        self.log.append(text)
        self.log.ensureCursorVisible()


    # Run inference
    def run_prediction(self):
        self.save()

        if not (
            os.path.isfile(self.python_exec.currentText()) and
            os.path.isdir(self.model_path.text()) and
            os.path.isdir(self.dem_path.text()) and
            os.path.isdir(self.out_path.text())
        ):
            self.log_write("Missing required paths!")
            return

        # Ensure at least one output checkbox is selected (backend requires it)
        if not (self.cb_prob.isChecked() or self.cb_class.isChecked() or self.cb_depth.isChecked()):
            self.log_write("Select at least one output type (probability / binary / depth).")
            return

        self.run_btn.setEnabled(False)
        self.set_enabled(False)
        self.log_write("Running backend...\n")

        # worker with arguments matching InferenceConfig
        self.worker = InferenceWorker(
            python_exec=self.python_exec.currentText(),
            script=self.backend_script_path,
            model_dir=self.model_path.text(),
            input_dem_dir=self.dem_path.text(),
            output_dir=self.out_path.text(),
            threshold=self.threshold.value(),
            output_prob_map=self.cb_prob.isChecked(),
            output_binary_map=self.cb_class.isChecked(),
            output_depth_map=self.cb_depth.isChecked(),
            device=self.device_box.currentText()
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
            self.python_exec,
            self.model_path, self.dem_path, self.out_path,
            self.device_box,
            self.threshold, self.cb_prob, self.cb_class, self.cb_depth
        ]
        for w in widgets:
            w.setEnabled(state)
