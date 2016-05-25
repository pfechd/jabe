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

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5 import QtWidgets, QtGui
from ..session import Session


class SessionTreeItem(QTreeWidgetItem, Session):
    def __init__(self, configuration=None):
        super(SessionTreeItem, self).__init__(configuration=configuration)

    def load_configuration(self, configuration):
        super(SessionTreeItem, self).load_configuration(configuration)
        # Set the name in the first column of the QTreeWidgetItem
        self.setText(0, self.name)

    def remove_item(self):
        remove = None
        if  self.description != "" or self.mask is not None or self.stimuli is not None or self.anatomy is not None or\
                self.brain is not None or self.plot_settings != {}:
            remove = QMessageBox.question(None, "Remove", "Are you sure you want to remove this?",
                                          QMessageBox.Yes | QMessageBox.No)
        if remove == QMessageBox.No:
            return
        self.parent().remove_session(self)
        self.treeWidget().window().update_gui()
        self.parent().removeChild(self)

    def create_buttons(self):
        tree = self.treeWidget()
        b2 = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/minus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b2.setFixedSize(16, 16)
        b2.setIcon(icon)
        b2.setFlat(True)
        b2.clicked.connect(self.remove_item)
        tree.setItemWidget(self, 1, b2)

    def update_name(self, text):
        # Set the name in the first column of the QTreeWidgetItem
        self.setText(0, text)
        self.name = text
