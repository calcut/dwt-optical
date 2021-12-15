from time import sleep
import os
import sys
import pandas as pd
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLineEdit, QWidget, QFrame,
QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
from GUI_tableView import ExportTable, MetaTable

import lib.csv_helpers as csv

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class ExportWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, metapath, meta_df, outfile):
        super().__init__()
        self.path = os.path.dirname(metapath)
        self.meta_df = meta_df
        self.outfile = outfile

    def run(self):
        logging.info(f'running csv.export_dataframes with path={self.path} meta_df={self.meta_df}')
        self.export = csv.export_dataframes(self.path, self.meta_df, self.outfile)
        self.finished.emit()

class ExportTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)


        default_metafile = './imported/index.tsv'
        # default_outfile = './export.tsv'
        default_outfile = ''
        
        # New Widget (to be used as a tab)
        self.tab = QWidget()
        self.tab.setObjectName(u"ExportTab")

        # Make a Vertical layout within the new tab
        self.vbox = QVBoxLayout(self.tab)

        label_title = QLabel("Exports data to large tsv table, ready for LDA processing")
        label_index = QLabel("Metadata Index File:")
        label_selection = QLabel("Selection to Export:")
        label_output = QLabel("Output File:")
        
        # tooltip_selection = ("Should extract at least [sensor, element, fluid] as in example\n"
        #     +"Other metadata can be captured and will be also be saved")

        self.tbox_meta = QLineEdit()
        self.tbox_meta.editingFinished.connect(self.update_meta_df)
        self.tbox_meta.setText(default_metafile)
        self.tbox_output = QLineEdit()
        self.tbox_output.setText(default_outfile)

        browse_meta = QPushButton("Browse")
        browse_meta.clicked.connect(self.get_meta)

        btn_preview_meta = QPushButton("Preview")
        btn_preview_meta.clicked.connect(self.preview_meta)

        btn_preview_selection = QPushButton("Preview")
        btn_preview_selection.clicked.connect(self.preview_selection)

        btn_apply_selection = QPushButton("Apply")
        btn_apply_selection.clicked.connect(self.select_meta)

        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output)

        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.run_export)

        btn_preview_export= QPushButton("Preview")
        btn_preview_export.clicked.connect(self.preview_export)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_index)
        hbox_input.addWidget(self.tbox_meta)
        hbox_input.addWidget(browse_meta)
        hbox_input.addWidget(btn_preview_meta)

        self.grid_sel = QGridLayout()
        self.grid_sel.setContentsMargins(0, 0, 0, 0)
        self.add_sel_row()
        self.update_meta_df()

        hbox_selection = QHBoxLayout()
        hbox_selection.addStretch()
        hbox_selection.addWidget(btn_apply_selection)
        hbox_selection.addWidget(btn_preview_selection)

        hbox_output = QHBoxLayout()
        hbox_output.addWidget(label_output)
        hbox_output.addWidget(self.tbox_output)
        hbox_output.addWidget(browse_output)
        hbox_output.addWidget(btn_preview_export)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_export)

        self.vbox.addWidget(label_title)
        self.vbox.addWidget(QHLine())
        self.vbox.addLayout(hbox_input)
        self.vbox.addWidget(QHLine())
        self.vbox.addWidget(label_selection)
        self.vbox.addLayout(self.grid_sel)
        self.vbox.addLayout(hbox_selection)
        self.vbox.addWidget(QHLine())
        self.vbox.addLayout(hbox_output)
        self.vbox.addLayout(hbox_run)
        self.vbox.addStretch()

    def get_meta(self):
        metafile, _ = QFileDialog.getOpenFileName(self.tab, "Metadata File:", filter ='(*.csv *.tsv)')
        self.tbox_meta.setText(metafile)
        self.update_meta_df()

    def get_output(self):
        outfile = QFileDialog.getSaveFileName(self.tab, "Select Output File:")
        self.tbox_output.setText(outfile)

    def select_meta(self):
        self.selection_df = self.meta_df

        rows = self.grid_sel.rowCount()
        # columns = self.grid_sel.columnCount()
        # print(f'columns = {columns}')

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
        print(f'keyindex {key}')
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

       
    def run_export(self):
        print('run export')
        outfile = self.tbox_output.text()

        if outfile == '':
            outfile = None

        self.thread = QThread()
        try:
            logging.info(f"Exporting selected data from {self.metapath}")
            self.worker = ExportWorker(self.metapath, self.selection_df, outfile)
        except AttributeError:
            logging.info(f"Exporting all data from {self.metapath}")
            self.worker = ExportWorker(self.metapath, self.meta_df, outfile)
            

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btn_export.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.btn_export.setEnabled(True)
        )

    def update_meta_df(self):
        self.metapath = os.path.abspath(self.tbox_meta.text())
        if os.path.isfile(self.metapath):
            self.meta_df = csv.read_metadata(self.metapath)

        # Update the 'key' combo boxes with fields from current meta_df 
        rows = self.grid_sel.rowCount()
        for row in range(rows):
            if row == 0:
                # This is the header row
                continue
            keyCombo = self.grid_sel.itemAtPosition(row,1).widget()
            keyCombo.clear()
            items = self.meta_df.columns.tolist()
            keyCombo.addItem('')
            keyCombo.addItems(items)

    def preview_meta(self):
        self.update_meta_df()
        self.metaTable = MetaTable(self.meta_df, self.metapath)
        self.metaTable.show()

    def preview_selection(self):
        title = 'Selected Data'
        self.selectedTable = MetaTable(self.selection_df, title)
        self.selectedTable.show()

    def preview_export(self):
        title = os.path.abspath(self.tbox_output.text())
        try:
            self.table = ExportTable(self.worker.export, title)
        except AttributeError:
            logging.error("Please run export first")
        summary = self.worker.export.to_string(max_cols=15, max_rows=15)
        for line in summary.splitlines():
            logging.info(line) #This looks crap just now... maybe due to html parser
        self.table.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = ExportTab()
    window.setLayout(window.vbox)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
