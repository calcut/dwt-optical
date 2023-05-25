"""
A tab to measure a single location repeatedly over time.

Stage must be positioned manually
The name of the element (e.g. A02) must be specified manually.

Grid shape measurement is not supported

Additional light references are not supported
"""
import sys
import os
from PySide6.QtCore import QObject, QThread, Signal, QSize, QTimer, QTime, Qt
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget, QCheckBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox, QProgressBar, QGridLayout, QTimeEdit)
import logging
from GUI_commonWidgets import QHLine
from GUI_tableView import MetaTable
import lib.csv_helpers as csv
import lib.json_setup as json_setup
import lib.data_process

import signal
import time
import pandas as pd
from GUI_plotCanvas import Pyqtgraph_canvas

class EpisodicWorker(QObject):
    finished = Signal(str)
    progress = Signal(int)
    plotdata = Signal(pd.DataFrame)

    def __init__(self, setup, interval_s, meta_dict, measure_func, merge):
        super().__init__()
        self.setup = setup
        self.meta_dict = meta_dict
        self.measure_func = measure_func
        self.merge = merge
        self.stop_requested = False
        self.pause = False
        self.timer_update_requested = False

        self.interval_s = interval_s

        self.interval_timer = QTimer(self)
        self.service_timer = QTimer(self)

        self.runs = 0

        # Dummy data processor, everything disabled for now
        self.dp = lib.data_process.DataProcessor()
        self.dp.apply_avg_repeats = False
        self.dp.apply_normalise = False
        self.dp.apply_smooth = False
        self.dp.apply_trim = False
        self.dp.apply_interpolate = False
        self.dp.apply_round = False

        # dp.smooth_points = 3
        # dp.wavelength_trim_min = 540
        # dp.wavelength_trim_max = 730
        # dp.round_decimals = 3

    def run(self):
        # This has come from csv.run_measure, but is interruptable and reports progress.
        logging.info(f"Running episodic measurements as thread/worker")
        
        self.interval_timer.timeout.connect(self.capture_save_spectrum)
        self.interval_timer.setInterval(self.interval_s*1000)
        self.interval_timer.start()

        self.service_timer.timeout.connect(self.service)
        self.service_timer.setInterval(100)
        self.service_timer.start()

    def capture_save_spectrum(self):

        # call the measure function to get data
        try:
            self.runs += 1
            logging.info(f"capturing run {self.runs}")
            df = self.measure_func()
            timestamp = pd.Timestamp.utcnow().timestamp()
            df.rename(columns={"transmission (%)" : timestamp }, inplace=True)

            # Construct the data path
            filename = '-'.join(self.meta_dict[p] for p in self.setup['primary_metadata'])
            subdir=[]
            for s in self.setup['subdirs']:
                subdir.append(self.meta_dict[s])
            subdir = os.path.join(*subdir)
            datapath = os.path.join(self.setup['datadir'], subdir, f'{filename}.txt')
            
            # write the df to txt file
            csv.write_df_txt(df, datapath, merge=self.merge)

            # update the index
            meta_df = pd.DataFrame(self.meta_dict, index=[filename])
            meta_df.index.name = 'index'
            csv.write_meta_df_txt(self.setup, meta_df, merge=self.merge)

            measurement_stats = self.dp.get_stats(df, peak_type='Min', round_digits=self.dp.round_decimals, std_deviation=False)
            measurement_stats['timestamp'] = pd.to_datetime(measurement_stats.index,unit='s')
            measurement_stats['fluid'] = self.meta_dict['fluid']

            self.progress.emit(self.runs)
            self.plotdata.emit((df, f'{filename} run{self.runs}', measurement_stats))

        except Exception as e:
            logging.error(e)
            self.finished.emit('Run aborted')


    
    def service(self):

        if self.timer_update_requested:
            self.interval_timer.start(self.interval_s*1000)
            self.timer_update_requested = False
            
        if self.stop_requested:
            logging.warning('STOPPING run')
            self.interval_timer.stop()
            self.finished.emit('Run Stopped')
            return

        if self.pause:
            logging.warning('PAUSING run')
            self.interval_timer.stop()
            while self.pause:
                if self.stop_requested:
                    logging.warning('STOPPING run')
                    self.finished.emit('Run Stopped')
                    return
                time.sleep(1)
            logging.warning('RESUMING run')
            self.interval_timer.start(self.interval_s*1000)

class EpisodicTab(QWidget):

    run_finished = Signal(str)

    def __init__(self, measure_func):
        QWidget.__init__(self)
        self.setObjectName(u"EpisodicTab")

        self.thread = None

        btn_width = 80

        label_info = QLabel("Episodic (time series) measurements with manual stage positioning")

        tooltip_info = ("Generates a Run List based on the parameters in setup input_config\n"
            +"i.e. Adds a row for each permutation of 'fluids' and 'elements'\n\n"
            +"The correct measurement function must be selected for the spectrometer\n\n"
            +"Output data is stored in the path/subdirs defined in setup.json\n"
            +"Files and metadata can be optionally merged with existing data"
        )
        label_info.setToolTip(tooltip_info)

        self.stats_df = None
        self.measure_func = measure_func

        # Run parameters

        rungrid = QGridLayout()
        rungrid.setContentsMargins(0, 0, 0, 0)

        self.time_interval = QTimeEdit()
        self.time_interval.setDisplayFormat("HH:mm:ss")
        self.time_interval.setCurrentSectionIndex(2)
        self.time_interval.setFixedWidth = btn_width*2
        self.time_interval.setTime(QTime(0,0,1))
        # self.time_interval.editingFinished.connect(self.interval_changed)
        self.time_interval.timeChanged.connect(self.interval_changed)

        rungrid.addWidget(QLabel("Measurement Interval (HH:mm:ss)"), 0, 0, alignment=Qt.AlignRight)
        rungrid.addWidget(self.time_interval, 0, 1)

        btn_metadata_update = QPushButton("Update")
        btn_metadata_update.setFixedWidth(btn_width)
        btn_metadata_update.clicked.connect(self.generate_run_dict)
        rungrid.addWidget(QLabel("Dynamically update Metadata"),1,0, alignment=Qt.AlignRight)
        rungrid.addWidget(btn_metadata_update,1,1)


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

        self.tbox_structure = QLineEdit()
        grid.addWidget(QLabel("Structure"), 3, 0)
        grid.addWidget(self.tbox_structure, 3, 1)

        self.tbox_surface = QLineEdit()
        grid.addWidget(QLabel("Surface"), 4, 0)
        grid.addWidget(self.tbox_surface, 4, 1)

        self.combo_fluid = QComboBox()
        self.combo_fluid.setEditable(True)
        grid.addWidget(QLabel("Fluid"), 5, 0)
        grid.addWidget(self.combo_fluid, 5, 1) 

        self.tbox_comment = QLineEdit()
        grid.addWidget(QLabel("Comment"), 6, 0)
        grid.addWidget(self.tbox_comment, 6, 1)

        hbox_grid = QHBoxLayout()
        hbox_grid.addStretch(1)
        hbox_grid.addLayout(grid, stretch=10)
        hbox_grid.addStretch(1)


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

        self.btn_pause= QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_resume)
        self.btn_pause.setFixedWidth(btn_width)

        self.btn_stop= QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_measurements)
        self.btn_stop.setFixedWidth(btn_width)

        self.elapsed_time = 0

        self.plot = Pyqtgraph_canvas()

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_run)
        hbox_run.addWidget(self.btn_pause)
        hbox_run.addWidget(self.btn_stop)

        vbox_output = QVBoxLayout()
        vbox_output.addWidget(self.tbox_outpath)
        vbox_output.addLayout(hbox_merge)
        vbox_output.addLayout(rungrid)
        vbox_output.addLayout(hbox_run)
        hbox_output = QHBoxLayout()
        hbox_output.addStretch(1)
        hbox_output.addLayout(vbox_output, stretch=10)
        hbox_output.addStretch(1)

        # Overall Layout
        vbox = QVBoxLayout()
        vbox.addWidget(label_info)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_metadata)
        vbox.addLayout(hbox_grid)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_output)
        vbox.addLayout(hbox_output)
        vbox.addWidget(self.plot)
        vbox.addStretch()

        self.setLayout(vbox)

    def sizeHint(self):
        return QSize(840, 600)
    
    def generate_run_dict(self):

        self.run_dict = {
            'date'          : pd.Timestamp.utcnow().strftime('%Y-%m-%d'),
            'instrument'    : self.tbox_instrument.text(),
            'sensor'        : self.tbox_sensor.text(),
            'element'       : self.combo_element.currentText(),
            'structure'     : self.tbox_structure.text(),
            'surface'       : self.tbox_surface.text(),
            'fluid'         : self.combo_fluid.currentText(),
            'comment'       : self.tbox_comment.text()
        }

        # To allow dynamically updating while the thread is running.
        if self.thread:
            self.worker.meta_dict = self.run_dict

    def run_measurements(self):

        merge = self.cbox_merge.isChecked()
        self.generate_run_dict()

        interval = self.time_interval.time()
        interval_s = interval.hour()*60*60 + interval.minute()*60 + interval.second()

        self.thread = QThread()

        self.worker = EpisodicWorker(self.setup, interval_s, self.run_dict, self.measure_func, merge)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btn_run.setEnabled(False)
        self.elapsed_time = 0
        self.worker.finished.connect(self.run_complete)
        # self.worker.progress.connect(self.set_progress)
        self.worker.plotdata.connect(self.update_plot)


    def update_plot(self, plotdata):
        title = plotdata[1]
        data = plotdata[0]
        measurement_stats = plotdata[2]

        self.stats_df = pd.concat([measurement_stats, self.stats_df])

        series = measurement_stats.iloc[0]

        self.plot.append_datapoint(x = series['timestamp'].timestamp(), y = series["Peak"])

    def run_complete(self, status):
        self.btn_run.setEnabled(True)
        self.btn_pause.setText('Pause')
        self.run_finished.emit(status)
        logging.info(status)

    def pause_resume(self):
        if self.thread:
            if self.btn_pause.text() == "Pause":
                self.worker.pause = True
                self.btn_pause.setText('Resume')
            else:
                self.worker.pause = False
                self.btn_pause.setText('Pause')
        
    def stop_measurements(self):
        if self.thread:
            self.worker.stop_requested = True

    def interval_changed(self):
        interval = self.time_interval.time()
        interval_s = interval.hour()*60*60 + interval.minute()*60 + interval.second()
        if self.thread:
            self.worker.interval_s = interval_s
            self.worker.timer_update_requested = True


    def element_changed(self, element):
        try:
            surface = self.setup['sensor']['surface_map']['map'][element]
            if type(surface) == list:
                surface = f'{surface[0]}'
        except KeyError:
            pass
            # surface = 'Unknown - Please update the setup file'

        try:
            structure = self.setup['sensor']['structure_map']['map'][element]
            if type(structure) == list:
                structure = f'{structure[0]}'
        except KeyError:
            pass
            # structure = 'Unknown - Please update the setup file'
        self.tbox_surface.setText(surface)
        self.tbox_structure.setText(structure)

    def setup_changed(self, setup):
        logging.debug(f"episodicTab: got new setup {setup['name']}")
        self.setup = setup

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

    with open('rootpath_cache', 'r') as f:
        rootpath = f.readline().strip()
    os.chdir(rootpath)

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = EpisodicTab(measure_func=csv.dummy_measurement)
    setup = csv.get_default_setup()
    window.setup_changed(setup)
    window.resize(1024, 768)
    window.show()

    stats_df = pd.read_csv("temp.csv")
    window.plot.show_stats(stats_df)
    sys.exit(app.exec())

