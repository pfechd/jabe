from PyQt5 import QtWidgets
from src.python.generated_ui.hello_world import Ui_MainWindow
from src.python.sessionmanager import SessionManager


class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.manager = SessionManager()
        # sets the variable 'data' to 3 in MATLAB
        self.manager.set_data("data", 3)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.button_pressed)
        self.show()

    def button_pressed(self, e):
        # retrieves and prints what is in the variable 'data' in MATLAB
        print(self.manager.get_data("data"))
