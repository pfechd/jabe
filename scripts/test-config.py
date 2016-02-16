#!/bin/env python

# This script should be launched from the project root checks whether
# the following applications are correctly installed:
# * Qt5
# * PyQt5
# * Matlab
# * SPM

import sys
from PyQt5 import QtWidgets
import matlab.engine

engine = matlab.engine.connect_matlab()

engine.addpath(engine.pwd() + '/spm12')
engine.spm('colour')

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
button = QtWidgets.QPushButton("Bra jobbat, allt fungerar! :-)")
window.setCentralWidget(button)
window.show()
app.exec_()
