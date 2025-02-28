from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import pyqtgraph as pg

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from modularpy.io import SerialWorker
    from modularpy.config import ExperimentConfig

class EncoderWidget(QWidget):
    def __init__(self, cfg: 'ExperimentConfig'):
        super().__init__()
        self.config = cfg
        self.encoder: SerialWorker = cfg.hardware.encoder
        self.init_ui()
        self.init_data()
        self.setFixedHeight(300)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Status label to show connection status
        self.status_label = QLabel("Click 'Start Live View' to begin.")
        self.info_label = QLabel(f'Viewing data from {self.encoder} at Port: {self.encoder.serial_port} | Baud: {self.encoder.baud_rate} | Resistor: {self.encoder.resistor}')
        self.start_button = QPushButton("Start Live View")
        self.start_button.setCheckable(True)
        self.plot_widget = pg.PlotWidget()

        self.start_button.clicked.connect(self.toggle_serial_thread)
        self.start_button.setEnabled(True)

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.plot_widget)
        self.setLayout(self.layout)

        self.plot_widget.setTitle('Lick Detection')
        self.plot_widget.setLabel('left', 'Change in Capacitance')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.capacitance_curve = self.plot_widget.plot(pen='y')

        # Limit the range of the y-axis to +/- 2
        self.plot_widget.setYRange(-1, 1000)
        self.plot_widget.showGrid(x=True, y=True)
        
        #================================= SerialWorker Signals ================================#
        # self.encoder.serialStreamStarted.connect(self.start_live_view)
        # self.encoder.serialDataReceived.connect(self.process_data)
        # self.encoder.serialStreamStopped.connect(self.stop_timer)
        self.encoder.serialCapacitanceUpdated.connect(self.receive_lick_data) 
        #========================================================================================#

    def init_data(self):
        self.times = []
        self.licks = []
        self.start_time = None
        self.timer = None
        self.previous_time = 0

    def toggle_serial_thread(self):
        if self.start_button.isChecked():
            self.encoder.start()
            self.status_label.setText("Serial thread started.")
        else:
            self.stop_serial_thread()
            self.status_label.setText("Serial thread stopped.")

    def stop_serial_thread(self):
        if self.encoder is not None:
            self.encoder.stop()

    def receive_lick_data(self, time, lick):
        self.times.append(time)
        self.licks.append(lick)
        # Keep only the last 100 data points
        self.times = self.times[-100:]
        self.licks = self.licks[-100:]
        self.update_plot()


    def update_plot(self):
        try:
            if self.times and self.licks:
                # Update the curve with the last 100 data points
                self.capacitance_curve.setData(self.times, self.licks)
                # Adjust x-axis range to show the recent data points
                self.plot_widget.setXRange(self.times[0], self.times[-1], padding=0)
            else:
                self.plot_widget.clear()
                self.plot_widget.setTitle('No data received.')
        except Exception as e:
            print(f"Exception in update_plot: {e}")
