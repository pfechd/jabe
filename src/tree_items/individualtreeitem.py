from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui
from sessiontreeitem import SessionTreeItem
from ..group import Group


class IndividualTreeItem(QTreeWidgetItem, Group):
    def __init__(self, configuration=None):
        super(IndividualTreeItem, self).__init__(configuration=configuration)
        self.setText(0, self.name)

    def load_configuration(self, configuration):
        super(IndividualTreeItem, self).load_configuration(configuration)
        self.setText(0, self.name)

        if 'sessions' in configuration:
                for session_configuration in configuration['sessions']:
                        session_tree_item = SessionTreeItem(configuration=session_configuration)
                        self.add_session(session_tree_item)

    def add_session(self, session):
        super(IndividualTreeItem, self).add_session(session)
        self.addChild(session)
        session.create_buttons()
        self.setExpanded(True)
        self.treeWidget().window().update_gui()

    def add_new_session(self):
        session = SessionTreeItem(name="Session " + str(len(self.sessions) + 1))
        self.add_session(session)

    def remove_item(self):
        self.parent().remove_child(self)
        self.treeWidget().window().update_gui()
        self.parent().removeChild(self)

    def create_buttons(self):
        """
        Create/add plus and minus buttons to item
        """

        tree = self.treeWidget()
        b = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plus-icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        b.setFixedSize(16, 16)
        b.setIcon(icon)
        b.setFlat(True)
        b.clicked.connect(self.add_new_session)
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
        """
        Get overview tree of session-children

        :return: List of QTreeWidgetItems
        """
        top_tree_items = []
        for session in self.children:
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

    def add_sessions_boxes(self, layout):
        """
        Add checkboxes for sessions to layout

        :param layout: QLayout
        """
        for session in self.children:
            box = QtWidgets.QCheckBox(session.name)
            layout.addWidget(box)

    def update_name(self, text):
        self.setText(0, text)
        self.name = text
