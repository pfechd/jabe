from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5 import QtWidgets, QtGui
from individualtreeitem import IndividualTreeItem
from ..group import Group
import src.generated_ui.icons_rc


class GroupTreeItem(QTreeWidgetItem):
    def __init__(self, group):
        super(GroupTreeItem, self).__init__([group.name])

        self.group = group
        self.nr_of_individuals = 0

    def add_individual(self):
        individual = Group()
        individual.name = 'Individual ' + str(self.nr_of_individuals)
        self.group.add_child(individual)
        individual_item = IndividualTreeItem(individual)
        self.addChild(individual_item)
        individual_item.create_buttons()
        self.setExpanded(True)
        self.nr_of_individuals += 1
        self.treeWidget().window().update_gui()

    def remove_item(self):
        tree = self.treeWidget()
        tree.takeTopLevelItem(tree.indexFromItem(self).row())
        tree.parent().parent().groups.remove(self.group)
        if len(tree.selectedItems()) == 0:
                tree.window().ui.stackedWidget.setCurrentIndex(1)

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

    def get_overview_tree(self):
        top_tree_items = []
        for individual in self.group.children:
            tree_item = QTreeWidgetItem([individual.name])
            for session in individual.children:
                sess_item = QTreeWidgetItem([session.name])
                tree_item.addChild(sess_item)

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

                sess_item.addChildren([epi_path_item, mask_path_item, stim_path_item])

            top_tree_items.append(tree_item)
        return top_tree_items

    def add_individuals_boxes(self, layout):
        for individual in self.group.children:
            box = QtWidgets.QCheckBox(individual.name)
            box.setChecked(True)
            layout.addWidget(box)

    def update_name(self, text):
        self.setText(0, text)
        self.group.name = text
