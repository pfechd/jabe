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
            with open('configuration.json', 'r') as f:
                configuration = json.load(f)

            self.load_brain(configuration['brains'][0]['brain_path'])

            self.load_mask(configuration['mask']['mask_path'])

            self.load_stimuli(configuration['stimuli_onset']['stimuli_onset_path'])
            self.visual_stimuli.tr = configuration['stimuli_onset']['tr']

    def calculate_button_pressed(self):
        """ Callback function, run when the calculate button is pressed."""

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
        self.brain.plot_mean(fwhm=True)

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
        self.brain = Brain(path)
        self.ui.brainLabel.setText('EPI-images chosen: ' + path)

    def load_mask(self, path):
        self.mask = Mask(path)
        self.ui.maskLabel.setText('Mask picked: ' + path)

    def load_stimuli(self, path):
        self.visual_stimuli = VisualStimuli(path, 0.5)
        self.ui.stimuliLabel.setText('Stimuli picked: ' + path)

    def configure_spm(self):
        """ Callback function, run when the spm menu item is pressed."""
        SPMPath(self.manager).exec_()
