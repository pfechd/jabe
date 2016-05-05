import numpy as np
import random

from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from src.generated_ui.create_mask import Ui_CreateMask
from mask import Mask


class CreateMaskWindow(QDialog):
    """
        Class used to create a mask window, for creating a mask
    """
    def __init__(self, parent, brain_file):
        super(CreateMaskWindow, self).__init__(parent)

        self.ui = Ui_CreateMask()
        self.ui.setupUi(self)
        self.setWindowTitle('Create mask')
        self.add_shape_types()
        self.mask_name = None
        self.brain_file = brain_file

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
        # if the contents > 0
        if len(self.ui.lineEdit_radius_width.text()) and len(self.ui.lineEdit_x.text())\
                and len(self.ui.lineEdit_y.text()) and len(self.ui.lineEdit_z.text()):
            self.ui.pushButton_create.setEnabled(True)
        else:
            self.ui.pushButton_create.setEnabled(False)

    # If the coordinate and radius/width are numbers, then choose a path and create the mask
    def save_mask_window(self):
        if self.is_number(self.ui.lineEdit_radius_width.text()) and self.is_number(self.ui.lineEdit_x.text())\
                and self.is_number(self.ui.lineEdit_y.text()) and self.is_number(self.ui.lineEdit_z.text()):

            # TODO: if the coordinates and radius/width are valid (not bigger than size dimensions) do everything below,
            # else show a QMessageBox.warning that describes the problem

            file_name = QFileDialog.getSaveFileName(self, "Save file as nii", "", ".nii")
            path = file_name[0]+file_name[1]
            shape = self.ui.comboBox_shape.currentText()
            coordinate = [float(self.ui.lineEdit_x.text()), float(self.ui.lineEdit_y.text()), float(self.ui.lineEdit_z.text())]
            radius_width = float(self.ui.lineEdit_radius_width.text())
            radius_width = (radius_width, radius_width, radius_width)
            Mask(path, shape, coordinate, radius_width, self.brain_file)
            self.close()
            self.parent().load_mask(path)
        else:
            QMessageBox.warning(self, "Warning", "You have entered one or more invalid values. Please enter only numbers.")