import sys
import os
import pandas as pd
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
 QHBoxLayout, QLineEdit, QWidget, QFrame, QMainWindow, QMessageBox,
QVBoxLayout, QFileDialog, QPushButton, QLabel, QTableWidget)
import logging
from GUI_tableView import MetaTable, SurfaceTable
from GUI_commonWidgets import QHLine, MetaBrowse

import lib.csv_helpers as csv

class SurfacesTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName(u"SurfacesTab")

        default_metafile = './imported/index.tsv'

        self.surfaceData = {
            'element'             : None,
            'chemistry'           : None
        }
        
        vbox = QVBoxLayout()

        label_title = QLabel("Reads in a Metadata Index file and updates"
            +" the 'chemistry' column based on the mapping defined below"
            +"\n\n[Functionality is currently quite limited, probably want to load/save mappings and possibly use a metadata filter]")
        label_mapping = QLabel("Mapping to Apply:")

        # btn_preview_mapping = QPushButton("Preview")
        # btn_preview_mapping.clicked.connect(self.preview_mapping)

        btn_apply_mapping = QPushButton("Apply")
        btn_apply_mapping.clicked.connect(self.apply_mapping)

        self.surfaceTable = SurfaceTable()


        hbox_mapping = QHBoxLayout()
        hbox_mapping.addStretch()
        hbox_mapping.addWidget(btn_apply_mapping)
        # hbox_mapping.addWidget(btn_preview_mapping)

        self.metaBrowse = MetaBrowse()
        # self.metaFilter = MetaFilter()
        self.metaBrowse.new_metapath.connect(self.metapath_changed)
        self.metaBrowse.update_meta_df()

        vbox.addWidget(label_title)
        vbox.addWidget(QHLine())
        vbox.addWidget(self.metaBrowse)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_mapping)
        vbox.addWidget(self.surfaceTable)
        vbox.addLayout(hbox_mapping)
        # vbox.addStretch()
        self.setLayout(vbox)

    def get_output(self):
        outfile = QFileDialog.getSaveFileName(self.tab, "Select Output File:")
        self.tbox_output.setText(outfile)


    def metapath_changed(self, metapath):
        self.meta_df = csv.read_metadata(metapath)
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


if __name__ == "__main__":

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = SurfacesTab()
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
