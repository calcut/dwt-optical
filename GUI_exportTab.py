import os
import sys
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget,
    QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
from GUI_dataProcess import DataProcess
from GUI_tableView import ExportTable
from GUI_commonWidgets import QHLine, SetupBrowse, MetaFilter
import lib.csv_helpers as csv

class ExportWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, setup, meta_df, outfile, data_proc=None):
        super().__init__()
        self.setup = setup
        self.meta_df = meta_df
        self.outfile = outfile
        self.data_proc = data_proc

    def run(self):
        logging.info(f"running csv.export_dataframes with path={self.setup['datadir']} meta_df=\n{self.meta_df}")
        self.export = csv.export_dataframes(self.setup, self.meta_df, self.outfile, dp=self.data_proc)
        self.finished.emit()

class ExportTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName(u"ExportTab")

        # default_outfile = './export.txt'
        default_outfile = ''
        default_statsfile = 'stats.txt'

        # Make a Vertical layout within the new tab
        vbox = QVBoxLayout()

        label_info = QLabel("Exports data to large tsv table, ready for LDA processing")
        label_select = QLabel("Select Measurements")
        label_select.setStyleSheet("font-weight: bold")
        label_process = QLabel("Apply Processing")
        label_process.setStyleSheet("font-weight: bold")
        label_output = QLabel("Output")
        label_output.setStyleSheet("font-weight: bold")

        self.tbox_output = QLineEdit()
        self.tbox_output.setText(default_outfile)

        self.tbox_stats = QLineEdit()
        self.tbox_stats.setText(default_statsfile)

        btn_width = 80
        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output)
        browse_output.setFixedWidth(btn_width)

        browse_stats = QPushButton("Browse")
        browse_stats.clicked.connect(self.get_stats_path)
        browse_stats.setFixedWidth(btn_width)

        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.run_export)
        self.btn_export.setFixedWidth(btn_width)

        self.btn_export_stats = QPushButton("Export")
        self.btn_export_stats.clicked.connect(self.run_stats)
        self.btn_export_stats.setFixedWidth(btn_width)

        btn_view_stats= QPushButton("View")
        btn_view_stats.clicked.connect(self.view_stats)
        btn_view_stats.setFixedWidth(btn_width)

        btn_view_export= QPushButton("View")
        btn_view_export.clicked.connect(self.view_export)
        btn_view_export.setFixedWidth(btn_width)

        hbox_outpath = QHBoxLayout()
        hbox_outpath.addWidget(QLabel('Export data file:'))
        hbox_outpath.addWidget(self.tbox_output)
        hbox_outpath.addWidget(browse_output)

        hbox_statspath = QHBoxLayout()
        hbox_statspath.addWidget(QLabel('Export stats file:'))
        hbox_statspath.addWidget(self.tbox_stats)
        hbox_statspath.addWidget(browse_stats)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_export)
        hbox_run.addWidget(btn_view_export)

        hbox_stats = QHBoxLayout()
        hbox_stats.addStretch()
        hbox_stats.addWidget(self.btn_export_stats)
        hbox_stats.addWidget(btn_view_stats)  

        vbox_output = QVBoxLayout()
        vbox_output.addLayout(hbox_outpath)
        vbox_output.addLayout(hbox_run) 
        vbox_output.addLayout(hbox_statspath)
        vbox_output.addLayout(hbox_stats)   

        # self.setupBrowse = SetupBrowse()
        self.metaFilter = MetaFilter()
        self.dataProcess = DataProcess()
        # self.setupBrowse.new_setup.connect(self.metaFilter.setup_changed)
        # self.setupBrowse.new_setup.connect(self.dataProcess.setup_changed)
        # self.setupBrowse.update_setup_json()
        self.metaFilter.add_sel_row()
        self.metaFilter.new_selection_df.connect(self.dataProcess.selection_df_changed)
        self.metaFilter.select_meta()

        vbox.addWidget(label_info)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_select)
        hbox_select = QHBoxLayout()
        hbox_select.addStretch(1)
        hbox_select.addWidget(self.metaFilter, stretch=10)
        hbox_select.addStretch(1)
        vbox.addLayout(hbox_select)
        
        vbox.addWidget(QHLine())
        vbox.addWidget(label_process)
        hbox_process = QHBoxLayout()
        hbox_process.addStretch(1)
        hbox_process.addWidget(self.dataProcess, stretch=10)
        hbox_process.addStretch(1)
        vbox.addLayout(hbox_process)
        vbox.addWidget(QHLine())
        
        vbox.addWidget(label_output)
        hbox_output = QHBoxLayout()
        hbox_output.addStretch(1)
        hbox_output.addLayout(vbox_output, stretch=10)
        hbox_output.addStretch(1)
        vbox.addLayout(hbox_output)
 
        vbox.addStretch()

        self.setLayout(vbox)

    def setup_changed(self, setup):
        logging.debug(f"exportTab: got new setup {setup['name']}")
        self.setup = setup
        self.metaFilter.setup_changed(setup)
        self.dataProcess.setup_changed(setup)

    def get_output(self):
        outfile, _ = QFileDialog.getSaveFileName(self, "Select Output File:")
        self.tbox_output.setText(outfile)

    def get_stats_path(self):
        statsfile, _ = QFileDialog.getSaveFileName(self, "Select Stats Output File:")
        self.tbox_stats.setText(statsfile)

    def run_export(self):
        outfile = self.tbox_output.text()

        if outfile == '':
            outfile = None

        self.thread = QThread()

        selection_df = self.metaFilter.selection_df

        self.worker = ExportWorker(self.setup, selection_df, outfile, self.dataProcess.dp)
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


    def view_export(self):
        title = os.path.abspath(self.tbox_output.text())
        try:
            self.table = ExportTable(self.worker.export, title)
            self.table.show()
        except AttributeError:
            logging.error("Please run export first")

    def run_stats(self):
        selection_df = self.metaFilter.selection_df
        self.stats = csv.export_stats(self.setup, self.dataProcess.dp, selection_df, outfile='stats.txt')

    def view_stats(self):
        self.table_stats = ExportTable(self.stats, 'title')
        self.table_stats.show()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = ExportTab()
    setup = csv.get_default_setup()
    window.setup_changed(setup)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
