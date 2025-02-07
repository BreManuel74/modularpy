import click
from PyQt6.QtWidgets import QApplication

from modularpy.gui.maingui import MainWindow
from modularpy.config import ExperimentConfig


# Functions called by the CLI
# =============================================================================

def launch_modularpy(params):
    """Launch the modularpy acquisition interface."""
    print('Launching modularpy acquisition interface...')
    app = QApplication([]) # create the QT application object
    config = ExperimentConfig(params) # create the ExperimentConfig object
    modularpy = MainWindow(config) # create the MainWindow object, passing the ExperimentConfig object
    modularpy.show() # show the MainWindow object
    app.exec() # start the QT event loop

# -----------------------------------------------------------------------------


# CLI
# =============================================================================

@click.group()
def cli():
    """mesofields Command Line Interface"""

@cli.command()
@click.option('--params', default='hardware.yaml', help='Path to the config file')
def launch(params):
    launch_modularpy(params)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
