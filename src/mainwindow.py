import json
import os
from collections import Iterable
import sys
from sys import platform as _platform

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QSpacerItem, QSizePolicy, QMessageBox

from generated_ui.mainwindow import Ui_MainWindow
from mask import Mask
from plotwindow import CustomPlot
from stimuliwindow import StimuliWindow
from stimuli import Stimuli
from tree_items.grouptreeitem import GroupTreeItem
from tree_items.individualtreeitem import IndividualTreeItem
from tree_items.sessiontreeitem import SessionTreeItem
from createmaskwindow import CreateMaskWindow
from namedialog import NameDialog

try:
    import Cocoa    # Only used on Mac OS when building .app
    COCOA_AVAILABLE = True
except ImportError:
    COCOA_AVAILABLE = False


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
        self.ui.add_session_anatomy_btn.clicked.connect(self.anatomy_button_pressed)
        self.ui.add_session_epi_btn.clicked.connect(self.brain_button_pressed)
        self.ui.add_session_mask_btn.clicked.connect(self.mask_button_pressed)
        self.ui.create_session_mask_btn.clicked.connect(self.create_mask_button_pressed)
        self.ui.add_session_stimuli_btn.clicked.connect(self.stimuli_button_pressed)
        self.ui.create_session_stimuli_btn.clicked.connect(self.create_stimuli_button_pressed)
        self.ui.add_group_menu_btn.triggered.connect(self.add_group_pressed)
        self.ui.load_config_menu_btn.triggered.connect(self.load_configuration_button_pressed)
        self.ui.save_config_menu_btn.triggered.connect(self.save_configuration)
        self.ui.save_config_as_menu_btn.triggered.connect(self.save_configuration_as)
        self.ui.new_config_menu_btn.triggered.connect(self.create_new_configuration)
        self.ui.add_group_btn.clicked.connect(self.add_group_pressed)
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

        self.ui.session_description.textChanged.connect(self.description_changed)
        self.ui.group_description.textChanged.connect(self.description_changed)
        self.ui.individual_description.textChanged.connect(self.description_changed)

        plot_buttons = [self.ui.global_normalization_individual_btn, self.ui.local_normalization_individual_btn,
                   self.ui.percent_individual_btn, self.ui.subtract_individual_btn,
                   self.ui.global_normalization_session_btn, self.ui.local_normalization_session_btn,
                   self.ui.percent_session_btn, self.ui.subtract_session_btn,
                   self.ui.global_normalization_group_btn, self.ui.local_normalization_group_btn,
                   self.ui.percent_group_btn, self.ui.subtract_group_btn]

        for button in plot_buttons:
            button.clicked.connect(self.plot_settings_changed)

        self.ui.stackedWidget.setCurrentIndex(1)
        self.show()

        self.individual_buttons = [self.ui.extract_session_btn, self.ui.add_session_epi_btn,
                                   self.ui.add_session_mask_btn, self.ui.add_session_stimuli_btn]

        self.current_config_path = ""
        self.ui.tree_widget.setColumnWidth(0, 200)
        self.groups = []
        self.update_gui()

    def check_paths(self, configuration, type = None):
        missing_paths = []
        for group in configuration['groups']:
            missing_paths += (self.check_paths_in_object(group))
            for individual in group['individuals']:
                missing_paths += (self.check_paths_in_object(individual))
                for session in individual['sessions']:
                    missing_paths += (self.check_paths_in_object(session))

        return missing_paths

    def check_paths_in_object(self, config_obj):
        missing_paths = []
        if 'path' in config_obj and not os.path.exists(config_obj['path']):
            missing_paths.append(config_obj['path'])
        if 'anatomy_path' in config_obj and not os.path.exists(config_obj['anatomy_path']):
            missing_paths.append(config_obj['anatomy_path'])
        if 'mask' in config_obj and 'path' in config_obj['mask'] and not os.path.exists(config_obj['mask']['path']):
            missing_paths.append(config_obj['mask']['path'] )
        if 'stimuli' in config_obj and 'path' in config_obj['stimuli'] and \
                not os.path.exists(config_obj['stimuli']['path']):
            missing_paths.append(config_obj['stimuli']['path'])

        return missing_paths

    def closeEvent(self, event):
        if self.groups != []:
            button = QMessageBox.question(self, "Save",
                                          "Do you want to save the current workspace before quitting?",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if button == QMessageBox.Cancel:
                event.ignore()
            if button == QMessageBox.Yes:
                self.save_configuration()

    def save_configuration_as(self):
        config_file = QFileDialog.getSaveFileName(self, "", "", ".json")
        if config_file[0]:
            self.current_config_path = config_file[0] + config_file[1]
            self.save_configuration()

    def save_configuration(self):
        """
        Save configuration file (configuration.json).
        """
        config_filename = self.current_config_path
        if config_filename == "":
            self.save_configuration_as()
            return

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

        if hasattr(sys, 'frozen'):
            dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        else:
            dir_path = os.getcwd()

        # Set OS specific path to configuration file
        if _platform == "linux" or _platform == "linux2":
            config_path = os.path.join(dir_path, config_filename)
        elif _platform == "darwin":
            if COCOA_AVAILABLE:
                path = Cocoa.NSBundle.mainBundle().bundlePath()     # Get path to .app bundle (Mac only)

            if hasattr(sys, 'frozen') and path.endswith('.app'):
                config_path = os.path.join(path, 'Contents', config_filename)
            else:
                config_path = os.path.join(dir_path, config_filename)

        elif _platform == "win32":
            if hasattr(sys, 'frozen'):
                dir_path = os.path.dirname(os.path.realpath(__file__))

            config_path = os.path.join(dir_path, config_filename)

        with open(config_path, 'w') as f:
            json.dump(configuration, f, indent=4)

    def load_configuration_button_pressed(self):
        if self.groups != []:
            button = QMessageBox.question(
                self, "Save",
                "Do you want to save the current workspace before loading?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if button == QMessageBox.Cancel:
                return
            if button == QMessageBox.Yes:
                self.save_configuration()

        config_path = QFileDialog.getOpenFileName(self, 'Open file', "", "*.json")
        if config_path[0]:
            self.current_config_path = config_path[0]
            self.load_configuration()

    def load_configuration(self):
        """
        Load configuration file (configuration.json).
        """

        config_filename = self.current_config_path

        if hasattr(sys, 'frozen'):
            dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        else:
            dir_path = os.getcwd()

        # Set OS specific path to configuration file
        if _platform == "linux" or _platform == "linux2":
            config_path = os.path.join(dir_path, config_filename)
        elif _platform == "darwin":
            if COCOA_AVAILABLE:
                path = Cocoa.NSBundle.mainBundle().bundlePath()     # Get path to .app bundle (Mac only)

            if hasattr(sys, 'frozen') and path.endswith('.app'):
                config_path = os.path.join(path, 'Contents', config_filename)
            else:
                config_path = os.path.join(dir_path, config_filename)

        elif _platform == "win32":
            if hasattr(sys, 'frozen'):
                dir_path = os.path.dirname(os.path.realpath(__file__))

            config_path = os.path.join(dir_path, config_filename)

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                configuration = json.load(f)

            missing_paths = self.check_paths(configuration)
            if missing_paths:
                QMessageBox.warning(self, "File error", "The following files are missing and will not be loaded:\n" +
                                    "\n".join(missing_paths))


            self.ui.tree_widget.clear()
            self.groups = []

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

    def create_new_configuration(self):
        if self.groups != []:
            button = QMessageBox.question(
                self, "Save",
                "Do you want to save the current workspace before creating a new one?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if button == QMessageBox.Cancel:
                return
            if button == QMessageBox.Yes:
                self.save_configuration()

        self.current_config_path = ""
        self.groups = []
        self.ui.tree_widget.clear()
        self.ui.stackedWidget.setCurrentIndex(2)

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
                self.ui.tree_widget.selectedItems()[0].add_new_individual()
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
        """ Callback function run when the calculate button is pressed."""
        # Make sure to update plot settings at least once before running
        self.plot_settings_changed()
        CustomPlot(self, self.ui.tree_widget.selectedItems()[0])

    def brain_button_pressed(self):
        """ Callback function run when the choose brain button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii*)")
        if file_name[0]:
            self.load_brain(file_name[0])
        else:
            print 'File not chosen'
        self.update_gui()

    def anatomy_button_pressed(self):
        """ Callback function run when the choose anatomy button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii*)")
        if file_name[0]:
            self.load_anatomy(file_name[0])
        else:
            print 'File not chosen'
        self.update_gui()

    def mask_button_pressed(self):
        """ Callback function run when the choose mask button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.nii*)")
        if file_name[0]:
            self.load_mask(file_name[0])
        else:
            print 'Mask not chosen'
        self.update_gui()

    def create_mask_button_pressed(self):
        """ Callback function run when the create mask button is pressed."""
        # Make sure EPI-file is choosen before running
        if self.ui.tree_widget.selectedItems()[0].brain:
            CreateMaskWindow(self, self.ui.tree_widget.selectedItems()[0].brain.brain_file)
        else:
            QMessageBox.warning(self, "Warning", "You have not chosen an EPI-image. Please choose an EPI-image.")
        self.update_gui()

    def stimuli_button_pressed(self):
        """ Callback function run when the choose stimuli button is pressed."""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', "", "Images (*.mat)")
        if file_name[0]:
            self.load_stimuli(file_name[0])
        else:
            print 'Stimuli not chosen'
        self.update_gui()

    def create_stimuli_button_pressed(self):
        """ Callback function run when the create simuli button is pressed."""
        
        self.stimuli_window = StimuliWindow(self)
        
    def load_brain(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            error = session.load_sequence(path)
            if error:
                QMessageBox.warning(self, "File error", error)
                self.brain_button_pressed()
            self.update_gui()

    def load_anatomy(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            error = session.load_anatomy(path)
            if error:
                QMessageBox.warning(self, "File error", error)
                self.anatomy_button_pressed()
            self.update_gui()

    def load_mask(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            error = session.load_mask(path)
            if error:
                QMessageBox.warning(self, "File error", error)
                self.mask_button_pressed()
            self.update_gui()

    def load_stimuli(self, path):
        if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
            session = self.ui.tree_widget.selectedItems()[0]
            error = session.load_stimuli(path, 0.5)
            if error:
                QMessageBox.warning(self, "File error", error)
                self.stimuli_button_pressed()
            self.update_gui()

    def update_gui(self):
        self.update_buttons()
        self.update_text()
        self.update_stacked_widget()
        self.ui.tree_widget.update()

    def update_stacked_widget(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
                self.ui.stackedWidget.setCurrentIndex(2)
                individual = self.ui.tree_widget.selectedItems()[0]
                self.ui.individual_name.setText(individual.text(0))
                self.ui.individual_description.setText(individual.description)

                if individual.get_setting('global'):
                    self.ui.global_normalization_individual_btn.setChecked(True)
                else:
                    self.ui.local_normalization_individual_btn.setChecked(True)
                if individual.get_setting('percent'):
                    self.ui.percent_individual_btn.setChecked(True)
                else:
                    self.ui.subtract_individual_btn.setChecked(True)

                # Add overview tree in individual panel
                self.ui.sessions_overview_tree.clear()
                self.ui.sessions_overview_tree.addTopLevelItems(individual.get_overview_tree())

                # Add checkboxes for individuals in individual panel

            elif isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                self.ui.stackedWidget.setCurrentIndex(3)
                session = self.ui.tree_widget.selectedItems()[0]
                self.ui.session_name.setText(session.text(0))
                self.ui.session_description.setText(session.description)

                if session.get_setting('global'):
                    self.ui.global_normalization_session_btn.setChecked(True)
                else:
                    self.ui.local_normalization_session_btn.setChecked(True)
                if session.get_setting('percent'):
                    self.ui.percent_session_btn.setChecked(True)
                else:
                    self.ui.subtract_session_btn.setChecked(True)
            else:
                self.ui.stackedWidget.setCurrentIndex(0)
                group = self.ui.tree_widget.selectedItems()[0]
                self.ui.group_name.setText(group.text(0))
                self.ui.group_description.setText(group.description)

                if group.get_setting('global'):
                    self.ui.global_normalization_group_btn.setChecked(True)
                else:
                    self.ui.local_normalization_group_btn.setChecked(True)
                if group.get_setting('percent'):
                    self.ui.percent_group_btn.setChecked(True)
                else:
                    self.ui.subtract_group_btn.setChecked(True)

                # Add overview tree in group panel
                self.ui.individual_overview_tree.clear()
                self.ui.individual_overview_tree.addTopLevelItems(group.get_overview_tree())

                # Add checkboxes for individuals in group panel

    def update_text(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                individual = self.ui.tree_widget.selectedItems()[0]

                if individual.brain:
                    self.ui.session_epi_label.setText('EPI-images chosen: ' + individual.brain.path.split('/')[-1])
                else:
                    self.ui.session_epi_label.setText('No EPI-images chosen')

                if individual.anatomy:
                    self.ui.session_anatomy_label.setText('Anatomy chosen: ' + individual.anatomy.path.split('/')[-1])
                else:
                    self.ui.session_anatomy_label.setText('No anatomy chosen')

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

    def description_changed(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
                text = self.ui.individual_description.toPlainText()
            elif isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                text = self.ui.session_description.toPlainText()
            else:
                text = self.ui.group_description.toPlainText()

            self.ui.tree_widget.selectedItems()[0].description = text

    def plot_settings_changed(self):
        if self.ui.tree_widget.selectedItems():
            if isinstance(self.ui.tree_widget.selectedItems()[0], IndividualTreeItem):
                individual = self.ui.tree_widget.selectedItems()[0]
                individual.plot_settings['global'] = self.ui.global_normalization_individual_btn.isChecked()
                individual.plot_settings['percent'] = self.ui.percent_individual_btn.isChecked()
            elif isinstance(self.ui.tree_widget.selectedItems()[0], SessionTreeItem):
                session = self.ui.tree_widget.selectedItems()[0]
                session.plot_settings['global'] = self.ui.global_normalization_session_btn.isChecked()
                session.plot_settings['percent'] = self.ui.percent_session_btn.isChecked()
            else:
                group = self.ui.tree_widget.selectedItems()[0]
                group.plot_settings['global'] = self.ui.global_normalization_group_btn.isChecked()
                group.plot_settings['percent'] = self.ui.percent_group_btn.isChecked()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())
