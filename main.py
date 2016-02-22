import sys
from src.python.gui import GUI
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
x = GUI()
sys.exit(app.exec_())