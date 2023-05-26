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
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox, QProgressBar, QGridLayout, QTimeEdit, QRadioButton)
import logging
from GUI_commonWidgets import QHLine
from GUI_tableView import MetaTable
import lib.csv_helpers as csv
import lib.json_setup as json_setup
import lib.data_process

import signal
import time
import pandas as pd
from GUI_plotCanvas import Pyqtgraph_canvas, PlotCanvasBasic
from GUI_tableView import PreviewTable

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
            measurement_stats['timestamp'] = pd.Timestamp((measurement_stats.index[0]),unit='s').tz_localize('UTC')
            measurement_stats['fluid'] = self.meta_dict['fluid']
            measurement_stats.index = [filename]

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

       # Metadata
        label_metadata = QLabel("Measurement Metadata")
        label_metadata.setStyleSheet("font-weight: bold")

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)

        self.tbox_sensor = QLineEdit()
        grid.addWidget(QLabel("Sensor"), 1, 0)
        grid.addWidget(self.tbox_sensor, 1, 1)    

        self.combo_element = QComboBox()
        self.combo_element.setEditable(True)
        grid.addWidget(QLabel("Element"), 2, 0)
        grid.addWidget(self.combo_element, 2, 1)

        self.combo_fluid = QComboBox()
        self.combo_fluid.setEditable(True)
        grid.addWidget(QLabel("Fluid"), 3, 0)
        grid.addWidget(self.combo_fluid, 3, 1) 

        hbox_grid = QHBoxLayout()
        hbox_grid.addStretch(1)
        hbox_grid.addLayout(grid, stretch=10)
        hbox_grid.addStretch(1)


        self.time_interval = QTimeEdit()
        self.time_interval.setDisplayFormat("HH:mm:ss")
        self.time_interval.setCurrentSectionIndex(2)
        self.time_interval.setFixedWidth = btn_width*2
        self.time_interval.setTime(QTime(0,0,1))
        # self.time_interval.editingFinished.connect(self.interval_changed)
        self.time_interval.timeChanged.connect(self.interval_changed)



        btn_metadata_update = QPushButton("Update")
        btn_metadata_update.setFixedWidth(btn_width)
        btn_metadata_update.clicked.connect(self.generate_run_dict)

        self.radio_spectrum = QRadioButton("Spectrum")
        self.radio_spectrum.setChecked(True)
        self.radio_spectrum.toggled.connect(lambda:self.plot_type(self.radio_spectrum))
        self.radio_peak = QRadioButton("Peak")
        self.radio_peak.setChecked(False)
        self.radio_peak.toggled.connect(lambda:self.plot_type(self.radio_peak))


        # Output Path
        label_output = QLabel("Output:")
        label_output.setStyleSheet("font-weight: bold")

        self.tbox_outpath = QLineEdit()
        self.tbox_outpath.setReadOnly(True)

        self.tbox_statspath = QLineEdit()
        self.tbox_statspath.setReadOnly(False)

        btn_view_export= QPushButton("View")
        btn_view_export.clicked.connect(self.view_export)
        btn_view_export.setFixedWidth(btn_width)

        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output)
        browse_output.setFixedWidth(btn_width)

        self.btn_run= QPushButton("Run")
        self.btn_run.clicked.connect(self.run_measurements)
        self.btn_run.setFixedWidth(btn_width)

        self.btn_pause= QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_resume)
        self.btn_pause.setFixedWidth(btn_width)

        self.btn_stop= QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_measurements)
        self.btn_stop.setFixedWidth(btn_width)

        self.plot_peak = Pyqtgraph_canvas()
        self.plot_peak.hide()
        self.plot_spectrum = PlotCanvasBasic()


        rungrid = QGridLayout()
        rungrid.setContentsMargins(0, 0, 0, 0)
        rungrid.setRowMinimumHeight(2,20)
        # rungrid.setColumnMinimumWidth(1, 100)

        rungrid.addWidget(QLabel('Spectral Data:'),0,0, alignment=Qt.AlignLeft)
        rungrid.addWidget(self.tbox_outpath,0,1,1,5)

        rungrid.addWidget(QLabel('Stats file:'), 1, 0)
        rungrid.addWidget(self.tbox_statspath, 1,1,1,3)
        rungrid.addWidget(browse_output,1, 4, 1, 1)
        rungrid.addWidget(btn_view_export, 1, 5, 1, 1)

        rungrid.addWidget(QLabel("Measurement Interval (HH:mm:ss):"), 3, 3, 1, 1, alignment=Qt.AlignRight)
        rungrid.addWidget(self.time_interval, 3, 4, 1, 2, alignment=Qt.AlignRight)
        rungrid.addWidget(QLabel("Update Metadata during run:"),4,3, alignment=Qt.AlignRight)
        rungrid.addWidget(btn_metadata_update,4,5)
        rungrid.addWidget(QLabel("Plot Type:"),5,3, alignment=Qt.AlignRight)
        rungrid.addWidget(self.radio_spectrum,5,4, Qt.AlignRight)
        rungrid.addWidget(self.radio_peak,5,5, Qt.AlignRight)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_run)
        hbox_run.addWidget(self.btn_pause)
        hbox_run.addWidget(self.btn_stop)




        # hbox_outpath = QHBoxLayout()
        # hbox_outpath.addWidget(QLabel('Spectral Data:'))
        # hbox_outpath.addWidget(self.tbox_outpath)

        # hbox_statspath = QHBoxLayout()
        # hbox_statspath.addWidget(QLabel('Stats file:'))
        # hbox_statspath.addWidget(self.tbox_statspath, stretch=3)
        # hbox_statspath.addWidget(browse_output)
        # hbox_statspath.addWidget(btn_view_export)

        vbox_output = QVBoxLayout()
        # vbox_output.addLayout(hbox_outpath)
        # vbox_output.addLayout(hbox_statspath)
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
        vbox.addWidget(self.plot_spectrum)
        vbox.addWidget(self.plot_peak)
        vbox.addStretch()

        self.setLayout(vbox)

    def sizeHint(self):
        return QSize(840, 600)
    
    def generate_run_dict(self):

        element = self.combo_element.currentText()
        sensor = self.tbox_sensor.text()

        self.run_dict = {
            'date'          : pd.Timestamp.utcnow().strftime('%Y-%m-%d'),
            'instrument'    : self.setup['instrument']['name'],
            'sensor'        : sensor,
            'element'       : element,
            'structure'     : self.setup['sensor']['structure_map']['map'][element][0],
            'surface'       : self.setup['sensor']['surface_map']['map'][element][0],
            'fluid'         : self.combo_fluid.currentText(),
            'comment'       : None,
        }

        # To allow dynamically updating while the thread is running.
        if self.thread:
            self.worker.meta_dict = self.run_dict

    def run_measurements(self):

        # merge = self.cbox_merge.isChecked()
        merge = True
        self.generate_run_dict()

        interval = self.time_interval.time()
        interval_s = interval.hour()*60*60 + interval.minute()*60 + interval.second()

        self.stats_df = None
        self.plot_peak.clear_data()
        self.run_starttime = pd.Timestamp.utcnow()

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
        self.worker.finished.connect(self.run_complete)
        # self.worker.progress.connect(self.set_progress)
        self.worker.plotdata.connect(self.update_plot)


    def update_plot(self, plotdata):
        title = plotdata[1]
        data = plotdata[0]
        measurement_stats = plotdata[2]

        series = measurement_stats.iloc[0]
        timestamp = measurement_stats.at[series.name, 'timestamp']

        delta = timestamp - self.run_starttime
        runtime_s = delta.seconds

        # Possibly bad practice to hard code time zone, but at least it has the UTC offset included
        timestamp_str = timestamp.tz_convert('Europe/London').strftime('%Y-%m-%d %H:%M:%S%z')

        # Don't know why this is necessary, but the value wouldn't update otherwise
        measurement_stats.drop(columns=['timestamp'], inplace=True)

        # Add runtime and timestamp to stats
        measurement_stats.at[series.name, 'runtime_s'] = runtime_s
        measurement_stats.at[series.name, 'timestamp'] = timestamp_str

        data.columns = ['spectrum']
        self.plot_spectrum.set_data(data, title, stats_df=measurement_stats)

        self.stats_df = pd.concat([measurement_stats, self.stats_df])
        self.stats_df.to_csv(self.tbox_statspath.text(), sep='\t', na_rep='NA')

        self.plot_peak.append_datapoint(x = runtime_s/60, y = series["Peak"], name=series["fluid"])

    def plot_type(self, button):
	
        pass
        if button.text() == "Spectrum":
            if button.isChecked() == True:
                self.plot_spectrum.show()
            else:
                self.plot_spectrum.hide()

        if button.text() == "Peak":
            if button.isChecked() == True:
                self.plot_peak.show()
            else:
                self.plot_peak.hide()

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

    def setup_changed(self, setup):
        logging.debug(f"episodicTab: got new setup {setup['name']}")
        self.setup = setup

        self.tbox_sensor.setText(setup['sensor']['name'])

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

        self.tbox_statspath.setText(setup['output_config']['outfile'])

    def view_export(self):
        title = "Stats Data"
        if self.stats_df is not None:
            self.table = PreviewTable(self.stats_df, title, process_info=None)
            self.table.show()
        else:
            logging.error("No Stats Data to view")

    def get_output(self):
        outfile, _ = QFileDialog.getSaveFileName(self, "Select Stats File:")
        self.tbox_statspath.setText(outfile)

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

