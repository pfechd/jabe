from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui


class SessionTreeItem(QTreeWidgetItem):
    def __init__(self, session):
        super(SessionTreeItem, self).__init__([session.name])

        self.session = session

    def remove_item(self):
        self.parent().individual.remove_session(self.session)
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
        self.setText(0, text)
        self.session.name = text
