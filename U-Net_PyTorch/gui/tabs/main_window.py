from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from tabs.inference_tab import InferenceTab
from tabs.training_tab import TrainingTab
from tabs.test_tab import TestTab
from tabs.age_tab import AgeDeterminationTab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DitchNet – GUI")
        self.setFixedWidth(650)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.tabs.addTab(InferenceTab(), "Inference")
        self.tabs.addTab(TrainingTab(), "Training")
        self.tabs.addTab(TestTab(), "Testing")
        self.tabs.addTab(AgeDeterminationTab(), "Age determination")

        layout.addWidget(self.tabs)
