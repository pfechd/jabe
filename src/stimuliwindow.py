import numpy as np
import scipy.io as sio
from PyQt5.QtWidgets import QFileDialog, QDialog

from src.generated_ui.create_stimuli import Ui_Stimuli_window


class StimuliWindow(QDialog):
     def __init__(self):
        #super(StimuliWindow, self).__init__(parent)
        self.ui = Ui_Stimuli_window(self)
        self.ui.setupUi(self)
        self.show();

     def add_row(self):
         #stuffs about to go down

