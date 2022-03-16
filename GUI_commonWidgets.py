import os
import sys
import pandas as pd
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QFrame,
    QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
import json
from GUI_tableView import MetaTable
from GUI_tableView import SetupTable
import lib.csv_helpers as csv

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class SetupBrowse(QWidget):

    new_setup = Signal(dict)

    def __init__(self):
        QWidget.__init__(self)

        # default_metafile = './dummydata/defa.txt'

        label_index = QLabel("Setup File:")

        btn_width = 80
        browse_setup = QPushButton("Browse")
        browse_setup.clicked.connect(self.get_setup)
        browse_setup.setFixedWidth(btn_width)

        btn_preview_setup = QPushButton("Preview")
        btn_preview_setup.clicked.connect(self.preview_setup)
        btn_preview_setup.setFixedWidth(btn_width)

        self.tbox_setup = QLineEdit()
        self.tbox_setup.setReadOnly(True)
        # self.tbox_setup.editingFinished.connect(self.update_setup_json)
        self.tbox_setup.setText('setups/default-setup.json')

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_index)
        hbox_input.addWidget(self.tbox_setup)
        hbox_input.addWidget(browse_setup)
        hbox_input.addWidget(btn_preview_setup)

        self.setLayout(hbox_input)
        self.update_setup_json()

    def get_setup(self):
        self.setuppath, _ = QFileDialog.getOpenFileName(self, "Setup File:", filter ='*.json')
        self.tbox_setup.setText(self.setuppath)
        self.update_setup_json()

    def update_setup_json(self):
        self.setuppath = self.tbox_setup.text()
        if os.path.isfile(self.setuppath):
            self.setup = csv.read_setup_json(self.setuppath)
            self.new_setup.emit(self.setup)
        else:
            logging.error('No Setup File found')

    def preview_setup(self):
        self.setupTable = SetupTable(self.setup, self.setuppath)
        self.setupTable.show()

# class MetaBrowse(QWidget):

#     new_metapath = Signal(str)

#     def __init__(self, setup):
#         QWidget.__init__(self)

#         self.setup = setup

#         # default_metafile = './imported/index.txt'

#         label_index = QLabel("Metadata Index File:")

#         btn_width = 80
#         browse_meta = QPushButton("Browse")
#         browse_meta.clicked.connect(self.get_meta)
#         browse_meta.setFixedWidth(btn_width)

#         btn_preview_meta = QPushButton("Preview")
#         btn_preview_meta.clicked.connect(self.preview_meta)
#         btn_preview_meta.setFixedWidth(btn_width)

#         self.tbox_meta = QLineEdit()
#         self.tbox_meta.editingFinished.connect(self.update_meta_df)
#         self.tbox_meta.setText()

#         hbox_input = QHBoxLayout()
#         hbox_input.addWidget(label_index)
#         hbox_input.addWidget(self.tbox_meta)
#         hbox_input.addWidget(browse_meta)
#         hbox_input.addWidget(btn_preview_meta)

#         self.setLayout(hbox_input)

#     # def get_meta(self):
#     #     metafile, _ = QFileDialog.getOpenFileName(self, "Metadata File:", filter ='(*.csv *.tsv *.txt)')
#     #     self.tbox_meta.setText(metafile)
#     #     self.update_meta_df()

#     def update_meta_df(self):
#         self.metapath = os.path.join(self.setup['path'], self.setup['metafile'])
#         # self.metapath = os.path.abspath(self.tbox_meta.text())
#         if os.path.isfile(self.metapath):
#             self.new_metapath.emit(self.metapath)

#     def preview_meta(self):
#         meta_df = csv.read_metadata(self.metapath)
#         self.metaTable = MetaTable(meta_df, self.metapath)
#         self.metaTable.show()

class MetaFilter(QWidget):

    new_selection_df = Signal(pd.DataFrame)

    def __init__(self):
        QWidget.__init__(self)

        self.setObjectName(u"MetaFilter")
        vbox = QVBoxLayout()

        label = QLabel("Select/Filter from Metadata file:")

        btn_width = 80
        btn_apply_selection = QPushButton("Apply")
        btn_apply_selection.clicked.connect(self.select_meta)
        btn_apply_selection.setFixedWidth(btn_width)

        btn_preview_selection = QPushButton("Preview")
        btn_preview_selection.clicked.connect(self.preview_selection)
        btn_preview_selection.setFixedWidth(btn_width)

        self.grid_sel = QGridLayout()
        self.grid_sel.setContentsMargins(0, 0, 0, 0)
        self.add_sel_row()

        hbox_selection = QHBoxLayout()
        hbox_selection.addStretch()
        hbox_selection.addWidget(btn_apply_selection)
        hbox_selection.addWidget(btn_preview_selection)

        vbox.addWidget(label)
        vbox.addLayout(self.grid_sel)
        vbox.addLayout(hbox_selection)
        self.setLayout(vbox)

    def select_meta(self):
        self.selection_df = self.meta_df

        rows = self.grid_sel.rowCount()
        for i in range(rows):
            if i == 0:
                # This is the header row
                continue
            try:
                if i == 1:
                    # First filter is effectively an AND with the orginal index
                    logic = 'AND'
                else:
                    logic = self.grid_sel.itemAtPosition(i, 0).widget().currentText()
                
                key = self.grid_sel.itemAtPosition(i, 1).widget().currentText()
                value = self.grid_sel.itemAtPosition(i, 2).widget().currentText()
                wildcard = self.grid_sel.itemAtPosition(i, 3).widget().isChecked()
            except AttributeError:
                # This can happen if rows are deleted then recreated, ghost row
                # indicies still exist.
                continue

            if key == '':
                continue
            if logic == 'AND':
                self.selection_df = csv.select_from_metadata(key, value,
                     self.selection_df,
                     regex=wildcard)
            if logic == 'OR':
                filtered_df = csv.select_from_metadata(key, value,
                     self.meta_df,
                     regex=wildcard)
                self.selection_df.reset_index(inplace=True)
                filtered_df.reset_index(inplace=True)
                self.selection_df = pd.merge(self.selection_df,
                                             filtered_df,
                                             how = 'outer')
                self.selection_df.set_index('index', verify_integrity=True, inplace=True)

        logging.info(f'{len(self.selection_df)} metadata rows in selection, '
            + f'with {self.selection_df["repeats"].sum()} total measurements')
       
        self.new_selection_df.emit(self.selection_df)
        
    def add_sel_row(self):
        
        rows = self.grid_sel.rowCount()
        columns = self.grid_sel.columnCount()
        btn_width = 80

        item = self.grid_sel.itemAtPosition(0, 0)
        if item is None:
            widget = QPushButton('Add Filter')
            widget.clicked.connect(self.add_sel_row)
            widget.setFixedWidth(btn_width)
            self.grid_sel.addWidget(widget, 0, 4, 1, 1, alignment=Qt.AlignRight)

            self.grid_sel.addWidget(QLabel("Metadata Key"), 0, 1, 1, 1)
            self.grid_sel.addWidget(QLabel("Value"), 0, 2, 1, 1)
            self.grid_sel.addWidget(QLabel("Wildcard"), 0, 3, 1, 1)
            self.grid_sel.addWidget(QLabel(""), 0, 0, 1, 1)

        else:
            self.logicCombo = QComboBox()
            self.logicCombo.addItem('AND')
            self.logicCombo.addItem('OR')

            self.keyCombo = QComboBox()
            self.keyCombo.setEditable(True)
            self.keyCombo.addItem('')
            self.keyCombo.currentTextChanged.connect(self.keyChanged)

            if hasattr(self, 'meta_df'):
                if isinstance(self.meta_df, pd.DataFrame):
                    items = self.meta_df.columns.tolist()
                    self.keyCombo.addItems(items)

            self.valCombo = QComboBox()
            self.valCombo.setEditable(True)
            self.valCombo.addItem('')

            if not rows == 1:
                # Logic Operator doesn't make sense on first row
                self.grid_sel.addWidget(self.logicCombo, rows, 0, 1, 1)
            self.grid_sel.addWidget(self.keyCombo, rows, 1, 1, 1)
            self.grid_sel.addWidget(self.valCombo, rows, 2, 1, 1)
            self.grid_sel.addWidget(QCheckBox(), rows, 3, 1, 1)
            widget = QPushButton('Remove')
            widget.clicked.connect(self.remove_sel_row)
            widget.setFixedWidth(btn_width)
            self.grid_sel.addWidget(widget, rows, 4, 1, 1, alignment=Qt.AlignRight)

    def remove_sel_row(self):
            index = self.grid_sel.indexOf(self.sender())
            row = self.grid_sel.getItemPosition(index)[0]
            for column in range(self.grid_sel.columnCount()):
                layout = self.grid_sel.itemAtPosition(row, column)
                if layout is not None:
                    layout.widget().deleteLater()
                    self.grid_sel.removeItem(layout)

    def keyChanged(self, key):
        index = self.grid_sel.indexOf(self.sender())
        row = self.grid_sel.getItemPosition(index)[0]
        valuebox = self.grid_sel.itemAtPosition(row, 2).widget()
        # print(f'sender text = {self.sender.currentText()}')
        valuebox.clear()
        try:
            items = sorted(self.meta_df[key].unique())
            items = [str(i) for i in items]
            valuebox.addItem('')
            valuebox.addItems(items)
        except KeyError:
            logging.debug(f'Key "{key}" not found in Metadata index file')

    def setup_changed(self, setup):

        logging.debug(f"MetaFilter : got new setup")
        self.meta_df = csv.read_metadata(setup)


        # Update the 'key' combo boxes with fields from new meta_df 
        rows = self.grid_sel.rowCount()
        for row in range(rows):
            if row == 0:
                # This is the header row
                continue
            # try:
            keyCombo = self.grid_sel.itemAtPosition(row,1).widget()
            keyCombo.clear()
            # except AttributeError as e:
                # logging.debug(e)
                # logging.debug(f"row {row}")
            items = self.meta_df.columns.tolist()
            keyCombo.addItem('')
            keyCombo.addItems(items)

    def preview_selection(self):
        title = 'Selected Data'
        try:
            self.selectedTable = MetaTable(self.selection_df, title)
            self.selectedTable.show()
        except AttributeError:
            logging.error("Please Apply filter first")

if __name__ == "__main__":

    app = QApplication(sys.argv)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    window = QMainWindow()
    centralwidget = QWidget()
    centralwidget.setObjectName(u"centralwidget")
    window.setCentralWidget(centralwidget)

    metaBrowse = MetaBrowse()
    metaFilter = MetaFilter()
    metaBrowse.new_metapath.connect(metaFilter.metapath_changed)
    metaBrowse.update_meta_df()
    
    vbox = QVBoxLayout()
    vbox.addWidget(metaBrowse)
    vbox.addWidget(QHLine())
    vbox.addWidget(metaFilter)
    centralwidget.setLayout(vbox)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
