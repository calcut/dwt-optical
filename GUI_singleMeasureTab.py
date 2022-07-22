
from math import comb
import sys
import os
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget, QCheckBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox, QGridLayout)
import logging
from GUI_commonWidgets import QHLine
from GUI_tableView import MetaTable
import lib.csv_helpers as csv
from lib.stellarnet_thorlabs import Stellarnet_Thorlabs_Hardware



class SingleMeasureTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName(u"SingleMeasureTab")

        btn_width = 80

        self.hw = Stellarnet_Thorlabs_Hardware()

        # List of functions to interface with spectrometer APIs
        # self.measure_funcs = [csv.dummy_measurement, self.hw.measure]

        label_info = QLabel("Capture a single measurement")

        tooltip_info = ("Generates a Run List based on setup.json\n"
            +"i.e. Adds a row for each permutation of 'fluids' and 'elements'\n\n"
            +"The correct measurement function must be selected for the spectrometer\n\n"
            +"Output data is stored in the path/subdirs defined in setup.json\n"
            +"Files and metadata can be optionally merged with existing data"
        )
        label_info.setToolTip(tooltip_info)


        # Metadata
        label_metadata = QLabel("Measurement Metadata")
        label_metadata.setStyleSheet("font-weight: bold")

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)

        self.tbox_instrument = QLineEdit()
        self.tbox_instrument.setReadOnly(True)
        grid.addWidget(QLabel("Instrument"), 0, 0)
        grid.addWidget(self.tbox_instrument, 0, 1)

        self.tbox_sensor = QLineEdit()
        self.tbox_sensor.setReadOnly(True)
        grid.addWidget(QLabel("Sensor"), 1, 0)
        grid.addWidget(self.tbox_sensor, 1, 1)    

        self.combo_element = QComboBox()
        self.combo_element.setEditable(True)
        self.combo_element.currentTextChanged.connect(self.element_changed)
        grid.addWidget(QLabel("Element"), 2, 0)
        grid.addWidget(self.combo_element, 2, 1)

        self.tbox_layout = QLineEdit()
        self.tbox_layout.setReadOnly(True)
        grid.addWidget(QLabel("Position"), 3, 0)
        grid.addWidget(self.tbox_layout, 3, 1)

        self.tbox_structure = QLineEdit()
        self.tbox_structure.setReadOnly(True)
        grid.addWidget(QLabel("Structure"), 4, 0)
        grid.addWidget(self.tbox_structure, 4, 1)

        self.tbox_surface = QLineEdit()
        self.tbox_surface.setReadOnly(True)
        grid.addWidget(QLabel("Surface"), 5, 0)
        grid.addWidget(self.tbox_surface, 5, 1)

        self.combo_fluid = QComboBox()
        self.combo_fluid.setEditable(True)
        grid.addWidget(QLabel("Fluid"), 6, 0)
        grid.addWidget(self.combo_fluid, 6, 1) 

        self.tbox_comment = QLineEdit()
        grid.addWidget(QLabel("Comment"), 7, 0)
        grid.addWidget(self.tbox_comment, 7, 1)

        hbox_grid = QHBoxLayout()
        hbox_grid.addStretch(1)
        hbox_grid.addLayout(grid, stretch=10)
        hbox_grid.addStretch(1)

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

        self.btn_disconnect= QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self.hw.disable_stage)
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
        self.btn_reference.clicked.connect(self.set_reference)
        self.btn_reference.setFixedWidth(btn_width)

        self.btn_position= QPushButton("Refresh")
        self.btn_position.clicked.connect(self.refresh_position)
        self.btn_position.setFixedWidth(btn_width)

        self.btn_home= QPushButton("Home")
        self.btn_home.clicked.connect(self.hw.home_stage)
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

        # Output Path
        label_output = QLabel("Output Directory Structure")
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

        # Run Measurements
        btn_run= QPushButton("Run")
        btn_run.clicked.connect(self.run_measurement)
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
        vbox.addWidget(label_metadata)
        vbox.addLayout(hbox_grid)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_hw)
        vbox.addLayout(hbox_hardware_outer)
        # vbox.addWidget(label_mf)
        # vbox.addLayout(hbox_mf)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_output)
        vbox.addLayout(hbox_output)
        vbox.addLayout(hbox_merge)
        vbox.addStretch()

        self.setLayout(vbox)

    def generate_run_df(self):
        self.run_df = csv.generate_run_df(self.setup)
        print(self.run_df)

    def scan_serial_ports(self):
        ports = self.hw.scan_serial_ports()
        self.combo_sp.clear()
        for port, desc, hwid in sorted(ports):
            self.combo_sp.addItem(port)

    def connect_hw(self):
        self.hw.connect(setup=self.setup, serial_port=self.combo_sp.currentText())

    def preview_run_df(self):
        if self.run_df is None:
            self.generate_run_df()
        self.runTable = MetaTable(self.run_df, "Run List DataFrame")
        self.runTable.show()

    def run_measurement(self):
        
        element = self.combo_element.currentText()
        fluid = self.combo_fluid.currentText()
        comment = self.tbox_comment.text()

        # for f in self.measure_funcs:
        #     if f.__name__ == self.combo_mf.currentText():
        #         mf = f

        # logging.info(f'measure_function = {mf.__name__}')

        merge = self.cbox_merge.isChecked()        
        csv.simple_measurement(self.setup, element, fluid, measure_func=self.hw.measure, merge=merge, comment=comment)

    def element_changed(self, element):
        try:
            layout = self.setup['sensor']['layout']['map'][element]
            if type(layout) == list:
                layout = f'{layout[0]}, {layout[1]}'
        except KeyError:
            layout = 'Unknown - Please update the setup file'

        try:
            surface = self.setup['sensor']['surface_map']['map'][element]
            if type(surface) == list:
                surface = f'{surface[0]}, {surface[1]}'
        except KeyError:
            surface = 'Unknown - Please update the setup file'

        try:
            structure = self.setup['sensor']['structure_map']['map'][element]
            if type(structure) == list:
                structure = f'{structure[0]}, {structure[1]}'
        except KeyError:
            structure = 'Unknown - Please update the setup file'
        self.tbox_layout.setText(layout)
        self.tbox_surface.setText(surface)
        self.tbox_structure.setText(structure)

    def set_reference(self):
        self.hw.store_position_reference()
        self.label_reference.setText(f'Reference {self.hw.ref_x},{self.hw.ref_y}')

    def refresh_position(self):
        self.hw.get_stage_position()
        self.label_position.setText(f'Position {self.hw.pos_x},{self.hw.pos_y}')


    def setup_changed(self, setup):
        logging.debug(f"singleMeasureTab: got new setup {setup['name']}")
        self.setup = setup
        
        # self.tbox_setup.setText(setup['name'])
        self.tbox_sensor.setText(setup['sensor']['name'])
        self.tbox_instrument.setText(setup['instrument']['name'])

        # Update the fluid / element options
        fluids = setup['input_config']['fluids']
        self.combo_fluid.clear()
        self.combo_fluid.addItems(fluids)

        elements = setup['sensor']['layout']['map'].keys()
        self.combo_element.clear()
        self.combo_element.addItems(elements)

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
    window = SingleMeasureTab()

    setup = csv.get_default_setup()
    window.setup_changed(setup)

    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())

