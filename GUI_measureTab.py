
import sys
import os
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget, QCheckBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox)
import logging
from GUI_commonWidgets import QHLine
from GUI_tableView import MetaTable
import lib.csv_helpers as csv
from lib.stellarnet_thorlabs import Stellarnet_Thorlabs_Hardware


class MeasureTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName(u"MeasureTab")

        btn_width = 80

        self.hw = Stellarnet_Thorlabs_Hardware()

        label_info = QLabel("Capture a series of measurements\n")

        tooltip_info = ("Generates a Run List based on the parameters in setup input_config\n"
            +"i.e. Adds a row for each permutation of 'fluids' and 'elements'\n\n"
            +"The correct measurement function must be selected for the spectrometer\n\n"
            +"Output data is stored in the path/subdirs defined in setup.json\n"
            +"Files and metadata can be optionally merged with existing data"
        )
        label_info.setToolTip(tooltip_info)

        self.run_df = None

        # Run_df
        label_run_df = QLabel("Generate Run List")
        label_run_df.setStyleSheet("font-weight: bold")
        label_run_idea = QLabel("[Could add import/export options here to allow manual editing?]")

        btn_generate = QPushButton("Generate")
        btn_generate.clicked.connect(self.generate_run_df)
        btn_generate.setFixedWidth(btn_width)

        btn_preview_run_df= QPushButton("Preview")
        btn_preview_run_df.clicked.connect(self.preview_run_df)
        btn_preview_run_df.setFixedWidth(btn_width)

        hbox_run_df_btns = QHBoxLayout()
        hbox_run_df_btns.addWidget(label_run_idea)
        hbox_run_df_btns.addStretch()
        hbox_run_df_btns.addWidget(btn_generate)
        hbox_run_df_btns.addWidget(btn_preview_run_df)

        hbox_run_df = QHBoxLayout()
        # hbox_run_df.addWidget(label_run_df)
        hbox_run_df.addStretch(1)
        hbox_run_df.addLayout(hbox_run_df_btns, stretch=10)
        hbox_run_df.addStretch(1)

        # Hardware
        label_hw = QLabel("Hardware Setup")
        label_hw.setStyleSheet("font-weight: bold")

        label_sp = QLabel("Serial Port")
        self.combo_sp = QComboBox()
        
        self.btn_scan= QPushButton("Scan")
        self.btn_scan.clicked.connect(self.scan_serial_ports)
        self.btn_scan.setFixedWidth(btn_width)

        self.btn_connect= QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_hw)
        self.btn_connect.setFixedWidth(btn_width)

        hbox_hardware = QHBoxLayout()
        hbox_hardware.addStretch(3)
        hbox_hardware.addWidget(label_sp)
        hbox_hardware.addWidget(self.combo_sp, 1)
        hbox_hardware.addWidget(self.btn_scan)
        hbox_hardware.addWidget(self.btn_connect)

        hbox_hardware_outer = QHBoxLayout()
        hbox_hardware_outer.addStretch(1)
        hbox_hardware_outer.addLayout(hbox_hardware, 10)
        hbox_hardware_outer.addStretch(1)
        

        # Output Path
        label_output = QLabel("Output Directory Structure:")
        label_output.setStyleSheet("font-weight: bold")

        self.tbox_outpath = QLineEdit()
        self.tbox_outpath.setReadOnly(True)

        # Merge
        label_merge = QLabel('Merge into existing files')
        self.cbox_merge = QCheckBox()
        self.cbox_merge.setChecked(True)

        hbox_merge = QHBoxLayout()
        hbox_merge.addWidget(self.cbox_merge)
        hbox_merge.addWidget(label_merge)
        hbox_merge.addStretch()

        btn_run= QPushButton("Run")
        btn_run.clicked.connect(self.run_measurements)
        btn_run.setFixedWidth(btn_width)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(btn_run)

        vbox_output = QVBoxLayout()
        vbox_output.addWidget(self.tbox_outpath)
        vbox_output.addLayout(hbox_merge)
        vbox_output.addLayout(hbox_run)

        hbox_output = QHBoxLayout()
        hbox_output.addStretch(1)
        hbox_output.addLayout(vbox_output, stretch=10)
        hbox_output.addStretch(1)

        # Overall Layout
        vbox = QVBoxLayout()
        vbox.addWidget(label_info)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_run_df)
        # vbox.addWidget(label_run_idea)
        vbox.addLayout(hbox_run_df)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_hw)
        vbox.addLayout(hbox_hardware_outer)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_output)
        vbox.addLayout(hbox_output)
        # vbox.addLayout(hbox_run)
        vbox.addStretch()

        self.setLayout(vbox)

    def generate_run_df(self):
        self.run_df = csv.generate_run_df(self.setup)
        print(self.run_df)

    def preview_run_df(self):
        if self.run_df is None:
            self.generate_run_df()
        self.runTable = MetaTable(self.run_df, "Run List DataFrame")
        self.runTable.show()

    def scan_serial_ports(self):
        ports = self.hw.scan_serial_ports()
        self.combo_sp.clear()
        for port, desc, hwid in sorted(ports):
            self.combo_sp.addItem(port)

    def connect_hw(self):
        self.hw.connect(setup=self.setup, serial_port=self.combo_sp.currentText())


    def run_measurements(self):
        if self.run_df is None:
            self.generate_run_df()

        for f in self.measure_funcs:
            if f.__name__ == self.combo_mf.currentText():
                mf = f

        logging.info(f'measure_function = {mf.__name__}')

        merge = self.cbox_merge.isChecked()        
        csv.run_measure(self.setup, self.run_df, measure_func=self.hw.measure, merge=merge)

    def setup_changed(self, setup):
        logging.debug(f"measureTab: got new setup {setup['name']}")
        self.setup = setup

        # reconnect to hardware
        if self.hw.port:
            self.connect_hw()

        # Update the output path displayed
        outpath = os.path.abspath(setup['datadir'])
        for dir in setup['subdirs']:
            outpath = os.path.join(outpath, f"<{dir}>")

        filename = '-'.join(f'<{p}>' for p in setup['primary_metadata'])+".txt"
        outpath = os.path.join(outpath, filename)

        self.tbox_outpath.setText(outpath)

if __name__ == "__main__":



    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = MeasureTab()
    setup = csv.get_default_setup()
    window.setup_changed(setup)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())

