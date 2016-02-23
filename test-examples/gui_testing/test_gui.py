from PyQt5 import QtWidgets
from testform import Ui_Form
import sys

class MyWidget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(MyWidget, self).__init__(parent)
		self.ui = Ui_Form()
		self.ui.setupUi(self)
		self.ui.pushButton.clicked.connect()




if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MyWidget()
	window.resize(300, 200)
	window.show()
	window.print_first_test()
	sys.exit(app.exec_())