import json
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from generated_ui.hello_world import Ui_MainWindow
from spmpath import SPMPath
from brain import Brain
from mask import Mask
from visual_stimuli import VisualStimuli


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
        self.show()

        self.masktest = Mask(None,(5,5,5),(10,10,10),"sphere",4)
        print self.masktest.data
        self.brain = None
        self.mask = None
        self.visual_stimuli = None

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
            configuration = None
            with open('configuration.json', 'r') as f:
                configuration = json.load(f)

            for brain in configuration['brains']:
                self.brain = Brain(brain['brain_path'])

            self.visual_stimuli = VisualStimuli(configuration['stimuli_onset']['stimuli_onset_path'],
                                                configuration['stimuli_onset']['tr'])
            self.mask = Mask(configuration['mask']['mask_path'])

    def calculate_button_pressed(self):
        """ Callback function run when the calculate button is pressed."""

        # TODO: Prompt user for brain and mask paths instead of falling
        # back unto hardcoded defaults

        # Check for the data needed for data extraction
        if not self.brain:
            self.brain = Brain("test-data/brain_exp1_1.nii")
        if not self.mask:
            self.mask = Mask("test-data/mask.nii")
        if not self.visual_stimuli:
            self.visual_stimuli = VisualStimuli("test-data/stimall.mat", 0.5)

        self.brain.apply_mask(self.mask)
        self.brain.normalize_to_mean(self.visual_stimuli)
        self.brain.plot_std()

    def brain_button_pressed(self):
        """ Callback function run when the choose brain button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.brain = Brain(file_name[0])
            self.ui.brainLabel.setText("Brain picked!")
        else:
            print 'File not chosen'

    def mask_button_pressed(self):
        """ Callback function run when the choose mask button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.mask = Mask(file_name[0])
            self.ui.maskLabel.setText("Mask picked!")
        else:
            print 'Mask not chosen'

    def stimuli_button_pressed(self):
        """ Callback function run when the choose stimuli button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.mat)")
        if file_name[0]:
            self.visual_stimuli = VisualStimuli(file_name[0], 0.5)
            self.ui.stimuliLabel.setText("Stimuli picked!")
        else:
            print 'Stimuli not chosen'

    def configure_spm(self):
        """ Callback function run when the spm menu item is pressed."""
        SPMPath(self.manager).exec_()
