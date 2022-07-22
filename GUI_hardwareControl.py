import os
import sys
import pandas as pd
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QFrame, QMessageBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
from lib.thorlabs_stage import Thorlabs_Stage
from lib.stellarnet_spectrometer import Stellarnet_Spectrometer

class HardwareControl(QWidget):

    # new_setup = Signal(dict)

    def __init__(self):
        QWidget.__init__(self)

        btn_width = 80

        self.stage = Thorlabs_Stage()
        self.spec = Stellarnet_Spectrometer()

        label_hw = QLabel("Hardware Setup")
        label_hw.setStyleSheet("font-weight: bold")

        label_sp = QLabel("Serial Port")
        self.combo_sp = QComboBox()
        
        self.btn_scan= QPushButton("Scan")
        self.btn_scan.clicked.connect(self.scan_serial_ports)
        self.btn_scan.setFixedWidth(btn_width)

        self.btn_connect= QPushButton("Connect")
        # self.btn_connect.clicked.connect(self.connect_hw)
        self.btn_connect.setFixedWidth(btn_width)

        self.btn_disconnect= QPushButton("Disconnect")
        # self.btn_disconnect.clicked.connect(self.hw.disable())
        self.btn_disconnect.setFixedWidth(btn_width)

        hbox_hw_connect = QHBoxLayout()
        hbox_hw_connect.addStretch(3)
        hbox_hw_connect.addWidget(label_sp)
        hbox_hw_connect.addWidget(self.combo_sp, 1)
        hbox_hw_connect.addWidget(self.btn_scan)
        hbox_hw_connect.addWidget(self.btn_connect)
        hbox_hw_connect.addWidget(self.btn_disconnect)

        self.label_reference = QLabel("Reference 0,0")
        self.label_position = QLabel("Position 0,0")


        self.btn_reference= QPushButton("Set")
        # self.btn_reference.clicked.connect(self.set_reference)
        self.btn_reference.setFixedWidth(btn_width)

        self.btn_position= QPushButton("Refresh")
        # self.btn_position.clicked.connect(self.refresh_position)
        self.btn_position.setFixedWidth(btn_width)

        self.btn_home= QPushButton("Home")
        # self.btn_home.clicked.connect(self.hw.home_stage)
        self.btn_home.setFixedWidth(btn_width)

        hbox_hw_ref = QHBoxLayout()
        hbox_hw_ref.addStretch(3)
        hbox_hw_ref.addWidget(self.label_reference)
        hbox_hw_ref.addWidget(self.btn_reference)
        hbox_hw_ref.addWidget(self.label_position)
        hbox_hw_ref.addWidget(self.btn_position)
        hbox_hw_ref.addWidget(self.btn_home)

        vbox_hardware = QVBoxLayout()
        vbox_hardware.addLayout(hbox_hw_connect)
        vbox_hardware.addLayout(hbox_hw_ref)

        hbox_hardware_outer = QHBoxLayout()
        hbox_hardware_outer.addStretch(1)
        hbox_hardware_outer.addLayout(vbox_hardware, 10)
        hbox_hardware_outer.addStretch(1)

        self.setLayout(hbox_hardware_outer)

    def scan_serial_ports(self):
        ports = self.stage.scan_serial_ports()
        self.combo_sp.clear()
        for port, desc, hwid in sorted(ports):
            self.combo_sp.addItem(port)
            logging.debug(f'added {port}')

    def connect_hw(self):
        self.stage.connect_serial(serial_port=self.combo_sp.currentText())

    def set_reference(self):
        self.stage.store_position_reference()
        self.label_reference.setText(f'Reference {self.stage.ref_x},{self.stage.ref_y}')

    def refresh_position(self):
        self.stage.get_position()
        self.label_position.setText(f'Position {self.stage.pos_x},{self.stage.pos_y}')



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
    
    vbox = QVBoxLayout()
    vbox.addWidget(hardwareControl)
    vbox.addStretch()
    centralwidget.setLayout(vbox)
    window.resize(1024, 400)
    window.show()
    sys.exit(app.exec())
