from PyQt5.QtWidgets import QFileDialog, QDialog
from src.python.generated_ui.export_window import Ui_Export_Window
import numpy as np
import scipy.io as sio


class ExportWindow(QDialog):
    def __init__(self, brain):
        super(ExportWindow, self).__init__()
        self.ui = Ui_Export_Window()
        self.ui.setupUi(self)
        self.brain = brain
        self.ui.export_mat_button.clicked.connect(self.export_mat)
        self.ui.export_txt_button.clicked.connect(self.export_txt)
        self.ui.export_image_button.clicked.connect(self.export_image)
        self.show()

    def export_image(self):
        self.toolbar.save_figure()

    def export_mat(self):
        filename = QFileDialog.getSaveFileName(None,"Save file as mat","",".mat")
        sio.savemat(filename[0] + filename[1], {'data':self.brain.calculate_mean()[0]})

    def export_txt(self):
        filename = QFileDialog.getSaveFileName(None,"Save file as txt","",".txt")
        np.savetxt(filename[0] + filename[1],self.brain.calculate_mean()[0], "%.18f")
