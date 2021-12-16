import os
import sys
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QFrame,
    QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
from GUI_tableView import MetaTable
from GUI_plotCanvas import PlotCanvas
import lib.csv_helpers as csv

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class MetaBrowse(QWidget):

    new_meta_df = Signal(pd.DataFrame)

    def __init__(self):
        QWidget.__init__(self)

        default_metafile = './imported/index.tsv'

        label_index = QLabel("Metadata Index File:")

        browse_meta = QPushButton("Browse")
        browse_meta.clicked.connect(self.get_meta)

        btn_preview_meta = QPushButton("Preview")
        btn_preview_meta.clicked.connect(self.preview_meta)

        self.tbox_meta = QLineEdit()
        self.tbox_meta.editingFinished.connect(self.update_meta_df)
        self.tbox_meta.setText(default_metafile)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_index)
        hbox_input.addWidget(self.tbox_meta)
        hbox_input.addWidget(browse_meta)
        hbox_input.addWidget(btn_preview_meta)

        self.setLayout(hbox_input)

    def get_meta(self):
        metafile, _ = QFileDialog.getOpenFileName(self, "Metadata File:", filter ='(*.csv *.tsv)')
        self.tbox_meta.setText(metafile)
        self.update_meta_df()

    def update_meta_df(self):
        self.metapath = os.path.abspath(self.tbox_meta.text())
        if os.path.isfile(self.metapath):
            self.meta_df = csv.read_metadata(self.metapath)
        self.new_meta_df.emit(self.metapath)

    def preview_meta(self):
        self.update_meta_df()
        self.metaTable = MetaTable(self.meta_df, self.metapath)
        self.metaTable.show()

class MetaFilter(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.meta_df = None
        self.metapath = None

        self.setObjectName(u"MetaFilter")
        vbox = QVBoxLayout()

        label = QLabel("Select/Filter from Metadata file:")

        btn_apply_selection = QPushButton("Apply")
        btn_apply_selection.clicked.connect(self.select_meta)

        btn_preview_selection = QPushButton("Preview")
        btn_preview_selection.clicked.connect(self.preview_selection)

        btn_plot= QPushButton("Plot")
        btn_plot.clicked.connect(self.plot_selection)

        self.grid_sel = QGridLayout()
        self.grid_sel.setContentsMargins(0, 0, 0, 0)
        self.add_sel_row()

        hbox_selection = QHBoxLayout()
        hbox_selection.addStretch()
        hbox_selection.addWidget(btn_apply_selection)
        hbox_selection.addWidget(btn_preview_selection)
        hbox_selection.addWidget(btn_plot)

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
                self.selection_df = csv.filter_by_metadata(key, value,
                     self.selection_df,
                     regex=wildcard)
            if logic == 'OR':
                filtered_df = csv.filter_by_metadata(key, value,
                     self.meta_df,
                     regex=wildcard)
                self.selection_df = pd.merge(self.selection_df,
                                             filtered_df,
                                             how = 'outer')

        logging.info(f'{len(self.selection_df)} rows in selection after filtering')
        
    def add_sel_row(self):
        
        rows = self.grid_sel.rowCount()
        columns = self.grid_sel.columnCount()

        item = self.grid_sel.itemAtPosition(0, 0)
        if item is None:
            widget = QPushButton('Add Filter')
            widget.clicked.connect(self.add_sel_row)
            self.grid_sel.addWidget(widget, 0, 4, 1, 1)

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
            widget = QPushButton('Remove Filter')
            widget.clicked.connect(self.remove_sel_row)
            self.grid_sel.addWidget(widget, rows, 4, 1, 1)

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

    def metaChanged(self, metapath):
        self.metapath = metapath
        self.meta_df = csv.read_metadata(metapath)

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

    def plot_selection(self):
        # title = 'Selected Data'
        try:
            self.plot = PlotCanvas()
            self.plot.set_data(self.selection_df, self.metapath)
            self.plot.show()
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
    metaBrowse.new_meta_df.connect(metaFilter.metaChanged)
    metaBrowse.update_meta_df()
    
    vbox = QVBoxLayout()
    vbox.addWidget(metaBrowse)
    vbox.addWidget(QHLine())
    vbox.addWidget(metaFilter)
    centralwidget.setLayout(vbox)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
