import os
import numpy as np
import scipy.io as sio
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt5 import QtWidgets
import sys

from src.generated_ui.create_stimuli import Ui_Stimuli_window


class StimuliWindow(QDialog):
    """
    Window for creating a stimuli by manually putting in onset times
    and stimule values in a table.

    """
    
    def __init__(self, parent):
        """
        Create stimuli window.

        :param parent: Parent window object.
        """
        
        super(StimuliWindow, self).__init__(parent)
        self.ui = Ui_Stimuli_window()
        self.ui.setupUi(self)
        self.ui.cancel.clicked.connect(self.close_window)
        self.ui.add_row.clicked.connect(self.add_row)
        self.ui.remove_row.clicked.connect(self.remove_row)
        self.ui.create_stimuli.clicked.connect(self.save_stimuli)

        # Makes this window block the main window
        self.exec_()

    def add_row(self):
        rows = self.ui.stimuli_table.rowCount()
        self.ui.stimuli_table.setRowCount(rows+1)

    def remove_row(self):
        rows = self.ui.stimuli_table.rowCount()
        self.ui.stimuli_table.setRowCount(rows-1)
        
    def close_window(self):
        self.close()

    def create_stimuli_array(self):
        """
        Tries to create an array of the values in the table. 

        :return: If successful, an array representing the table. If
        not, an empty array.  
        :return example: array = [[12.3, 60],[13.7, 90], [15.2, 40]]

        """
        
        stimuli = []
        all_rows = self.ui.stimuli_table.rowCount()
        if all_rows == 0:
            QMessageBox.warning(self, "Warning", "Your table contains no rows. Please add rows and values.")
            return []
        else:
            for row in xrange(0, all_rows):
                # Goes through all columns in all rows of the table, converts them to
                # float and adds them to the stimuli array if they are numbers
                value = ''
                time = ''

                if self.ui.stimuli_table.item(row, 0):
                    time = self.ui.stimuli_table.item(row, 0).text()

                if self.ui.stimuli_table.item(row, 1):
                    value = self.ui.stimuli_table.item(row,1).text()

                if self.is_number(time) and self.is_number(value):
                    stimuli.append([float(time), float(value)])
                    if row == all_rows-1:
                        # If the end of the table has been reached,
                        # put the value from the end time box at the end of the array
                        time = self.ui.end_time_box.text()

                        if self.is_number(time):
                            stimuli.append([float(time), 0])
                        else:
                            QMessageBox.warning(self, "Warning", "You have entered an inaccurate end time value. Please enter only a number.")
                            return []
                else:
                    QMessageBox.warning(self, "Warning", "You have entered one or more invalid values. Please enter only numbers.")
                    return []
                
        return stimuli
        
    def save_stimuli(self):
        """ Saves the values from the table to a .mat file."""

        # Refreshes the table
        self.ui.stimuli_table.setDisabled(True)
        self.ui.stimuli_table.setDisabled(False)

        stimuli = self.create_stimuli_array()
        if stimuli:
            # If the table is valid, eg is not empty, save it and load
            # the created stimuli to the main window.
            file_path = QFileDialog.getSaveFileName(self, "Save stimuli", "", ".mat")
            if file_path[0]:
                filename = file_path[0].split(os.path.sep)[-1].split('.')[0]
                if filename:
                    # Checks if the filename is valid
                    self.close()
                    stimuli = np.array(stimuli)
                    sio.savemat(filename, {'visual_stimuli':stimuli})
                    self.parent().load_stimuli(filename +file_path[1])
                else:
                    QMessageBox.warning(self, "Warning", "Invalid filename.")
                
    def is_number(self, s):
        """
        Checks if a value is a number.
        
        :param s: Value that you want to validate
        :return: True if value is a number.
        """
        
        try:
            float(s)
            return True
        except ValueError:
            return False
