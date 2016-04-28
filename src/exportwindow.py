import numpy as np
import scipy.io as sio
from PyQt5.QtWidgets import QFileDialog, QDialog

from src.generated_ui import Ui_Export_Window


class ExportWindow(QDialog):
    def __init__(self, parent, brain, toolbar):
        super(ExportWindow, self).__init__(parent)
        self.ui = Ui_Export_Window()
        self.ui.setupUi(self)
        self.brain = brain
        self.toolbar = toolbar
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
            sio.savemat(filename[0] + filename[1], {'data': self.brain.calculate_mean()[0]})
        self.close()

    def export_txt(self):
        filename = QFileDialog.getSaveFileName(self, "Save file as txt", "", ".txt")
        if filename[0]:
            np.savetxt(filename[0] + filename[1], self.brain.calculate_mean()[0], "%.18f")
        self.close()

