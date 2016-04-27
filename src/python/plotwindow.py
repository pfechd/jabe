import numpy as np
import random

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from exportwindow import ExportWindow
from src.python.generated_ui.custom_plot import Ui_Dialog


class CustomPlot(QDialog):
    """
    Class used to create a plot window

    Data is read from session object
    """

    def __init__(self, parent, session):
        """
        Create plot window

        :param parent: Parent window object
        :param session: Session object to plot data from
        :return:
        """
        super(CustomPlot, self).__init__(parent)
        self.amp = None
        self.fwhm = None
        self.mean = None
        self.std = None
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.scroll = 0

        self.session = session
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(121)
        self.img = self.fig.add_subplot(122)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.toolbar.hide()

        self.ui.mplvl.addWidget(self.canvas)

        self.ui.checkBox_fwhm.clicked.connect(self.apply_fwhm)
        self.ui.checkBox_std.clicked.connect(self.plot_std)
        self.ui.checkBox_mean.clicked.connect(self.plot_mean)
        self.ui.checkBox_amp.clicked.connect(self.plot_amplitude)
        self.ui.checkBox_points.clicked.connect(self.show_points)

        self.ui.toolButton_home.clicked.connect(self.toolbar.home)
        self.ui.toolButton_export.clicked.connect(self.tool_export)
        self.ui.toolButton_pan.clicked.connect(self.toolbar.pan)
        self.ui.toolButton_zoom.clicked.connect(self.toolbar.zoom)

        self.setWindowTitle('Plot - ' + session.name)
        self.export_window = None

        self.plot_mean()
        self.show_brain()

        if parent.ui.peak_checkbox.isChecked():
            self.ui.checkBox_amp.setChecked(True)
            self.plot_amplitude()

        if parent.ui.fwhm_checkbox.isChecked():
            self.ui.checkBox_fwhm.setChecked(True)
            self.apply_fwhm()

        #if parent.ui.sem_checkbox_2.isChecked():
         #   self.ui.sem_checkbox_2.setChecked(True)


        self.show()

    def tool_export(self):
        """
        Export button callback. Creates a custom export window
        :return:
        """
        self.export_window = ExportWindow(self, self.session, self.toolbar)

    def apply_fwhm(self):
        """
        FWHM checkbox callback. Plot FWHM for current graph. Disabled if no graph plotted

        :return:
        """

        if self.ui.checkBox_fwhm.isChecked():
            if self.mean is not None:
                y = self.ax.lines[0].get_ydata()
                x = np.arange(len(y))
                smooth = self.ui.spinBox.value()
                r1, r2 = self.session.calculate_fwhm(x, y, smooth)
                self.fwhm = self.ax.axvspan(r1, r2, facecolor='g', alpha=0.3)
                self.canvas.draw()
        else:
            if self.fwhm is not None:
                self.fwhm.remove()
            self.canvas.draw()

    def plot_mean(self):
        """
        Mean checkbox callback. Plot mean from session object

        :return:
        """
        if self.ui.checkBox_mean.isChecked():
            mean = self.session.calculate_mean()[0]
            self.ax.relim()
            self.mean, = self.ax.plot(mean, color=self.generate_random_color())

            self.canvas.draw()

            self.ui.checkBox_fwhm.setEnabled(True)
            self.ui.checkBox_amp.setEnabled(True)
            self.ui.checkBox_points.setEnabled(True)
            self.ui.spinBox.setEnabled(True)
        else:
            self.mean.remove()

            self.canvas.draw()

            self.ui.checkBox_amp.setDisabled(True)
            self.ui.checkBox_fwhm.setDisabled(True)
            self.ui.checkBox_points.setDisabled(True)
            self.ui.spinBox.setDisabled(True)

    def plot_std(self):
        """
        Standard deviation checkbox callback. Plot standard deviation of mean.

        :return:
        """

        if self.ui.checkBox_std.isChecked():
            mean = self.session.calculate_mean()[0]
            x = np.arange(mean.size)
            self.ax.relim()
            self.std = self.ax.errorbar(x, mean, yerr=self.session.calculate_std()[0])
            self.canvas.draw()
        else:
            self.std[0].remove()
            for line in self.std[1]:
                line.remove()
            for line in self.std[2]:
                line.remove()

            self.canvas.draw()


    #def plot_sem(self):
        """
            Standard error of mean checkbox callback. Plot standard error of mean.

            :return:
            """
     #   if self.ui.sem_checkbox_2.isChecked():

      #      self.canvas.draw()
       # else:

        #    self.canvas.draw()



    def plot_amplitude(self):
        """
        Amplitude checkbox callback. Annotate amplitude and time of peak in graph

        :return:
        """

        if self.ui.checkBox_amp.isChecked():
            y = self.ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_amp = self.session.calculate_amplitude(x, y, 0)
            self.amp = self.ax.annotate(
                'Time: %.2f\nAmp: %.2f' % (max_amp[0], max_amp[1]),
                xy=(max_amp[0], max_amp[1]), xytext=(max_amp[0] + 12, max_amp[1] - 1),
                ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc=self.generate_random_color(), alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3, rad=0')
            )
            self.canvas.draw()
        else:
            self.amp.remove()
            self.canvas.draw()

    def show_points(self):
        """
        Points checkbox callback. Show data points in graph

        :return:
        """

        if self.ui.checkBox_points.isChecked():
            self.mean.set_marker('o')
            self.canvas.draw()
        else:
            self.mean.set_marker('')
            self.canvas.draw()

    @staticmethod
    def generate_random_color():
        """
        Generate random color for graph

        :return: RGB hex string
        """

        def r():
            return random.randint(0, 255)

        return '#%02X%02X%02X' % (r(), r(), r())

    def show_brain(self):
        self.img.imshow(self.session.data[:,:,5,self.scroll])
        self.fig.canvas.mpl_connect('scroll_event', self.change_scroll)

    def change_scroll(self, event):
        if event.button == "up" and self.scroll < 8:
            self.scroll+=1
        elif event.button == "down" and self.scroll > 1:
            self.scroll-=1
        self.img.clear()
        self.img.imshow(self.session.data[:,:,5,self.scroll])
        self.canvas.draw()

