import os
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, QSpinBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import QSettings
from workers.test_worker import TestWorker
from utils.conda_scanner import find_conda_pythons

class TestTab(QWidget):
    def __init__(self):
        super().__init__()
        self.test_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "test.py")
        )
        self.settings = QSettings("DitchNet", "GUI")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        env_box = QHBoxLayout()
        self.python_exec = QComboBox()
        self.python_exec.setEditable(True)
        self.python_exec.setMinimumWidth(300)
        try:
            for exe in find_conda_pythons(): self.python_exec.addItem(exe)
        except: pass
        self.python_exec.setCurrentText(self.settings.value("test_python", ""))
        self.python_exec.setToolTip("Path to python.exe used for testing.")
        
        btn_browse_py = QPushButton("Browse")
        btn_browse_py.clicked.connect(lambda: self.select_file(self.python_exec, "Python (python.exe)"))

        env_box.addWidget(QLabel("Python Interpreter:"))
        env_box.addWidget(self.python_exec)
        env_box.addWidget(btn_browse_py)
        layout.addLayout(env_box)

        grp_in = QGroupBox("Inputs")
        frm_in = QFormLayout()
        
        self.model_path = QLineEdit(self.settings.value("test_model", ""))
        self.model_path.setToolTip("Path to the trained LightningDitchNet model checkpoint (.ckpt file).")
        btn_mod = QPushButton("Browse .ckpt")
        btn_mod.clicked.connect(lambda: self.select_file(self.model_path, "Checkpoint (*.ckpt)"))
        row_mod = QHBoxLayout(); row_mod.addWidget(self.model_path); row_mod.addWidget(btn_mod)
        frm_in.addRow("Model Checkpoint Path:", row_mod)

        self.hparams_path = QLineEdit(self.settings.value("test_hparams", ""))
        self.hparams_path.setToolTip("Path to the hparams.yaml file saved during training.")
        btn_yaml = QPushButton("Browse .yaml")
        btn_yaml.clicked.connect(lambda: self.select_file(self.hparams_path, "Hparams (*.yaml)"))
        row_yaml = QHBoxLayout(); row_yaml.addWidget(self.hparams_path); row_yaml.addWidget(btn_yaml)
        frm_in.addRow("Hparams Path:", row_yaml)

        self.feature_dir = QLineEdit(self.settings.value("test_feat", ""))
        self.feature_dir.setToolTip("Path to directory containing input feature images (e.g. test_data/feature_chips).")
        btn_feat = QPushButton("Browse")
        btn_feat.clicked.connect(lambda: self.select_dir(self.feature_dir))
        row_feat = QHBoxLayout(); row_feat.addWidget(self.feature_dir); row_feat.addWidget(btn_feat)
        frm_in.addRow("Feature Dir:", row_feat)

        self.label_dir = QLineEdit(self.settings.value("test_label", ""))
        self.label_dir.setToolTip("Path to directory containing label (mask) images (e.g. test_data/label_chips).")
        btn_label = QPushButton("Browse")
        btn_label.clicked.connect(lambda: self.select_dir(self.label_dir))
        row_label = QHBoxLayout(); row_label.addWidget(self.label_dir); row_label.addWidget(btn_label)
        frm_in.addRow("Label Dir:", row_label)
        
        grp_in.setLayout(frm_in)
        layout.addWidget(grp_in)

        grp_par = QGroupBox("Parameters")
        frm_par = QFormLayout()
        
        self.batch_size = QSpinBox(); self.batch_size.setRange(1, 2048); self.batch_size.setValue(int(self.settings.value("test_bs", 4)))
        self.batch_size.setToolTip("Batch size for testing.")
        frm_par.addRow("Batch Size:", self.batch_size)

        self.num_workers = QSpinBox(); self.num_workers.setRange(0, 64); self.num_workers.setValue(int(self.settings.value("test_workers", 0)))
        self.num_workers.setToolTip("Number of parallel CPU workers used for loading batches from disk.")
        frm_par.addRow("Num Workers:", self.num_workers)

        self.precision = QComboBox()
        self.precision.addItems(["32-true", "16-mixed", "16-true", "bf16-mixed", "64-true"])
        self.precision.setCurrentText(self.settings.value("test_prec", "32-true"))
        self.precision.setToolTip("Computation precision for testing.")
        frm_par.addRow("Precision:", self.precision)
        
        grp_par.setLayout(frm_par)
        layout.addWidget(grp_par)

        self.run_btn = QPushButton("Start Testing")
        self.run_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.run_btn.clicked.connect(self.start_test)
        layout.addWidget(self.run_btn)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        layout.addWidget(self.log)

        self.setLayout(layout)

    def select_dir(self, w):
        d = QFileDialog.getExistingDirectory(self)
        if d: w.setText(d)

    def select_file(self, w, f_filter):
        if isinstance(w, QComboBox):
            file, _ = QFileDialog.getOpenFileName(self, "Select", "", f_filter)
            if file: w.setEditText(file)
        else:
            file, _ = QFileDialog.getOpenFileName(self, "Select", "", f_filter)
            if file: w.setText(file)

    def start_test(self):
        self.settings.setValue("test_python", self.python_exec.currentText())
        self.settings.setValue("test_model", self.model_path.text())
        self.settings.setValue("test_hparams", self.hparams_path.text())
        self.settings.setValue("test_feat", self.feature_dir.text())
        self.settings.setValue("test_label", self.label_dir.text())
        self.settings.setValue("test_bs", self.batch_size.value())
        self.settings.setValue("test_workers", self.num_workers.value())
        self.settings.setValue("test_prec", self.precision.currentText())
        
        config = {
            "python_exec": self.python_exec.currentText(),
            "script": self.test_script_path,
            "model_path": self.model_path.text(),
            "hparams_path": self.hparams_path.text(), 
            "feature_dir": self.feature_dir.text(),
            "label_dir": self.label_dir.text(),
            "batch_size": self.batch_size.value(),
            "num_workers": self.num_workers.value(),
            "precision": self.precision.currentText()
        }
        
        self.log.clear()
        
        if not all([config["model_path"], config["hparams_path"], config["feature_dir"], config["label_dir"]]):
            self.log.append("ERROR: Please select all required files and directories (Model, Hparams, Feature, Label).")
            return

        self.run_btn.setEnabled(False)
        self.worker = TestWorker(config)
        self.worker.log_signal.connect(self.log.append)
        self.worker.done_signal.connect(lambda: self.run_btn.setEnabled(True))
        self.worker.start()