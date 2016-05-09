import numpy as np
from nibabel.affines import apply_affine

import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5.QtWidgets import QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.generated_ui.anatomy_window import Ui_Dialog

class AnatomyWindow(QDialog):
    """
    Class used to create a plot window

    Data is read from session object
    """

    def __init__(self, parent, session):
        """
        Create plot window

        :param parent: Parent window object
        :param session: Session object to plot data from
        """
        super(AnatomyWindow, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.session = session
        self.fig = plt.figure()

        self.img1 = self.fig.add_subplot(131)
        self.img2 = self.fig.add_subplot(132)
        self.img3 = self.fig.add_subplot(133)

        self.canvas = FigureCanvas(self.fig)
        self.ui.anatomy_layout.addWidget(self.canvas)

        self.setWindowTitle('Anatomy - ' + session.name)

        self.show_brain()

        self.show()

    def convert_coord(self, coord):
        conversion_matrix = np.linalg.inv(self.session.anatomy.brain_file._affine).dot(self.session.brain.brain_file._affine)
        return apply_affine(conversion_matrix, coord)

    def show_brain(self):
        most_ones = np.around(self.convert_coord(self.session.mask.get_index_of_roi())).astype(int)
        new_mask = np.zeros(self.session.anatomy.brain_file.shape)

        shape_size = 20

        for z in range(int(most_ones[0][2]) - shape_size / 2, int(most_ones[0][2]) + shape_size / 2 + 1):
            for y in range(int(most_ones[0][1]) - shape_size / 2, int(most_ones[0][1]) + shape_size / 2 + 1):
                for x in range(int(most_ones[0][0]) - shape_size / 2, int(most_ones[0][0]) + shape_size / 2 + 1):
                    new_mask[x, y ,z] = 1

        masked_array = np.ma.masked_where(new_mask == 0, new_mask)
        self.img1.imshow(self.session.anatomy.sequence[:,:,most_ones[0][2]], cmap=mpl.cm.gray)
        self.img1.imshow(masked_array[:,:,most_ones[0][2]], cmap=mpl.cm.spring, alpha=0.8)
        self.img2.imshow(self.session.anatomy.sequence[:,most_ones[0][1],:], cmap=mpl.cm.gray)
        self.img2.imshow(masked_array[:,most_ones[0][1],:], cmap=mpl.cm.spring, alpha=0.8)
        self.img3.imshow(self.session.anatomy.sequence[most_ones[0][0],:,:], cmap=mpl.cm.gray)
        self.img3.imshow(masked_array[most_ones[0][0],:,:], cmap=mpl.cm.spring, alpha=0.8)

        self.img1.xaxis.set_visible(False)
        self.img1.yaxis.set_visible(False)
        self.img2.xaxis.set_visible(False)
        self.img2.yaxis.set_visible(False)
        self.img3.xaxis.set_visible(False)
        self.img3.yaxis.set_visible(False)

        self.canvas.draw()
