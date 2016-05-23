import numpy as np

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from scipy.interpolate import UnivariateSpline

from exportwindow import ExportWindow
from src.generated_ui.custom_plot import Ui_Dialog
from session import Session
from anatomywindow import AnatomyWindow


class CustomPlot(QDialog):
    """
    Class used to create a plot window

    Data is read from session object
    """

    _colors = ['#FF0000', '#0000FF', '#00FF00', '#00002C', '#FF1AB9',
                '#FFD300', '#005800', '#8484FF', '#9E4F46', '#00FFC1',
                '#008495', '#00007B', '#95D34F', '#F69EDC', '#D312FF']

    def __init__(self, parent, session):
        """
        Create plot window

        :param parent: Parent window object
        :param session: Session object to plot data from
        """

        super(CustomPlot, self).__init__(parent)
        self.amp = None
        self.peak_time = None
        self.fwhm = None
        self.regular = []
        self.smooth = []
        self.sem = None
        self.scroll = 3
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.color_index = 0

        self.session = session
        self.fig = plt.figure()

        self.ax = self.fig.add_subplot(111)
        self.ui.toolButton_anatomy.hide()

        if session.anatomy is not None:
            self.ui.toolButton_anatomy.show()

        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.toolbar.hide()

        self.ui.mplvl.addWidget(self.canvas)

        self.ui.checkBox_fwhm.toggled.connect(self.apply_fwhm)
        self.ui.checkBox_sem.toggled.connect(self.plot_sem)
        self.ui.checkBox_regular.toggled.connect(self.plot_regular)
        self.ui.checkBox_smooth.toggled.connect(self.plot_smooth)
        self.ui.checkBox_amp.toggled.connect(self.plot_amplitude)
        #self.ui.checkBox_points.toggled.connect(self.show_points)
        self.ui.checkBox_peak.toggled.connect(self.plot_peak)
        self.ui.stimuliBox.currentIndexChanged.connect(self.replot)
        self.ui.mean_response_btn.toggled.connect(self.replot)

        self.ui.spinBox.valueChanged.connect(self.replot)

        self.ui.toolButton_home.clicked.connect(self.toolbar.home)
        self.ui.toolButton_export.clicked.connect(self.tool_export)
        self.ui.toolButton_pan.clicked.connect(self.toolbar.pan)
        self.ui.toolButton_zoom.clicked.connect(self.toolbar.zoom)
        self.ui.toolButton_anatomy.clicked.connect(self.tool_anatomy)

        self.setWindowTitle('Plot - ' + session.name)
        self.export_window = None
        self.add_stimuli_types()

        # Enable the 'plot several' button if the object has more than 1 child
        children = self.session.children + self.session.sessions
        if children and len(children) > 1:
            self.ui.several_responses_btn.setEnabled(True)

        self.ui.checkBox_peak.setChecked(self.session.get_setting('peak'))

        self.ui.checkBox_fwhm.setChecked(self.session.get_setting('fwhm'))

        self.ui.checkBox_amp.setChecked(self.session.get_setting('amplitude'))

        self.ui.checkBox_sem.setChecked(self.session.get_setting('sem'))

        # Move the subplot to make space for the legend
        self.fig.subplots_adjust(right=0.8)

        self.set_allowed_buttons()

        self.show()

    def tool_anatomy(self):
         self.anatomy_window = AnatomyWindow(self, self.session)

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
            if self.regular is not None:
                y = self.ax.lines[0].get_ydata()
                x = np.arange(len(y))*self.session.get_tr()
                smooth = self.ui.spinBox.value()
                r1, r2 = self.session.calculate_fwhm(x, y, smooth)
                self.fwhm = self.ax.axvspan(r1, r2, facecolor='g', alpha=0.3)
                self.ui.fwhm_label.setText("FWHM begins at %.2f s\nFWHM ends at %.2f s\nDuration: %.2f s" %
                                           (r1, r2, r2-r1))
                self.ui.fwhm_label.show()
                self.canvas.draw()
        else:
            self.remove_fwhm()

        self.canvas.draw()

    def replot(self):
        """
        Replot regular and smoothed curve. Used when changing the data to plot
        """
        self.remove_peak_time()
        self.remove_amplitude()
        self.remove_fwhm()
        self.remove_sem()

        self.remove_regular_plots()
        self.plot_regular()
        self.remove_smoothed_plots()
        self.plot_smooth()
        
        self.plot_amplitude()
        self.plot_peak()
        self.apply_fwhm()
        self.plot_sem()
        self.set_allowed_buttons()

    def remove_peak_time(self):
        if self.peak_time:
            self.peak_time.remove()
            self.peak_time = None
            self.ui.peak_label.hide()

    def remove_sem(self):
        if self.sem:
            self.sem[0].remove()
            for line in self.sem[1]:
                line.remove()
            for line in self.sem[2]:
                line.remove()
            self.sem = None

    def remove_amplitude(self):
        if self.amp:
            self.amp.remove()
            self.amp = None
            self.ui.amp_label.hide()

    def remove_fwhm(self):
        if self.fwhm is not None:
            self.fwhm.remove()
            self.fwhm = None
            self.ui.fwhm_label.hide()

    def remove_regular_plots(self):
        if self.regular:
            for axis in self.regular:
                axis.remove()
            self.regular = []

    def plot_smooth(self):
        """
        Smooth checkbox callback. Plot smooth from session object
        """
        if self.ui.checkBox_smooth.isChecked() and self.ui.mean_response_btn.isChecked():
            self.ax.relim()
            before_smooth = self.session.get_mean()

            if self.ui.stimuliBox.currentText() == "All":
                for stimuli_type,stimuli_data in before_smooth.iteritems():
                    x = np.arange(stimuli_data.shape[0])*self.session.get_tr()
                    curr = UnivariateSpline(x, stimuli_data, s=self.ui.spinBox.value())
                    axis, = self.ax.plot(x,curr(x), color=self.get_color(), label=stimuli_type + ", smoothed")
                    self.smooth.append(axis)
            else:
                x = np.arange(before_smooth[self.ui.stimuliBox.currentText()].shape[0])*self.session.get_tr()
                curr = UnivariateSpline(x, before_smooth[self.ui.stimuliBox.currentText()], s=self.ui.spinBox.value())
                axis, = self.ax.plot(x,curr(x), color=self.get_color(), label=self.ui.stimuliBox.currentText() + ", smoothed")
                self.smooth.append(axis)

        else:
            self.remove_smoothed_plots()

        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0., prop={'size':11})
        self.canvas.draw()

    def remove_smoothed_plots(self):
        if self.smooth:
            for axis in self.smooth:
                axis.remove()
            self.smooth = []

    def plot_mean(self):
        """
        Mean checkbox callback. Plot mean from session object
        """
        if self.ui.checkBox_regular.isChecked():
            self.ax.relim()
            mean = self.session.get_mean()
            self.plot_data(mean)

        else:
            self.remove_regular_plots()

        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0., prop={'size':11})
        self.canvas.draw()

    def plot_sem(self):
        """
        Standard error of mean checkbox callback. Plot standard error of mean.
        """

        if self.ui.checkBox_sem.isChecked() and self.ui.stimuliBox.currentText() != "All":
            mean = self.session.get_mean()[self.ui.stimuliBox.currentText()]
            x = np.arange(mean.size)*self.session.get_tr()
            self.ax.relim()
            sem = self.session.get_sem()
            self.sem =self.ax.errorbar(x, mean, yerr=sem[self.ui.stimuliBox.currentText()])
            self.canvas.draw()
        else:
            self.remove_sem()
            self.canvas.draw()

    def plot_amplitude(self):
        """
        Amplitude checkbox callback. Annotate amplitude in graph with a horizontal line
        """

        if self.ui.checkBox_amp.isChecked() and (self.regular or self.smooth):
            y = self.ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_amp = self.session.calculate_amplitude(x, y, 0)
            self.amp = self.ax.axhline(max_amp[1], color=self.get_color())
            self.ui.amp_label.setText("Amplitude: %.2f" % max_amp[1])
            self.ui.amp_label.show()
        else:
            self.remove_amplitude()

        self.canvas.draw()

    def plot_peak(self):
        """
        Peak checkbox callback. Annotate time of peak in graph with a vertical line
        """
        if self.ui.checkBox_peak.isChecked() and (self.regular or self.smooth):
            y = self.ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_peak = self.session.calculate_amplitude(x, y, 0)
            self.peak_time = self.ax.axvline(max_peak[0] * self.session.get_tr(), color=self.get_color())
            self.ui.peak_label.setText("Peak: " + str(max_peak[0] * self.session.get_tr()))
            self.ui.peak_label.show()
        else:
            self.remove_peak_time()

        self.canvas.draw()

    def show_points(self):
        """
        Points checkbox callback. Show data points in graph
        """
        if self.regular:
            if self.ui.checkBox_points.isChecked():
                for axis in self.regular:
                    axis.set_marker('o')
                self.canvas.draw()
            else:
                for axis in self.regular:
                    axis.set_marker('')
                self.canvas.draw()

    def get_color(self):
        """
        Generate random color for graph

        :return: RGB hex string
        """

        if len(self.ax.lines) == 0:
            self.color_index = 0

        color = CustomPlot._colors[self.color_index]
        self.color_index = (self.color_index + 1) % len(CustomPlot._colors)

        return color

    def add_stimuli_types(self):
        """
        Add all stimuli types that exists in the data to a combobox
        """
        data = self.session.get_mean()
        if len(data) > 1:
            self.ui.stimuliBox.addItem("All")
        for stimuli_type in data:
            self.ui.stimuliBox.addItem(stimuli_type)

    def plot_several_sessions(self):
        """
        Plot the active object's children, each as a separate plot
        """
        if self.ui.checkBox_regular.isChecked():
            self.remove_smoothed_plots()
            self.ax.relim()
            children = self.session.sessions + self.session.children
            for child in children:
                if child.ready_for_calculation(self.session.get_mask(), self.session.get_stimuli()):
                    child_mean = child.get_mean(self.session.get_setting('percent'),
                                                self.session.get_setting('global'))
                    self.plot_data(child_mean, child.name)

        else:
            self.remove_regular_plots()

        plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0., prop={'size':11})
        self.canvas.draw()

    def plot_data(self, data_dict, name = None):
        """
        Plots the data that exists in the dictionary data_dict, depending on stimuli selected
        """
        if self.ui.stimuliBox.currentText() == "All":
            for stimuli_type, stimuli_data in data_dict.iteritems():
                x = np.arange(len(stimuli_data))*self.session.get_tr()
                if name:
                    stimuli_type = name + "\n" + stimuli_type
                axis, = self.ax.plot(x, stimuli_data, color=self.get_color(), label=stimuli_type)
                self.regular.append(axis)
        else:
            type = self.ui.stimuliBox.currentText()
            if type in data_dict:
                data = data_dict[type]
                x = np.arange(len(data))*self.session.get_tr()
                if name:
                    type = name + "\n" + type
                axis, = self.ax.plot(x, data, color=self.get_color(), label=type)
                self.regular.append(axis)

    def plot_regular(self):
        """
        Plot either the mean of the object's data, or its children separately,
        depending on if the radiobutton is checked
        """
        if self.ui.mean_response_btn.isChecked():
            self.plot_mean()
        elif not isinstance(self.session,Session):
            self.plot_several_sessions()

    def set_allowed_buttons(self):
        """
        Enable or disable buttons depending on if they are meaningful in the current situation
        """
        # Enable the buttons if there are exactly 1 regular curve, or if there is one smoothed curve
        if len(self.regular) == 1 or (len(self.regular) == 0 and len(self.smooth) == 1):
            self.ui.checkBox_amp.setEnabled(True)
            self.ui.checkBox_fwhm.setEnabled(True)
            self.ui.checkBox_peak.setEnabled(True)
            self.ui.checkBox_sem.setEnabled(True)
        else:
            self.ui.checkBox_amp.setEnabled(False)
            self.remove_amplitude()
            self.ui.checkBox_fwhm.setEnabled(False)
            self.remove_fwhm()
            self.ui.checkBox_peak.setEnabled(False)
            self.remove_peak_time()
            self.ui.checkBox_sem.setEnabled(False)
            self.remove_sem()
            self.canvas.draw()
        # Only allow smooth if we are plotting mean
        if self.ui.mean_response_btn.isChecked():
            self.ui.checkBox_smooth.setEnabled(True)
        else:
            self.ui.checkBox_smooth.setEnabled(False)
