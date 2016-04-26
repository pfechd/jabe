from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui
from sessiontreeitem import SessionTreeItem
from ..session import Session
import src.python.generated_ui.icons_rc


class IndividualTreeItem(QTreeWidgetItem):
    def __init__(self, individual):
        super(IndividualTreeItem, self).__init__([individual.name])

        self.individual = individual

    def add_session(self):
        session = Session(name="Session " + str(len(self.individual.sessions)))
        self.individual.add_session(session)
        sess_tree_item = SessionTreeItem(session)
        self.addChild(sess_tree_item)
        sess_tree_item.create_buttons()
        self.setExpanded(True)

    def remove_item(self):
        self.parent().group.remove_individual(self.individual)
        self.parent().removeChild(self)

    def create_buttons(self):
        tree = self.treeWidget()
        b = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b.setFixedSize(16, 16)
        b.setIcon(icon)
        b.setFlat(True)
        b.clicked.connect(self.add_session)
        tree.setItemWidget(self, 2, b)

        b2 = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/minus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b2.setFixedSize(16, 16)
        b2.setIcon(icon)
        b2.setFlat(True)
        b2.clicked.connect(self.remove_item)
        tree.setItemWidget(self, 1, b2)

    def update_name(self, text):
        self.setText(0, text)
        self.individual.name = text
