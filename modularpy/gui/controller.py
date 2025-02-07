import numpy as np
import os
import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTableWidget,
    QHeaderView,
    QFileDialog,
    QTableWidgetItem,
    QInputDialog,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from modularpy.config import ExperimentConfig


class ConfigController(QWidget):
    """AcquisitionEngine object for the napari-modularpy plugin.
    The object connects to the Micro-Manager Core object instances and the Config object.

    The ConfigController widget is a QWidget that allows the user to select a save directory,
    load a JSON configuration file, and edit the configuration parameters in a table.
    
    The ConfigController widget emits signals to notify other widgets when the configuration is updated
        
    """
    # ==================================== Signals ===================================== #
    configUpdated = pyqtSignal(object)
    # ------------------------------------------------------------------------------------- #
    
    def __init__(self, cfg: 'ExperimentConfig'):
        super().__init__()
        self.config = cfg
        # Create main layout
        self.layout = QVBoxLayout(self)
        self.setFixedWidth(500)

        # ==================================== GUI Widgets ===================================== #
        # 1. Selecting an Experimental directory
        self.directory_label = QLabel('Select Directory:')
        self.directory_line_edit = QLineEdit()
        self.directory_line_edit.setReadOnly(True)
        self.directory_button = QPushButton('Browse')

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.directory_label)
        dir_layout.addWidget(self.directory_line_edit)
        dir_layout.addWidget(self.directory_button)

        self.layout.addLayout(dir_layout)

        # 2. Dropdown Widget for JSON configuration files
        self.json_dropdown_label = QLabel('Select JSON Config:')
        self.json_dropdown = QComboBox()

        json_layout = QHBoxLayout()
        json_layout.addWidget(self.json_dropdown_label)
        json_layout.addWidget(self.json_dropdown)

        self.layout.addLayout(json_layout)

        # 3. Table widget to display the configuration parameters loaded from the JSON
        self.layout.addWidget(QLabel('Experiment Config:'))
        self.config_table = QTableWidget()
        self.config_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.config_table)
        
        # 4. Add Note button to add a note to the configuration
        self.add_note_button = QPushButton("Add Note")
        self.layout.addWidget(self.add_note_button)
        # ------------------------------------------------------------------------------------- #

        # ============ Callback connections between widget values and functions ================ #
        self.directory_button.clicked.connect(self._select_directory)
        self.json_dropdown.currentIndexChanged.connect(self._update_config)
        self.config_table.cellChanged.connect(self._on_table_edit)
        self.add_note_button.clicked.connect(self.add_note)
        # ------------------------------------------------------------------------------------- #

        # Initialize the config table
        self._refresh_config_table()

    # ============================== Public Class Methods ============================================ #
    
    def add_note(self):
        """ Open a dialog to get a note from the user and save it to the ExperimentConfig.notes list.
        """
        text, ok = QInputDialog.getText(self, 'Add Note', 'Enter your note:')
        if ok and text:
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note_with_timestamp = f"{time}: {text}"
            self.config.notes.append(note_with_timestamp)
            print("Note added to configuration.")
    #-----------------------------------------------------------------------------------------------#
    
    #============================== Private Class Methods ==========================================#

    def _select_directory(self):
        """ Open a dialog to select a directory and update the GUI accordingly.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if directory:
            self.directory_line_edit.setText(directory)
            self._get_json_file_choices(directory)

    def _get_json_file_choices(self, path):
        """ Return a list of JSON files in the current directory.
        """
        import glob
        self.config.save_dir = path
        try:
            json_files = glob.glob(os.path.join(path, "*.json"))
            self.json_dropdown.clear()
            self.json_dropdown.addItems(json_files)
        except Exception as e:
            print(f"Error getting JSON files from directory: {path}\n{e}")

    def _update_config(self, index):
        """ Update the experiment configuration from a new JSON file.
        """
        json_path_input = self.json_dropdown.currentText()

        if json_path_input and os.path.isfile(json_path_input):
            try:
                self.config.load_parameters(json_path_input)
                # Refresh the GUI table
                # FIXME: This implicitly assumes mmc1 is the Dhyana core with the arduino-switch device
                self._refresh_config_table()
            except Exception as e:
                print(f"Trouble updating ExperimentConfig from AcquisitionEngine:\n{json_path_input}\nConfiguration not updated.")
                print(e) 

    def _on_table_edit(self, row, column):
        """ Update the configuration parameters when the table is edited.
        """
        try:
            if self.config_table.item(row, 0) and self.config_table.item(row, 1):
                key = self.config_table.item(row, 0).text()
                value = self.config_table.item(row, 1).text()
                self.config.update_parameter(key, value)
            self.configUpdated.emit(self.config) # EMIT SIGNAL TO LISTENERS                
        except Exception as e:
            print(f"Error updating config from table: check AcquisitionEngine._on_table_edit()\n{e}")

    def _refresh_config_table(self):
        """ Refresh the configuration table to reflect current parameters.
        """
        df = self.config.dataframe
        self.config_table.blockSignals(True)  # Prevent signals while updating the table
        self.config_table.clear()
        self.config_table.setRowCount(len(df))
        self.config_table.setColumnCount(len(df.columns))
        self.config_table.setHorizontalHeaderLabels(df.columns.tolist())

        for i, row in df.iterrows():
            for j, (col_name, value) in enumerate(row.items()):
                item = QTableWidgetItem(str(value))
                self.config_table.setItem(i, j, item)

        self.config_table.blockSignals(False)  # Re-enable signals

        self.configUpdated.emit(self.config) # EMIT SIGNAL TO LISTENERS
    # ----------------------------------------------------------------------------------------------- #




