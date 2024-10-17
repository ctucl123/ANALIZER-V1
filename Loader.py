import sys
import pandas as pd
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget


#desarrollado por MECDEVS - 2024 www.mecdevs.com
class FileLoader(QWidget):
    def __init__(self):
        super().__init__()

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("JSON files (*.json)")
        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]
            return file_name
        return None

    def load_json(self, file_name):
        df = pd.read_json(file_name)
        print(df)