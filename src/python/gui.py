from PyQt5 import QtWidgets
from src.python.generated_ui.hello_world import Ui_MainWindow
from src.python.sessionmanager import SessionManager
from src.python.spmpath import SPMPath
from src.python.brain import Brain
from src.python.mask import Mask
from src.python.visual_stimuli import VisualStimuli

class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.manager = SessionManager()
        # sets the variable 'data' to 3 in MATLAB
        self.manager.set_data("data", 3)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.button_pressed)
        self.ui.configureSPMButton.clicked.connect(self.configure_spm)
        self.show()

    def button_pressed(self, e):
        # retrieves and prints what is in the variable 'data' in MATLAB
        print(self.manager.get_data("data"))
        # TODO: Prompt user for brain and mask paths
        brain = Brain("../../test-data/brain_exp1_1", self.manager.session)
        mask = Mask("../../test-data/mask", self.manager.session)
        visual_stimuli = VisualStimuli("../../test-data/stimall", 0.5, self.manager.session)
        brain.apply_mask(mask)
        brain.normalize_to_mean(visual_stimuli)
        brain.plot_mean()
        brain.plot_std()

    def configure_spm(self, e):
        SPMPath(self.manager).exec_()