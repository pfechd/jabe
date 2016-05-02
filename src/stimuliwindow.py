import numpy as np
import scipy.io as sio
from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5 import QtWidgets
import sys

from src.generated_ui.create_stimuli import Ui_Stimuli_window


class StimuliWindow(QDialog):
    def __init__(self):
        super(StimuliWindow, self).__init__()
        self.ui = Ui_Stimuli_window()
        self.ui.setupUi(self)
        self.ui.add_row.clicked.connect(self.add_row)
        self.show();

    def add_row(self):
        rows = self.ui.stimuli_table.rowCount()
        self.ui.stimuli_table.setRowCount(rows+1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    s = StimuliWindow()
    sys.exit(app.exec_())

