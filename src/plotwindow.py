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

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog, QMessageBox
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
        self.amp = []
        self.peak_time = []
        self.fwhm = []
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

        if isinstance(self.session, Session) and session.anatomy is not None:
            self.ui.toolButton_anatomy.show()

        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.toolbar.hide()

        self.ui.mplvl.addWidget(self.canvas)

        self.ui.checkBox_fwhm.toggled.connect(self.plot_fwhm)
        self.ui.checkBox_sem.toggled.connect(self.plot_sem)
        self.ui.checkBox_regular.toggled.connect(self.replot)
        self.ui.checkBox_smooth.toggled.connect(self.replot)
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
        self.ui.verticalLayout_3.update()

    def tool_anatomy(self):
         self.anatomy_window = AnatomyWindow(self, self.session)

    def tool_export(self):
        """
        Export button callback. Creates a custom export window
        """
        self.export_window = ExportWindow(self, self.session, self.toolbar, self.ui.stimuliBox.currentText())

    def plot_fwhm(self):
        """
        If fwhm checkbox is checked this function will update fwhm
        span and datalog info.
        If fwhm checkbox is not checked this function will remove 
        fwhm span and datalog info.
        """
        self.remove_fwhm()
        if not (self.ui.checkBox_smooth.isChecked() \
                or self.ui.checkBox_regular.isChecked()) \
                or self.ui.several_responses_btn.isChecked():
            self.ui.fwhm_label.hide()
            return
        
        if self.ui.checkBox_fwhm.isChecked():
            try:
                fwhm = self.session.get_fwhm(self.ui.stimuliBox.currentText(),
                                      self.ui.spinBox.value())
            except Exception as exc:
                self.ui.checkBox_fwhm.setChecked(False)
                QMessageBox.warning(self, exc.args[0], exc.args[1])
                return
            fwhm_text = ""
            for stimuli_val, values in fwhm.iteritems():
                self.fwhm.append(self.ax.axvspan(
                        values[0], values[1], facecolor='g', alpha=0.2))
                fwhm_text += "FWHM " + stimuli_val + " width: " + \
                        str(values[1] - values[0]) + "\n"
            self.ui.fwhm_label.setText(fwhm_text[0:-1])
            self.ui.fwhm_label.show()
            self.canvas.draw()
        else:
            self.ui.fwhm_label.hide()
                
    def replot(self):
        """
        Replot regular and smoothed curve, amplitude, peak and fwhm. 
        Used when changing the data to plot and callback function for
        many checkboxes.
        """
        self.remove_sem()

        self.remove_regular_plots()
        self.plot_regular()
        self.remove_smoothed_plots()
        self.plot_smooth()
        
        self.plot_peak()
        self.plot_amplitude()
        self.plot_fwhm()
        self.plot_sem()
        self.set_allowed_buttons()

    def remove_peak_time(self):
        if self.peak_time:
            for peak in self.peak_time:
                peak.remove()
            self.peak_time = []
            self.canvas.draw()

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
            for amp in self.amp:
                amp.remove()
            self.amp = []
            self.canvas.draw()

    def remove_fwhm(self):
        if self.fwhm:
            for fwhm in self.fwhm:
                fwhm.remove()
            self.fwhm = []

    def remove_regular_plots(self):
        if self.regular:
            for axis in self.regular:
                axis.remove()
            self.regular = []

    def plot_smooth(self):
        """
        Plot smoothed responses from session object if smoothed checkbox 
        is checked.
        Will otherwise hide smoothed responses
        """
        if self.ui.checkBox_smooth.isChecked() and self.ui.mean_response_btn.isChecked():
            self.ax.relim()
            try:
                smooth = self.session.get_smooth(self.ui.spinBox.value())
            except Exception as exc:
                self.ui.checkBox_smooth.setChecked(False)
                QMessageBox.warning(self, exc.args[0], exc.args[1])
                return

            if self.ui.stimuliBox.currentText() == "All":
                for stimuli_type, smoothed_data in smooth.iteritems():
                    axis, = self.ax.plot(
                            self.session.get_x_axis(), smoothed_data,
                            color=self.get_color(), label=stimuli_type + ", smoothed")
                    self.smooth.append(axis)
            else:
                stimuli_value = self.ui.stimuliBox.currentText()
                axis, = self.ax.plot(
                        self.session.get_x_axis(), smooth[stimuli_value],
                        color=self.get_color(), label=stimuli_value + ", smoothed")
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
        Plot mean responses from session object if mean checkbox 
        is checked.
        Will otherwise hide mean responses
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
        If amplitude checkbox is checked this function will update amplitude
        lines and datalog info.
        If amplitude checkbox is not checked this function will remove 
        amplitude lines and datalog info.
        """
        self.remove_amplitude()
        if not (self.ui.checkBox_smooth.isChecked() \
                or self.ui.checkBox_regular.isChecked()) \
                or self.ui.several_responses_btn.isChecked():
            self.ui.amp_label.hide()
            return

        if self.ui.checkBox_amp.isChecked():
            try:
                points = self.session.get_peaks(
                        self.ui.spinBox.value(),
                        smooth=self.ui.checkBox_smooth.isChecked())
            except Exception as exc:
                self.ui.checkBox_amp.setChecked(False)
                QMessageBox.warning(self, exc.args[0], exc.args[1])
                return
            amp_text = ""
            if self.ui.stimuliBox.currentText() == "All":
                for stimuli_val, position in points.iteritems():
                    self.amp.append(
                            self.ax.axhline(position[1], color=self.get_color()))
                    amp_text += "Amplitude " + stimuli_val + ": " + \
                            str(position[1]) + "\n"
            else:
                stimuli_val = self.ui.stimuliBox.currentText()
                self.amp.append(
                        self.ax.axhline(points[stimuli_val][1], color=self.get_color()))
                amp_text += "Amplitude " + stimuli_val + ": " + \
                        str(points[stimuli_val][1]) + "\n"
            self.ui.amp_label.setText(amp_text[0:-1])
            self.ui.amp_label.show()
        else:
            self.ui.amp_label.hide()

    def plot_peak(self):
        """
        If peak checkbox is checked this function will update peak
        lines and datalog info.
        If peak checkbox is not checked this function will remove 
        peak lines and datalog info.
        """
        self.remove_peak_time()
        if not (self.ui.checkBox_smooth.isChecked() \
                or self.ui.checkBox_regular.isChecked()) \
                or self.ui.several_responses_btn.isChecked():
            self.ui.peak_label.hide()
            return

        if self.ui.checkBox_peak.isChecked():
            try:
                points = self.session.get_peaks(
                        self.ui.spinBox.value(),
                        smooth=self.ui.checkBox_smooth.isChecked())
            except Exception as exc:
                self.ui.checkBox_amp.setChecked(False)
                QMessageBox.warning(self, exc.args[0], exc.args[1])
                return
            peak_text = ""
            if self.ui.stimuliBox.currentText() == "All":
                for stimuli_val, position in points.iteritems():
                    self.peak_time.append(
                            self.ax.axvline(position[0], color=self.get_color()))
                    peak_text += "Peak " + stimuli_val + ": " + \
                            str(position[0]) + "\n"
            else:
                stimuli_val = self.ui.stimuliBox.currentText()
                self.peak_time.append(
                        self.ax.axvline(points[stimuli_val][0], color=self.get_color()))
                peak_text += "Peak " + stimuli_val + ": " + \
                        str(points[stimuli_val][0]) + "\n"
            self.ui.peak_label.setText(peak_text[0:-1])
            self.ui.peak_label.show()
        else:
            self.ui.peak_label.hide()

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
                if child.ready_for_calculation():
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
        elif not isinstance(self.session, Session):
            self.plot_several_sessions()

    def set_allowed_buttons(self):
        """
        Enable or disable buttons depending on if they are meaningful in the current situation
        """
        # Enable the buttons if there are exactly 1 regular curve, or if there is one smoothed curve
        if len(self.regular) == 1 or (len(self.regular) == 0 and len(self.smooth) == 1):
            self.ui.checkBox_sem.setEnabled(True)
        else:
            self.ui.checkBox_sem.setEnabled(False)
            self.remove_sem()
            self.canvas.draw()
        # Only allow smooth if we are plotting mean
        if self.ui.mean_response_btn.isChecked():
            self.ui.checkBox_smooth.setEnabled(True)
            self.ui.checkBox_peak.setEnabled(True)
            self.ui.checkBox_amp.setEnabled(True)
            self.ui.checkBox_fwhm.setEnabled(True)
        else:
            self.ui.checkBox_smooth.setEnabled(False)
            self.ui.checkBox_peak.setEnabled(False)
            self.ui.checkBox_amp.setEnabled(False)
            self.ui.checkBox_fwhm.setEnabled(False)
