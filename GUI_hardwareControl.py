import os
import sys
import pandas as pd
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QFrame, QMessageBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel)
from GUI_commonWidgets import QHLine
from GUI_plotCanvas import PlotCanvas
import logging
from lib.thorlabs_stage import Thorlabs_Stage
from lib.stellarnet_spectrometer import Stellarnet_Spectrometer

class HardwareTop(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        btn_width = 80

        self.hardware = HardwareControl()
        label_hardware = QLabel("Hardware Setup and References")
        btn_hardware_control = QPushButton("References")
        btn_hardware_control.clicked.connect(self.view_hardware)
        btn_hardware_control.setFixedWidth(btn_width)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(label_hardware)
        hbox.addWidget(btn_hardware_control)

        hbox_outer = QHBoxLayout()
        hbox_outer.addStretch(1)
        hbox_outer.addLayout(hbox, stretch=10)
        hbox_outer.addStretch(1)

        self.setLayout(hbox_outer)


    def view_hardware(self):
        self.hardware.resize(640, 400)
        self.hardware.show()

class StageControl(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        btn_width = 80

        label = QLabel("Thorlabs Stage")
        label.setStyleSheet("font-weight: bold")

        self.stage = Thorlabs_Stage()
        self.stage._calculate_rotation()

        label_sp = QLabel("Serial Port")
        self.combo_sp = QComboBox()

        self.btn_scan= QPushButton("Scan")
        self.btn_scan.clicked.connect(self.scan_serial_ports)
        self.btn_scan.setFixedWidth(btn_width)

        self.btn_connect= QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect)
        self.btn_connect.setFixedWidth(btn_width)

        self.btn_disconnect= QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self.stage.disconnect_serial)
        self.btn_disconnect.setFixedWidth(btn_width)

        hbox_serial = QHBoxLayout()
        hbox_serial.addStretch(3)
        hbox_serial.addWidget(label_sp)
        hbox_serial.addWidget(self.combo_sp, 1)
        hbox_serial.addWidget(self.btn_scan)
        hbox_serial.addWidget(self.btn_connect)
        hbox_serial.addWidget(self.btn_disconnect)

        self.btn_set_ref_a= QPushButton("Set")
        self.btn_set_ref_a.clicked.connect(self.set_reference_a)
        self.btn_set_ref_a.setFixedWidth(btn_width)

        self.btn_set_ref_b= QPushButton("Set")
        self.btn_set_ref_b.clicked.connect(self.set_reference_b)
        self.btn_set_ref_b.setFixedWidth(btn_width)

        self.btn_refresh= QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_position)
        self.btn_refresh.setFixedWidth(btn_width)

        self.btn_enable= QPushButton("Enable")
        self.btn_enable.clicked.connect(self.stage.enable)
        self.btn_enable.setFixedWidth(btn_width)

        self.btn_disable= QPushButton("Disable")
        self.btn_disable.clicked.connect(self.stage.disable)
        self.btn_disable.setFixedWidth(btn_width)

        self.btn_home= QPushButton("Home")
        self.btn_home.clicked.connect(self.stage.home)
        self.btn_home.setFixedWidth(btn_width)

        self.btn_move= QPushButton("Move")
        self.btn_move.clicked.connect(self.move)
        self.btn_move.setFixedWidth(btn_width)
        self.move_x = QLineEdit('0')
        self.move_y = QLineEdit('0')

        hbox_enable = QHBoxLayout()
        hbox_enable.addStretch(1)
        hbox_enable.addWidget(QLabel("Motor Channels"))
        hbox_enable.addWidget(self.btn_home)
        hbox_enable.addWidget(self.btn_enable)
        hbox_enable.addWidget(self.btn_disable)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0,1)
        grid.setColumnStretch(1,5)
        grid.setColumnStretch(2,5)
        grid.setColumnStretch(3,5)
        grid.setColumnStretch(4,5)

        row_title = 0
        grid.addWidget(QLabel('X (mm)'), row_title, 2)
        grid.addWidget(QLabel('Y (mm)'), row_title, 3)

        row_pos = 1
        grid.addWidget(QLabel('Current Position'), row_pos, 1)
        self.label_pos_x = QLabel(str(self.stage.pos_x))
        self.label_pos_y = QLabel(str(self.stage.pos_y))
        grid.addWidget(self.label_pos_x, row_pos, 2)
        grid.addWidget(self.label_pos_y, row_pos, 3)
        grid.addWidget(self.btn_refresh, row_pos, 4)

        row_ref_a = 2
        grid.addWidget(QLabel('Reference A'), row_ref_a, 1)
        self.label_ref_ax = QLabel(str(self.stage.ref_ax))
        self.label_ref_ay = QLabel(str(self.stage.ref_ay))
        grid.addWidget(self.label_ref_ax, row_ref_a, 2)
        grid.addWidget(self.label_ref_ay, row_ref_a, 3)
        grid.addWidget(self.btn_set_ref_a, row_ref_a, 4)

        row_ref_b = 3
        grid.addWidget(QLabel('Reference B'), row_ref_b, 1)
        self.label_ref_bx = QLabel(str(self.stage.ref_bx))
        self.label_ref_by = QLabel(str(self.stage.ref_by))
        grid.addWidget(self.label_ref_bx, row_ref_b, 2)
        grid.addWidget(self.label_ref_by, row_ref_b, 3)
        grid.addWidget(self.btn_set_ref_b, row_ref_b, 4)

        row_move = 4
        grid.addWidget(QLabel('Move vs Ref A'), row_move, 1)
        grid.addWidget(self.move_x, row_move, 2)
        grid.addWidget(self.move_y, row_move, 3)
        grid.addWidget(self.btn_move, row_move, 4)

        row_rotation = 5
        grid.addWidget(QLabel('Rotation'), row_rotation, 1)
        logging.debug(self.stage.slide_rotation)
        self.label_rotation = QLabel(str(self.stage.slide_rotation))
        grid.addWidget(self.label_rotation, row_rotation, 2) 
        grid.addWidget(QLabel('degrees'), row_rotation, 3)       


        hbox_grid = QHBoxLayout()
        hbox_grid.addStretch()
        hbox_grid.addLayout(grid)

        vbox = QVBoxLayout()
        vbox.addWidget(QHLine())
        vbox.addWidget(label)
        vbox.addLayout(hbox_serial)
        vbox.addLayout(hbox_enable)
        vbox.addLayout(hbox_grid)
        self.setLayout(vbox)

    def scan_serial_ports(self):
        ports = self.stage.scan_serial_ports()
        self.combo_sp.clear()
        for port, desc, hwid in sorted(ports):
            self.combo_sp.addItem(port)
            logging.debug(f'added {port}')

    def connect(self):
        self.stage.connect_serial(serial_port=self.combo_sp.currentText())

    def set_reference_a(self):
        self.stage.set_position_reference_a()
        self.label_ref_ax.setText(str(self.stage.ref_ax))
        self.label_ref_ay.setText(str(self.stage.ref_ay))
        self.label_rotation.setText(str(self.stage.slide_rotation))

    def set_reference_b(self):
        self.stage.set_position_reference_b()
        self.label_ref_bx.setText(str(self.stage.ref_bx))
        self.label_ref_by.setText(str(self.stage.ref_by))
        self.label_rotation.setText(str(self.stage.slide_rotation))

    def refresh_position(self):
        self.stage.get_position()
        self.label_pos_x.setText(str(self.stage.pos_x))
        self.label_pos_y.setText(str(self.stage.pos_y))

    def move(self):
        self.stage.move_vs_ref(float(self.move_x.text()), float(self.move_y.text()))

class SpectrometerControl(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        btn_width = 80

        label = QLabel("Stellarnet Spectrometer")
        label.setStyleSheet("font-weight: bold")

        self.spec = Stellarnet_Spectrometer()

        self.btn_connect= QPushButton("Connect")
        self.btn_connect.clicked.connect(self.spec.connect)
        self.btn_connect.setFixedWidth(btn_width)

        self.btn_light_ref= QPushButton("Capture")
        self.btn_light_ref.clicked.connect(self.capture_light_ref)
        self.btn_light_ref.setFixedWidth(btn_width)
        
        self.btn_dark_ref= QPushButton("Capture")
        self.btn_dark_ref.clicked.connect(self.capture_dark_ref)
        self.btn_dark_ref.setFixedWidth(btn_width)

        self.btn_capture_spectrum = QPushButton("Capture")
        self.btn_capture_spectrum.clicked.connect(self.capture_spectrum)
        self.btn_capture_spectrum.setFixedWidth(btn_width)

        self.btn_view_spectrum = QPushButton("View")
        self.btn_view_spectrum.clicked.connect(self.plot)
        self.btn_view_spectrum.setFixedWidth(btn_width)

        self.plotcanvas = PlotCanvas()

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0,5)
        grid.setColumnStretch(1,5)
        # grid.setColumnStretch(2,5)

        grid.addWidget(QLabel('USB'), 0, 0)
        grid.addWidget(self.btn_connect, 0, 1)

        grid.addWidget(QLabel('Light Reference'), 1, 0)
        grid.addWidget(self.btn_light_ref, 1, 1)
        grid.addWidget(QLabel('Dark Reference'), 2, 0)
        grid.addWidget(self.btn_dark_ref, 2, 1)

        grid.addWidget(QLabel('Capture Spectrum'), 3, 0)
        grid.addWidget(self.btn_capture_spectrum, 3, 1)
        grid.addWidget(self.btn_view_spectrum, 4, 1)


        self.label_scans_to_avg = QLabel(str(self.spec.scans_to_avg))
        self.label_int_time = QLabel(str(self.spec.int_time))
        self.label_x_timing = QLabel(str(self.spec.x_timing))
        self.label_x_smooth = QLabel(str(self.spec.x_smooth))
        self.label_wl_min = QLabel(str(self.spec.wl_min))
        self.label_wl_max = QLabel(str(self.spec.wl_max))

        row_info = 5
        grid.addWidget(QLabel('scans_to_avg'), row_info, 0)
        grid.addWidget(self.label_scans_to_avg, row_info, 1)
        grid.addWidget(QLabel('int_time'), row_info+1, 0)
        grid.addWidget(self.label_int_time, row_info+1, 1)
        grid.addWidget(QLabel('x_timing'), row_info+2, 0)
        grid.addWidget(self.label_x_timing, row_info+2, 1)
        grid.addWidget(QLabel('x_smooth'), row_info+3, 0)
        grid.addWidget(self.label_x_smooth, row_info+3, 1)
        grid.addWidget(QLabel('wl_min'), row_info+4, 0)
        grid.addWidget(self.label_wl_min, row_info+4, 1)
        grid.addWidget(QLabel('wl_max'), row_info+5, 0)
        grid.addWidget(self.label_wl_max, row_info+5, 1)

        hbox_grid = QHBoxLayout()
        hbox_grid.addStretch()
        hbox_grid.addLayout(grid)

        
        vbox = QVBoxLayout()
        vbox.addWidget(QHLine())
        vbox.addWidget(label)
        vbox.addLayout(hbox_grid)
        self.setLayout(vbox)

    def capture_light_ref(self):
        self.spec.capture_light_reference()

    def capture_dark_ref(self):
        self.spec.capture_dark_reference()

    def capture_spectrum(self):
        self.spec.get_spectrum()

    def setup_changed(self, setup):
        logging.debug(f"Spectrometer Control : got new setup")
        self.spec.int_time = setup['input_config']['integration_time']
        self.spec.scans_to_avg = setup['input_config']['scans_to_avg']
        self.spec.x_timing = setup['input_config']['x_timing']
        self.spec.x_smooth = setup['input_config']['x_smooth']
        self.spec.wl_min = setup['input_config']['wavelength_range'][0]
        self.spec.wl_max = setup['input_config']['wavelength_range'][1]

    def plot(self):
        # df = self.spec.last_capture
        df =  pd.merge(self.spec.light_reference, self.spec.dark_reference, how='outer', on='wavelength')
        df =  pd.merge(self.spec.last_capture_raw, df, how='outer', on='wavelength')
        self.plotcanvas.set_data(df)

class HardwareControl(QWidget):

    # new_setup = Signal(dict)

    def __init__(self):
        QWidget.__init__(self)

        btn_width = 80

        label = QLabel("Hardware Setup")
        label.setStyleSheet("font-weight: bold")

        self.spectrometerControl=SpectrometerControl()
        self.stageControl = StageControl()

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(self.stageControl)
        vbox.addWidget(self.spectrometerControl)

        hbox_margins = QHBoxLayout()
        hbox_margins.addStretch(1)
        hbox_margins.addLayout(vbox, 10)
        hbox_margins.addStretch(1)

        self.setLayout(hbox_margins)

    def measure(self, setup, row):
        # try:
        element = row['element']
        x_pos = setup['sensor']['layout']['map'][element][0]
        y_pos = setup['sensor']['layout']['map'][element][1]

        logging.info(f"\n\nMeasuring Element {element}")
        logging.info(f'{x_pos=} {y_pos=}')
            
        self.stageControl.stage.move_vs_ref(x_pos, y_pos)
        df = self.spectrometerControl.spec.get_spectrum()

        return df

if __name__ == "__main__":

    app = QApplication(sys.argv)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    window = QMainWindow()
    centralwidget = QWidget()
    centralwidget.setObjectName(u"centralwidget")
    window.setCentralWidget(centralwidget)

    # metaBrowse = MetaBrowse()
    hardwareControl = HardwareControl()
    hardwareTop = HardwareTop()
    
    vbox = QVBoxLayout()
    vbox.addWidget(hardwareTop)
    vbox.addWidget(hardwareControl)
    vbox.addStretch()
    centralwidget.setLayout(vbox)
    window.resize(1024, 400)
    window.show()
    sys.exit(app.exec())
