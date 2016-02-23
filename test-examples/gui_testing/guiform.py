# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guiform.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(300, 200)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 59, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 59, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 59, 16))
        self.label_3.setObjectName("label_3")
        self.testText1 = QtWidgets.QLineEdit(Form)
        self.testText1.setGeometry(QtCore.QRect(80, 10, 201, 21))
        self.testText1.setMaxLength(5)
        self.testText1.setObjectName("testText1")
        self.testText2 = QtWidgets.QLineEdit(Form)
        self.testText2.setGeometry(QtCore.QRect(80, 40, 201, 21))
        self.testText2.setMaxLength(5)
        self.testText2.setObjectName("testText2")
        self.testText3 = QtWidgets.QLineEdit(Form)
        self.testText3.setGeometry(QtCore.QRect(80, 70, 201, 21))
        self.testText3.setMaxLength(5)
        self.testText3.setObjectName("testText3")
        self.testSlider = QtWidgets.QSlider(Form)
        self.testSlider.setGeometry(QtCore.QRect(99, 100, 181, 22))
        self.testSlider.setMaximum(12)
        self.testSlider.setProperty("value", 4)
        self.testSlider.setOrientation(QtCore.Qt.Horizontal)
        self.testSlider.setObjectName("testSlider")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(10, 100, 59, 16))
        self.label_4.setObjectName("label_4")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(160, 160, 113, 32))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Test1:"))
        self.label_2.setText(_translate("Form", "Test2:"))
        self.label_3.setText(_translate("Form", "Test3:"))
        self.testText1.setText(_translate("Form", "a"))
        self.testText2.setText(_translate("Form", "b"))
        self.testText3.setText(_translate("Form", "c"))
        self.label_4.setText(_translate("Form", "TestSlide:"))
        self.pushButton.setText(_translate("Form", "Ok"))

