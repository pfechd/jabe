from PyQt5.QtWidgets import QTreeWidgetItem
from individualtreeitem import IndividualTreeItem
from ..individual import Individual


class GroupTreeItem(QTreeWidgetItem):
    def __init__(self, group):
        super(GroupTreeItem, self).__init__([group.name])

        self.group = group

    def add_individual(self, name):
        individual = Individual()
        individual.name = name
        self.group.add_individual(individual)
        self.addChild(IndividualTreeItem(individual))
