#!/bin/env python

# This script should be launched from the project root checks whether
# the following applications are correctly installed:
# * Qt5
# * PyQt5
# * numpy
# * matplotlib
# * scipy
# * nibabel

import sys
import numpy
import scipy
import nibabel
import matplotlib.pyplot
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
button = QtWidgets.QPushButton("Bra jobbat, allt fungerar! :-)")
window.setCentralWidget(button)
window.show()
app.exec_()

assert sys.version_info >= (2,5)
assert sys.version_info[0] != 3
