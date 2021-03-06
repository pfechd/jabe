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
from nibabel.affines import apply_affine

import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5.QtWidgets import QDialog, QMessageBox
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

        self.show()

        self.show_brain()

    def convert_coord(self, coord):
        conversion_matrix = np.linalg.inv(self.session.anatomy.brain_file._affine).dot(self.session.mask.mask_file._affine)
        return apply_affine(conversion_matrix, coord)

    def show_brain(self):
        most_ones = np.around(self.convert_coord(self.session.mask.get_index_of_roi())).astype(int)
        new_mask = np.zeros(self.session.anatomy.brain_file.shape)

        shape_size = 20

        for z in range(int(most_ones[0][2]) - shape_size / 2, int(most_ones[0][2]) + shape_size / 2 + 1):
            for y in range(int(most_ones[0][1]) - shape_size / 2, int(most_ones[0][1]) + shape_size / 2 + 1):
                for x in range(int(most_ones[0][0]) - shape_size / 2, int(most_ones[0][0]) + shape_size / 2 + 1):
                    try:
                        new_mask[x, y ,z] = 1
                    except IndexError:
                        self.close()
                        QMessageBox.warning(self, "Anatomy image error", "The mask's position is outside the bounds"
                                                                         " of the anatomy image")
                        return

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
