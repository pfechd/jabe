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
        self.ui.print_configuration.clicked.connect(self.save_configuration)
        self.ui.load_configuration.clicked.connect(self.load_configuration)
        self.ui.add_individual_button.clicked.connect(self.add_individual_pressed)
        self.ui.remove_individual_button.clicked.connect(self.remove_individual_pressed)
        self.ui.list_widget.currentRowChanged.connect(self.current_item_changed)
        self.show()

        self.individual_buttons = [self.ui.pushButton, self.ui.brainButton,
                                   self.ui.maskButton, self.ui.stimuliButton]

        self.individuals = []

    def save_configuration(self):
        configuration = {
            'brains': [self.brain.get_configuration()],
            'mask': self.mask.get_configuration(),
            'stimuli_onset': self.visual_stimuli.get_configuration()
        }
        with open('configuration.json', 'w') as f:
            json.dump(configuration, f, indent=4)

    def load_configuration(self):
        if os.path.exists('configuration.json'):
            with open('configuration.json', 'r') as f:
                configuration = json.load(f)

            self.load_brain(configuration['brains'][0]['brain_path'])

            self.load_mask(configuration['mask']['mask_path'])

            self.load_stimuli(configuration['stimuli_onset']['stimuli_onset_path'])
            self.visual_stimuli.tr = configuration['stimuli_onset']['tr']

    def add_individual_pressed(self):
        current_row = len(self.individuals)
        text = 'New individual ' + str(current_row)

        individual = Individual()
        individual.name = text
        self.individuals.append(individual)

        self.ui.list_widget.addItem(text)
        self.ui.list_widget.setCurrentRow(current_row)

    def remove_individual_pressed(self):
        current_row = self.ui.list_widget.currentRow()
        if current_row != -1:
            self.ui.list_widget.takeItem(current_row)
            del self.individuals[current_row]

    def current_item_changed(self, row):
        individual = self.individuals[row]
        self.update_buttons()

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

    def mask_button_pressed(self):
        """ Callback function, run when the choose mask button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.load_mask(file_name[0])
        else:
            print 'Mask not chosen'

    def stimuli_button_pressed(self):
        """ Callback function, run when the choose stimuli button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.mat)")
        if file_name[0]:
            self.load_stimuli(file_name[0])
        else:
            print 'Stimuli not chosen'

    def load_brain(self, path):
        individual = self.individuals[self.ui.list_widget.currentRow()]
        individual.brain = Brain(path)
        self.ui.brainLabel.setText('EPI-images chosen: ' + path)
        self.update_buttons()

    def load_mask(self, path):
        individual = self.individuals[self.ui.list_widget.currentRow()]
        individual.mask = Mask(path)
        self.ui.maskLabel.setText('Mask picked: ' + path)
        self.update_buttons()

    def load_stimuli(self, path):
        individual = self.individuals[self.ui.list_widget.currentRow()]
        individual.stimuli_onset = StimuliOnset(path, 0.5)
        self.ui.stimuliLabel.setText('Stimuli picked: ' + path)
        self.update_buttons()

    def configure_spm(self):
        """ Callback function, run when the spm menu item is pressed."""
        SPMPath(self.manager).exec_()
