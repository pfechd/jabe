from PyQt5 import QtWidgets
from src.python.generated_ui.message import Ui_message


class Message(QtWidgets.QDialog):
    """ Simple window for showing messages."""
    def __init__(self, message):
        super(Message, self).__init__()
        self.ui = Ui_message()
        self.ui.setupUi(self)
        self.ui.textBrowser.setText(message)
        self.ui.pushButton.clicked.connect(self.close)
        self.show()
