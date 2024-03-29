
import sys
import os
from PySide6.QtCore import QObject, QThread, Signal, QSize, QTimer
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget, QCheckBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QComboBox, QProgressBar)
import logging
from GUI_commonWidgets import QHLine
from GUI_tableView import MetaTable
import lib.csv_helpers as csv
import time
import pandas as pd
from GUI_plotCanvas import PlotCanvas, PlotCanvasBasic

class MeasureWorker(QObject):
    finished = Signal(str)
    progress = Signal(int)
    plotdata = Signal(pd.DataFrame)

    def __init__(self, setup, run_df, measure_func, merge):
        super().__init__()
        self.setup = setup
        self.run_df = run_df
        self.measure_func = measure_func
        self.merge = merge
        self.stop_requested = False
        self.pause = False

    def run(self):
        # This has come from csv.run_measure, but is interruptable and reports progress.
        logging.info(f"Running batch measurements as thread/worker")

        # meta_df accumulates the metadata for rows that have been succesfully completed.
        meta_df = pd.DataFrame()
        

        gsp = 0
        if 'grid_spacing' in self.setup['input_config']:
            gsp = float(self.setup['input_config']['grid_spacing'])

        grid_measure_coords = [[0,0]]
        if 'grid_shape' in self.setup['input_config']:
            shape = self.setup['input_config']['grid_shape']
            if shape == '3x3_grid':
                grid_measure_coords = [[0,0], [-gsp, -gsp], [-gsp, 0], [-gsp, gsp], [0, -gsp], [0, gsp], [gsp, -gsp], [gsp, 0], [gsp, gsp]]
            elif shape == 'cross':
                grid_measure_coords = [[0,0], [-gsp, 0], [gsp, 0], [0, gsp], [0,-gsp]]
            elif shape == 'None' or shape == None:
                pass
            else:
                logging.warning(f'Grid shape "{shape}" not recognised, valid options are "3x3_grid", "cross" or "None"')

        progress = 0
        total_measurements = self.run_df['repeats'].sum()*len(grid_measure_coords)

        row_count = 0
        for row in self.run_df.index:
            row_count += 1
            meta_row = self.run_df.loc[row]
            df = pd.DataFrame()

            lightref_interval = self.setup['input_config']['lightref_interval']
            lr_offset_x = None
            if lightref_interval > 0:
                if row_count % lightref_interval == 0:
                    lr_offset_x = self.setup['input_config']['lightref_offset_x']                

            for g in grid_measure_coords:
                x_modifier = g[0]
                y_modifier = g[1]
                for rep in range(meta_row['repeats']):
                    progress +=1
                    progress_percent = int(progress / total_measurements * 100)
                    logging.debug(f'{progress_percent}% {row}, grid {g}, repeat {rep+1}')
                    if self.stop_requested:
                        logging.warning('STOPPING run')
                        self.save_and_abort(meta_df)
                        return

                    # call the measure function to get data
                    try:
                        df = self.measure_func(self.setup, meta_row, lr_offset_x, x_modifier, y_modifier)
                        timestamp = pd.Timestamp.utcnow().timestamp()
                        df.rename(columns={"transmission (%)" : timestamp }, inplace=True)
                        lr_offset_x = None # don't keep requesting new light references
                    except Exception as e:
                        logging.error(e)
                        self.save_and_abort(meta_df)
                        return
            
                    if self.pause:
                        logging.warning('PAUSING run')
                        while self.pause:
                            if self.stop_requested:
                                logging.warning('STOPPING run')
                                self.save_and_abort(meta_df)
                                return
                            time.sleep(1)
                        logging.warning('RESUMING run')

                    self.progress.emit(progress_percent)
                    self.plotdata.emit((df, f'{row} repeat{rep+1}'))

                    # Construct the data path
                    datapath = csv.find_datapath(self.setup, self.run_df, row)
                    # write the df to txt file
                    csv.write_df_txt(df, datapath, merge=self.merge)

                    if 'delay_between_reps' in self.setup['input_config']:
                        delay = self.setup['input_config']['delay_between_reps']
                        if delay > 0:
                            logging.info(f"delaying for {delay}s")
                            time.sleep(delay)

            # Update the date column in the run_df
            meta_df = pd.concat([meta_df, pd.DataFrame(meta_row).T])
            meta_df.at[row, 'date'] = pd.Timestamp.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        meta_df.index.name = 'index'
        csv.write_meta_df_txt(self.setup, meta_df, merge=self.merge)
        self.finished.emit('Run Complete')

    def save_and_abort(self, meta_df):
        #Need to save/merge the current meta_df
        # otherwise there will be data files not present in the index file
        logging.debug('saving meta_df after abort')
        if len(meta_df) > 0:
            meta_df.index.name = 'index'
            csv.write_meta_df_txt(self.setup, meta_df, merge=self.merge)
        self.finished.emit('Run aborted')
        

class MeasureTab(QWidget):

    run_finished = Signal(str)

    def __init__(self, measure_func):
        QWidget.__init__(self)
        self.setObjectName(u"MeasureTab")

        self.thread = None

        btn_width = 80

        label_info = QLabel("Capture a series of measurements")

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
        label_run_df = QLabel("Run List")
        label_run_df.setStyleSheet("font-weight: bold")

        self.combo_fluid = QComboBox()
        self.combo_fluid.setEditable(True)

        self.tbox_comment = QLineEdit()

        btn_preview_run_df= QPushButton("Preview")
        btn_preview_run_df.clicked.connect(self.preview_run_df)
        btn_preview_run_df.setFixedWidth(btn_width)

        hbox_run_df = QHBoxLayout()
        hbox_run_df.addStretch(2)
        hbox_run_df.addWidget(QLabel("Fluid"))
        hbox_run_df.addWidget(self.combo_fluid, stretch=1)
        hbox_run_df.addWidget(QLabel("Comment"))
        hbox_run_df.addWidget(self.tbox_comment, stretch=1)
        hbox_run_df.addWidget(btn_preview_run_df)

        hbox_run_df_margins = QHBoxLayout()
        # hbox_run_df.addWidget(label_run_df)
        hbox_run_df_margins.addStretch(1)
        hbox_run_df_margins.addLayout(hbox_run_df, stretch=10)
        hbox_run_df_margins.addStretch(1)

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

        self.progbar = QProgressBar()
        self.progbar.setMaximum(100)
        self.proglabel = QLabel("00:00 / 00:00")
        self.progtimer = QTimer()
        self.elapsed_time = 0
        self.estimated_total_time = 0
        self.progtimer.timeout.connect(self.increment_elapsed_time)

        self.plot = PlotCanvasBasic()

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.proglabel)
        hbox_run.addWidget(self.progbar)
        hbox_run.addWidget(self.btn_run)
        hbox_run.addWidget(self.btn_pause)
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
        vbox.addLayout(hbox_run_df_margins)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_output)
        vbox.addLayout(hbox_output)
        vbox.addWidget(self.plot)
        # vbox.addLayout(hbox_run)
        vbox.addStretch()

        self.setLayout(vbox)

    def sizeHint(self):
        return QSize(840, 600)

    def generate_run_df(self):
        self.run_df = csv.generate_run_df(self.setup, fluid=self.combo_fluid.currentText())
        self.run_df['comment'] = self.tbox_comment.text()

    def preview_run_df(self):
        self.generate_run_df()
        self.runTable = MetaTable(self.run_df, "Run List DataFrame")
        self.runTable.show()


    def run_measurements(self):

        merge = self.cbox_merge.isChecked()
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
        self.elapsed_time = 0
        self.progtimer.start(100)
        self.worker.finished.connect(self.run_complete)
        self.worker.progress.connect(self.set_progress)
        self.worker.plotdata.connect(self.update_plot)

    def set_progress(self, progress):
        self.progbar.setValue(progress)
        max = self.progbar.maximum()
        measure_time = self.elapsed_time / progress
        self.estimated_total_time =  round(max * measure_time, 1)
        
    def increment_elapsed_time(self):
        self.elapsed_time += 0.1
        elapsed = time.strftime('%M:%S', time.gmtime(self.elapsed_time))
        total = time.strftime('%M:%S', time.gmtime(self.estimated_total_time))
        self.proglabel.setText(f"{elapsed} / {total}")

    def update_plot(self, plotdata):
        title = plotdata[1]
        data = plotdata[0]
        self.plot.set_data(data, title=title, ylim=[-10,120])

    def run_complete(self, status):
        self.btn_run.setEnabled(True)
        self.progbar.reset()
        self.progtimer.stop()
        self.btn_pause.setText('Pause')
        self.run_finished.emit(status)
        logging.info(status)

    def pause_resume(self):
        if self.thread:
            if self.btn_pause.text() == "Pause":
                self.worker.pause = True
                self.progtimer.stop()
                self.btn_pause.setText('Resume')
            else:
                self.worker.pause = False
                self.progtimer.start(100)
                self.btn_pause.setText('Pause')
        
    def stop_measurements(self):
        if self.thread:
            self.worker.stop_requested = True
            self.progtimer.stop()

    def setup_changed(self, setup):
        logging.debug(f"measureTab: got new setup {setup['name']}")
        self.setup = setup

        # Update the fluid options
        fluids = setup['input_config']['fluids']
        self.combo_fluid.clear()
        self.combo_fluid.addItems(fluids)

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
    window = MeasureTab(measure_func=csv.dummy_measurement)
    setup = csv.get_default_setup()
    window.setup_changed(setup)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())

