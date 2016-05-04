import json
import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QSpacerItem, QSizePolicy

from generated_ui.mainwindow import Ui_MainWindow
from group import Group
from mask import Mask
from plotwindow import CustomPlot
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
        self.ui.tree_widget.setColumnWidth(1, 25)
        self.ui.tree_widget.setColumnWidth(2, 25)
        self.ui.extract_session_btn.clicked.connect(self.calculate_button_pressed)
        self.ui.extract_btn_individual.clicked.connect(self.calculate_button_pressed)
        self.ui.extract_btn_group.clicked.connect(self.calculate_button_pressed)
        self.ui.add_session_epi_btn.clicked.connect(self.brain_button_pressed)
        self.ui.add_session_mask_btn.clicked.connect(self.mask_button_pressed)
        self.ui.add_session_stimuli_btn.clicked.connect(self.stimuli_button_pressed)
        self.ui.add_group_menu_btn.triggered.connect(self.add_group_pressed)
        self.ui.exit_menu_btn.triggered.connect(self.exit_button_pressed)
        self.ui.add_individual_btn.clicked.connect(self.add_item_clicked)
        self.ui.add_session_btn.clicked.connect(self.add_item_clicked)
        self.ui.remove_session_btn.clicked.connect(self.remove_pressed)
        self.ui.remove_group_btn.clicked.connect(self.remove_pressed)
        self.ui.remove_individual_btn.clicked.connect(self.remove_pressed)
        self.ui.tree_widget.itemSelectionChanged.connect(self.update_gui)
        self.ui.session_name.textChanged.connect(self.name_changed)
        self.ui.group_name.textChanged.connect(self.name_changed)
        self.ui.individual_name.textChanged.connect(self.name_changed)
        self.ui.session_name.returnPressed.connect(self.ui.session_name.clearFocus)
        self.ui.group_name.returnPressed.connect(self.ui.group_name.clearFocus)
        self.ui.individual_name.returnPressed.connect(self.ui.individual_name.clearFocus)
        self.ui.stackedWidget.setCurrentIndex(1)
        self.show()

        self.individual_buttons = [self.ui.extract_session_btn, self.ui.add_session_epi_btn,
                                   self.ui.add_session_mask_btn, self.ui.add_session_stimuli_btn]

        self.ui.tree_widget.setColumnWidth(0, 200)
        self.groups = []
        self.load_configuration()
        self.update_gui()

    def closeEvent(self, event):
        self.save_configuration()

    def save_configuration(self):
        if self.ui.tree_widget.selectedItems():
            selected = self.ui.tree_widget.selectedItems()[0]
            current = []

            if selected.parent():
                parent_selected = selected.parent()
                if parent_selected.parent():
                    top = parent_selected.parent()
                    current.append(self.ui.tree_widget.indexFromItem(top).row())
                current.append(self.ui.tree_widget.indexFromItem(parent_selected).row())
            current.append(self.ui.tree_widget.indexFromItem(selected).row())
        else:
            current = []

        configuration = {
            'groups': [group.get_configuration() for group in self.groups],
            'current': current
        }

        with open('configuration.json', 'w') as f:
            json.dump(configuration, f, indent=4)

    def load_configuration(self):
        if os.path.exists('configuration.json'):
            with open('configuration.json', 'r') as f:
                configuration = json.load(f)

            for group_configuration in configuration['groups']:
                group_tree_item = GroupTreeItem()
                self.ui.tree_widget.addTopLevelItem(group_tree_item)
                group_tree_item.load_configuration(group_configuration)
                self.groups.append(group_tree_item)
                group_tree_item.create_buttons()

            self.update_gui()

            if 'current' in configuration:
                current = configuration['current']
                if isinstance(current, list):  # Compatibility with old config files
                    if len(current) >= 1:
                        top_item = self.ui.tree_widget.topLevelItem(current[0])
                        top_item.setSelected(True)
                        if len(current) >= 2:
                            top_item.setExpanded(True)
                            mid_item = top_item.child(current[1])
                            mid_item.setSelected(True)
                            top_item.setSelected(False)
                            if len(current) == 3:
                                mid_item.setExpanded(True)
                                mid_item.child(current[2]).setSelected(True)
                                mid_item.setSelected(False)

            self.update_gui()

    def add_group_pressed(self):
        current_row = len(self.groups)
        name = 'Group ' + str(current_row + 1)
        group = GroupTreeItem()
        group.update_name(name)
        self.groups.append(group)
        self.ui.tree_widget.addTopLevelItem(group)
        group.create_buttons()

    def exit_button_pressed(self):
        self.close()

    def add_item_clicked(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], GroupTreeItem):
                self.ui.tree_widget.selectedItems()[0].add_child()
            elif isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
                self.ui.tree_widget.selectedItems()[0].add_new_session()

    def remove_pressed(self):
        if self.ui.tree_widget.selectedItems():
            self.ui.tree_widget.selectedItems()[0].remove_item()

            if len(self.ui.tree_widget.selectedItems()) == 0:
                self.ui.stackedWidget.setCurrentIndex(1)

    def update_buttons(self):
        if self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            individual = self.ui.tree_widget.selectedItems()[0]
            for button in self.individual_buttons:
                button.setEnabled(True)
            self.ui.extract_session_btn.setEnabled(individual.ready_for_calculation())
        elif self.ui.tree_widget.selectedItems() and \
                (isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem) or
                     isinstance(self.ui.tree_widget.selectedItems()[0], GroupTreeItem)):
            for button in self.individual_buttons:
                button.setEnabled(False)
            self.ui.extract_btn_group.setEnabled(True)
            self.ui.extract_btn_individual.setEnabled(True)
        else:
            for button in self.individual_buttons:
                button.setEnabled(False)

    def calculate_button_pressed(self):
        """ Callback function, run when the calculate button is pressed."""

        if self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            session.prepare_for_calculation(
                self.ui.percent_session_btn.isChecked(),
                self.ui.global_normalization_session_btn.isChecked())
            CustomPlot(self, session)

        if self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
            individual = self.ui.tree_widget.selectedItems()[0]
            individual.prepare_for_calculation(
                self.ui.percent_individual_btn.isChecked(),
                self.ui.global_normalization_individual_btn.isChecked())
            CustomPlot(self, individual)

        if self.ui.tree_widget.selectedItems() and isinstance(self.ui.tree_widget.selectedItems()[0], GroupTreeItem):
            group = self.ui.tree_widget.selectedItems()[0]
            group.prepare_for_calculation(
                self.ui.percent_group_btn.isChecked(),
                self.ui.global_normalization_group_btn.isChecked())
            CustomPlot(self, group)


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

    def create_stimuli_button_pressed(self):
        """ Callback function, run when the chreate simuli button is pressed."""
        
    def load_brain(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            session.load_data(path)
            self.update_gui()

    def load_mask(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            session.mask = Mask(path)
            self.update_gui()

    def load_stimuli(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            session.stimuli = StimuliOnset(path, 0.5)
            self.update_gui()

    def update_gui(self):
        self.update_buttons()
        self.update_text()
        self.update_stackedwidget()
        self.ui.tree_widget.update()

    def update_stackedwidget(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
                self.ui.stackedWidget.setCurrentIndex(2)
                self.ui.individual_name.setText(self.ui.tree_widget.selectedItems()[0].text(0))

                # Add overview tree in individual panel
                self.ui.sessions_overview_tree.clear()
                self.ui.sessions_overview_tree.addTopLevelItems(self.ui.tree_widget.selectedItems()[0].get_overview_tree())

                # Add checkboxes for individuals in individual panel
                self.clear_layout(self.ui.sessions_plot)
                self.ui.tree_widget.selectedItems()[0].add_sessions_boxes(self.ui.sessions_plot)
                self.ui.sessions_plot.insertSpacerItem(-1, QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

            elif isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                self.ui.stackedWidget.setCurrentIndex(3)
                self.ui.session_name.setText(self.ui.tree_widget.selectedItems()[0].text(0))
            else:
                self.ui.stackedWidget.setCurrentIndex(0)
                self.ui.group_name.setText(self.ui.tree_widget.selectedItems()[0].text(0))

                # Add overview tree in group panel
                self.ui.individual_overview_tree.clear()
                self.ui.individual_overview_tree.addTopLevelItems(self.ui.tree_widget.selectedItems()[0].get_overview_tree())

                # Add checkboxes for individuals in group panel
                self.clear_layout(self.ui.individuals_plot)
                self.ui.tree_widget.selectedItems()[0].add_individuals_boxes(self.ui.individuals_plot)
                self.ui.individuals_plot.insertSpacerItem(-1, QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def update_text(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                individual = self.ui.tree_widget.selectedItems()[0]

                if individual.path:
                    self.ui.session_epi_label.setText('EPI-images chosen: ' + individual.path.split('/')[-1])
                else:
                    self.ui.session_epi_label.setText('No EPI-images chosen')

                if individual.mask:
                    self.ui.session_mask_label.setText('Mask picked: ' + individual.mask.path.split('/')[-1])
                else:
                    self.ui.session_mask_label.setText('No mask chosen')

                if individual.stimuli:
                    self.ui.session_stimuli_label.setText('Stimuli picked: ' + individual.stimuli.path.split('/')[-1])
                else:
                    self.ui.session_stimuli_label.setText('No stimuli chosen')
        else:
            for label in [self.ui.session_epi_label, self.ui.session_mask_label, self.ui.session_stimuli_label]:
                label.setText('')

    def name_changed(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
                text = self.ui.individual_name.text()
            elif isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                text = self.ui.session_name.text()
            else:
                text = self.ui.group_name.text()

            self.ui.tree_widget.selectedItems()[0].update_name(text)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())

    def configure_spm(self):
        """ Callback function, run when the spm menu item is pressed."""
        SPMPath(self.manager).exec_()
