from PyQt5.QtWidgets import QDialog
from src.python.generated_ui.namedialog import Ui_namedialog


class NameDialog(QDialog):
    def __init__(self, parent, name=''):
        super(NameDialog, self).__init__(parent)
        self.ui = Ui_namedialog()
        self.ui.setupUi(self)
        self.name = name

        self.ui.inputName.setText(name)
        self.ui.okButton.clicked.connect(self.ok_clicked)
        self.ui.cancelButton.clicked.connect(self.cancel_clicked)

        self.exec_()

    def ok_clicked(self):
        self.name = self.ui.inputName.text()
        self.close()

    def cancel_clicked(self):
        self.close()

    def get_name(self):
        return self.name