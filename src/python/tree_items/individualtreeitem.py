from PyQt5.QtWidgets import QTreeWidgetItem

class IndividualTreeItem(QTreeWidgetItem):
    def __init__(self,name,individual):
        super(IndividualTreeItem, self).__init__([name])

        self.individual = individual
