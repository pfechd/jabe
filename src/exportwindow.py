 # Copyright (C) 2016 pfechd
#
# This file is part of JABE.
#
# JABE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# JABE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JABE.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import scipy.io as sio
from PyQt5.QtWidgets import QFileDialog, QDialog

from src.generated_ui.export_window import Ui_Export_Window


class ExportWindow(QDialog):
    def __init__(self, parent, brain, toolbar, stimuli_type):
        super(ExportWindow, self).__init__(parent)
        self.ui = Ui_Export_Window()
        self.ui.setupUi(self)
        self.brain = brain
        self.toolbar = toolbar
        self.stimuli_type = stimuli_type
        self.ui.export_mat_button.clicked.connect(self.export_mat)
        self.ui.export_txt_button.clicked.connect(self.export_txt)
        self.ui.export_image_button.clicked.connect(self.export_image)

        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.show()


    def export_image(self):
        self.close()
        self.toolbar.save_figure()

    def export_mat(self):
        filename = QFileDialog.getSaveFileName(self, "Save file as mat", "", ".mat")
        if filename[0]:
            if self.stimuli_type == "All":
                sio.savemat(filename[0] + filename[1], self.brain.get_mean())
            else:
                sio.savemat(filename[0] + filename[1], {'data': self.brain.get_mean()[self.stimuli_type]})
        self.close()

    def export_txt(self):
        filename = QFileDialog.getSaveFileName(self, "Save file as txt", "", ".txt")
        if filename[0]:
            data = self.brain.get_mean()
            if self.stimuli_type == "All":
                txtdata = None
                for type,stim_data in data.iteritems():
                    stim_data = np.concatenate((np.asarray([int(type)]), stim_data))
                    if txtdata is None:
                        txtdata = stim_data.reshape(1, stim_data.shape[0])
                    else:
                        txtdata = np.concatenate((txtdata,stim_data.reshape(1, stim_data.shape[0])))

                np.savetxt(filename[0] + filename[1], txtdata, "%.18f")
            else:
                np.savetxt(filename[0] + filename[1], data[self.stimuli_type], "%.18f")
        self.close()
