import numpy as np
import random

from PyQt5.QtWidgets import QDialog, QFileDialog
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
        self.mask_name = None

        self.ui.lineEdit_x.textChanged.connect(self.update_buttons)
        self.ui.lineEdit_y.textChanged.connect(self.update_buttons)
        self.ui.lineEdit_z.textChanged.connect(self.update_buttons)
        self.ui.lineEdit_radius_width.textChanged.connect(self.update_buttons)


        self.ui.pushButton_cancel.clicked.connect(self.close_window)
        self.ui.pushButton_create.clicked.connect(self.save_mask_window)
        self.show()

    def close_window(self):
        self.close()

    def add_shape_types(self):
        """
        Add all shape types that exists to a combobox
        """
        self.ui.comboBox_shape.addItem("Box")
        self.ui.comboBox_shape.addItem("Sphere")

    def is_number(self, s):
        if len(s):
            try:
                float(s)
                return True
            except ValueError:
                return False
        return False

    def update_buttons(self):
        # if the contents > 0 and are numbers
        text1 = self.ui.lineEdit_radius_width.text()
        text2 = self.ui.lineEdit_x.text()
        text3 = self.ui.lineEdit_y.text()
        text4 = self.ui.lineEdit_z.text()

        if self.is_number(text1) and self.is_number(text2) and self.is_number(text3) and self.is_number(text4):
            self.ui.pushButton_create.setEnabled(True)
        else:
            self.ui.pushButton_create.setEnabled(False)

    def save_mask_window(self):
        file_name = QFileDialog.getSaveFileName(self, "Save file as nii", "", ".nii")
        if len(file_name[0]):
            path = file_name[0]+file_name[1]
            #self.parent().save_mask(path)
            #self.parent().load_mask(path)
        else:
            print 'Mask name not chosen'