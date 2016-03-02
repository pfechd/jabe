import os.path
from PyQt5 import QtWidgets
from generated_ui.spmpathph import Ui_spm_path
from message import Message


class SPMPath(QtWidgets.QDialog):
    """
    Window for adding a path to an SPM directory.
    """

    def __init__(self, manager):
        super(SPMPath, self).__init__()
        self.manager = manager
        self.ui = Ui_spm_path()
        self.ui.setupUi(self)
        self.ui.submit.clicked.connect(self.submit_spm_path)
        self.show()

    def submit_spm_path(self, e):
        """
        Check and save given SPM path.

        Reads a path from the user interface text window.
        Any '~' in given path will be replaced with a path to the user's home
        directory. A valid path will be added to the matlab engine and saved.
        :param e: Event description
        """
        if self.check_spm():
            Message("SPM path already set").exec_()
            self.close()

        path = os.path.expanduser(self.ui.lineEdit.text())
        if self.check_path(path):
            self.manager.session.addpath(path, nargout=0)
            if self.check_spm():
                Message("Path has been added").exec_()
                # TODO save path to settings
                self.close()
            else:
                Message("SPM is not working").exec_()
                self.manager.session.rmpath(path, nargout=0)
        else:
            Message("Not an existing directory").exec_()

    def check_path(self, path):
        """Check if given path is a valid SPM directory."""
        return os.path.exists(path)

    def check_spm(self):
        """Check if spm function exists in matlab engine."""
        return self.manager.session.exist('spm', nargout=1) == 2
