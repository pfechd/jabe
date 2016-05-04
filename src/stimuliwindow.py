import numpy as np
import scipy.io as sio
from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5 import QtWidgets
import sys

from src.generated_ui.create_stimuli import Ui_Stimuli_window


class StimuliWindow(QDialog):
    """
    Window for creating a stimuli by manually putting in values in a table.
    """
    
    def __init__(self):
        super(StimuliWindow, self).__init__()
        self.ui = Ui_Stimuli_window()
        self.ui.setupUi(self)
        self.ui.cancel.clicked.connect(self.close_window)
        self.ui.add_row.clicked.connect(self.add_row)
        self.ui.create_stimuli.clicked.connect(self.save_stimuli)
        self.show();

    def add_row(self):
        rows = self.ui.stimuli_table.rowCount()
        self.ui.stimuli_table.setRowCount(rows+1)

    def close_window(self):
        self.close()

    def save_stimuli(self):
        """Saves the values from the table to a .mat file"""

        stimuli = []
        filename = QFileDialog.getSaveFileName(self, "Save stimuli", "", ".mat")
        all_rows = self.ui.stimuli_table.rowCount()
        if filename[0]:
            for row in xrange(0, all_rows):
                # Goes through all values in all rows in the table, converts them to
                # float and adds them to the stimuli array
                onset = []
                time = float(self.ui.stimuli_table.item(row, 0).text())
                value = float(self.ui.stimuli_table.item(row,1).text())
                onset.append(time)
                onset.append(value)
                stimuli.append(onset)
                
            self.close()
            
        stimuli = np.array(stimuli)
        sio.savemat(filename[0] + filename[1], {'visual_stimuli':stimuli})

        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    s = StimuliWindow()
    sys.exit(app.exec_())
     
          
     

