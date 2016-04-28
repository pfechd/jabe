import numpy as np
import random

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from scipy.interpolate import UnivariateSpline

from exportwindow import ExportWindow
from src.generated_ui.custom_plot import Ui_Dialog
from session import Session


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
        """
        super(CustomPlot, self).__init__(parent)
        self.amp = None
        self.fwhm = None
        self.mean = []
        self.smooth = []
        self.sem = None
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.session = session
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.toolbar.hide()

        self.ui.mplvl.addWidget(self.canvas)

        self.ui.checkBox_fwhm.toggled.connect(self.apply_fwhm)
        self.ui.checkBox_sem.toggled.connect(self.plot_sem)
        self.ui.checkBox_mean.toggled.connect(self.plot_mean)
        self.ui.checkBox_smooth.toggled.connect(self.plot_smooth)
        self.ui.checkBox_amp.toggled.connect(self.plot_amplitude)
        self.ui.checkBox_points.toggled.connect(self.show_points)
        self.ui.stimuliBox.currentIndexChanged.connect(self.replot)

        self.ui.spinBox.valueChanged.connect(self.replot)

        self.ui.toolButton_home.clicked.connect(self.toolbar.home)
        self.ui.toolButton_export.clicked.connect(self.tool_export)
        self.ui.toolButton_pan.clicked.connect(self.toolbar.pan)
        self.ui.toolButton_zoom.clicked.connect(self.toolbar.zoom)

        self.setWindowTitle('Plot - ' + session.name)
        self.export_window = None
        self.add_stimuli_types()
        self.plot_mean()

        if parent.ui.checkbox_peak_session.isChecked():
            self.ui.checkBox_amp.setChecked(True)

        if parent.ui.checkbox_fwhm_session.isChecked():
            self.ui.checkBox_fwhm.setChecked(True)

        #if parent.ui.sem_checkbox_2.isChecked():
         #   self.ui.sem_checkbox_2.setChecked(True)


        self.show()

    def tool_export(self):
        """
        Export button callback. Creates a custom export window
        """
        self.export_window = ExportWindow(self, self.session, self.toolbar, self.ui.stimuliBox.currentText())

    def apply_fwhm(self):
        """
        FWHM checkbox callback. Plot FWHM for current graph. Disabled if no graph plotted
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

    def replot(self):
        if self.mean:
            for axis in self.mean:
                axis.remove()
            self.mean = []
        self.plot_mean()
        if self.smooth:
            for axis in self.smooth:
                axis.remove()
            self.smooth = []
        self.plot_smooth()

    def plot_smooth(self):
        """
        Smooth checkbox callback. Plot smooth from session object
        """
        if self.ui.checkBox_smooth.isChecked():
            self.ax.relim()
            before_smooth = self.session.calculate_mean()

            if self.ui.stimuliBox.currentText() == "All":
                for stimuli_type,stimuli_data in before_smooth.iteritems():
                    x = np.arange(stimuli_data.shape[0])
                    curr = UnivariateSpline(x, stimuli_data, s=self.ui.spinBox.value())
                    axis, = self.ax.plot(curr(x), color=self.generate_random_color())
                    self.smooth.append(axis)
            else:
                x = np.arange(before_smooth[self.ui.stimuliBox.currentText()].shape[0])
                curr = UnivariateSpline(x, before_smooth[self.ui.stimuliBox.currentText()], s=self.ui.spinBox.value())
                axis, = self.ax.plot(curr(x), color=self.generate_random_color())
                self.smooth.append(axis)

            self.canvas.draw()
        else:
            for axis in self.smooth:
                axis.remove()
            self.smooth = []
            self.canvas.draw()


    def plot_mean(self):
        """
        Mean checkbox callback. Plot mean from session object
        """
        if self.ui.checkBox_mean.isChecked():
            self.ax.relim()
            self.ui.checkBox_points.setChecked(False)
            self.ui.checkBox_fwhm.setChecked(False)
            self.ui.checkBox_amp.setChecked(False)
            self.ui.checkBox_sem.setChecked(False)
            mean = self.session.calculate_mean()
            if self.ui.stimuliBox.currentText() == "All":
                for stimuli_type,stimuli_data in mean.iteritems():
                    axis, = self.ax.plot(stimuli_data, color=self.generate_random_color())
                    self.mean.append(axis)
            else:
                axis, = self.ax.plot(mean[self.ui.stimuliBox.currentText()], color=self.generate_random_color())
                self.mean.append(axis)

            self.canvas.draw()

        else:
            for axis in self.mean:
                axis.remove()
            self.mean = []
            self.canvas.draw()

    def plot_sem(self):
        """
        Standard error of mean checkbox callback. Plot standard error of mean.
        """

        if self.ui.checkBox_sem.isChecked() and self.ui.stimuliBox.currentText() != "All" and isinstance(self.session, Session):
            mean = self.session.calculate_mean()[self.ui.stimuliBox.currentText()]
            x = np.arange(mean.size)
            self.ax.relim()
            sem = self.session.calculate_sem()
            self.sem =self.ax.errorbar(x, mean, yerr=sem[self.ui.stimuliBox.currentText()])
            self.canvas.draw()
        else:
            if self.sem:
                self.sem[0].remove()
                for line in self.sem[1]:
                    line.remove()
                for line in self.sem[2]:
                    line.remove()
                self.sem = None

            self.canvas.draw()

    def plot_amplitude(self):
        """
        Amplitude checkbox callback. Annotate amplitude in graph
        """

        if self.ui.checkBox_amp.isChecked():
            y = self.ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_amp = self.session.calculate_amplitude(x, y, 0)
            self.amp = self.ax.axhline(max_amp[1], color=self.generate_random_color())
            self.canvas.draw()
        else:
            self.amp.remove()
            self.canvas.draw()

    def show_peak(self):
        """
        Peak checkbox callback. Annotate time of peak in graph
        """
        
        if self.ui.checkBox_peak.isChecked():
            y = self.ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_amp = self.session.calculate_amplitude(x, y, 0)
            self.amp_time = self.ax.axvline(max_amp[0], color=self.generate_random_color())
            self.canvas.draw()
        else:
            self.amp_time.remove()
            self.canvas.draw()
            
    def show_points(self):
        """
        Points checkbox callback. Show data points in graph
        """
        if self.mean:
            if self.ui.checkBox_points.isChecked():
                for axis in self.mean:
                    axis.set_marker('o')
                self.canvas.draw()
            else:
                for axis in self.mean:
                    axis.set_marker('')
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

    def add_stimuli_types(self):
        """
        Add all stimuli types that exists in the data to a combobox
        """
        self.ui.stimuliBox.addItem("All")
        data = self.session.calculate_mean()
        for stimuli_type in data:
            self.ui.stimuliBox.addItem(stimuli_type)
