from PyQt5.QtWidgets import QTreeWidgetItem


class SessionTreeItem(QTreeWidgetItem):
    def __init__(self, session):
        super(SessionTreeItem, self).__init__([session.name.decode()])

        self.session = session
