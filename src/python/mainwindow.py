import json
import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from generated_ui.mainwindow import Ui_MainWindow
from group import Group
from mask import Mask
from plotwindow import CustomPlot
from spmpath import SPMPath
from stimulionset import StimuliOnset
from tree_items.grouptreeitem import GroupTreeItem
from tree_items.individualtreeitem import IndividualTreeItem
from tree_items.sessiontreeitem import SessionTreeItem
from namedialog import NameDialog


class MainWindow(QMainWindow):
    """
    The main window of the application.

    The window is the main entry point for the user into the applications. It
    mostly consists of callback functions for the various user interface
    events.
    """

    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionSettings.triggered.connect(self.configure_spm)
        self.ui.pushButton.clicked.connect(self.calculate_button_pressed)
        self.ui.brainButton.clicked.connect(self.brain_button_pressed)
        self.ui.maskButton.clicked.connect(self.mask_button_pressed)
        self.ui.stimuliButton.clicked.connect(self.stimuli_button_pressed)
        self.ui.add_group_button.clicked.connect(self.add_group_pressed)
        self.ui.remove_button.clicked.connect(self.remove_pressed)
        self.ui.tree_widget.itemSelectionChanged.connect(self.update_gui)
        self.ui.editName.textChanged.connect(self.name_changed)
        self.ui.editName.returnPressed.connect(self.ui.editName.clearFocus)
        self.ui.editName.hide()
        self.show()

        self.individual_buttons = [self.ui.pushButton, self.ui.brainButton,
                                   self.ui.maskButton, self.ui.stimuliButton]


        self.ui.tree_widget.setColumnWidth(0, 200)
        self.groups = []
        self.load_configuration()
        self.update_gui()

    def closeEvent(self, event):
        self.save_configuration()

    def save_configuration(self):
        configuration = {
            'groups': [group.get_configuration() for group in self.groups],
            'current': 0
        }

        with open('configuration.json', 'w') as f:
            json.dump(configuration, f, indent=4)

    def load_configuration(self):
        if os.path.exists('configuration.json'):
            with open('configuration.json', 'r') as f:
                configuration = json.load(f)

            self.groups = []

            if 'groups' in configuration:
                for group_configuration in configuration['groups']:
                    group = Group(configuration=group_configuration)
                    self.groups.append(group)

            for group in self.groups:
                group_tree_item = GroupTreeItem(group)
                self.ui.tree_widget.addTopLevelItem(group_tree_item)
                group_tree_item.create_buttons()
                for individual in group.individuals:
                    individual_tree_item = IndividualTreeItem(individual)

                    group_tree_item.addChild(individual_tree_item)
                    individual_tree_item.create_buttons()

                    for session in individual.sessions:
                        session_tree_item = SessionTreeItem(session)
                        individual_tree_item.addChild(session_tree_item)

            self.update_gui()

            if 'current' in configuration:
                print 'Please select the', configuration['current']  # TODO: Do something about this!

            self.update_gui()

    def add_group_pressed(self):
        current_row = len(self.groups)
        #nd = NameDialog(self, name='New group ' + str(current_row))
        name = 'New group ' + str(current_row)
        group = Group(name=name)
        self.groups.append(group)
        group_item = GroupTreeItem(group)
        self.ui.tree_widget.addTopLevelItem(group_item)
        group_item.create_buttons()

    def remove_pressed(self):
        if self.ui.tree_widget.selectedItems():
            selected = self.ui.tree_widget.selectedItems()[0]
            if isinstance(selected, IndividualTreeItem):
                selected.parent().group.remove_individual(selected.individual)
                selected.parent().removeChild(selected)
            elif isinstance(selected, GroupTreeItem):
                self.groups.remove(selected.group)
                self.ui.tree_widget.takeTopLevelItem(self.ui.tree_widget.indexFromItem(selected).row())
            elif isinstance(selected, SessionTreeItem):
                selected.parent().individual.remove_session(selected.session)
                selected.parent().removeChild(selected)
            self.update_gui()
            if len(self.ui.tree_widget.selectedItems()) == 0:
                self.ui.editName.hide()

    def update_buttons(self):
        if self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            individual = self.ui.tree_widget.selectedItems()[0].session
            for button in self.individual_buttons:
                button.setEnabled(True)
            self.ui.pushButton.setEnabled(individual.ready_for_calculation())
        elif self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
            self.ui.pushButton.setEnabled(True)
        else:
            for button in self.individual_buttons:
                button.setEnabled(False)

    def calculate_button_pressed(self):
        """ Callback function, run when the calculate button is pressed."""

        # TODO: Prompt user for brain and mask paths instead of falling
        # back unto hardcoded defaults

        if self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0].session
            session.calculate()
            CustomPlot(self, session)

        if self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
            individual = self.ui.tree_widget.selectedItems()[0].individual
            individual.calculate()
            CustomPlot(self, individual)


    def brain_button_pressed(self):
        """ Callback function, run when the choose brain button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.load_brain(file_name[0])
        else:
            print 'File not chosen'
        self.update_gui()

    def mask_button_pressed(self):
        """ Callback function, run when the choose mask button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii)")
        if file_name[0]:
            self.load_mask(file_name[0])
        else:
            print 'Mask not chosen'
        self.update_gui()

    def stimuli_button_pressed(self):
        """ Callback function, run when the choose stimuli button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.mat)")
        if file_name[0]:
            self.load_stimuli(file_name[0])
        else:
            print 'Stimuli not chosen'
        self.update_gui()

    def load_brain(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0].session
            session.load_data(path)
            self.update_gui()

    def load_mask(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0].session
            session.mask = Mask(path)
            self.update_gui()

    def load_stimuli(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0].session
            session.stimuli = StimuliOnset(path, 0.5)
            self.update_gui()

    def update_gui(self):
        self.update_buttons()
        self.update_text()
        self.ui.tree_widget.update()

    def update_text(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                individual = self.ui.tree_widget.selectedItems()[0].session

                if individual.path:
                    self.ui.brainLabel.setText('EPI-images chosen: ' + individual.path)
                else:
                    self.ui.brainLabel.setText('No EPI-images chosen')

                if individual.mask:
                    self.ui.maskLabel.setText('Mask picked: ' + individual.mask.path)
                else:
                    self.ui.maskLabel.setText('No mask chosen')

                if individual.stimuli:
                    self.ui.stimuliLabel.setText('Stimuli picked: ' + individual.stimuli.path)
                else:
                    self.ui.stimuliLabel.setText('No stimuli chosen')
            self.ui.editName.setText(self.ui.tree_widget.selectedItems()[0].text(0))
            self.ui.editName.show()
        else:
            for label in [self.ui.brainLabel, self.ui.maskLabel, self.ui.stimuliLabel]:
                label.setText('')

    def name_changed(self):
        if self.ui.tree_widget.selectedItems():
            text = self.ui.editName.text()
            self.ui.tree_widget.selectedItems()[0].update_name(text)

    def configure_spm(self):
        """ Callback function, run when the spm menu item is pressed."""
        SPMPath(self.manager).exec_()
