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
        self.amp = []
        self.peak_time = []
        self.fwhm = []
        self.regular = []
        self.smooth = []
        self.sem = []
        self.scroll = 3
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.used_colors = []

        self.session = session
        self.fig = plt.figure()

        self.current_ax = self.fig.add_subplot(111)
        self.axes = {}
        self.ax_list = []

        self.add_ax(self.current_ax)

        self.ui.toolButton_anatomy.hide()

        if isinstance(self.session, Session) and session.anatomy is not None:
            self.ui.toolButton_anatomy.show()

        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.toolbar.hide()

        self.ui.mplvl.addWidget(self.canvas)

        self.ui.checkBox_fwhm.clicked.connect(self.apply_fwhm)
        self.ui.checkBox_sem.clicked.connect(self.plot_sem)
        self.ui.checkBox_regular.clicked.connect(self.plot_regular)
        self.ui.checkBox_smooth.clicked.connect(self.plot_smooth)
        self.ui.checkBox_amp.clicked.connect(self.plot_amplitude)
        self.ui.checkBox_peak.clicked.connect(self.plot_peak)
        self.ui.stimuliBox.currentTextChanged.connect(self.replot)
        self.ui.mean_response_btn.clicked.connect(self.replot)
        self.ui.several_responses_btn.clicked.connect(self.replot)
        self.ui.checkBox_labels.clicked.connect(self.show_legends)
        self.ui.label_size.valueChanged.connect(self.show_legends)

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
        else:
            self.ui.several_responses_btn.hide()

        self.ui.checkBox_peak.setChecked(self.session.get_setting('peak'))

        self.ui.checkBox_fwhm.setChecked(self.session.get_setting('fwhm'))

        self.ui.checkBox_amp.setChecked(self.session.get_setting('amplitude'))

        self.ui.checkBox_sem.setChecked(self.session.get_setting('sem'))

        self.ui.toolButton_add_subplot.clicked.connect(self.add_subplot)
        self.ui.toolButton_rem_subplot.clicked.connect(self.remove_subplot)

        self.canvas.mpl_connect('button_press_event', self.click_plot)
        self.fig.tight_layout(pad=2.0)

        self.replot()
        self.show()

    def highlight_current_axis(self):
        if self.current_ax is not None:
            for ax in self.axes:
                ax.spines['bottom'].set_color('black')
                ax.spines['top'].set_color('black')
                ax.spines['right'].set_color('black')
                ax.spines['left'].set_color('black')

            self.current_ax.spines['bottom'].set_color('red')
            self.current_ax.spines['top'].set_color('red')
            self.current_ax.spines['right'].set_color('red')
            self.current_ax.spines['left'].set_color('red')

    def add_subplot(self):
        n = len(self.axes)
        i = 0

        for ax in self.ax_list:
            self.fig.delaxes(ax)
            ax.change_geometry(((n + 1) / 2) + (1 * ((n + 1) % 2)), 2,  (i + 1))
            i += 1

        if n == 0:
            new_ax = self.fig.add_subplot(1, 1, 1)
        else:
            for ax in self.ax_list:
                self.fig.add_axes(ax)
            new_ax = self.fig.add_subplot(((n + 1) / 2) + (1 * ((n + 1) % 2)), 2, n + 1)

        self.add_ax(new_ax)

        if len(self.axes) == 1:
            self.current_ax = new_ax
            self.load_ax_settings()
        else:
            self.highlight_current_axis()

        self.fig.tight_layout()
        self.set_allowed_buttons()
        self.canvas.draw()

    def remove_subplot(self):
        self.axes.pop(self.current_ax)
        self.ax_list.remove(self.current_ax)
        self.fig.delaxes(self.current_ax)

        n = len(self.axes)

        if n == 1:
            self.fig.axes[0].change_geometry(1, 1, 1)
        else:
            for i in xrange(n):
                self.fig.axes[i].change_geometry((n / 2) + (1 * (n % 2)), 2,  (i + 1))

        if self.fig.axes:
            self.current_ax = self.fig.axes[0]
            self.load_ax_settings()
        else:
            self.current_ax = None

        self.highlight_current_axis()
        self.set_allowed_buttons()
        self.canvas.draw()

    def add_ax(self, ax):
        if ax is not None:
            self.ax_list.append(ax)
            self.axes[ax] = {'plot': 'mean',
                             'data': {'regular': False,
                                      'smooth': False,
                                      'smooth_fact': 20,
                                      'stimuli_type': 0,
                                      },
                             'settings': {'amp': False,
                                          'peak': False,
                                          'sem': False,
                                          'fwhm': False},
                             'used_colors': []
                             }

    def save_ax_settings(self, ax):
        if self.ui.mean_response_btn.isChecked():
            plot = 'mean'
        else:
            plot = 'several'

        if ax is not None:
            self.axes[ax] = {'plot': plot,
                             'data': {'regular': self.ui.checkBox_regular.isChecked(),
                                      'smooth': self.ui.checkBox_smooth.isChecked(),
                                      'smooth_fact': self.ui.spinBox.value(),
                                      'stimuli_type': self.ui.stimuliBox.currentIndex(),
                                      },
                             'settings': {'amp': self.ui.checkBox_amp.isChecked(),
                                          'peak': self.ui.checkBox_peak.isChecked(),
                                          'sem': self.ui.checkBox_sem.isChecked(),
                                          'fwhm': self.ui.checkBox_fwhm.isChecked()},
                             'used_colors': self.used_colors
                             }

    def load_ax_settings(self):
        ax = self.current_ax

        print self.current_ax.lines

        self.ui.mean_response_btn.setChecked(self.axes[ax]['plot'] == 'mean')
        self.ui.several_responses_btn.setChecked(self.axes[ax]['plot'] == 'several')

        self.ui.checkBox_regular.setChecked(self.axes[ax]['data']['regular'])
        self.ui.checkBox_smooth.setChecked(self.axes[ax]['data']['smooth'])

        self.ui.spinBox.blockSignals(True)
        self.ui.spinBox.setValue(self.axes[ax]['data']['smooth_fact'])
        self.ui.spinBox.blockSignals(False)

        self.ui.stimuliBox.blockSignals(True)
        self.ui.stimuliBox.setCurrentIndex(self.axes[ax]['data']['stimuli_type'])
        self.ui.stimuliBox.blockSignals(False)

        self.ui.checkBox_amp.setChecked(self.axes[ax]['settings']['amp'])
        self.ui.checkBox_peak.setChecked(self.axes[ax]['settings']['peak'])
        self.ui.checkBox_sem.setChecked(self.axes[ax]['settings']['sem'])
        self.ui.checkBox_fwhm.setChecked(self.axes[ax]['settings']['fwhm'])

        self.used_colors = self.axes[ax]['used_colors']

    def click_plot(self, event):
        if event.inaxes:
            self.save_ax_settings(self.current_ax)
            self.current_ax = event.inaxes
            self.load_ax_settings()
            self.set_allowed_buttons()
            self.highlight_current_axis()
            self.canvas.draw()

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
                y = self.current_ax.lines[0].get_ydata()
                x = np.arange(len(y))*self.session.get_tr()
                smooth = self.ui.spinBox.value()
                r1, r2 = self.session.calculate_fwhm(x, y, smooth)
                self.fwhm.append(self.current_ax.axvspan(r1, r2, facecolor='g', alpha=0.3))
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
            for peak in self.peak_time:
                if peak.axes == self.current_ax:
                    peak.remove()
        self.ui.peak_label.hide()
        self.ui.checkBox_peak.setChecked(False)

    def remove_sem(self):
        if self.sem:
            for sem in self.sem:
                if sem[0].axes == self.current_ax:
                    self.used_colors.remove(sem[0].get_color())
                    sem[0].remove()
                    for line in sem[1]:
                        line.remove()
                    for line in sem[2]:
                        line.remove()

        self.ui.checkBox_sem.setChecked(False)

    def remove_amplitude(self):
        if self.amp:
            for amp in self.amp:
                if amp.axes == self.current_ax:
                    amp.remove()

        self.ui.amp_label.hide()
        self.ui.checkBox_amp.setChecked(False)

    def remove_fwhm(self):
        if self.fwhm:
            for fwhm in self.fwhm:
                if fwhm.axes == self.current_ax:
                    fwhm.remove()

        self.ui.checkBox_fwhm.setChecked(False)

    def remove_regular_plots(self):
        if self.regular:
            for axis in self.regular:
                if axis.axes == self.current_ax:
                    self.used_colors.remove(axis.get_color())
                    axis.remove()

    def plot_smooth(self):
        """
        Smooth checkbox callback. Plot smooth from session object
        """

        if self.ui.checkBox_smooth.isChecked() and self.ui.mean_response_btn.isChecked():
            self.current_ax.relim()
            before_smooth = self.session.calculate_mean()

            if self.ui.stimuliBox.currentText() == "All":
                for stimuli_type,stimuli_data in before_smooth.iteritems():
                    x = np.arange(stimuli_data.shape[0])*self.session.get_tr()
                    curr = UnivariateSpline(x, stimuli_data, s=self.ui.spinBox.value())
                    axis, = self.current_ax.plot(x,curr(x), color=self.get_color(), label=stimuli_type + ", smoothed")
                    self.smooth.append(axis)
            else:
                x = np.arange(before_smooth[self.ui.stimuliBox.currentText()].shape[0])*self.session.get_tr()
                curr = UnivariateSpline(x, before_smooth[self.ui.stimuliBox.currentText()], s=self.ui.spinBox.value())
                axis, = self.current_ax.plot(x,curr(x), color=self.get_color(), label=self.ui.stimuliBox.currentText() + ", smoothed")
                self.smooth.append(axis)
        else:
            self.remove_smoothed_plots()

        self.show_legends()
        self.canvas.draw()

    def remove_smoothed_plots(self):
        if self.smooth:
            for axis in self.smooth:
                if axis.axes == self.current_ax:
                    self.used_colors.remove(axis.get_color())
                    axis.remove()

    def plot_mean(self):
        """
        Mean checkbox callback. Plot mean from session object
        """
        if self.ui.checkBox_regular.isChecked():
            self.current_ax.relim()
            mean = self.session.calculate_mean()
            self.plot_data(mean)

        else:
            self.remove_regular_plots()

        self.show_legends()
        self.canvas.draw()

    def plot_sem(self):
        """
        Standard error of mean checkbox callback. Plot standard error of mean.
        """

        if self.ui.checkBox_sem.isChecked() and self.ui.stimuliBox.currentText() != "All":
            mean = self.session.calculate_mean()[self.ui.stimuliBox.currentText()]
            x = np.arange(mean.size)*self.session.get_tr()
            self.current_ax.relim()
            sem = self.session.calculate_sem()
            self.sem.append(self.current_ax.errorbar(x, mean, color=self.get_color(), yerr=sem[self.ui.stimuliBox.currentText()]))
            self.canvas.draw()
        else:
            self.remove_sem()
            self.canvas.draw()

    def plot_amplitude(self):
        """
        Amplitude checkbox callback. Annotate amplitude in graph with a horizontal line
        """

        if self.ui.checkBox_amp.isChecked() and (self.regular or self.smooth):
            y = self.current_ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_amp = self.session.calculate_amplitude(x, y, 0)
            self.amp.append(self.current_ax.axhline(max_amp[1], color=CustomPlot._colors[-1]))
            self.ui.amp_label.setText("Amplitude: %.2f" % max_amp[1])
            self.ui.amp_label.show()
            self.canvas.draw()
        else:
            self.remove_amplitude()

        self.canvas.draw()

    def plot_peak(self):
        """
        Peak checkbox callback. Annotate time of peak in graph with a vertical line
        """
        if self.ui.checkBox_peak.isChecked() and (self.regular or self.smooth):
            y = self.current_ax.lines[0].get_ydata()
            x = np.arange(len(y))
            max_peak = self.session.calculate_amplitude(x, y, 0)
            self.peak_time.append(self.current_ax.axvline(max_peak[0] * self.session.get_tr(), color=CustomPlot._colors[-1]))
            self.ui.peak_label.setText("Peak: " + str(max_peak[0] * self.session.get_tr()))
            self.ui.peak_label.show()
        else:
            self.remove_peak_time()

        self.canvas.draw()

    def get_color(self):
        """
        :return: RGB hex string
        """

        for color in CustomPlot._colors:
            if color not in self.used_colors:
                self.used_colors.append(color)
                return color

    def add_stimuli_types(self):
        """
        Add all stimuli types that exists in the data to a combobox
        """
        data = self.session.calculate_mean()
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
            self.current_ax.relim()
            children = self.session.sessions + self.session.children
            for child in children:
                if child.ready_for_calculation():
                    child_mean = child.calculate_mean(self.session.get_setting('percent'),
                                                      self.session.get_setting('global'))
                    self.plot_data(child_mean, child.name)

        else:
            self.remove_regular_plots()

        self.show_legends()
        self.canvas.draw()

    def plot_data(self, data_dict, name = None):
        """
        Plots the data that exists in the dictionary data_dict, depending on stimuli selected
        """
        if self.ui.stimuliBox.currentText() == "All":
            for stimuli_type, stimuli_data in data_dict.iteritems():
                x = np.arange(len(stimuli_data))*self.session.get_tr()
                if name:
                    stimuli_type = name + " - " + stimuli_type
                axis, = self.current_ax.plot(x, stimuli_data, color=self.get_color(), label=stimuli_type)
                self.regular.append(axis)
        else:
            type = self.ui.stimuliBox.currentText()
            if type in data_dict:
                data = data_dict[type]
                x = np.arange(len(data))*self.session.get_tr()
                if name:
                    type = name + " - " + type
                axis, = self.current_ax.plot(x, data, color=self.get_color(), label=type)
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

        self.set_allowed_buttons()

    def show_legends(self):
        for ax in self.axes:
            handles, labels = ax.get_legend_handles_labels()
            lgd = ax.legend(handles, labels, prop={'size': self.ui.label_size.value()})

            if not handles or not self.ui.checkBox_labels.isChecked():
                lgd.set_visible(False)
            else:
                lgd.set_visible(True)

        if self.ui.checkBox_labels.isChecked():
            self.ui.label_size.setEnabled(True)
        else:
            self.ui.label_size.setEnabled(False)

        self.canvas.draw()

    def set_allowed_buttons(self):
        """
        Enable or disable buttons depending on if they are meaningful in the current situation
        """
        # Enable the buttons if there are exactly 1 regular curve, or if there is one smoothed curve
        if self.current_ax is None:
            self.ui.toolButton_rem_subplot.setEnabled(False)

            self.ui.checkBox_amp.setEnabled(False)
            self.ui.checkBox_fwhm.setEnabled(False)
            self.ui.checkBox_peak.setEnabled(False)
            self.ui.checkBox_sem.setEnabled(False)
            self.ui.checkBox_regular.setEnabled(False)
            self.ui.checkBox_smooth.setEnabled(False)

            self.ui.mean_response_btn.setEnabled(False)
            self.ui.several_responses_btn.setEnabled(False)
            self.ui.spinBox.setEnabled(False)
            self.ui.stimuliBox.setEnabled(False)
        else:
            self.ui.toolButton_rem_subplot.setEnabled(True)
            self.ui.mean_response_btn.setEnabled(True)
            self.ui.several_responses_btn.setEnabled(True)
            self.ui.spinBox.setEnabled(True)
            self.ui.stimuliBox.setEnabled(True)
            self.ui.checkBox_regular.setEnabled(True)

            if self.ui.stimuliBox.currentText() != "All":
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

            # Only allow smooth if we are plotting mean
            if self.ui.mean_response_btn.isChecked():
                self.ui.checkBox_smooth.setEnabled(True)
            else:
                self.ui.checkBox_smooth.setEnabled(False)

    def resizeEvent(self, QResizeEvent):
        try:
            self.fig.tight_layout(pad=2.0)
        except:
            pass