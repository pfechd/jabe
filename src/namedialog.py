# Copyright (C) 2016 pfechd
#
# This file is part of JABE.
#
# JABE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# JABE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JABE.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QDialog

from src.generated_ui.namedialog import Ui_namedialog


class NameDialog(QDialog):
    def __init__(self, parent, name=''):
        super(NameDialog, self).__init__(parent)
        self.ui = Ui_namedialog()
        self.ui.setupUi(self)
        self.name = name

        self.ui.inputName.setText(name)
        self.ui.okButton.clicked.connect(self.ok_clicked)
        self.ui.cancelButton.clicked.connect(self.cancel_clicked)

        self.exec_()

    def ok_clicked(self):
        self.name = self.ui.inputName.text()
        self.close()

    def cancel_clicked(self):
        self.close()

    def get_name(self):
        return self.name