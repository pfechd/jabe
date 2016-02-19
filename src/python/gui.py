from PyQt5 import QtWidgets
from PyQt5 import Qt
from src.python.generated_ui.hello_world import Ui_MainWindow
import src.python.session_manager



class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(GUI,self).__init__()
        self.session = src.python.session_manager.session_manager()
        # sets the varibale 'data' to 3 in matlab
        self.session.add_data("data",3)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.button_pressed)
        self.show()

    def button_pressed(self,e):
        # retrieves and prints what is in the variable 'data' in matlab
        print(self.session.get_data("data"))