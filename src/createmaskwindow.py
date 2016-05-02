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

        self.ui = Ui_CreateMask()
        self.ui.setupUi(self)
        self.setWindowTitle('Create mask')
        self.add_shape_types()
        #self.ui.textEdit_x.textChanged.connect(self.update_buttons)

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

    def update_buttons(self):
        # if the contents > 0
        if self.ui.textEdit_x and self.ui.textEdit_y and self.ui.textEdit_z and self.ui.textEdit_radius_width:
            self.ui.pushButton_create.setEnabled(True)
        else:
            self.ui.pushButton_create.setEnabled(False)
        #self.ui.pushButton_create.setEnabled(True)
