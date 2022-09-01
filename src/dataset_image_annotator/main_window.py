from pathlib import Path

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        path = Path(__file__).resolve().parent / 'main_window.ui'
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()
