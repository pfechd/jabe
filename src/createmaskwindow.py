import numpy as np
import random
from nibabel.affines import apply_affine

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

    def is_pos_number(self, s):
        """ Check if the input value is a number """
        if len(s):
            try:
                float(s) and float(s) >= 0
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

        width = self.ui.lineEdit_width.text().replace(",", ".")
        x = self.ui.lineEdit_x.text().replace(",", ".")
        y = self.ui.lineEdit_y.text().replace(",", ".")
        z = self.ui.lineEdit_z.text().replace(",", ".")

        # If the coordinates and radius_width are valid numbers, then choose a given path and create the mask
        if self.is_pos_number(width) and self.is_pos_number(x) and self.is_pos_number(y) and self.is_pos_number(z):
            if float(width) == 0:
                QMessageBox.warning(
                self, "Warning", "You have entered invalid width/radius. Please enter numbers larger than zero.")
            else:
                # Convert coordinates and shape_size to voxels, using the affine matrix of the brain file
                coordinate = np.array([float(self.ui.lineEdit_x.text()), float(self.ui.lineEdit_y.text()), float(self.ui.lineEdit_z.text())])
                coordinate = apply_affine(np.linalg.inv(self.brain_file._affine), coordinate)
                coordinate[0] = round(coordinate[0])
                coordinate[1] = round(coordinate[1])
                coordinate[2] = round(coordinate[2])

                # If the coordinates together with radius_width are valid create a mask
                # If not valid send an error message
                if self.ui.comboBox_shape.currentText() == "Sphere":
                    voxel_width = (float(width)/self.brain_file._header.get_zooms()[0],
                                   float(width)/self.brain_file._header.get_zooms()[1],
                                   float(width)/self.brain_file._header.get_zooms()[2],)
                else:
                    voxel_width = ((float(width)/2)/self.brain_file._header.get_zooms()[0],
                                    (float(width)/2)/self.brain_file._header.get_zooms()[1],
                                    (float(width)/2)/self.brain_file._header.get_zooms()[2])

                # Check if coordinates is within brain data
                # Generates parameters to and call Mask function
                if coordinate[0] <= self.brain_file.get_data().shape[0]\
                        and coordinate[1] <= self.brain_file.get_data().shape[1]\
                        and coordinate[2] <= self.brain_file.get_data().shape[2]:
                    if (coordinate[0] + voxel_width[0]) <= self.brain_file.get_data().shape[0]\
                            and (coordinate[1] + voxel_width[1]) <= self.brain_file.get_data().shape[1]\
                            and (coordinate[2] + voxel_width[2]) <= self.brain_file.get_data().shape[2]\
                            and (coordinate[0] - voxel_width[0]) >= 0 and (coordinate[1] - voxel_width[1]) >= 0\
                            and (coordinate[2] - voxel_width[2]) >= 0:
                        file_name = QFileDialog.getSaveFileName(self, "Save file as nii", "", ".nii")
                        if file_name[0] == "":
                            return
                        path = file_name[0]+file_name[1]
                        shape = self.ui.comboBox_shape.currentText()
                        width = voxel_width
                        Mask(path, shape, coordinate, width, self.brain_file)
                        self.close()
                        self.parent().load_mask(path)
                    else:
                        QMessageBox.warning(
                            self, "Warning",
                            "You have entered invalid values in width. Please enter a value within the dimensions.")
                else:
                    QMessageBox.warning(
                        self, "Warning",
                        "You have entered invalid values in coordinate. Please enter values within the dimensions.")
        else:
            QMessageBox.warning(
                self, "Warning", "You have entered one or more invalid values. Please enter only numbers.")