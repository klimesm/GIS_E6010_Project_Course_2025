import os

from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit,
    QDoubleSpinBox, QComboBox, QGroupBox, QSpinBox
)
from PySide6.QtCore import QSettings

from workers.inference_worker import InferenceWorker
from utils.conda_scanner import find_conda_pythons


# Static encoder list (no SMP import needed)
STATIC_ENCODERS = [
    "resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
    "efficientnet-b0", "efficientnet-b1", "efficientnet-b2",
    "efficientnet-b3", "efficientnet-b4", "efficientnet-b5",
    "efficientnet-b6", "efficientnet-b7",
    "mobilenet_v2",
    "vgg11", "vgg16", "vgg19",
    "timm-mobilenetv3_large_100",
    "timm-regnety_032",
    "timm-regnetx_064"
]


class InferenceTab(QWidget):
    def __init__(self):
        super().__init__()

        # path to inference backend
        self.backend_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "inference.py")
        )

        self.settings = QSettings("DitchNet", "GUI")

        main = QVBoxLayout()

        # ==========================
        # BASIC SETTINGS  (only required!)
        # ==========================
        basic_box = QGroupBox("Basic settings")
        basic = QVBoxLayout()

        # Python executable
        basic.addWidget(QLabel("Backend python interpreter (conda env):"))
        row = QHBoxLayout()
        self.python_exec = QComboBox()
        self.python_exec.setEditable(True)
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
        basic.addLayout(row)

        # Model dir
        basic.addWidget(QLabel("Model directory:"))
        row = QHBoxLayout()
        self.model_path = QLineEdit(self.settings.value("model_path", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_model)
        row.addWidget(self.model_path)
        row.addWidget(btn)
        basic.addLayout(row)

        # DEM input dir
        basic.addWidget(QLabel("Input DEM directory:"))
        row = QHBoxLayout()
        self.dem_path = QLineEdit(self.settings.value("dem_path", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_dem)
        row.addWidget(self.dem_path)
        row.addWidget(btn)
        basic.addLayout(row)

        # Output dir
        basic.addWidget(QLabel("Output directory:"))
        row = QHBoxLayout()
        self.out_path = QLineEdit(self.settings.value("out_path", ""))
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_output)
        row.addWidget(self.out_path)
        row.addWidget(btn)
        basic.addLayout(row)

        basic_box.setLayout(basic)
        main.addWidget(basic_box)

        # ==========================
        # ADVANCED SETTINGS (hidden by toggle)
        # ==========================
        self.adv_toggle_btn = QPushButton("Show advanced settings")
        self.adv_toggle_btn.setCheckable(True)
        self.adv_toggle_btn.setChecked(False)
        self.adv_toggle_btn.clicked.connect(self.toggle_advanced)
        main.addWidget(self.adv_toggle_btn)

        # Container with advanced options (hidden initially)
        self.adv_container = QWidget()
        adv = QVBoxLayout(self.adv_container)
        self.adv_container.setVisible(False)

        # Encoder name
        adv.addWidget(QLabel("Encoder name (must match training):"))
        self.encoder_box = QComboBox()
        self.encoder_box.addItems(STATIC_ENCODERS)
        self.encoder_box.setCurrentText(self.settings.value("encoder_name", "efficientnet-b4"))
        adv.addWidget(self.encoder_box)

        # in_channels
        row = QHBoxLayout()
        row.addWidget(QLabel("Input channels (must match training):"))
        self.in_channels = QSpinBox()
        self.in_channels.setRange(1, 20)
        self.in_channels.setValue(int(self.settings.value("in_channels", 2)))
        row.addWidget(self.in_channels)
        adv.addLayout(row)

        # threshold
        row = QHBoxLayout()
        row.addWidget(QLabel("Binary map threshold:"))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.0, 1.0)
        self.threshold.setSingleStep(0.05)
        self.threshold.setValue(float(self.settings.value("threshold", 0.3)))
        row.addWidget(self.threshold)
        adv.addLayout(row)

        # probability map
        self.cb_prob = QCheckBox("Generate probability map")
        self.cb_prob.setChecked(self.settings.value("prob_map", "true") == "true")
        adv.addWidget(self.cb_prob)

        # binary map
        self.cb_class = QCheckBox("Generate binary map")
        self.cb_class.setChecked(self.settings.value("binary_map", "true") == "true")
        adv.addWidget(self.cb_class)

        # depth map
        self.cb_depth = QCheckBox("Generate depth map")
        self.cb_depth.setChecked(self.settings.value("depth_map", "true") == "true")
        adv.addWidget(self.cb_depth)

        main.addWidget(self.adv_container)

        # ==========================
        # RUN + LOG
        # ==========================
        self.run_btn = QPushButton("Run inference")
        self.run_btn.clicked.connect(self.run_prediction)
        main.addWidget(self.run_btn)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        main.addWidget(self.log)

        self.setLayout(main)

    # -----------------------------
    # Toggle advanced settings
    # -----------------------------
    def toggle_advanced(self):
        visible = self.adv_toggle_btn.isChecked()
        self.adv_container.setVisible(visible)
        self.adv_toggle_btn.setText(
            "Hide advanced settings" if visible else "Show advanced settings"
        )

    # -----------------------------
    # Save settings
    # -----------------------------
    def save(self):
        self.settings.setValue("python_exec", self.python_exec.currentText())
        self.settings.setValue("model_path", self.model_path.text())
        self.settings.setValue("dem_path", self.dem_path.text())
        self.settings.setValue("out_path", self.out_path.text())

        # advanced
        self.settings.setValue("encoder_name", self.encoder_box.currentText())
        self.settings.setValue("in_channels", self.in_channels.value())
        self.settings.setValue("threshold", self.threshold.value())
        self.settings.setValue("prob_map", "true" if self.cb_prob.isChecked() else "false")
        self.settings.setValue("binary_map", "true" if self.cb_class.isChecked() else "false")
        self.settings.setValue("depth_map", "true" if self.cb_depth.isChecked() else "false")

    # -----------------------------
    # File selection
    # -----------------------------
    def select_python(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select python.exe", "", "Python (python.exe)")
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

    # -----------------------------
    # Logging
    # -----------------------------
    def log_write(self, text):
        self.log.append(text)
        self.log.ensureCursorVisible()

    # -----------------------------
    # Run inference
    # -----------------------------
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

        self.run_btn.setEnabled(False)
        self.set_enabled(False)
        self.log_write("Running backend...\n")

        self.worker = InferenceWorker(
            python_exec=self.python_exec.currentText(),
            script=self.backend_script_path,
            encoder=self.encoder_box.currentText(),
            channels=self.in_channels.value(),
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
            self.python_exec,
            self.model_path, self.dem_path, self.out_path,
            self.encoder_box, self.in_channels,
            self.threshold, self.cb_prob, self.cb_class, self.cb_depth
        ]
        for w in widgets:
            w.setEnabled(state)
