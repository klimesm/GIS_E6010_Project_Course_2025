import os
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QTextEdit, QDoubleSpinBox, 
    QComboBox, QSpinBox, QGroupBox, QFormLayout, QTabWidget, QCheckBox
)
from PySide6.QtCore import QSettings

from workers.training_worker import TrainingWorker
from utils.conda_scanner import find_conda_pythons

class TrainingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.train_script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "train.py")
        )
        self.settings = QSettings("DitchNet", "GUI")
        self.worker = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        env_group = QGroupBox("Environment")
        env_layout = QHBoxLayout()
        self.python_exec = QComboBox()
        self.python_exec.setEditable(True)
        self.python_exec.setMinimumWidth(300)
        try:
            for exe in find_conda_pythons(): self.python_exec.addItem(exe)
        except: pass
        self.python_exec.setCurrentText(self.settings.value("train_python", ""))
        self.python_exec.setToolTip("Path to python.exe in the backend environment (with PyTorch & Lightning).")
        
        btn_browse_py = QPushButton("Browse")
        btn_browse_py.clicked.connect(self.select_python)
        
        env_layout.addWidget(QLabel("Python Interpreter:"))
        env_layout.addWidget(self.python_exec)
        env_layout.addWidget(btn_browse_py)
        env_group.setLayout(env_layout)
        main_layout.addWidget(env_group)

        self.tabs = QTabWidget()
        self.tab_general = QWidget(); self.init_general_tab(); self.tabs.addTab(self.tab_general, "General & Data")
        self.tab_model = QWidget(); self.init_model_tab(); self.tabs.addTab(self.tab_model, "Model Options")
        self.tab_scheduler = QWidget(); self.init_scheduler_tab(); self.tabs.addTab(self.tab_scheduler, "Scheduler")
        self.tab_advanced = QWidget(); self.init_advanced_tab(); self.tabs.addTab(self.tab_advanced, "Advanced")

        main_layout.addWidget(self.tabs)

        self.run_btn = QPushButton("Start Training")
        self.run_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.run_btn.clicked.connect(self.start_training)
        main_layout.addWidget(self.run_btn)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        main_layout.addWidget(self.log)

        self.setLayout(main_layout)


    def init_general_tab(self):
        layout = QFormLayout()
        
        self.feature_path = QLineEdit(self.settings.value("train_feat", ""))
        self.feature_path.setToolTip("Path to directory containing input feature images.")
        btn_feat = QPushButton("Browse")
        btn_feat.clicked.connect(lambda: self.select_dir(self.feature_path))
        row_feat = QHBoxLayout(); row_feat.addWidget(self.feature_path); row_feat.addWidget(btn_feat)
        layout.addRow("Feature Directory:", row_feat)

        self.label_path = QLineEdit(self.settings.value("train_label", ""))
        self.label_path.setToolTip("Path to directory containing label images.")
        btn_label = QPushButton("Browse")
        btn_label.clicked.connect(lambda: self.select_dir(self.label_path))
        row_label = QHBoxLayout(); row_label.addWidget(self.label_path); row_label.addWidget(btn_label)
        layout.addRow("Label Directory:", row_label)

        self.ckpt_path = QLineEdit(self.settings.value("train_ckpt", ""))
        self.ckpt_path.setPlaceholderText("(Optional) Select .ckpt to resume training")
        self.ckpt_path.setToolTip("Optional path to a checkpoint (.ckpt) for resuming training or fine-tuning.\nIf left empty, training starts from scratch.")
        btn_ckpt = QPushButton("Browse")
        btn_ckpt.clicked.connect(lambda: self.select_file(self.ckpt_path, "Checkpoint (*.ckpt)")) # 需要复用 select_file 辅助函数
        row_ckpt = QHBoxLayout(); row_ckpt.addWidget(self.ckpt_path); row_ckpt.addWidget(btn_ckpt)
        layout.addRow("Resume Checkpoint:", row_ckpt)

        self.max_epochs = QSpinBox(); self.max_epochs.setRange(1, 10000); self.max_epochs.setValue(int(self.settings.value("train_epochs", 50)))
        self.max_epochs.setToolTip("Maximum number of training epochs to run.")
        layout.addRow("Max Epochs:", self.max_epochs)

        self.batch_size = QSpinBox(); self.batch_size.setRange(1, 2048); self.batch_size.setValue(int(self.settings.value("train_bs", 4)))
        self.batch_size.setToolTip("Batch size for training.")
        layout.addRow("Batch Size:", self.batch_size)

        self.num_workers = QSpinBox(); self.num_workers.setRange(0, 64); self.num_workers.setValue(int(self.settings.value("train_workers", 0)))
        self.num_workers.setToolTip("Number of parallel CPU workers used for loading batches from disk.")
        layout.addRow("Num Workers:", self.num_workers)

        self.compute_precision = QComboBox()
        self.compute_precision.addItems(["32-true", "16-mixed", "bf16-mixed", "16-true", "64-true"])
        self.compute_precision.setCurrentText(self.settings.value("train_prec", "32-true"))
        self.compute_precision.setToolTip("Computation precision for training.\nMore info: https://lightning.ai/docs/pytorch/stable/common/precision_basic.html")
        layout.addRow("Precision:", self.compute_precision)

        self.tab_general.setLayout(layout)

    def init_model_tab(self):
        layout = QFormLayout()
        
        self.encoder_name = QComboBox()
        self.encoder_name.addItems(["efficientnet-b4", "resnet34", "resnet50", "mit_b0", "timm-efficientnet-b0"])
        self.encoder_name.setEditable(True)
        self.encoder_name.setCurrentText(self.settings.value("train_encoder", "efficientnet-b4"))
        self.encoder_name.setToolTip("Encoder backbone for DitchNet.\nChoices: https://smp.readthedocs.io/en/latest/encoders.html")
        layout.addRow("Encoder Name:", self.encoder_name)

        self.pos_weight = QDoubleSpinBox(); self.pos_weight.setRange(0, 1000); self.pos_weight.setValue(float(self.settings.value("train_pos_w", 3.0)))
        self.pos_weight.setToolTip("Weighting factor for positive (ditch) class in the BCE loss to handle imbalance.")
        layout.addRow("Pos Weight:", self.pos_weight)

        self.learning_rate = QLineEdit(self.settings.value("train_lr", "1e-4"))
        self.learning_rate.setToolTip("Learning rate for optimizer.")
        layout.addRow("Learning Rate:", self.learning_rate)

        self.weight_decay = QLineEdit(self.settings.value("train_wd", "1e-4"))
        self.weight_decay.setToolTip("Weight decay for the optimizer (L2 regularization).")
        layout.addRow("Weight Decay:", self.weight_decay)

        self.in_channels = QSpinBox(); self.in_channels.setValue(int(self.settings.value("train_ch", 2)))
        self.in_channels.setToolTip("Number of input channels for the model.")
        layout.addRow("Input Channels:", self.in_channels)
        self.tab_model.setLayout(layout)

    def init_scheduler_tab(self):
        layout = QFormLayout()
        
        self.use_scheduler = QCheckBox("Enable Learning Rate Scheduler")
        self.use_scheduler.setChecked(self.settings.value("train_use_sched", "true") == "true")
        self.use_scheduler.toggled.connect(self.toggle_scheduler_inputs)
        self.use_scheduler.setToolTip("Disable/Enable learning-rate scheduler.")
        layout.addRow(self.use_scheduler)

        self.metrics_list = ["val_loss", "val_acc", "val_recall", "val_prec", "val_f1", "val_mcc",
                             "train_loss", "train_acc", "train_recall", "train_prec", "train_mcc"]

        self.sched_monitor = QComboBox(); self.sched_monitor.addItems(self.metrics_list)
        self.sched_monitor.setCurrentText(self.settings.value("train_sched_mon", "val_loss"))
        self.sched_monitor.setToolTip("Metric name to monitor for learning rate scheduling.")
        layout.addRow("Monitor:", self.sched_monitor)

        self.sched_mode = QComboBox(); self.sched_mode.addItems(["min", "max"])
        self.sched_mode.setCurrentText(self.settings.value("train_sched_mode", "min"))
        self.sched_mode.setToolTip("ReduceLROnPlateau mode (min/max).")
        layout.addRow("Mode:", self.sched_mode)

        self.sched_factor = QDoubleSpinBox(); self.sched_factor.setRange(0.01, 1.0); self.sched_factor.setSingleStep(0.1)
        self.sched_factor.setValue(float(self.settings.value("train_fac", 0.5)))
        self.sched_factor.setToolTip("Factor by which to reduce the learning rate.")
        layout.addRow("Factor:", self.sched_factor)

        self.sched_patience = QSpinBox(); self.sched_patience.setRange(0, 1000); self.sched_patience.setValue(int(self.settings.value("train_pat", 5)))
        self.sched_patience.setToolTip("Epochs with no improvement before reducing learning rate.")
        layout.addRow("Patience:", self.sched_patience)

        self.sched_cooldown = QSpinBox(); self.sched_cooldown.setValue(int(self.settings.value("train_cool", 5)))
        self.sched_cooldown.setToolTip("Cooldown epochs after learning-rate reduction.")
        layout.addRow("Cooldown:", self.sched_cooldown)

        self.sched_min_lr = QLineEdit(self.settings.value("train_min_lr", "1e-7"))
        self.sched_min_lr.setToolTip("Minimum learning rate allowed.")
        layout.addRow("Min LR:", self.sched_min_lr)

        self.sched_threshold = QLineEdit(self.settings.value("train_sched_thr", "1e-4"))
        self.sched_threshold.setToolTip("Improvement threshold to trigger learning rate reduction.")
        layout.addRow("Threshold:", self.sched_threshold)

        self.sched_thr_mode = QComboBox(); self.sched_thr_mode.addItems(["rel", "abs"])
        self.sched_thr_mode.setCurrentText(self.settings.value("train_sched_thr_mode", "rel"))
        self.sched_thr_mode.setToolTip("Threshold mode for learning rate scheduler.")
        layout.addRow("Thr. Mode:", self.sched_thr_mode)

        self.tab_scheduler.setLayout(layout)
        self.toggle_scheduler_inputs(self.use_scheduler.isChecked())

    def init_advanced_tab(self):
        layout = QFormLayout()

        self.val_size = QDoubleSpinBox()
        self.val_size.setRange(0.01, 0.5)
        self.val_size.setSingleStep(0.05)
        self.val_size.setValue(float(self.settings.value("train_val_size", 0.2)))
        self.val_size.setToolTip("Fraction of samples used for validation.")
        layout.addRow("Validation Size (0-0.5):", self.val_size)

        layout.addRow(QLabel("<b>Checkpoints:</b>"))

        self.save_full = QCheckBox("Save Full Training State (Optimizer + Weights)")
        self.save_full.setChecked(self.settings.value("train_save_full", "false") == "true")
        self.save_full.setToolTip("If checked, save the full training state (optimizer included). Uncheck for weights-only.")
        layout.addRow(self.save_full)

        self.save_top_k = QSpinBox()
        self.save_top_k.setRange(1, 100)
        self.save_top_k.setValue(int(self.settings.value("train_top_k", 10)))
        self.save_top_k.setToolTip("Number of top checkpoints to keep based on the monitored metric.")
        layout.addRow("Save Top K:", self.save_top_k)

        self.ckpt_monitor = QComboBox(); self.ckpt_monitor.addItems(self.metrics_list)
        self.ckpt_monitor.setCurrentText(self.settings.value("train_ckpt_mon", "val_mcc"))
        self.ckpt_monitor.setToolTip("Metric name used to determine which checkpoints are considered best.")
        layout.addRow("Checkpoint Monitor:", self.ckpt_monitor)

        self.ckpt_mode = QComboBox(); self.ckpt_mode.addItems(["min", "max"])
        self.ckpt_mode.setCurrentText(self.settings.value("train_ckpt_mode", "max"))
        self.ckpt_mode.setToolTip("Optimization direction for the monitored metric ('min' or 'max').")
        layout.addRow("Checkpoint Mode:", self.ckpt_mode)

        layout.addRow(QLabel("<b>Early Stopping:</b>"))

        self.use_early_stop = QCheckBox("Enable Early Stopping")
        self.use_early_stop.setChecked(self.settings.value("train_use_es", "true") == "true")
        self.use_early_stop.toggled.connect(self.toggle_es_inputs)
        self.use_early_stop.setToolTip("Enable/Disable early stopping during training.")
        layout.addRow(self.use_early_stop)

        self.es_patience = QSpinBox(); self.es_patience.setRange(1, 1000)
        self.es_patience.setValue(int(self.settings.value("train_es_pat", 50)))
        self.es_patience.setToolTip("Number of epochs with no improvement before early stopping triggers.")
        layout.addRow("Patience:", self.es_patience)

        self.es_monitor = QComboBox(); self.es_monitor.addItems(self.metrics_list)
        self.es_monitor.setCurrentText(self.settings.value("train_es_mon", "val_loss"))
        self.es_monitor.setToolTip("Metric to monitor for early stopping.")
        layout.addRow("Monitor:", self.es_monitor)

        self.es_mode = QComboBox(); self.es_mode.addItems(["min", "max"])
        self.es_mode.setCurrentText(self.settings.value("train_es_mode", "min"))
        self.es_mode.setToolTip("Direction in which the monitored metric is optimized.")
        layout.addRow("Mode:", self.es_mode)

        self.tab_advanced.setLayout(layout)
        self.toggle_es_inputs(self.use_early_stop.isChecked())

    def select_file(self, w, f_filter):
        file, _ = QFileDialog.getOpenFileName(self, "Select", "", f_filter)
        if file: w.setText(file)

    def toggle_scheduler_inputs(self, checked):
        for i in range(1, self.tab_scheduler.layout().rowCount()):
            w = self.tab_scheduler.layout().itemAt(i, QFormLayout.FieldRole).widget()
            if w: w.setEnabled(checked)

    def toggle_es_inputs(self, checked):
        self.es_patience.setEnabled(checked)
        self.es_monitor.setEnabled(checked)
        self.es_mode.setEnabled(checked)

    def select_python(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select python.exe", "", "Python (python.exe)")
        if f: self.python_exec.setEditText(f)

    def select_dir(self, field):
        d = QFileDialog.getExistingDirectory(self)
        if d: field.setText(d)

    def log_write(self, t): self.log.append(t)

    def save_settings(self):
        s = self.settings
        s.setValue("train_python", self.python_exec.currentText())
        s.setValue("train_feat", self.feature_path.text())
        s.setValue("train_label", self.label_path.text())
        s.setValue("train_ckpt", self.ckpt_path.text())
        s.setValue("train_epochs", self.max_epochs.value())
        s.setValue("train_bs", self.batch_size.value())
        s.setValue("train_workers", self.num_workers.value())
        s.setValue("train_prec", self.compute_precision.currentText())
        s.setValue("train_encoder", self.encoder_name.currentText())
        s.setValue("train_pos_w", self.pos_weight.value())
        s.setValue("train_lr", self.learning_rate.text())
        s.setValue("train_wd", self.weight_decay.text())
        s.setValue("train_ch", self.in_channels.value())
        s.setValue("train_use_sched", "true" if self.use_scheduler.isChecked() else "false")
        s.setValue("train_sched_mon", self.sched_monitor.currentText())
        s.setValue("train_sched_mode", self.sched_mode.currentText())
        s.setValue("train_fac", self.sched_factor.value())
        s.setValue("train_pat", self.sched_patience.value())
        s.setValue("train_cool", self.sched_cooldown.value())
        s.setValue("train_min_lr", self.sched_min_lr.text())
        s.setValue("train_sched_thr", self.sched_threshold.text())
        s.setValue("train_sched_thr_mode", self.sched_thr_mode.currentText())
        s.setValue("train_val_size", self.val_size.value())
        s.setValue("train_top_k", self.save_top_k.value())
        s.setValue("train_save_full", "true" if self.save_full.isChecked() else "false")
        s.setValue("train_ckpt_mon", self.ckpt_monitor.currentText())
        s.setValue("train_ckpt_mode", self.ckpt_mode.currentText())
        s.setValue("train_use_es", "true" if self.use_early_stop.isChecked() else "false")
        s.setValue("train_es_pat", self.es_patience.value())
        s.setValue("train_es_mon", self.es_monitor.currentText())
        s.setValue("train_es_mode", self.es_mode.currentText())

    def start_training(self):
        self.save_settings()
        self.log.clear()
        
        config = {
            "python_exec": self.python_exec.currentText(),
            "script": self.train_script_path,
            "feature_dir": self.feature_path.text(),
            "label_dir": self.label_path.text(),
            "ckpt_path": self.ckpt_path.text(),
            "max_epochs": self.max_epochs.value(),
            "batch_size": self.batch_size.value(),
            "num_workers": self.num_workers.value(),
            "compute_precision": self.compute_precision.currentText(),
            "encoder_name": self.encoder_name.currentText(),
            "pos_weight": self.pos_weight.value(),
            "learning_rate": self.learning_rate.text(),
            "weight_decay": self.weight_decay.text(),
            "in_channels": self.in_channels.value(),
            "use_scheduler": self.use_scheduler.isChecked(),
            "scheduler_monitor": self.sched_monitor.currentText(),
            "scheduler_mode": self.sched_mode.currentText(),
            "scheduler_patience": self.sched_patience.value(),
            "scheduler_factor": self.sched_factor.value(),
            "scheduler_cooldown": self.sched_cooldown.value(),
            "scheduler_min_lr": self.sched_min_lr.text(),
            "scheduler_threshold": self.sched_threshold.text(),
            "scheduler_threshold_mode": self.sched_thr_mode.currentText(),
            "val_size": self.val_size.value(),
            "save_top_k": self.save_top_k.value(),
            "save_full_checkpoint": self.save_full.isChecked(),
            "checkpoint_monitor": self.ckpt_monitor.currentText(),
            "checkpoint_mode": self.ckpt_mode.currentText(),
            "use_early_stop": self.use_early_stop.isChecked(),
            "early_stop_patience": self.es_patience.value(),
            "early_stop_monitor": self.es_monitor.currentText(),
            "early_stop_mode": self.es_mode.currentText(),
        }

        self.run_btn.setEnabled(False)
        self.worker = TrainingWorker(config)
        self.worker.log_signal.connect(self.log_write)
        self.worker.done_signal.connect(lambda: self.run_btn.setEnabled(True))
        self.worker.start()