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
from sessiontreeitem import SessionTreeItem
from ..group import Group


class IndividualTreeItem(QTreeWidgetItem, Group):
    def __init__(self, configuration=None):
        super(IndividualTreeItem, self).__init__(configuration=configuration)

    def load_configuration(self, configuration):
        super(IndividualTreeItem, self).load_configuration(configuration)
        # Set the name in the first column of the QTreeWidgetItem
        self.setText(0, self.name)

        if 'sessions' in configuration:
            for session_configuration in configuration['sessions']:
                session_tree_item = SessionTreeItem(configuration=session_configuration)
                self.add_session(session_tree_item)

    def add_session(self, session):
        super(IndividualTreeItem, self).add_session(session)
        self.addChild(session)
        session.create_buttons()
        self.setExpanded(True)
        self.treeWidget().window().update_gui()

    def add_new_session(self):
        session = SessionTreeItem()
        session.update_name("Session " + str(len(self.sessions) + 1))
        self.add_session(session)

    def remove_item(self):
        remove = None
        if len(self.sessions) > 0 or self.description != "" or self.mask is not None or self.stimuli is not None or\
                self.anatomy is not None or self.plot_settings != {}:
            remove = QMessageBox.question(None, "Remove", "Are you sure you want to remove this?",
                                          QMessageBox.Yes | QMessageBox.No)
        if remove == QMessageBox.No:
            return
        self.parent().remove_child(self)
        self.treeWidget().window().update_gui()
        self.parent().removeChild(self)

    def create_buttons(self):
        """
        Create/add plus and minus buttons to item
        """

        tree = self.treeWidget()
        b = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b.setFixedSize(16, 16)
        b.setIcon(icon)
        b.setFlat(True)
        b.clicked.connect(self.add_new_session)
        tree.setItemWidget(self, 2, b)

        b2 = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/minus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b2.setFixedSize(16, 16)
        b2.setIcon(icon)
        b2.setFlat(True)
        b2.clicked.connect(self.remove_item)
        tree.setItemWidget(self, 1, b2)

    def get_overview_tree(self):
        """
        Get overview tree of session-children

        :return: List of QTreeWidgetItems
        """
        top_tree_items = []
        for session in self.sessions:
            tree_item = QTreeWidgetItem([session.name])
            if session.brain:
                epi_path_item = QTreeWidgetItem(['EPI: ' + session.brain.path.split('/')[-1]])
            else:
                epi_path_item = QTreeWidgetItem(['EPI: None'])

            if session.mask:
                mask_path_item = QTreeWidgetItem(['Mask: ' + session.mask.path.split('/')[-1]])
            else:
                mask_path_item = QTreeWidgetItem(['Mask: None'])

            if session.stimuli:
                stim_path_item = QTreeWidgetItem(['Stimuli: ' + session.stimuli.path.split('/')[-1]])
            else:
                stim_path_item = QTreeWidgetItem(['Stimuli: None'])

            tree_item.addChildren([epi_path_item, mask_path_item, stim_path_item])
            top_tree_items.append(tree_item)

        return top_tree_items

    def add_sessions_boxes(self, layout):
        """
        Add checkboxes for sessions to layout

        :param layout: QLayout
        """
        for session in self.sessions:
            box = QtWidgets.QCheckBox(session.name)
            layout.addWidget(box)

    def update_name(self, text):
        # Set the name in the first column of the QTreeWidgetItem
        self.setText(0, text)
        self.name = text
