import os
import sys

# Necessary modules for the IPython console
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, 
    QWidget, 
    QHBoxLayout, 
    QVBoxLayout,
)

from modularpy.gui.controller import ConfigController
from modularpy.gui.speedplotter import EncoderWidget
from modularpy.config import ExperimentConfig

class MainWindow(QMainWindow):
    def __init__(self, cfg: ExperimentConfig):
        super().__init__()

        self.config: ExperimentConfig = cfg

        #======================== Window Settings ===========================#
        self.setWindowTitle("ModularPy Acquisition Interface")
        window_icon = QIcon(os.path.join(os.path.dirname(__file__), "modularpy_icon.png"))
        self.setWindowIcon(window_icon)
        self.setMinimumSize(800, 600)
        #--------------------------------------------------------------------#

        #============================== Widgets =============================#
        self.config_controller = ConfigController(self.config)
        self.encoder_widget = EncoderWidget(self.config)
        self.initialize_console(cfg) # Initialize the IPython console
        #--------------------------------------------------------------------#

        #============================== Layout ==============================#
        if sys.platform == "darwin":
            self.menuBar().setNativeMenuBar(False)
        toggle_console_action = self.menuBar().addAction("Toggle Console")

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        mda_layout = QVBoxLayout()
        self.setCentralWidget(central_widget)

        main_layout.addLayout(mda_layout)
        main_layout.addWidget(self.config_controller)
        mda_layout.addWidget(self.encoder_widget)
        #--------------------------------------------------------------------#

        #============================== Signals =============================#
        toggle_console_action.triggered.connect(self.toggle_console)
        self.config_controller.configUpdated.connect(self._update_state_config)
        #--------------------------------------------------------------------#


    #============================== Methods =================================#    
    def toggle_console(self):
        """Show or hide the IPython console.
        """
        if self.console_widget and self.console_widget.isVisible():
            self.console_widget.hide()
        else:
            if not self.console_widget:
                self.initialize_console()
            else:
                self.console_widget.show()
                    
    def initialize_console(self, cfg: ExperimentConfig):
        """Initialize the IPython console and embed it into the application.
        """
        # Create an in-process kernel
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel
        self.kernel.gui = 'qt'

        # Create a kernel client and start channels
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

        # Create the console widget
        self.console_widget = RichJupyterWidget()
        self.console_widget.kernel_manager = self.kernel_manager
        self.console_widget.kernel_client = self.kernel_client

        # Expose variables to the console's namespace
        self.kernel.shell.push({
            'self': self,
            'config': cfg,
            # Optional, so you can use 'self' directly in the console
        })
    #----------------------------------------------------------------------------#

    #============================== Private Methods =============================#

    def _update_state_config(self, config):
        self.config: ExperimentConfig = config
        

