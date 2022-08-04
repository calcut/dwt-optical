import os
import sys
from PySide6 import QtWidgets
import pandas as pd
import PySide6.QtWidgets
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QFrame,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QSpinBox)
import logging
from GUI_plotCanvas import PlotCanvas
from GUI_tableView import PreviewTable
import lib.csv_helpers as csv
import lib.data_process


class DataProcess(QWidget):

    request_selection_df = Signal()

    def __init__(self):
        QWidget.__init__(self)

        self.df = None
        self.title = None
        self.process_info = None

        self.selection_df = None
        self.setup = None

        self.plotcanvas = PlotCanvas()
        self.selectedTable = None
        self.dp = lib.data_process.DataProcessor()

        self.setObjectName(u"DataProcess")
        vbox = QVBoxLayout()

        label = QLabel("Apply Processing Functions to selected Data:")

        btn_width = 80
        btn_apply = QPushButton("Apply")
        btn_apply.clicked.connect(self.apply)
        btn_apply.setFixedWidth(btn_width)

        btn_preview = QPushButton("Preview")
        btn_preview.clicked.connect(self.preview)
        btn_preview.setFixedWidth(btn_width)


        btn_plot= QPushButton("Plot")
        btn_plot.clicked.connect(self.plot)
        btn_plot.setFixedWidth(btn_width)


        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(btn_apply)
        hbox.addWidget(btn_preview)
        hbox.addWidget(btn_plot)

        vbox.addWidget(label)
        vbox.addLayout(self.grid)
        vbox.addLayout(hbox)
        vbox.addStretch()
        self.setLayout(vbox)

        self.grid.setColumnStretch(0,0) #Enable Checkbox
        self.grid.setColumnStretch(1,10) #Function Name
        self.grid.setColumnStretch(2,5) #Function Arg1 Name
        self.grid.setColumnStretch(3,5) #Function Arg1 Value
        self.grid.setColumnStretch(4,5) #Function Arg2 Name
        self.grid.setColumnStretch(5,5) #Function Arg2 Value
        self.grid.setColumnStretch(6,5) #Function Arg3 Name
        self.grid.setColumnStretch(7,5) #Function Arg3 Value

        row_avg = 0
        self.avg_reps = QCheckBox()
        self.grid.addWidget(self.avg_reps, row_avg, 0)
        self.grid.addWidget(QLabel("Average Measurement Repeats"), row_avg, 1, alignment=Qt.AlignLeft)
    
        row_trim = 1
        self.trim = QCheckBox()
        self.grid.addWidget(self.trim, row_trim, 0)
        self.grid.addWidget(QLabel("Wavelength Range"), row_trim, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(QLabel("Min(nm):"), row_trim, 2, alignment=Qt.AlignRight)
        self.trim_min_box = QSpinBox()
        self.trim_min_box.setRange(0,9999)
        self.trim_min_box.setValue(540)
        self.grid.addWidget(self.trim_min_box, row_trim, 3)
        self.grid.addWidget(QLabel("Max(nm):"), row_trim, 4, alignment=Qt.AlignRight)
        self.trim_max_box = QSpinBox()
        self.trim_max_box.setRange(0,9999)
        self.trim_max_box.setValue(730)
        self.grid.addWidget(self.trim_max_box, row_trim, 5)

        row_smooth = 2
        self.smooth = QCheckBox()
        self.grid.addWidget(self.smooth, row_smooth, 0)
        self.grid.addWidget(QLabel("Smooth (rolling mean)"), row_smooth, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(QLabel("SmoothPoints:"), row_smooth, 2, alignment=Qt.AlignRight)
        self.smoothpoints_box = QSpinBox()
        self.smoothpoints_box.setValue(3)
        self.grid.addWidget(self.smoothpoints_box, row_smooth, 3)
        
        row_interpolate = 3
        self.interpolate = QCheckBox()
        self.grid.addWidget(self.interpolate, row_interpolate, 0)
        self.grid.addWidget(QLabel("Interpolate"), row_interpolate, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(QLabel("SampleRate (nm):"), row_interpolate, 2, alignment=Qt.AlignRight)
        self.interpolate_sr_box = QtWidgets.QDoubleSpinBox()
        self.interpolate_sr_box.decimals = 1
        self.interpolate_sr_box.setRange(0.01,9999)
        self.interpolate_sr_box.setValue(1)
        self.interpolate_sr_box.setStepType(QtWidgets.QAbstractSpinBox.StepType(1))
        self.grid.addWidget(self.interpolate_sr_box, row_interpolate, 3)

        row_normalise = 4
        self.normalise = QCheckBox()
        self.grid.addWidget(self.normalise, row_normalise, 0)
        self.grid.addWidget(QLabel("Normalise"), row_normalise, 1, alignment=Qt.AlignLeft)

        row_round = 5
        self.round = QCheckBox()
        self.grid.addWidget(self.round, row_round, 0)
        self.grid.addWidget(QLabel("Round"), row_round, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(QLabel("Decimal Places:"), row_round, 2, alignment=Qt.AlignRight)
        self.round_box = QtWidgets.QSpinBox()
        self.round_box.setValue(3)
        self.round_box.setStepType(QtWidgets.QAbstractSpinBox.StepType(1))
        self.grid.addWidget(self.round_box, row_round, 3)

    def set_data_from_selection_df(self):
        if self.selection_df is None:
            logging.error('Please select data first')
        else:
            logging.info('Merging selected data into single dataframe')
            self.df, self.title = csv.merge_dataframes(self.setup, self.selection_df)
            self.df_orig = self.df.copy()
            self.title_orig = self.title
            logging.info(f'Selected data contains {len(self.df.columns)-1} measurements')

    def setup_changed(self, setup):
        self.setup = setup
        self.selection_df_changed(None)

    def selection_df_changed(self, selection_df):
        self.df = None
        self.title = None
        self.selection_df = selection_df

    def apply(self):
        self.request_selection_df.emit()
      
        if self.df is None:
            self.set_data_from_selection_df()

        if self.df is None:
            logging.error('No data selected for processing')
            return

        # This prevents the same procesing being re-applied every time
        # button is pressed
        self.df = self.df_orig.copy()
        self.process_info=''

        if self.avg_reps.isChecked():
            logging.info('Averging Measurement Repeats')
            self.dp.apply_avg_repeats = True
            self.process_info += 'Measurement Repeats Averaged\n'
        else:
            self.dp.apply_avg_repeats = False

        if self.normalise.isChecked():
            logging.info('Normalising')
            self.dp.apply_normalise = True
            self.process_info += 'Normalised\n'
        else:
            self.dp.apply_normalise = False

        if self.smooth.isChecked():
            smoothpoints = self.smoothpoints_box.value()
            logging.info(f'Smoothing using {smoothpoints} points')
            self.dp.smooth_points = smoothpoints
            self.dp.apply_smooth = True
            self.process_info += f'Smoothed using {smoothpoints} points\n'
        else:
            self.dp.apply_smooth = False

        if self.trim.isChecked():
            wl_min = self.trim_min_box.value()
            wl_max = self.trim_max_box.value()
            logging.info(f'Trimming using wavelength from {wl_min} to {wl_max}')
            self.dp.wavelength_trim_min = wl_min
            self.dp.wavelength_trim_max = wl_max
            self.dp.apply_trim = True
            self.process_info += f'Wavelength Trimmed from {wl_min}nm to {wl_max}nm\n'
        else:
            self.dp.apply_trim = False

        if self.interpolate.isChecked():
            samplerate = self.interpolate_sr_box.value()
            logging.info(f'Interpolating to rate of {samplerate}nm')
            self.dp.interpolate_sampling_rate = samplerate
            self.dp.apply_interpolate = True
            self.process_info += f'Interploated to rate of {samplerate}nm\n'
        else:
            self.dp.apply_interpolate = False

        if self.round.isChecked():
            round_decimals = self.round_box.value()
            logging.info(f'Rounding to {round_decimals} places')
            self.dp.round_decimals = round_decimals
            self.dp.apply_round = True
            self.process_info += f'Rounded to {round_decimals} decimal places\n'
        else:
            self.dp.apply_round = False  

        self.df = self.dp.process_dataframe(self.df)

        # Drop the last newline
        self.process_info = self.process_info[:-1]

        if self.plotcanvas.plot_visible:
            self.plotcanvas.set_data(self.df, self.title, self.process_info)
        
    def preview(self):
        if self.df is None:
            self.apply()

        windowtitle = 'Processed Data'
        print(self.df)
        self.selectedTable = PreviewTable(self.df, windowtitle, 
            common_info= self.title,
            process_info= self.process_info)
        self.selectedTable.show()

    def plot(self):
        self.apply() # Apply latest changes first
        self.plotcanvas.set_data(self.df, self.title, self.process_info)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = DataProcess()

    setup = csv.get_default_setup()

    meta_df = csv.read_metadata(setup)
    selection_df = csv.select_from_metadata('element', '01', meta_df)
    selection_df = csv.select_from_metadata('fluid', 'Beer', selection_df)
    df, title = csv.merge_dataframes(setup, selection_df)

    # window.set_data(df, title)
    window.selection_df = selection_df
    window.setup = setup
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())