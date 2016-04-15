from PyQt5.QtWidgets import QTreeWidgetItem
from sessiontreeitem import SessionTreeItem
from ..session import Session


class IndividualTreeItem(QTreeWidgetItem):
    def __init__(self, individual):
        super(IndividualTreeItem, self).__init__([individual.name])

        self.individual = individual

    def add_session(self):
        session = Session(name="Session " + str(len(self.individual.sessions)))
        self.individual.add_session(session)
        self.addChild(SessionTreeItem(session))
