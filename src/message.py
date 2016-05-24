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

from PyQt5 import QtWidgets

from src.generated_ui import Ui_message


class Message(QtWidgets.QDialog):
    """ Simple window for showing messages."""
    def __init__(self, message):
        super(Message, self).__init__()
        self.ui = Ui_message()
        self.ui.setupUi(self)
        self.ui.textBrowser.setText(message)
        self.ui.pushButton.clicked.connect(self.close)
        self.show()
