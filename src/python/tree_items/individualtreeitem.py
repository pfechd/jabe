from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui
from sessiontreeitem import SessionTreeItem
from ..session import Session
import src.python.generated_ui.icons_rc


class IndividualTreeItem(QTreeWidgetItem):
    def __init__(self, individual):
        super(IndividualTreeItem, self).__init__([individual.name])

        self.individual = individual

    def add_session(self):
        session = Session(name="Session " + str(len(self.individual.sessions)))
        self.individual.add_session(session)
        sess_tree_item = SessionTreeItem(session)
        self.addChild(sess_tree_item)
        sess_tree_item.create_buttons()
        self.setExpanded(True)
        self.treeWidget().window().update_gui()

    def remove_item(self):
        self.parent().group.remove_individual(self.individual)
        self.parent().removeChild(self)

    def create_buttons(self):
        tree = self.treeWidget()
        b = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b.setFixedSize(16, 16)
        b.setIcon(icon)
        b.setFlat(True)
        b.clicked.connect(self.add_session)
        tree.setItemWidget(self, 2, b)

        b2 = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/minus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b2.setFixedSize(16, 16)
        b2.setIcon(icon)
        b2.setFlat(True)
        b2.clicked.connect(self.remove_item)
        tree.setItemWidget(self, 1, b2)

    def get_overview_tree(self):
        top_tree_items = []
        for session in self.individual.sessions:
            tree_item = QTreeWidgetItem([session.name])
            if session.path:
                epi_path_item = QTreeWidgetItem(['EPI: ' + session.path.split('/')[-1]])
            else:
                epi_path_item = QTreeWidgetItem(['EPI: None'])

            if session.mask:
                mask_path_item = QTreeWidgetItem(['Mask: ' + session.mask.path.split('/')[-1]])
            else:
                mask_path_item = QTreeWidgetItem(['Mask: None'])

            if session.stimuli:
                stim_path_item = QTreeWidgetItem(['Stimuli: ' + session.stimuli.path.split('/')[-1]])
            else:
                stim_path_item = QTreeWidgetItem(['Stimuli: None'])

            tree_item.addChildren([epi_path_item, mask_path_item, stim_path_item])
            top_tree_items.append(tree_item)

        return top_tree_items

    def add_sessions_boxes(self):
        for session in self.individual.sessions:
            box = QtWidgets.QCheckBox(session.name)
            self.treeWidget().window().ui.sessions_plot.addWidget(box)

    def clear_sessions_boxes(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_sessions_boxes(child.layout())

    def remove_sessions_to_plot(self):
        pass

    def update_name(self, text):
        self.setText(0, text)
        self.individual.name = text
