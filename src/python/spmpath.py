from PyQt5 import QtWidgets
from src.python.generated_ui.spmpathph import Ui_spm_path
from src.python.sessionmanager import SessionManager
import os.path


class SPMPath(QtWidgets.QDialog):
    def __init__(self, manager):
        super(SPMPath, self).__init__()
        self.manager = manager
        self.ui = Ui_spm_path()
        self.ui.setupUi(self)
        self.ui.submit.clicked.connect(self.button_pressed)
        self.show()

    def button_pressed(self,e):
        # retrieves and prints what is in the variable 'data' in matlab
        path = self.ui.lineEdit.text()
        if os.path.exists(os.path.expanduser(path)):
            self.manager.session.addpath(path, nargout=0)
            status = self.manager.session.exist('spm', nargout=1)
            if status != 2: #
                self.ui.submit.setText("SPM is not working")
                self.manager.session.rmpath(path, nargout=0)
            else:
                self.ui.submit.setText("Working")
                self.close()
                # TODO save path to settings
        else:
            self.ui.submit.setText("Not a valid directory")
