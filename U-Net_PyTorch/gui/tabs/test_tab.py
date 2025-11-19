import os
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, QSpinBox
)

from workers.test_worker import TestWorker


class TestTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    # Helper: identical row layout as inference/training
    def row(self, label_text, widget, button=None):
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

        # === MODEL PATH ===
        self.model_path = QLineEdit()
        btn_model = QPushButton("Browse")
        btn_model.clicked.connect(
            lambda: self.model_path.setText(QFileDialog.getOpenFileName(self, "Select .ckpt model")[0])
        )
        layout.addLayout(self.row("Model (.ckpt):", self.model_path, btn_model))

        # === Feature directory ===
        self.feature_dir = QLineEdit()
        btn_feat = QPushButton("Browse")
        btn_feat.clicked.connect(
            lambda: self.feature_dir.setText(QFileDialog.getExistingDirectory(self))
        )
        layout.addLayout(self.row("Feature directory:", self.feature_dir, btn_feat))

        # === Label directory ===
        self.label_dir = QLineEdit()
        btn_label = QPushButton("Browse")
        btn_label.clicked.connect(
            lambda: self.label_dir.setText(QFileDialog.getExistingDirectory(self))
        )
        layout.addLayout(self.row("Label directory:", self.label_dir, btn_label))

        # === Batch size ===
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 4096)
        self.batch_size.setValue(4)
        layout.addLayout(self.row("Batch Size:", self.batch_size))

        # === Num Workers ===
        self.num_workers = QSpinBox()
        self.num_workers.setRange(0, 64)
        self.num_workers.setValue(0)
        layout.addLayout(self.row("Num Workers:", self.num_workers))

        # === Compute precision ===
        self.compute_precision = QComboBox()
        self.compute_precision.addItems([
            "32-true", "16-mixed", "16-true",
            "bf16-true", "bf16-mixed",
            "32", "64", "16", "bf16"
        ])
        layout.addLayout(self.row("Precision:", self.compute_precision))

        # === Python (conda) ===
        self.conda_python = QLineEdit()
        btn_python = QPushButton("Browse")
        btn_python.clicked.connect(
            lambda: self.conda_python.setText(QFileDialog.getOpenFileName(self, "Select python.exe")[0])
        )
        layout.addLayout(self.row("Python (conda):", self.conda_python, btn_python))

        # === Start button ===
        btn_run = QPushButton("Start Test")
        row_btn = QHBoxLayout()
        row_btn.addStretch()
        row_btn.addWidget(btn_run)
        layout.addLayout(row_btn)

        btn_run.clicked.connect(self.start_test)

        # === Log window ===
        layout.addWidget(QLabel("Test Log:"))

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        layout.addWidget(self.log)

        self.setLayout(layout)

    # =====================================================================
    #                          TEST START
    # =====================================================================
    def start_test(self):
        self.log.clear()

        self.worker = TestWorker(
            model_path=self.model_path.text(),
            feature_dir=self.feature_dir.text(),
            label_dir=self.label_dir.text(),
            batch_size=self.batch_size.value(),
            num_workers=self.num_workers.value(),
            compute_precision=self.compute_precision.currentText(),
            conda_python=self.conda_python.text(),
        )

        self.worker.log_signal.connect(self.log_output)
        self.worker.done_signal.connect(self.test_finished)
        self.worker.start()

    def log_output(self, txt):
        self.log.append(txt)

    def test_finished(self, success):
        self.log.append("\n=== TEST FINISHED ===")
        self.log.append("Status: SUCCESS\n" if success else "Status: FAILED\n")
