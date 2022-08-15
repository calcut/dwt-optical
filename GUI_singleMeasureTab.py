
from math import comb
import sys
import os
from PySide6.QtCore import QObject, QThread, Signal, QSize
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget, QCheckBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox, QGridLayout)
import logging
from GUI_commonWidgets import QHLine
from GUI_tableView import MetaTable
from GUI_plotCanvas import PlotCanvasBasic
import lib.csv_helpers as csv
import lib.json_setup as json_setup
import pandas as pd

class SingleMeasureTab(QWidget):

    def __init__(self, measure_func):
        QWidget.__init__(self)
        self.setObjectName(u"SingleMeasureTab")

        btn_width = 80

        self.measure_func = measure_func

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
        grid.addWidget(QLabel("Instrument"), 0, 0)
        grid.addWidget(self.tbox_instrument, 0, 1)

        self.tbox_sensor = QLineEdit()
        grid.addWidget(QLabel("Sensor"), 1, 0)
        grid.addWidget(self.tbox_sensor, 1, 1)    

        self.combo_element = QComboBox()
        self.combo_element.setEditable(True)
        self.combo_element.currentTextChanged.connect(self.element_changed)
        grid.addWidget(QLabel("Element"), 2, 0)
        grid.addWidget(self.combo_element, 2, 1)

        self.tbox_pos_x = QLineEdit()
        self.tbox_pos_y = QLineEdit()
        hbox_pos = QHBoxLayout()
        hbox_pos.addWidget(QLabel('X'))
        hbox_pos.addWidget(self.tbox_pos_x)
        hbox_pos.addWidget(QLabel('Y'))
        hbox_pos.addWidget(self.tbox_pos_y)
        grid.addWidget(QLabel("Position"), 3, 0)
        grid.addLayout(hbox_pos, 3, 1)

        self.tbox_structure = QLineEdit()
        grid.addWidget(QLabel("Structure"), 4, 0)
        grid.addWidget(self.tbox_structure, 4, 1)

        self.tbox_surface = QLineEdit()
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

        # Output Path
        label_output = QLabel("Output")
        label_output.setStyleSheet("font-weight: bold")
        self.tbox_outpath = QLineEdit()
        self.tbox_outpath.setReadOnly(True)

        # Merge
        label_merge = QLabel('Merge into existing files')
        self.cbox_merge = QCheckBox()
        self.cbox_merge.setChecked(False)
        hbox_merge = QHBoxLayout()
        hbox_merge.addWidget(self.cbox_merge)
        hbox_merge.addWidget(label_merge)
        hbox_merge.addStretch()

        # Run Measurements
        btn_run= QPushButton("Run")
        btn_run.clicked.connect(self.run_measurement)
        btn_run.setFixedWidth(btn_width)

        btn_save= QPushButton("Save")
        btn_save.clicked.connect(self.save_measurement)
        btn_save.setFixedWidth(btn_width)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(btn_run)
        hbox_run.addWidget(btn_save)

        vbox_output = QVBoxLayout()
        vbox_output.addWidget(self.tbox_outpath)
        vbox_output.addLayout(hbox_merge)
        vbox_output.addLayout(hbox_run)

        hbox_output = QHBoxLayout()
        hbox_output.addStretch(1)
        # hbox_output.addLayout(hbox_run, stretch=10)
        hbox_output.addLayout(vbox_output, stretch=10)
        hbox_output.addStretch(1)

        self.plot = PlotCanvasBasic()

        # Overall Layout
        vbox = QVBoxLayout()
        vbox.addWidget(label_info)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_metadata)
        vbox.addLayout(hbox_grid)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_output)
        vbox.addLayout(hbox_output)
        # vbox.addLayout(hbox_merge)
        vbox.addWidget(self.plot)
        vbox.addStretch()

        self.setLayout(vbox)

    def sizeHint(self):
        return QSize(840, 400)

    def run_measurement(self):
        
        run_dict = {
            'date'          : pd.Timestamp.utcnow().strftime('%Y-%m-%d'),
            'instrument'    : self.tbox_instrument.text(),
            'sensor'        : self.tbox_sensor.text(),
            'element'       : self.combo_element.currentText(),
            'structure'     : self.tbox_structure.text(),
            'surface'       : self.tbox_surface.text(),
            'fluid'         : self.combo_fluid.currentText(),
            'repeats'       : 1,
            'comment'       : self.tbox_comment.text()
        }

        # To manually override the position
        modified_setup = self.setup.copy()
        element = self.combo_element.currentText()
        modified_setup['sensor']['layout']['map'][element][0] = float(self.tbox_pos_x.text())
        modified_setup['sensor']['layout']['map'][element][1] = float(self.tbox_pos_y.text())

        row = '-'.join(run_dict[p] for p in self.setup['primary_metadata'])
        run_dict['index'] = row

        # Awkward way to get into a "run dataframe"
        # but this is done to mirror the batch measure version
        run_list = json_setup.default_metadata_columns.copy()
        run_list.pop('name')

        for col in run_dict.keys():
            run_list[col] = [run_dict[col]]

        self.run_df = pd.DataFrame(run_list)
        self.run_df.set_index('index', inplace=True)

        try:
            self.df = self.measure_func(modified_setup, self.run_df.loc[row])
        except Exception as e:
            logging.error(e)
            return

        self.plot.set_data(self.df)
        

    def save_measurement(self):

        merge = self.cbox_merge.isChecked()

        row = self.run_df.index[0]
        datapath = csv.find_datapath(self.setup, self.run_df, row)
        csv.write_df_txt(self.df, datapath, merge)
        logging.info(f'saved to {datapath}')

        self.run_df.at[row, 'date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        csv.write_meta_df_txt(self.setup, self.run_df, merge)

    def element_changed(self, element):
        try:
            layout = self.setup['sensor']['layout']['map'][element]
        except KeyError:
            pass
            # layout = 'Unknown - Please update the setup file'

        try:
            surface = self.setup['sensor']['surface_map']['map'][element]
            if type(surface) == list:
                surface = f'{surface[0]}, {surface[1]}'
        except KeyError:
            pass
            # surface = 'Unknown - Please update the setup file'

        try:
            structure = self.setup['sensor']['structure_map']['map'][element]
            if type(structure) == list:
                structure = f'{structure[0]}, {structure[1]}'
        except KeyError:
            pass
            # structure = 'Unknown - Please update the setup file'
        self.tbox_pos_x.setText(str(layout[0]))
        self.tbox_pos_y.setText(str(layout[1]))
        self.tbox_surface.setText(surface)
        self.tbox_structure.setText(structure)

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

