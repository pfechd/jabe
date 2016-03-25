from PyQt5.QtWidgets import QMainWindow, QFileDialog
from generated_ui.hello_world import Ui_MainWindow
from spmpath import SPMPath
from brain import Brain
from mask import Mask
from visual_stimuli import VisualStimuli


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionSettings.triggered.connect(self.configure_spm)
        self.ui.pushButton.clicked.connect(self.calculate_button_pressed)
        self.ui.brainButton.clicked.connect(self.brain_button_pressed)
        self.ui.maskButton.clicked.connect(self.mask_button_pressed)
        self.ui.stimuliButton.clicked.connect(self.stimuli_button_pressed)
        self.show()

        self.brain = None
        self.mask = None
        self.visual_stimuli = None

    def calculate_button_pressed(self):
        # TODO: Prompt user for brain and mask paths instead of falling
        # back unto hardcoded defaults
        if not self.brain:
            self.brain = Brain("../../test-data/brain_exp1_1")
        if not self.mask:
            self.mask = Mask("../../test-data/mask")
        if not self.visual_stimuli:
            self.visual_stimuli = VisualStimuli("../../test-data/stimall", 0.5)
        self.brain.apply_mask(self.mask)
        self.brain.normalize_to_mean(self.visual_stimuli)
        self.brain.plot_mean()

    def brain_button_pressed(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.brain = Brain(file_name[0])
            self.ui.brainLabel.setText("Brain picked!")
        else:
            print 'File not chosen'

    def mask_button_pressed(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.mask = Mask(file_name[0])
            self.ui.maskLabel.setText("Mask picked!")
        else:
            print 'Mask not chosen'

    def stimuli_button_pressed(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.mat)")
        if file_name[0]:
            self.visual_stimuli = VisualStimuli(file_name[0], 0.5)
            self.ui.stimuliLabel.setText("Stimuli picked!")
        else:
            print 'Stimuli not chosen'

    def configure_spm(self):
        SPMPath(self.manager).exec_()
