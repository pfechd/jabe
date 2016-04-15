from PyQt5.QtWidgets import QTreeWidgetItem

class SessionTreeItem(QTreeWidgetItem):
    def __init__(self, name, session):
        super(SessionTreeItem, self).__init__([name])

        self.session = session
