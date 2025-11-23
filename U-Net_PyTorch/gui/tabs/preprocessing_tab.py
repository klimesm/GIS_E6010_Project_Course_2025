import os
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, QDoubleSpinBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import QSettings
from workers.preprocessing_worker import PreprocessingWorker
from utils.conda_scanner import find_conda_pythons

class PreprocessingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "preprocessing.py")
        )
        self.settings = QSettings("DitchNet", "GUI")
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        env_box = QHBoxLayout()
        self.python_exec = QComboBox()
        self.python_exec.setEditable(True)
        self.python_exec.setMinimumWidth(300)
        try:
            for exe in find_conda_pythons(): 
                self.python_exec.addItem(exe)
        except: pass
        self.python_exec.setCurrentText(self.settings.value("prep_python", ""))
        self.python_exec.setToolTip("Path to python.exe (must have PyTorch & WhiteboxTools installed).")
        
        btn_browse_py = QPushButton("Browse")
        btn_browse_py.clicked.connect(lambda: self.select_file(self.python_exec, "Python (python.exe)"))

        env_box.addWidget(QLabel("Python Interpreter:"))
        env_box.addWidget(self.python_exec)
        env_box.addWidget(btn_browse_py)
        layout.addLayout(env_box)

        grp_in = QGroupBox("Inputs & Outputs")
        frm_in = QFormLayout()

        self.input_dem = QLineEdit(self.settings.value("prep_dem", ""))
        self.input_dem.setToolTip("Directory containing input DEM (.tif) files to preprocess.")
        btn_dem = QPushButton("Browse")
        btn_dem.clicked.connect(lambda: self.select_dir(self.input_dem))
        row_dem = QHBoxLayout(); row_dem.addWidget(self.input_dem); row_dem.addWidget(btn_dem)
        frm_in.addRow("Input DEM Dir (.tif):", row_dem)

        self.label_vec = QLineEdit(self.settings.value("prep_vec", ""))
        self.label_vec.setToolTip("Vector dataset containing labeled ditch features (e.g., .shp, .gpkg).")
        btn_vec = QPushButton("Browse")
        btn_vec.clicked.connect(lambda: self.select_file(self.label_vec, "Vector (*.shp *.gpkg)"))
        row_vec = QHBoxLayout(); row_vec.addWidget(self.label_vec); row_vec.addWidget(btn_vec)
        frm_in.addRow("Label Vector Data:", row_vec)

        self.out_dir = QLineEdit(self.settings.value("prep_out", ""))
        self.out_dir.setToolTip('Directory where output "training_data" or "test_data" directory will be written.')
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(lambda: self.select_dir(self.out_dir))
        row_out = QHBoxLayout(); row_out.addWidget(self.out_dir); row_out.addWidget(btn_out)
        frm_in.addRow("Output Directory:", row_out)

        grp_in.setLayout(frm_in)
        layout.addWidget(grp_in)

        grp_par = QGroupBox("Parameters")
        frm_par = QFormLayout()

        self.mode = QComboBox()
        self.mode.addItems(["train", "test"])
        self.mode.setCurrentText(self.settings.value("prep_mode", "train"))
        self.mode.setToolTip('Dataset generation mode:\n"train" for training data\n"test" for test data.')
        frm_par.addRow("Mode:", self.mode)

        self.ditch_width = QDoubleSpinBox()
        self.ditch_width.setRange(0.1, 10.0)
        self.ditch_width.setSingleStep(0.5)
        self.ditch_width.setValue(float(self.settings.value("prep_width", 1.5)))
        self.ditch_width.setToolTip("Determines how wide the ditch features appear in the generated label mask.")
        frm_par.addRow("Ditch Width (m):", self.ditch_width)

        self.hpmf_thr = QDoubleSpinBox()
        self.hpmf_thr.setRange(-1.0, 1.0)
        self.hpmf_thr.setSingleStep(0.01)
        self.hpmf_thr.setDecimals(3)
        self.hpmf_thr.setValue(float(self.settings.value("prep_thr", -0.075)))
        self.hpmf_thr.setToolTip("Keep pixels with HPMF ≤ threshold as label; higher values are ignored.")
        frm_par.addRow("HPMF Threshold:", self.hpmf_thr)

        grp_par.setLayout(frm_par)
        layout.addWidget(grp_par)

        self.run_btn = QPushButton("Start Preprocessing")
        self.run_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.run_btn.clicked.connect(self.start_preprocessing)
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

    def start_preprocessing(self):
        self.settings.setValue("prep_python", self.python_exec.currentText())
        self.settings.setValue("prep_dem", self.input_dem.text())
        self.settings.setValue("prep_vec", self.label_vec.text())
        self.settings.setValue("prep_out", self.out_dir.text())
        self.settings.setValue("prep_mode", self.mode.currentText())
        self.settings.setValue("prep_width", self.ditch_width.value())
        self.settings.setValue("prep_thr", self.hpmf_thr.value())

        config = {
            "python_exec": self.python_exec.currentText(),
            "script": self.script_path,
            "input_dem_dir": self.input_dem.text(),
            "label_vector_data": self.label_vec.text(),
            "output_dir": self.out_dir.text(),
            "mode": self.mode.currentText(),
            "ditch_width": self.ditch_width.value(),
            "label_hpmf_threshold": self.hpmf_thr.value()
        }

        self.log.clear()
        
        if not all([config["input_dem_dir"], config["label_vector_data"], config["output_dir"]]):
            self.log.append("ERROR: Please select Input DEM Dir, Label Vector Data, and Output Dir.")
            return

        self.run_btn.setEnabled(False)
        self.worker = PreprocessingWorker(config)
        self.worker.log_signal.connect(self.log.append)
        self.worker.done_signal.connect(lambda: self.run_btn.setEnabled(True))
        self.worker.start()