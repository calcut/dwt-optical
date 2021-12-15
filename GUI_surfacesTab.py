import sys
import os
import pandas as pd
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
 QHBoxLayout, QLineEdit, QWidget, QFrame, QMainWindow, QMessageBox,
QVBoxLayout, QFileDialog, QPushButton, QLabel, QTableWidget)
import logging
from GUI_tableView import MetaTable, SurfaceTable

import lib.csv_helpers as csv

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class SurfacesTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)


        default_metafile = './imported/index.tsv'
        # default_outfile = './export.tsv'
        # default_outfile = ''

        self.surfaceData = {
            'element'             : None,
            'chemistry'           : None
        }
        
        # New Widget (to be used as a tab)
        self.tab = QWidget()
        self.tab.setObjectName(u"ExportTab")

        # Make a Vertical layout within the new tab
        self.vbox = QVBoxLayout(self.tab)

        label_title = QLabel("Reads in a Metadata Index file and populates"
            +" the 'chemistry' column based on the mapping defined below")
        label_index = QLabel("Metadata Index File:")
        label_mapping = QLabel("Mapping to Apply:")
        # label_output = QLabel("Output File:")

        self.tbox_meta = QLineEdit()
        self.tbox_meta.editingFinished.connect(self.update_meta_df)
        self.tbox_meta.setText(default_metafile)

        browse_meta = QPushButton("Browse")
        browse_meta.clicked.connect(self.get_meta)

        btn_preview_meta = QPushButton("Preview")
        btn_preview_meta.clicked.connect(self.preview_meta)

        btn_preview_mapping = QPushButton("Preview")
        # btn_preview_mapping.clicked.connect(self.preview_mapping)

        btn_apply_mapping = QPushButton("Apply")
        btn_apply_mapping.clicked.connect(self.apply_mapping)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_index)
        hbox_input.addWidget(self.tbox_meta)
        hbox_input.addWidget(browse_meta)
        hbox_input.addWidget(btn_preview_meta)

        self.surfaceTable = SurfaceTable()

        # self.add_sel_row()
        self.update_meta_df()


        hbox_mapping = QHBoxLayout()
        hbox_mapping.addStretch()
        hbox_mapping.addWidget(btn_apply_mapping)
        hbox_mapping.addWidget(btn_preview_mapping)

        hbox_output = QHBoxLayout()
        # hbox_output.addWidget(label_output)
        # hbox_output.addWidget(self.tbox_output)
        # hbox_output.addWidget(browse_output)
        # hbox_output.addWidget(btn_preview_export)

        self.vbox.addWidget(label_title)
        self.vbox.addWidget(QHLine())
        self.vbox.addLayout(hbox_input)
        self.vbox.addWidget(QHLine())
        self.vbox.addWidget(label_mapping)
        self.vbox.addWidget(self.surfaceTable)
        self.vbox.addLayout(hbox_mapping)
        # self.vbox.addStretch()

    def get_meta(self):
        metafile, _ = QFileDialog.getOpenFileName(self.tab, "Metadata File:", filter ='(*.csv *.tsv)')
        self.tbox_meta.setText(metafile)
        self.update_meta_df()

    def get_output(self):
        outfile = QFileDialog.getSaveFileName(self.tab, "Select Output File:")
        self.tbox_output.setText(outfile)


    def update_meta_df(self):
        self.metapath = os.path.abspath(self.tbox_meta.text())
        if os.path.isfile(self.metapath):
            self.meta_df = csv.read_metadata(self.metapath)
        try:
            elements = sorted(self.meta_df['element'].unique())
            elements = [str(e) for e in elements]
            chemistries = []

            for e in elements:
                chem = self.meta_df.loc[self.meta_df['element']== e]['chemistry'].unique()
                if len(chem) > 1:
                    logging.error('more than 1 surface chemistry found per element, this script cannot handle that')
                    return
                chemistries.append(chem[0])
            logging.debug(f'Found elements: {elements}')
            logging.debug(f'Found chemistries: {chemistries}')
            self.surfaceData['element'] = elements
            self.surfaceData['chemistry'] = chemistries
            self.update_surface_table()
        except KeyError as e:
            logging.error(f'{e} Perhaps "element" column not found in Metadata index file')

    def update_surface_table(self):
        surface_df = pd.DataFrame(self.surfaceData)
        self.surfaceTable.set_data(surface_df)
        # logging.debug(f'setting surface table with {surface_df}')


    def preview_meta(self):
        self.update_meta_df()
        self.metaTable = MetaTable(self.meta_df, self.metapath)
        self.metaTable.show()

    def apply_mapping(self, askfirst=True):
        self.surfaceData = self.surfaceTable.model._data
        logging.debug(f'About to apply\n{self.surfaceData}')
        msg = QMessageBox()
        ret = msg.information(self,'', f"This will modify the metadata file:\n\n"
            +f"{self.metapath}\n\nContinue?", msg.Yes | msg.No)

        if ret == msg.Yes:
            print('applying now')
            csv.apply_chem_map(self.surfaceData, self.metapath)
            self.update_meta_df()

    # def preview_mapping(self):
    #     title = 'Selected Data'
    #     self.selectedTable = MetaTable(self.mapping_df, title)
    #     self.selectedTable.show()

    # def preview_export(self):
    #     title = os.path.abspath(self.tbox_output.text())
    #     try:
    #         self.table = ExportTable(self.worker.export, title)
    #     except AttributeError:
    #         logging.error("Please run export first")
    #     summary = self.worker.export.to_string(max_cols=15, max_rows=15)
    #     for line in summary.splitlines():
    #         logging.info(line) #This looks crap just now... maybe due to html parser
    #     self.table.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = SurfacesTab()
    window.setLayout(window.vbox)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
