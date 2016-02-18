from PyQt5 import QtWidgets
from PyQt5 import Qt
from src.python.generated_ui.hello_world import Ui_MainWindow
import src.python.session_manager



class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(GUI,self).__init__()
        self.session = src.python.session_manager.session_manager()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.button_pressed)
        self.show()

    def button_pressed(self,e):
        self.session.hello_world()
