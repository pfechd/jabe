from PyQt5.QtWidgets import QTreeWidgetItem


class SessionTreeItem(QTreeWidgetItem):
    def __init__(self, session):
        super(SessionTreeItem, self).__init__([session.name])

        self.session = session

    def update_name(self, text):
        self.setText(0, text)
        self.session.name = text
