from PyQt5.QtWidgets import QMainWindow, QFileDialog
from src.python.generated_ui.hello_world import Ui_MainWindow
from src.python.sessionmanager import SessionManager
from src.python.spmpath import SPMPath
from src.python.brain import Brain
from src.python.mask import Mask
from src.python.visual_stimuli import VisualStimuli

class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.manager = SessionManager()
        # sets the variable 'data' to 3 in MATLAB
        self.manager.set_data("data", 3)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.button_pressed)
        self.ui.brainButton.clicked.connect(self.brain_button_pressed)
        self.ui.maskButton.clicked.connect(self.mask_button_pressed)
        self.ui.configureSPMButton.clicked.connect(self.configure_spm)
        self.show()

        self.brain = None
        self.mask = None

    def button_pressed(self, e):
        # retrieves and prints what is in the variable 'data' in MATLAB
        print(self.manager.get_data("data"))
        # TODO: Prompt user for brain and mask paths
        if not self.brain:
            self.brain = Brain("../../test-data/brain_exp1_1", self.manager.session)
        if not self.mask:
            self.mask = Mask("../../test-data/mask", self.manager.session)
        visual_stimuli = VisualStimuli("../../test-data/stimall", 0.5, self.manager.session)
        self.brain.apply_mask(self.mask)
        data = self.brain.normalize_to_mean(visual_stimuli)
        data.plot_mean()
        # data.plot_std()

    def brain_button_pressed(self, e):
        dialog = QFileDialog()
        file_name = QFileDialog.getOpenFileName(self, 'Open file')
        if file_name[0]:
            self.brain = Brain(file_name[0][:-len('.nii')], self.manager.session)
        else:
            print 'File not chosen'

    def mask_button_pressed(self, e):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')
        if file_name[0]:
            self.mask = Mask(file_name[0][:-len('.nii')], self.manager.session)
        else:
            print 'Mask not chosen'

    def configure_spm(self, e):
        SPMPath(self.manager).exec_()