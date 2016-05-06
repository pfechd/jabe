import numpy as np
import random

from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from src.generated_ui.create_mask import Ui_CreateMask
from mask import Mask


class CreateMaskWindow(QDialog):
    """ Class used to create a mask window, for creating a mask """

    def __init__(self, parent, brain_file):
        """
            Create mask window

            :param parent: Parent window object
            :param brain_file: The EPI-image
        """
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
        self.ui.lineEdit_width.textChanged.connect(self.update_buttons)

        self.ui.pushButton_cancel.clicked.connect(self.close_window)
        self.ui.pushButton_create.clicked.connect(self.save_mask_window)
        self.show()

    def close_window(self):
        self.close()

    def add_shape_types(self):
        """ Add all shape types that exists to a combobox """
        self.ui.comboBox_shape.addItem("Box")
        self.ui.comboBox_shape.addItem("Sphere")

    def is_number(self, s):
        """ Check if the input value is a number """
        if len(s):
            try:
                float(s)
                return True
            except ValueError:
                return False
        return False

    def update_buttons(self):
        """ Check if all text fields are not empty and enables/disables the create mask button """
        if len(self.ui.lineEdit_width.text()) and len(self.ui.lineEdit_x.text())\
                and len(self.ui.lineEdit_y.text()) and len(self.ui.lineEdit_z.text()):
            self.ui.pushButton_create.setEnabled(True)
        else:
            self.ui.pushButton_create.setEnabled(False)

    def save_mask_window(self):
        """ Creates and saves the mask """

        # If the coordinates and radius_width are numbers, then choose a given path and create the mask
        if self.is_number(self.ui.lineEdit_width.text()) and self.is_number(self.ui.lineEdit_x.text())\
                and self.is_number(self.ui.lineEdit_y.text()) and self.is_number(self.ui.lineEdit_z.text()):

            # If the coordinates together with radius_width are valid create a mask
            # If not valid send an error message
            voxel_x = (float(self.ui.lineEdit_x.text())*self.brain_file._header.get_zooms())
            voxel_y = (float(self.ui.lineEdit_y.text())*self.brain_file._header.get_zooms())
            voxel_z = (float(self.ui.lineEdit_z.text())*self.brain_file._header.get_zooms())
            voxel_radius_width = (float(self.ui.lineEdit_width.text())*self.brain_file._header.get_zooms())

            if voxel_x <= self.brain_file.brain_file.get_data().shape[0]\
                and voxel_y <= self.brain_file.brain_file.get_data().shape[1]\
                    and voxel_z <= self.brain_file.brain_file.get_data().shape[2]:
                if (voxel_x + voxel_radius_width) <= self.brain_file.brain_file.get_data().shape[0]\
                        and (voxel_y + voxel_radius_width) <= self.brain_file.brain_file.get_data().shape[1]\
                    and (voxel_z + voxel_radius_width) <= self.brain_file.brain_file.get_data().shape[2]\
                    and (voxel_x - voxel_radius_width) <= 0 and (voxel_y - voxel_radius_width) <= 0\
                        and (voxel_z - voxel_radius_width) <= 0:
                    file_name = QFileDialog.getSaveFileName(self, "Save file as nii", "", ".nii")
                    path = file_name[0]+file_name[1]
                    shape = self.ui.comboBox_shape.currentText()
                    coordinate = [float(self.ui.lineEdit_x.text()), float(self.ui.lineEdit_y.text()),
                                  float(self.ui.lineEdit_z.text())]
                    width = (float(self.ui.lineEdit_width.text()), float(self.ui.lineEdit_width.text()),
                             float(self.ui.lineEdit_width.text()))
                    Mask(path, shape, coordinate, width, self.brain_file)
                    self.close()
                    self.parent().load_mask(path)
                else:
                    QMessageBox.warning(self, "Warning", "You have entered invalid values in width. Please enter a value within the dimentions")
            else:
                QMessageBox.warning(self, "Warning", "You have entered invalid values in coordinate. Please enter values within the dimentions")
        else:
            QMessageBox.warning(self, "Warning", "You have entered one or more invalid values. Please enter only numbers.")