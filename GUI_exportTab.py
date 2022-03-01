import os
import sys
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget,
    QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
from GUI_dataProcess import DataProcess
from GUI_tableView import ExportTable
from GUI_commonWidgets import QHLine, MetaBrowse, MetaFilter
import lib.csv_helpers as csv

class ExportWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, metapath, meta_df, outfile, data_proc=None):
        super().__init__()
        self.datadir = os.path.dirname(metapath)
        self.meta_df = meta_df
        self.outfile = outfile
        self.data_proc = data_proc

    def run(self):
        logging.info(f'running csv.export_dataframes with path={self.datadir} meta_df=\n{self.meta_df}')
        self.export = csv.export_dataframes(self.datadir, self.meta_df, self.outfile, dp=self.data_proc)
        self.finished.emit()

class ExportTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName(u"ExportTab")

        # default_outfile = './export.txt'
        default_outfile = ''

        # Make a Vertical layout within the new tab
        vbox = QVBoxLayout()

        label_title = QLabel("Exports data to large tsv table, ready for LDA processing")
        label_output = QLabel("Output File:")
        
        self.tbox_output = QLineEdit()
        self.tbox_output.setText(default_outfile)

        btn_width = 80
        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output)
        browse_output.setFixedWidth(btn_width)

        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.run_export)
        self.btn_export.setFixedWidth(btn_width)

        btn_preview_export= QPushButton("Preview")
        btn_preview_export.clicked.connect(self.preview_export)
        self.btn_export.setFixedWidth(btn_width)

        hbox_output = QHBoxLayout()
        hbox_output.addWidget(label_output)
        hbox_output.addWidget(self.tbox_output)
        hbox_output.addWidget(browse_output)
        hbox_output.addWidget(btn_preview_export)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_export)

        self.metaBrowse = MetaBrowse()
        self.metaFilter = MetaFilter()
        self.dataProcess = DataProcess()
        self.metaBrowse.new_metapath.connect(self.metaFilter.metapath_changed)
        self.metaBrowse.new_metapath.connect(self.dataProcess.metapath_changed)
        self.metaBrowse.update_meta_df()
        self.metaFilter.add_sel_row()
        self.metaFilter.new_selection_df.connect(self.dataProcess.selection_df_changed)
        self.metaFilter.select_meta()

        vbox.addWidget(label_title)
        vbox.addWidget(QHLine())
        vbox.addWidget(self.metaBrowse)
        vbox.addWidget(QHLine())
        vbox.addWidget(self.metaFilter)
        vbox.addWidget(QHLine())
        vbox.addWidget(self.dataProcess)
        vbox.addWidget(QHLine())
        vbox.addLayout(hbox_output)
        vbox.addLayout(hbox_run)    
        vbox.addStretch()

        self.setLayout(vbox)



    def get_output(self):
        outfile = QFileDialog.getSaveFileName(self, "Select Output File:")
        self.tbox_output.setText(outfile)

    def run_export(self):
        outfile = self.tbox_output.text()
        metapath = self.metaBrowse.metapath

        if outfile == '':
            outfile = None

        self.thread = QThread()

        selection_df = self.metaFilter.selection_df

        self.worker = ExportWorker(metapath, selection_df, outfile, self.dataProcess.dp)
        # self.worker = ExportWorker(metapath, selection_df, outfile)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btn_export.setEnabled(False)
        self.thread.finished.connect(self.export_complete)

    def export_complete(self):
        self.btn_export.setEnabled(True)
        logging.info('Export Complete, Summary:\n')
        summary = self.worker.export.to_string(max_cols=15, max_rows=15)
        for line in summary.splitlines():
            logging.info(line)


    def preview_export(self):
        title = os.path.abspath(self.tbox_output.text())
        try:
            self.table = ExportTable(self.worker.export, title)
            self.table.show()
        except AttributeError:
            logging.error("Please run export first")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = ExportTab()
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
