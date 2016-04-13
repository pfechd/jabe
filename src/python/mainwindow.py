import json
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel
from generated_ui.hello_world import Ui_MainWindow
from spmpath import SPMPath
from brain import Brain
from mask import Mask
from stimulionset import StimuliOnset
from individual import Individual
from message import Message
from plotWindow import CustomPlot


class MainWindow(QMainWindow):
    """
    The main window of the application.

    The window is the main entry point for the user into the applications. It
    mostly consists of callback functions for the various user interface
    events.
    """
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionSettings.triggered.connect(self.configure_spm)
        self.ui.pushButton.clicked.connect(self.calculate_button_pressed)
        self.ui.brainButton.clicked.connect(self.brain_button_pressed)
        self.ui.maskButton.clicked.connect(self.mask_button_pressed)
        self.ui.stimuliButton.clicked.connect(self.stimuli_button_pressed)
        self.ui.add_individual_button.clicked.connect(self.add_individual_pressed)
        self.ui.remove_individual_button.clicked.connect(self.remove_individual_pressed)
        self.ui.list_widget.currentRowChanged.connect(self.current_item_changed)
        self.show()

        self.individual_buttons = [self.ui.pushButton, self.ui.brainButton,
                                   self.ui.maskButton, self.ui.stimuliButton]

        self.individuals = []
        self.load_configuration()
        self.update_gui()

    def closeEvent(self, event):
        self.save_configuration()

    def save_configuration(self):
        configuration = {
            'individuals': [individual.get_configuration() for individual in self.individuals],
            'current': self.ui.list_widget.currentRow()
        }
        with open('configuration.json', 'w') as f:
            json.dump(configuration, f, indent=4)

    def load_configuration(self):
        if os.path.exists('configuration.json'):
            with open('configuration.json', 'r') as f:
                configuration = json.load(f)

            self.individuals = []
            self.ui.list_widget.clear()
            if 'individuals' in configuration:
                for individual_configuration in configuration['individuals']:
                    individual = Individual(individual_configuration)
                    self.individuals.append(individual)
                    self.ui.list_widget.addItem(individual.name)

            if 'current' in configuration:
                self.ui.list_widget.setCurrentRow(configuration['current'])

            self.update_gui()

    def add_individual_pressed(self):
        current_row = len(self.individuals)
        text = 'New individual ' + str(current_row)
        self.add_individual(text)

    def remove_individual_pressed(self):
        current_row = self.ui.list_widget.currentRow()
        if current_row != -1:
            self.ui.list_widget.takeItem(current_row)
            del self.individuals[current_row]
        self.update_gui()

    def current_item_changed(self, row):
        if row != -1:
            individual = self.individuals[row]
            self.update_gui()

    def update_buttons(self):
        current_row = self.ui.list_widget.currentRow()
        if current_row == -1:
            for button in self.individual_buttons:
                button.setEnabled(False)
        else:
            individual = self.individuals[current_row]

            for button in self.individual_buttons:
                button.setEnabled(True)
            print individual.ready_for_calculation()
            self.ui.pushButton.setEnabled(individual.ready_for_calculation())

    def calculate_button_pressed(self):
        """ Callback function, run when the calculate button is pressed."""

        # TODO: Prompt user for brain and mask paths instead of falling
        # back unto hardcoded defaults

        individual = self.individuals[self.ui.list_widget.currentRow()]
        individual.calculate()


    def brain_button_pressed(self):
        """ Callback function, run when the choose brain button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.load_brain(file_name[0])
        else:
            print 'File not chosen'
        self.update_gui()

    def mask_button_pressed(self):
        """ Callback function, run when the choose mask button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.load_mask(file_name[0])
        else:
            print 'Mask not chosen'
        self.update_gui()

    def stimuli_button_pressed(self):
        """ Callback function, run when the choose stimuli button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.mat)")
        if file_name[0]:
            self.load_stimuli(file_name[0])
        else:
            print 'Stimuli not chosen'
        self.update_gui()

    def add_individual(self, text):
        current_row = len(self.individuals)
        individual = Individual()
        individual.name = text
        self.individuals.append(individual)

        self.ui.list_widget.addItem(text)
        self.ui.list_widget.setCurrentRow(current_row)

    def load_brain(self, path):
        individual = self.individuals[self.ui.list_widget.currentRow()]
        individual.brain = Brain(path)
        self.update_gui()

    def load_mask(self, path):
        individual = self.individuals[self.ui.list_widget.currentRow()]
        individual.mask = Mask(path)
        self.update_gui()

    def load_stimuli(self, path):
        individual = self.individuals[self.ui.list_widget.currentRow()]
        individual.stimuli_onset = StimuliOnset(path, 0.5)
        self.update_gui()

    def update_gui(self):
        self.update_buttons()
        self.update_text()

    def update_text(self):
        current_row = self.ui.list_widget.currentRow()
        if current_row != -1:
            individual = self.individuals[current_row]

            if individual.brain:
                self.ui.brainLabel.setText('EPI-images chosen: ' + individual.brain.path)
            else:
                self.ui.brainLabel.setText('No EPI-images chosen')

            if individual.mask:
                self.ui.maskLabel.setText('Mask picked: ' + individual.mask.path)
            else:
                self.ui.maskLabel.setText('No mask chosen')

            if individual.stimuli_onset:
                self.ui.stimuliLabel.setText('Stimuli picked: ' + individual.stimuli_onset.path)
            else:
                self.ui.stimuliLabel.setText('No stimuli chosen')
        else:
            for label in [self.ui.brainLabel, self.ui.maskLabel, self.ui.stimuliLabel]:
                label.setText('')

    def configure_spm(self):
        """ Callback function, run when the spm menu item is pressed."""
        SPMPath(self.manager).exec_()
