from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui
from individualtreeitem import IndividualTreeItem
from ..individual import Individual


class GroupTreeItem(QTreeWidgetItem):
    def __init__(self, group):
        super(GroupTreeItem, self).__init__([group.name])

        self.group = group
        self.nr_of_individuals = 0

    def add_individual(self):
        individual = Individual()
        individual.name = 'Individual ' + str(self.nr_of_individuals)
        self.group.add_individual(individual)
        individual_item = IndividualTreeItem(individual)
        self.addChild(individual_item)
        individual_item.create_buttons()
        self.setExpanded(True)
        self.nr_of_individuals += 1

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

    def update_name(self, text):
        self.setText(0, text)
        self.group.name = text

