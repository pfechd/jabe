from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui
from individualtreeitem import IndividualTreeItem
from ..individual import Individual


class GroupTreeItem(QTreeWidgetItem):
    def __init__(self, group):
        super(GroupTreeItem, self).__init__([group.name])

        self.group = group

    def add_individual(self):
        individual = Individual()
        individual.name = 'test'
        self.group.add_individual(individual)
        individual_item = IndividualTreeItem(individual)
        self.addChild(individual_item)
        individual_item.create_buttons()
        self.setExpanded(True)

    def create_buttons(self):
        tree = self.treeWidget()
        b = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/plus-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b.setFixedSize(16, 16)
        b.setIcon(icon)
        b.setFlat(True)
        b.clicked.connect(self.add_individual)
        tree.setItemWidget(self, 1, b)

