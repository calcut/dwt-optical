import sys
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox)
import logging
from GUI_dataProcess import DataProcess
from GUI_tableView import ExportTable, PreviewTable
from GUI_commonWidgets import QHLine, MetaFilter
import lib.csv_helpers as csv
import pandas as pd

class ExportWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, setup, meta_df, data_proc=None, std_dev=False):
        super().__init__()
        self.setup = setup
        self.meta_df = meta_df
        self.outfile = None
        self.dp = data_proc

        if self.dp.apply_avg_repeats == False:
            self.std_dev = False
        else:
            self.std_dev = std_dev

    def run_spectra(self):
        logging.info(f"running csv.export_dataframes with path={self.setup['datadir']} meta_df=\n{self.meta_df}")
        try:
            self.export = csv.export_dataframes(self.setup, self.meta_df, self.outfile, dp=self.dp)
        except Exception as e:
            logging.error(e)
        self.finished.emit()

    def run_stats(self):
        try:
            self.export = pd.DataFrame()
            progress = 0
            row_num = 0
            total = len(self.meta_df)

            if self.dp.apply_avg_repeats and self.std_dev:
                std_dev = True
            else:
                std_dev = False

            for row in self.meta_df.index:
                row_num += 1
                progress = int(row_num/total * 100)
                self.progress.emit(progress)

                logging.info(f"Processing stats {progress}%")
                stats_df = csv.get_stats_single(self.setup, self.dp, self.meta_df, row, peak_type='Min', std_deviation=std_dev)

                # Accumulate the dataframes in a large 'result' dataframe
                self.export = pd.concat([self.export, stats_df], axis=0)

            self.export.sort_values(by=['element'], inplace=True)
            # self.export.reset_index(drop=True, inplace=True)

        except Exception as e:
            logging.error(e)
        
        self.finished.emit()

class ExportTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName(u"ExportTab")

        default_outfile = 'export.txt'
        self.export = None

        self.format_options = ["Stats", "Stats (with Std Dev)", "LDA Spectra"]

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

        btn_width = 80
        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output)
        browse_output.setFixedWidth(btn_width)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_export)
        self.btn_save.setFixedWidth(btn_width)

        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.run_export)
        self.btn_apply.setFixedWidth(btn_width)

        btn_view_export= QPushButton("View")
        btn_view_export.clicked.connect(self.view_export)
        btn_view_export.setFixedWidth(btn_width)

        self.combo_export = QComboBox()
        self.combo_export.addItems(self.format_options)

        hbox_outpath = QHBoxLayout()
        hbox_outpath.addWidget(QLabel('Export file:'))
        hbox_outpath.addWidget(self.tbox_output, stretch=3)
        hbox_outpath.addWidget(browse_output)
        hbox_outpath.addWidget(self.btn_save)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch(2)
        hbox_run.addWidget(QLabel('Format:'))
        hbox_run.addWidget(self.combo_export, stretch=1)
        hbox_run.addWidget(self.btn_apply)
        hbox_run.addWidget(btn_view_export)

        vbox_output = QVBoxLayout()
        vbox_output.addLayout(hbox_run) 
        vbox_output.addLayout(hbox_outpath)

        # self.setupBrowse = SetupBrowse()
        self.metaFilter = MetaFilter()
        self.dataProcess = DataProcess()
        self.dataProcess.request_selection_df.connect(self.metaFilter.select_meta)
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

    def save_export(self):
        outfile = self.tbox_output.text()
        if self.export is not None:
            logging.info(f"Writing to {outfile} ...")
            self.export.to_csv(outfile, sep='\t', na_rep='NA')
        else:
            logging.warning(f"Please apply output formatting first")


    def run_export(self):

        self.thread = QThread()
        self.metaFilter.select_meta()
        self.dataProcess.apply()
        selection_df = self.metaFilter.selection_df


        export_format = self.combo_export.currentText()
        if export_format == self.format_options[0]:
            self.worker = ExportWorker(self.setup, selection_df, self.dataProcess.dp, std_dev=False)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run_stats)
        if export_format == self.format_options[1]:
            self.worker = ExportWorker(self.setup, selection_df, self.dataProcess.dp, std_dev=True)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run_stats)
        if export_format == self.format_options[2]:
            self.worker = ExportWorker(self.setup, selection_df, self.dataProcess.dp, std_dev=False)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run_spectra)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btn_apply.setEnabled(False)
        self.thread.finished.connect(self.export_complete)

    def export_complete(self):
        self.btn_apply.setEnabled(True)
        self.export = self.worker.export

    def view_export(self):
        title = "Export Data"
        if self.export is not None:
            if self.combo_export.currentText() == self.format_options[2]:
                self.table = ExportTable(self.export, title)
            else:
                self.table = PreviewTable(self.export, title, process_info=self.dataProcess.process_info)
            self.table.show()
        else:
            logging.error("Please run export first")

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
