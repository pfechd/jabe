from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui
from individualtreeitem import IndividualTreeItem
from ..individual import Individual
import src.python.generated_ui.icons_rc


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

    def remove_item(self):
        tree = self.treeWidget()
        tree.takeTopLevelItem(tree.indexFromItem(self).row())
        tree.parent().parent().groups.remove(self.group)
        if len(tree.selectedItems()) == 0:
                tree.parent().parent().ui.stackedWidget.setCurrentIndex(1)

    def create_buttons(self):
        tree = self.treeWidget()
        b = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b.setFixedSize(16, 16)
        b.setIcon(icon)
        b.setFlat(True)
        b.clicked.connect(self.add_individual)
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
        self.group.name = text

