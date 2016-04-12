from PyQt5.QtWidgets import QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from src.python.generated_ui.custom_plot import Ui_Dialog


class CustomPlot(QDialog):
    def __init__(self, brain):
        super(CustomPlot, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Plot - ' + brain.path)

        self.brain = brain
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.toolbar.hide()

        self.ui.mplvl.addWidget(self.canvas)

        self.ui.checkBox_fwhm.clicked.connect(self.apply_fwhm)
        self.ui.checkBox_std.clicked.connect(self.plot_std)
        self.ui.checkBox_mean.clicked.connect(self.plot_mean)
        self.ui.checkBox_amp.clicked.connect(self.plot_amplitude)
        self.ui.toolButton_home.clicked.connect(self.tool_home)
        self.ui.toolButton_export.clicked.connect(self.tool_export)
        self.ui.toolButton_pan.clicked.connect(self.tool_pan)
        self.ui.toolButton_zoom.clicked.connect(self.tool_zoom)

    def tool_home(self):
        self.toolbar.home()

    def tool_export(self):
        self.toolbar.save_figure()

    def tool_pan(self):
        self.toolbar.pan()

    def tool_zoom(self):
        self.toolbar.zoom()

    def apply_fwhm(self):
        if self.ui.checkBox_fwhm.isChecked():
            if self.mean is not None:
                y = self.ax.lines[0].get_ydata()
                x = np.arange(len(y))
                r1, r2 = self.brain.calculate_fwhm(x, y, 20)
                self.fwhm = self.ax.axvspan(r1, r2, facecolor='g', alpha=0.3)
                self.canvas.draw()
            else:
                self.fwhm = None
        else:
            if self.fwhm is not None:
                self.fwhm.remove()
            self.canvas.draw()

    def plot_response(self):
        if self.ui.checkBox_response.isChecked():
            self.resp = self.ax.plot(self.brain.response)
            self.canvas.draw()
        else:
            for line in self.resp:
                line.remove()
            self.canvas.draw()

    def plot_mean(self):
        if self.ui.checkBox_mean.isChecked():
            mean = self.brain.calculate_mean()[0]
            self.mean, = self.ax.plot(mean)
            self.canvas.draw()
        else:
            if self.mean is not None:
                self.mean.remove()
                self.mean = None
            self.canvas.draw()

    def plot_std(self):
        if self.ui.checkBox_std.isChecked():
            mean = self.brain.calculate_mean()[0]
            x = np.arange(mean.size)
            self.std = self.ax.errorbar(x, mean, yerr=self.brain.calculate_std()[0])
            self.canvas.draw()
        else:
            if self.std is not None:
                self.std[0].remove()
                for line in self.std[1]:
                    line.remove()
                for line in self.std[2]:
                    line.remove()

            self.canvas.draw()

    def plot_amplitude(self):
        if self.ui.checkBox_amp.isChecked():
            if self.mean is not None:
                y = self.ax.lines[0].get_ydata()
                x = np.arange(len(y))
                max_amp = self.brain.calculate_amplitude(x, y, 0)
                self.ampx, = self.ax.plot([x[0], x[-1]], [max_amp[1]] * 2, '--')
                self.ampy, = self.ax.plot([max_amp[0]] * 2, [max(y) - 1, max(y) + 1], '--')
                self.canvas.draw()
            else:
                self.ampx = None
                self.ampy = None
        else:
            if self.ampx is not None:
                self.ampx.remove()
            if self.ampy is not None:
                self.ampy.remove()
            self.canvas.draw()
