import unittest
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
import sys
import widget

app = QtWidgets.QApplication(sys.argv)

class TestMyWidget(unittest.TestCase):

    def setUp(self):
        self.form = widget.MyWidget()

    def tearDown(self):
        self.form = None

    def set_form_to_zero(self):
        self.form.set_form_to_zero()

    def set_form_to_default(self):
        self.form.set_form_to_default()

    def test_default_values(self):
        QTest.mouseClick(self.form.ui.pushButton, Qt.LeftButton)
        self.assertEqual(self.form.text1, 'a')
        self.assertEqual(self.form.text2, 'b')
        self.assertEqual(self.form.text3, 'c')
        self.assertEqual(self.form.slider, 4)

    def test_text1(self):
        self.set_form_to_zero()

        self.form.ui.testText1.clear()
        QTest.keyClicks(self.form.ui.testText1, 'abcdef')
        self.assertEqual(self.form.ui.testText1.text(), 'abcde')

        self.form.ui.testText1.clear()
        QTest.keyClicks(self.form.ui.testText1, 'abc')

        QTest.mouseClick(self.form.ui.pushButton, Qt.LeftButton)
        self.assertEqual(self.form.text1, 'abc')

    def test_slider(self):
        self.set_form_to_zero()
       
        self.form.ui.testSlider.setValue(13)
        self.assertEqual(self.form.ui.testSlider.value(), 12)

        self.form.ui.testSlider.setValue(-1)
        self.assertEqual(self.form.ui.testSlider.value(), 0)

        self.form.ui.testSlider.setValue(6)

        QTest.mouseClick(self.form.ui.pushButton, Qt.LeftButton)
        self.assertEqual(self.form.slider, 6)


if __name__ == "__main__":
    unittest.main()