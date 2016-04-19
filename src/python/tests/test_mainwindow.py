import sys
import unittest
from PyQt5 import QtWidgets
from src.python import mainwindow


app = QtWidgets.QApplication(sys.argv)


class TestMainWindow(unittest.TestCase):

    def setUp(self):
        self.main_window = mainwindow.MainWindow()

    def test_add_group(self):
        self.main_window.ui.add_group_button.click()
        self.main_window.ui.add_group_button.click()
        self.main_window.ui.add_group_button.click()

        for index, group in enumerate(self.main_window.groups):
            self.assertEqual(group.name, 'New group ' + str(index))

    def test_add_individual(self):
        self.main_window.ui.add_group_button.click()

    def test_add_session(self):
        pass

    def tearDown(self):
        self.main_window.close()


if __name__ == "__main__":
    unittest.main()