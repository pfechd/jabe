import sys
from src.python.mainwindow import MainWindow
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
x = MainWindow()
sys.exit(app.exec_())