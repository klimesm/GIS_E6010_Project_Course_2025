# import os
# from PySide6.QtWidgets import (
#     QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
#     QVBoxLayout, QHBoxLayout, QCheckBox, QTextEdit,
#     QDoubleSpinBox, QComboBox, QSpinBox
# )
# from PySide6.QtCore import QSettings
#
# from workers.training_worker import TrainingWorker
# from utils.conda_scanner import find_conda_pythons
#
#
# class TrainingTab(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.worker = None
#         self.init_ui()
#
#     def init_ui(self):
#         layout = QVBoxLayout()
#
#         # feature dir
#         self.feature_path = QLineEdit()
#         btn_feat = QPushButton("Select Feature Dir")
#         btn_feat.clicked.connect(
#             lambda: self.feature_path.setText(QFileDialog.getExistingDirectory(self))
#         )
#
#         # label dir
#         self.label_path = QLineEdit()
#         btn_label = QPushButton("Select Label Dir")
#         btn_label.clicked.connect(
#             lambda: self.label_path.setText(QFileDialog.getExistingDirectory(self))
#         )
#
#         # arguments
#         self.max_epochs = QSpinBox(); self.max_epochs.setRange(1, 9999); self.max_epochs.setValue(50)
#         self.batch_size = QSpinBox(); self.batch_size.setRange(1, 9999); self.batch_size.setValue(4)
#         self.num_workers = QSpinBox(); self.num_workers.setRange(0, 64); self.num_workers.setValue(0)
#         self.pos_weight = QDoubleSpinBox(); self.pos_weight.setRange(0, 9999); self.pos_weight.setValue(3.0)
#
#         self.encoder_name = QComboBox()
#         self.encoder_name.addItems([
#             "efficientnet-b4", "resnet34", "resnet50",
#             "timm-mobilenetv3_large_100", "timm-efficientnet-b0"
#         ])
#
#         self.compute_precision = QComboBox()
#         self.compute_precision.addItems([
#             "32-true", "16-mixed", "32", "16", "bf16-mixed"
#         ])
#
#         # python from conda
#         self.conda_python = QLineEdit()
#         btn_python = QPushButton("Select python.exe from environment")
#         btn_python.clicked.connect(
#             lambda: self.conda_python.setText(QFileDialog.getOpenFileName(self, "Select python.exe")[0])
#         )
#
#         # start
#         btn_run = QPushButton("Start Training")
#         btn_run.clicked.connect(self.start_training)
#
#         # log
#         self.log = QTextEdit()
#         self.log.setReadOnly(True)
#         self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
#
#         # add widgets
#         layout.addWidget(QLabel("Feature directory:"))
#         layout.addWidget(self.feature_path); layout.addWidget(btn_feat)
#
#         layout.addWidget(QLabel("Label directory:"))
#         layout.addWidget(self.label_path); layout.addWidget(btn_label)
#
#         layout.addWidget(QLabel("Epochs:")); layout.addWidget(self.max_epochs)
#         layout.addWidget(QLabel("Batch Size:")); layout.addWidget(self.batch_size)
#         layout.addWidget(QLabel("Num Workers:")); layout.addWidget(self.num_workers)
#         layout.addWidget(QLabel("Pos Weight:")); layout.addWidget(self.pos_weight)
#
#         layout.addWidget(QLabel("Encoder:")); layout.addWidget(self.encoder_name)
#         layout.addWidget(QLabel("Precision:")); layout.addWidget(self.compute_precision)
#
#         layout.addWidget(QLabel("Python (conda):"))
#         layout.addWidget(self.conda_python)
#         layout.addWidget(btn_python)
#
#         layout.addWidget(btn_run)
#         layout.addWidget(QLabel("Training Log:"))
#         layout.addWidget(self.log)
#
#         self.setLayout(layout)
#
#     def start_training(self):
#         self.log.clear()
#
#         self.worker = TrainingWorker(
#             feature_dir=self.feature_path.text(),
#             label_dir=self.label_path.text(),
#             max_epochs=self.max_epochs.value(),
#             encoder_name=self.encoder_name.currentText(),
#             pos_weight=self.pos_weight.value(),
#             batch_size=self.batch_size.value(),
#             num_workers=self.num_workers.value(),
#             compute_precision=self.compute_precision.currentText(),
#             conda_python=self.conda_python.text(),
#         )
#
#         self.worker.log_signal.connect(self.log_output)
#         self.worker.done_signal.connect(self.training_finished)
#
#         self.worker.start()
#
#     def log_output(self, text):
#         self.log.append(text)
#
#     def training_finished(self, success):
#         self.log.append("\n=== Training FINISHED ===")
#         self.log.append("Status: SUCCESS\n" if success else "Status: FAILED\n")

import os
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QTextEdit,
    QDoubleSpinBox, QComboBox, QSpinBox
)
from PySide6.QtCore import QSettings

from workers.training_worker import TrainingWorker


class TrainingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def row(self, label_text, widget, button=None):
        """Helper – creates a row identical to inference layout."""
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setMinimumWidth(140)

        row.addWidget(lbl)
        row.addWidget(widget)

        if button:
            row.addWidget(button)

        return row

    def init_ui(self):
        layout = QVBoxLayout()

        # === DIRECTORIES ===
        self.feature_path = QLineEdit()
        btn_feat = QPushButton("Browse")
        btn_feat.clicked.connect(
            lambda: self.feature_path.setText(QFileDialog.getExistingDirectory(self))
        )
        layout.addLayout(self.row("Feature directory:", self.feature_path, btn_feat))

        self.label_path = QLineEdit()
        btn_label = QPushButton("Browse")
        btn_label.clicked.connect(
            lambda: self.label_path.setText(QFileDialog.getExistingDirectory(self))
        )
        layout.addLayout(self.row("Label directory:", self.label_path, btn_label))

        # === Training hyperparameters ===
        self.max_epochs = QSpinBox(); self.max_epochs.setRange(1, 9999); self.max_epochs.setValue(50)
        layout.addLayout(self.row("Epochs:", self.max_epochs))

        self.batch_size = QSpinBox(); self.batch_size.setRange(1, 2048); self.batch_size.setValue(4)
        layout.addLayout(self.row("Batch Size:", self.batch_size))

        self.num_workers = QSpinBox(); self.num_workers.setRange(0, 64); self.num_workers.setValue(0)
        layout.addLayout(self.row("Num Workers:", self.num_workers))

        self.pos_weight = QDoubleSpinBox(); self.pos_weight.setRange(0, 9999); self.pos_weight.setValue(3.0)
        layout.addLayout(self.row("Pos Weight:", self.pos_weight))

        # === Encoder ===
        self.encoder_name = QComboBox()
        self.encoder_name.addItems([
            "efficientnet-b4", "resnet34", "resnet50",
            "timm-mobilenetv3_large_100", "timm-efficientnet-b0"
        ])
        layout.addLayout(self.row("Encoder:", self.encoder_name))

        # === Precision ===
        self.compute_precision = QComboBox()
        self.compute_precision.addItems([
            "32-true", "16-mixed", "32", "16", "bf16-mixed"
        ])
        layout.addLayout(self.row("Precision:", self.compute_precision))

        # === Python executable ===
        self.conda_python = QLineEdit()
        btn_python = QPushButton("Browse")
        btn_python.clicked.connect(
            lambda: self.conda_python.setText(QFileDialog.getOpenFileName(self, "Select python.exe")[0])
        )
        layout.addLayout(self.row("Python (conda):", self.conda_python, btn_python))

        # === Start training button ===
        btn_run = QPushButton("Start Training")
        row_run = QHBoxLayout()
        row_run.addStretch()
        row_run.addWidget(btn_run)
        layout.addLayout(row_run)

        btn_run.clicked.connect(self.start_training)

        # === Log window ===
        lbl_log = QLabel("Training Log:")
        layout.addWidget(lbl_log)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        layout.addWidget(self.log)

        self.setLayout(layout)

    def start_training(self):
        self.log.clear()

        self.worker = TrainingWorker(
            feature_dir=self.feature_path.text(),
            label_dir=self.label_path.text(),
            max_epochs=self.max_epochs.value(),
            encoder_name=self.encoder_name.currentText(),
            pos_weight=self.pos_weight.value(),
            batch_size=self.batch_size.value(),
            num_workers=self.num_workers.value(),
            compute_precision=self.compute_precision.currentText(),
            conda_python=self.conda_python.text(),
        )

        self.worker.log_signal.connect(self.log_output)
        self.worker.done_signal.connect(self.training_finished)
        self.worker.start()

    def log_output(self, text):
        self.log.append(text)

    def training_finished(self, success):
        self.log.append("\n=== Training FINISHED ===")
        self.log.append("Status: SUCCESS\n" if success else "Status: FAILED\n")
