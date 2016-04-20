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
        self.addChild(SessionTreeItem(session))
        self.setExpanded(True)

    def create_buttons(self):
        tree = self.treeWidget()
        b = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b.setFixedSize(16, 16)
        b.setIcon(icon)
        b.setFlat(True)
        b.clicked.connect(self.add_session)
        tree.setItemWidget(self, 1, b)

    def update_name(self, text):
        self.setText(0, text)
        self.individual.name = text
