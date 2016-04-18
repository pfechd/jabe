import random
from export_window import ExportWindow
from PyQt5.QtWidgets import QDialog, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from src.python.generated_ui.custom_plot import Ui_Dialog


class CustomPlot(QDialog):
    def __init__(self, parent, session):
        super(CustomPlot, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.session = session
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
        self.ui.checkBox_points.clicked.connect(self.show_points)

        self.ui.toolButton_home.clicked.connect(self.tool_home)
        self.ui.toolButton_export.clicked.connect(self.tool_export)
        self.ui.toolButton_pan.clicked.connect(self.tool_pan)
        self.ui.toolButton_zoom.clicked.connect(self.tool_zoom)

        self.setWindowTitle('Plot - ' + session.name)

        self.plot_mean()

        self.show()

    def tool_home(self):
        self.toolbar.home()

    def tool_pan(self):
        self.toolbar.pan()

    def tool_zoom(self):
        self.toolbar.zoom()

    def tool_export(self):
        self.exportwindow = ExportWindow(self.session, self.toolbar)

    def apply_fwhm(self):
        if self.ui.checkBox_fwhm.isChecked():
            if self.mean is not None:
                y = self.ax.lines[0].get_ydata()
                x = np.arange(len(y))
                smooth = self.ui.spinBox.value()
                r1, r2 = self.session.calculate_fwhm(x, y, smooth)
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
            self.resp = self.ax.plot(self.session.response)
            self.canvas.draw()
        else:
            for line in self.resp:
                line.remove()
            self.canvas.draw()

    def plot_mean(self):
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
            self.mean = None

            self.canvas.draw()

            self.ui.checkBox_amp.setDisabled(True)
            self.ui.checkBox_fwhm.setDisabled(True)
            self.ui.checkBox_points.setDisabled(True)
            self.ui.spinBox.setDisabled(True)

    def plot_std(self):
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

    def plot_amplitude(self):
        if self.ui.checkBox_amp.isChecked():
            y = self.ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_amp = self.session.calculate_amplitude(x, y, 0)
            self.amp = self.ax.annotate(
                'Time: %.2f\nAmp: %.2f' % (max_amp[0], max_amp[1]),
                xy=(max_amp[0], max_amp[1]), xytext=(max_amp[0] + 12, max_amp[1] - 1),
                ha='right', va='bottom',
                bbox=dict(boxstyle = 'round,pad=0.5', fc = self.generate_random_color(), alpha = 0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle = 'arc3, rad=0')
            )
            self.canvas.draw()
        else:
            self.amp.remove()
            self.canvas.draw()

    def show_points(self):
        if self.ui.checkBox_points.isChecked():
            self.mean.set_marker('o')
            self.canvas.draw()
        else:
            self.mean.set_marker('')
            self.canvas.draw()

    def generate_random_color(self):
        r = lambda: random.randint(0, 255)
        return '#%02X%02X%02X' % (r(), r(), r())
