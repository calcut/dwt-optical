
import sys
import os
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget, QCheckBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox)
import logging
from GUI_commonWidgets import QHLine
from GUI_tableView import MetaTable
import lib.csv_helpers as csv
import time

class MeasureWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, setup, run_df, measure_func, merge):
        super().__init__()
        self.setup = setup
        self.run_df = run_df
        self.measure_func = measure_func
        self.merge = merge
        self.stop_requested = False

    def run(self):
        logging.info(f"csv.run_measure as thread/worker")
        i=0
        while i < 8:
            i+=1
            time.sleep(1)
            if self.stop_requested:
                logging.warning('stopping now')
                break
            logging.info('sleeping 1')
            
        # csv.run_measure(self.setup, self.run_df, measure_func=self.measure_func, merge=self.merge)
        self.finished.emit()

    def stop(self):
        logging.warning('stop has been requested!!!')
        self.stop_requested = True



class MeasureTab(QWidget):

    def __init__(self, measure_func):
        QWidget.__init__(self)
        self.setObjectName(u"MeasureTab")

        self.thread = None

        btn_width = 80

        label_info = QLabel("Capture a series of measurements\n")

        tooltip_info = ("Generates a Run List based on the parameters in setup input_config\n"
            +"i.e. Adds a row for each permutation of 'fluids' and 'elements'\n\n"
            +"The correct measurement function must be selected for the spectrometer\n\n"
            +"Output data is stored in the path/subdirs defined in setup.json\n"
            +"Files and metadata can be optionally merged with existing data"
        )
        label_info.setToolTip(tooltip_info)

        self.run_df = None
        self.measure_func = measure_func

        # Run_df
        label_run_df = QLabel("Generate Run List")
        label_run_df.setStyleSheet("font-weight: bold")
        label_run_idea = QLabel("[Could add import/export options here to allow manual editing?]")

        btn_generate = QPushButton("Generate")
        btn_generate.clicked.connect(self.generate_run_df)
        btn_generate.setFixedWidth(btn_width)

        btn_preview_run_df= QPushButton("Preview")
        btn_preview_run_df.clicked.connect(self.preview_run_df)
        btn_preview_run_df.setFixedWidth(btn_width)

        hbox_run_df_btns = QHBoxLayout()
        hbox_run_df_btns.addWidget(label_run_idea)
        hbox_run_df_btns.addStretch()
        hbox_run_df_btns.addWidget(btn_generate)
        hbox_run_df_btns.addWidget(btn_preview_run_df)

        hbox_run_df = QHBoxLayout()
        # hbox_run_df.addWidget(label_run_df)
        hbox_run_df.addStretch(1)
        hbox_run_df.addLayout(hbox_run_df_btns, stretch=10)
        hbox_run_df.addStretch(1)

        # Output Path
        label_output = QLabel("Output Directory Structure:")
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

        self.btn_run= QPushButton("Run")
        self.btn_run.clicked.connect(self.run_measurements)
        self.btn_run.setFixedWidth(btn_width)

        self.btn_stop= QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_measurements)
        self.btn_stop.setFixedWidth(btn_width)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_run)
        hbox_run.addWidget(self.btn_stop)

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
        vbox.addWidget(label_run_df)
        # vbox.addWidget(label_run_idea)
        vbox.addLayout(hbox_run_df)
        vbox.addWidget(QHLine())
        vbox.addWidget(QHLine())
        vbox.addWidget(label_output)
        vbox.addLayout(hbox_output)
        # vbox.addLayout(hbox_run)
        vbox.addStretch()

        self.setLayout(vbox)

    def generate_run_df(self):
        self.run_df = csv.generate_run_df(self.setup)
        print(self.run_df)

    def preview_run_df(self):
        if self.run_df is None:
            self.generate_run_df()
        self.runTable = MetaTable(self.run_df, "Run List DataFrame")
        self.runTable.show()

    # def run_measurements(self):
    #     if self.run_df is None:
    #         self.generate_run_df()

    #     merge = self.cbox_merge.isChecked()        
    #     csv.run_measure(self.setup, self.run_df, measure_func=self.measure_func, merge=merge)

    def run_measurements(self):

        merge = self.cbox_merge.isChecked()
        if self.run_df is None:
            self.generate_run_df()

        self.thread = QThread()

        self.worker = MeasureWorker(self.setup, self.run_df, self.measure_func, merge)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btn_run.setEnabled(False)
        self.thread.finished.connect(self.run_complete)

    def run_complete(self):
        self.btn_run.setEnabled(True)
        logging.info('Run Complete')
        
    def stop_measurements(self):
        if self.thread:
            logging.warning('Stopping Run')
            self.worker.stop()
            self.thread.requestInterruption()

    def setup_changed(self, setup):
        logging.debug(f"measureTab: got new setup {setup['name']}")
        self.setup = setup

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
    window = MeasureTab()
    setup = csv.get_default_setup()
    window.setup_changed(setup)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())

