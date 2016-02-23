from PyQt5 import QtWidgets
from guiform import Ui_Form
import sys

class MyWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.button_click)

    def button_click(self):
        self.text1 = self.ui.testText1.text()
        self.text2 = self.ui.testText2.text()
        self.text3 = self.ui.testText3.text()
        self.slider = self.ui.testSlider.value()

    def set_form_to_zero(self):
        self.ui.testText1.setText('')
        self.ui.testText2.setText('')
        self.ui.testText3.setText('')
        self.ui.testSlider.setValue(0)

    def set_form_to_default(self):
        self.ui.testText1.setText('a')
        self.ui.testText2.setText('b')
        self.ui.testText3.setText('c')
        self.ui.testSlider.setValue(4)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.resize(300, 200)
    window.show()
    sys.exit(app.exec_())