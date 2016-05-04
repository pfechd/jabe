import numpy as np
import scipy.io as sio
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt5 import QtWidgets
import sys

from src.generated_ui.create_stimuli import Ui_Stimuli_window


class StimuliWindow(QDialog):
    """
    Window for creating a stimuli by manually putting in values in a table.
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
        self.ui.create_stimuli.clicked.connect(self.save_stimuli)
        self.show()

    def add_row(self):
        rows = self.ui.stimuli_table.rowCount()
        self.ui.stimuli_table.setRowCount(rows+1)

    def close_window(self):
        self.close()

    def create_stimuli_array(self):
        """
        Tries to create an array of the values in the table. 

        :return: If successful, an array representing the table. If not, an empty array.
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
                onset = []
                time = self.ui.stimuli_table.item(row, 0).text()
                value = self.ui.stimuli_table.item(row,1).text()
                if self.is_number(time) and self.is_number(value):
                    stimuli.append([float(time), float(value)])
                else:
                    QMessageBox.warning(self, "Warning", "You have entered one or more invalid values. Please enter only numbers.")
                    return []
                
        return stimuli
        
    def save_stimuli(self):
        """ Saves the values from the table to a .mat file"""

        stimuli = self.create_stimuli_array()
            if stimuli:
                # If the table is valid, eg is not empty, save it and load the created stimuli to the main window
                filename = QFileDialog.getSaveFileName(self, "Save stimuli", "", ".mat")
                if filename[0]:
                    self.close()
                    stimuli = np.array(stimuli)
                    sio.savemat(filename[0], {'visual_stimuli':stimuli})
                    self.parent().load_stimuli(filename[0] + filename[1])
                
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
