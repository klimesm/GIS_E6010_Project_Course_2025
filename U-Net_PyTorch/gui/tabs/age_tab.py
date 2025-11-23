# tabs/age_tab.py
import os
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileDialog, QLineEdit,
    QVBoxLayout, QHBoxLayout, QTextEdit, QGroupBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox,
    QSpinBox, QComboBox
)
from PySide6.QtCore import QSettings, Qt

from workers.age_worker import AgeWorker
from utils.conda_scanner import find_conda_pythons


class AgeDeterminationTab(QWidget):
    def __init__(self):
        super().__init__()

        # default script locations (adjust if needed)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.script_vectors = os.path.join(project_root, "age_classification_vectors.py")
        self.script_rasters = os.path.join(project_root, "find_new_ditches.py")

        self.settings = QSettings("DitchNet", "GUI")

        main = QVBoxLayout(self)

        # Python executable selector
        self.env_container = QGroupBox("Environment")
        env = QVBoxLayout()
        self.env_container.setLayout(env)

        env.addWidget(QLabel("Python executable (conda env):"))
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

        env.addLayout(row)
        main.addWidget(self.env_container)

        # Internal tab widget for two methods
        self.methods_tabs = QTabWidget()
        self._build_vectors_tab()
        self._build_rasters_tab()
        main.addWidget(self.methods_tabs)

        # Shared run button + log
        run_row = QHBoxLayout()
        self.run_btn = QPushButton("Run age determination")
        self.run_btn.clicked.connect(self.run_age)
        run_row.addWidget(self.run_btn)
        run_row.addStretch()
        main.addLayout(run_row)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        main.addWidget(self.log)

        # Load saved vector-table rows
        self._load_vec_table_from_settings()

        # Restore last used tab index
        last_index = int(self.settings.value("age_method_tab_index", 0))
        self.methods_tabs.setCurrentIndex(last_index)
        self.methods_tabs.currentChanged.connect(self._on_tab_changed)

    # --------------------------
    # Build VECTORS sub-tab
    # --------------------------
    def _build_vectors_tab(self):
        self.vectors_widget = QWidget()
        layout = QVBoxLayout(self.vectors_widget)

        # probability map
        row = QHBoxLayout()
        row.addWidget(QLabel("Probability map (.tif):"))
        self.prob_map_le = QLineEdit(self.settings.value("age_prob_map", ""))
        row.addWidget(self.prob_map_le)
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_prob_map)
        row.addWidget(btn)
        layout.addLayout(row)

        # # vector layers table
        # layout.addWidget(QLabel("Vector layers (Year | File | Layer)"))
        # self.vec_table = QTableWidget(0, 3)
        # self.vec_table.setHorizontalHeaderLabels(["Year", "File", "Layer"])
        # self.vec_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # layout.addWidget(self.vec_table)
        self.vec_table = QTableWidget(0, 4)
        self.vec_table.setHorizontalHeaderLabels(["Year", "File", "", "Layer"])
        self.vec_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vec_table.setColumnWidth(2, 90)  # column for Browse button
        layout.addWidget(self.vec_table)
        # self.vec_table = QTableWidget(0, 4)
        # self.vec_table.setHorizontalHeaderLabels(["Year", "File", "", "Layer"])  # 3rd is browse
        # self.vec_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.vec_table.setColumnWidth(2, 90)  # browse button column

        # add/remove buttons
        row = QHBoxLayout()
        add_btn = QPushButton("Add row")
        add_btn.clicked.connect(self.add_vec_row)
        rem_btn = QPushButton("Remove selected")
        rem_btn.clicked.connect(self.remove_selected_vec_rows)
        row.addWidget(add_btn)
        row.addWidget(rem_btn)
        row.addStretch()
        layout.addLayout(row)

        # output
        row = QHBoxLayout()
        row.addWidget(QLabel("Output GeoPackage:"))
        self.vec_output_le = QLineEdit(self.settings.value("age_vec_output", ""))
        row.addWidget(self.vec_output_le)
        out_btn = QPushButton("Browse")
        out_btn.clicked.connect(self.select_vec_output)
        row.addWidget(out_btn)
        layout.addLayout(row)

        # thresholds
        thr_row = QHBoxLayout()
        thr_row.addWidget(QLabel("Prob threshold:"))
        self.vec_prob_thr = QDoubleSpinBox()
        self.vec_prob_thr.setRange(0.0, 1.0)
        self.vec_prob_thr.setSingleStep(0.05)
        self.vec_prob_thr.setValue(float(self.settings.value("age_vec_prob_thr", 0.5)))
        thr_row.addWidget(self.vec_prob_thr)

        thr_row.addWidget(QLabel("Min overlap length:"))
        self.vec_min_overlap = QDoubleSpinBox()
        self.vec_min_overlap.setRange(0.0, 1e6)
        self.vec_min_overlap.setValue(float(self.settings.value("age_vec_min_overlap", 10.0)))
        thr_row.addWidget(self.vec_min_overlap)
        layout.addLayout(thr_row)

        self.methods_tabs.addTab(self.vectors_widget, "Vector-based")

    # --------------------------
    # Build RASTERS sub-tab
    # --------------------------
    def _build_rasters_tab(self):
        self.rasters_widget = QWidget()
        layout = QVBoxLayout(self.rasters_widget)

        row = QHBoxLayout()
        row.addWidget(QLabel("New layer (dir with .tif):"))
        self.r_new_le = QLineEdit(self.settings.value("age_r_new", ""))
        row.addWidget(self.r_new_le)
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_r_new)
        row.addWidget(btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Old layer (dir with .tif):"))
        self.r_old_le = QLineEdit(self.settings.value("age_r_old", ""))
        row.addWidget(self.r_old_le)
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_r_old)
        row.addWidget(btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Output directory:"))
        self.r_out_le = QLineEdit(self.settings.value("age_r_out", ""))
        row.addWidget(self.r_out_le)
        btn = QPushButton("Browse")
        btn.clicked.connect(self.select_r_out)
        row.addWidget(btn)
        layout.addLayout(row)

        params_row = QHBoxLayout()
        params_row.addWidget(QLabel("Threshold:"))
        self.r_threshold = QDoubleSpinBox()
        self.r_threshold.setRange(0.0, 1.0)
        self.r_threshold.setSingleStep(0.05)
        self.r_threshold.setValue(float(self.settings.value("age_r_threshold", 0.5)))
        params_row.addWidget(self.r_threshold)

        params_row.addWidget(QLabel("Tolerance:"))
        self.r_tolerance = QSpinBox()
        self.r_tolerance.setRange(0, 100)
        self.r_tolerance.setValue(int(self.settings.value("age_r_tolerance", 2)))
        params_row.addWidget(self.r_tolerance)

        params_row.addWidget(QLabel("Buffer (m):"))
        self.r_buffer = QSpinBox()
        self.r_buffer.setRange(0, 1000)
        self.r_buffer.setValue(int(self.settings.value("age_r_buffer", 3)))
        params_row.addWidget(self.r_buffer)

        layout.addLayout(params_row)
        self.methods_tabs.addTab(self.rasters_widget, "New ditches")

    # --------------------------
    # Tab change
    # --------------------------
    def _on_tab_changed(self, idx):
        self.settings.setValue("age_method_tab_index", idx)

    # --------------------------
    # Vector-table helpers
    # --------------------------

    def remove_selected_vec_rows(self):
        sel = self.vec_table.selectionModel().selectedRows()
        for index in sorted([s.row() for s in sel], reverse=True):
            self.vec_table.removeRow(index)

    def _load_vec_table_from_settings(self):
        saved = self.settings.value("age_vec_table", "")
        if not saved:
            return
        rows = str(saved).split(";")
        for r in rows:
            if not r:
                continue
            parts = r.split("|")
            if len(parts) != 3:
                continue
            year, path, layer = parts
            self.add_vec_row(year, path, layer)

    def _save_vec_table_to_settings(self):
        rows = []
        for r in range(self.vec_table.rowCount()):
            year = self.vec_table.item(r, 0).text() if self.vec_table.item(r, 0) else ""
            path = self.vec_table.item(r, 1).text() if self.vec_table.item(r, 1) else ""
            layer = self.vec_table.item(r, 3).text() if self.vec_table.item(r, 3) else ""
            # layer = self.vec_table.item(r, 3).text().strip() if self.vec_table.item(r, 3) else ""

            rows.append(f"{year}|{path}|{layer}")
        self.settings.setValue("age_vec_table", ";".join(rows))

    def add_vec_row(self, year="", path="", layer=""):
        row = self.vec_table.rowCount()
        self.vec_table.insertRow(row)

        # YEAR
        self.vec_table.setItem(row, 0, QTableWidgetItem(str(year)))

        # FILE
        self.vec_table.setItem(row, 1, QTableWidgetItem(path))

        # BROWSE BUTTON
        btn = QPushButton("Browse")
        btn.clicked.connect(lambda _, r=row: self.browse_vector_file(r))
        self.vec_table.setCellWidget(row, 2, btn)

        # LAYER
        self.vec_table.setItem(row, 3, QTableWidgetItem(layer))

    def browse_vector_file(self, row):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select vector file", "",
            "GeoPackage (*.gpkg);;Shapefile (*.shp);;All files (*)"
        )
        if path:
            if not self.vec_table.item(row, 1):
                self.vec_table.setItem(row, 1, QTableWidgetItem(path))
            else:
                self.vec_table.item(row, 1).setText(path)

    # --------------------------
    # File selectors
    # --------------------------
    def select_python(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select python executable", "", "Python (python*)")
        if file:
            self.python_exec.setText(file)
            self.settings.setValue("age_python_exec", file)

    def select_prob_map(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select probability map", "", "GeoTIFF (*.tif *.tiff)")
        if f:
            self.prob_map_le.setText(f)
            self.settings.setValue("age_prob_map", f)

    def select_vec_output(self):
        f, _ = QFileDialog.getSaveFileName(self, "Save GeoPackage as", "", "GeoPackage (*.gpkg)")
        if f:
            self.vec_output_le.setText(f)
            self.settings.setValue("age_vec_output", f)

    def select_r_new(self):
        d = QFileDialog.getExistingDirectory(self, "Select new raster directory")
        if d:
            self.r_new_le.setText(d)
            self.settings.setValue("age_r_new", d)

    def select_r_old(self):
        d = QFileDialog.getExistingDirectory(self, "Select old raster directory")
        if d:
            self.r_old_le.setText(d)
            self.settings.setValue("age_r_old", d)

    def select_r_out(self):
        d = QFileDialog.getExistingDirectory(self, "Select output directory")
        if d:
            self.r_out_le.setText(d)
            self.settings.setValue("age_r_out", d)

    # --------------------------
    # Logging
    # --------------------------
    def log_write(self, text):
        self.log.append(text)
        self.log.ensureCursorVisible()

    # --------------------------
    # Run method
    # --------------------------
    def run_age(self):
        # Save some settings
        self.settings.setValue("age_python_exec", self.python_exec.currentText())

        self._save_vec_table_to_settings()
        self.settings.setValue("age_vec_prob_thr", self.vec_prob_thr.value())
        self.settings.setValue("age_vec_min_overlap", self.vec_min_overlap.value())
        self.settings.setValue("age_r_threshold", self.r_threshold.value())
        self.settings.setValue("age_r_tolerance", self.r_tolerance.value())
        self.settings.setValue("age_r_buffer", self.r_buffer.value())

        current = self.methods_tabs.currentIndex()
        python_exec = self.python_exec.currentText() or "python"

        if current == 0:
            # VECTORS
            prob_map = self.prob_map_le.text().strip()
            if not prob_map or not os.path.isfile(prob_map):
                self.log_write("Invalid probability map path")
                return

            # Build vector_layers string
            vector_rows = []
            for r in range(self.vec_table.rowCount()):
                year = self.vec_table.item(r, 0).text().strip() if self.vec_table.item(r, 0) else ""
                path = self.vec_table.item(r, 1).text().strip() if self.vec_table.item(r, 1) else ""
                # layer = self.vec_table.item(r, 2).text().strip() if self.vec_table.item(r, 2) else ""
                layer = self.vec_table.item(r, 3).text().strip() if self.vec_table.item(r, 3) else ""

                if not year or not path or not layer:
                    self.log_write(f"Invalid vector row #{r+1}")
                    return
                try:
                    int(year)
                except ValueError:
                    self.log_write(f"Year must be integer in row #{r+1}")
                    return
                vector_rows.append(f"{year}:{path},{layer}")
            vector_layers_str = ";".join(vector_rows)

            output_vec = self.vec_output_le.text().strip()
            if not output_vec:
                self.log_write("Invalid output path for vector results")
                return

            args = {
                "probability_map": prob_map,
                "vector_layers_str": vector_layers_str,
                "output_vector": output_vec,
                "prob_threshold": self.vec_prob_thr.value(),
                "min_overlap_length": self.vec_min_overlap.value()
            }
            script = self.script_vectors
            method = "vectors"

        else:
            # RASTERS
            new_dir = self.r_new_le.text().strip()
            old_dir = self.r_old_le.text().strip()
            out_dir = self.r_out_le.text().strip()
            if not (new_dir and os.path.isdir(new_dir)):
                self.log_write("Invalid new raster directory")
                return
            if not (old_dir and os.path.isdir(old_dir)):
                self.log_write("Invalid old raster directory")
                return
            if not out_dir:
                self.log_write("Invalid output directory")
                return

            args = {
                "new_layer_dir": new_dir,
                "old_layer_dir": old_dir,
                "output_dir": out_dir,
                "threshold": self.r_threshold.value(),
                "tolerance": self.r_tolerance.value(),
                "buffer": self.r_buffer.value()
            }
            script = self.script_rasters
            method = "rasters"

        # disable UI
        self.run_btn.setEnabled(False)
        self.set_enabled(False)
        self.log_write("Starting age determination...\n")

        # start worker
        self.worker = AgeWorker(
            python_exec=python_exec,
            method=method,
            script_path=script,
            args=args
        )
        self.worker.log_signal.connect(self.log_write)
        self.worker.done_signal.connect(self._on_done)
        self.worker.start()

    def _on_done(self):
        self.log_write("\nAge determination finished.")
        self.run_btn.setEnabled(True)
        self.set_enabled(True)

    def set_enabled(self, state: bool):
        widgets = [
            self.python_exec,
            self.methods_tabs,
            # vectors
            self.prob_map_le, self.vec_table, self.vec_output_le, self.vec_prob_thr, self.vec_min_overlap,
            # rasters
            self.r_new_le, self.r_old_le, self.r_out_le, self.r_threshold, self.r_tolerance, self.r_buffer
        ]
        for w in widgets:
            w.setEnabled(state)
