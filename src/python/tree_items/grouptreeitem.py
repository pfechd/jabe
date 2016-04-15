from PyQt5.QtWidgets import QTreeWidgetItem
from individualtreeitem import IndividualTreeItem
from ..individual import Individual

class GroupTreeItem(QTreeWidgetItem):
    def __init__(self,name,group):
        super(GroupTreeItem, self).__init__([name])

        self.group = group

    def add_individual(self,name):
        individual = Individual()
        self.group.add_individual(individual)
        self.addChild(IndividualTreeItem(name,individual))
