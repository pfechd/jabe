import numpy as np
import random

from PyQt5.QtWidgets import QDialog
from src.generated_ui.create_mask import Ui_CreateMask



class CreateMaskWindow(QDialog):
    """
        Class used to create a mask window, for creating a mask
    """
    def __init__(self, parent):
        super(CreateMaskWindow, self).__init__(parent)

        #self.ui.comboBox_shape.addItem("Box")
        #self.ui.comboBox_shape.addItem("Sphere")
        self.ui = Ui_CreateMask()
        self.ui.setupUi(self)
        self.setWindowTitle('Create mask')
        self.add_shape_types()

        self.ui.pushButton_cancel.clicked.connect(self.close_window)
        self.show()

    def close_window(self):
        self.close()

    def add_shape_types(self):
        """
        Add all shape types that exists to a combobox
        """
        self.ui.comboBox_shape.addItem("Box")
        self.ui.comboBox_shape.addItem("Sphere")