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
from GUI_tableView import ExportTable
import lib.csv_helpers as csv
import lib.data_process as dp


class DataProcess(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.df = None
        self.title = None
        self.process_info = None

        self.selection_df = None
        self.datadir = None

        self.plotcanvas = PlotCanvas()

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

        row_normalise = 0
        self.normalise = QCheckBox()
        self.grid.addWidget(self.normalise, row_normalise, 0)
        self.grid.addWidget(QLabel("Normalise"), row_normalise, 1, alignment=Qt.AlignLeft)

        row_smooth = 1
        self.smooth = QCheckBox()
        self.grid.addWidget(self.smooth, row_smooth, 0)
        self.grid.addWidget(QLabel("Smooth (rolling mean)"), row_smooth, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(QLabel("SmoothPoints:"), row_smooth, 2, alignment=Qt.AlignRight)
        self.smoothpoints_box = QSpinBox()
        self.smoothpoints_box.setValue(3)
        self.grid.addWidget(self.smoothpoints_box, row_smooth, 3)
        
        row_trim = 2
        self.trim = QCheckBox()
        self.grid.addWidget(self.trim, row_trim, 0)
        self.grid.addWidget(QLabel("Wavelength Trim"), row_trim, 1, alignment=Qt.AlignLeft)
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

    # def set_data_directly(self, df, title=None):
    #     self.df = df
    #     self.df_orig = self.df.copy()
    #     self.title = title
    #     self.title_orig = title

    def set_data_from_selection_df(self):
        if self.selection_df is None:
            logging.error('Please select data first')
        else:
            logging.info('Merging selected data into single dataframe')
            self.df, self.title = csv.merge_dataframes(self.selection_df, self.datadir)
            self.df_orig = self.df.copy()
            self.title_orig = self.title
            logging.info(f'Selected data contains {len(self.df.columns)-1} measurements')

    def metapath_changed(self, metapath):
        self.datadir = os.path.dirname(metapath)

    def selection_df_changed(self, selection_df):
        self.df = None
        self.title = None
        self.selection_df = selection_df

    def apply(self):
      
        if self.df is None:
            self.set_data_from_selection_df()

        # This prevents the same procesing being re-applied every time
        # button is pressed
        self.df = self.df_orig.copy()
        self.process_info=''

        if self.normalise.isChecked():
            logging.info('Normalising')
            self.df = dp.normalise(self.df)
            self.process_info += 'Normalised\n'

        if self.smooth.isChecked():
            smoothpoints = self.smoothpoints_box.value()
            logging.info(f'Smoothing using {smoothpoints} points')
            self.df = dp.smooth(self.df, smoothpoints)
            self.process_info += f'Smoothed using {smoothpoints} points\n'


        if self.trim.isChecked():
            wl_min = self.trim_min_box.value()
            wl_max = self.trim_max_box.value()
            logging.info(f'Trimming using wavelength from {wl_min} to {wl_max}')
            self.df = dp.trim(self.df, wl_min, wl_max)
            self.process_info += f'Wavelength Trimmed from {wl_min}nm to {wl_max}nm\n'


        if self.interpolate.isChecked():
            samplerate = self.interpolate_sr_box.value()
            logging.info(f'Interpolating to rate of {samplerate}nm')
            self.df = dp.interpolate(self.df, samplerate)
            self.process_info += f'Interploated to rate of {samplerate}nm\n'
        
        self.process_info = self.process_info[:-1]


        if self.plotcanvas.plot_visible:
            self.plotcanvas.set_data(self.df, self.title, self.process_info)

        
    def preview(self):
        title = 'Processed Data'
        try:
            self.selectedTable = ExportTable(self.df, title)
            self.selectedTable.show()
        except AttributeError:
            logging.error("Please select data first")

    def plot(self):
        try:
            self.plotcanvas.set_data(self.df, self.title, self.process_info)
            # self.plotcanvas.show()
        except AttributeError:
            logging.error("Please Apply filter first")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = DataProcess()

    meta_tbox = './imported/index.tsv'

    meta_df = csv.read_metadata(meta_tbox)
    metapath = os.path.abspath(meta_tbox)
    datadir = os.path.dirname(metapath)
    selection_df = csv.filter_by_metadata('element', '01', meta_df)
    selection_df = csv.filter_by_metadata('fluid', 'Beer', selection_df)
    df, title = csv.merge_dataframes(selection_df, datadir)

    # window.set_data(df, title)
    window.selection_df = selection_df
    window.datadir = os.path.dirname(metapath) 
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())