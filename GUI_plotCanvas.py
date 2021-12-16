import sys
import os
import matplotlib
matplotlib.use('Qt5Agg')

import pandas as pd
import logging

from PySide6 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import lib.csv_helpers as csv

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.fig.set_tight_layout(True)

class PlotCanvas(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(PlotCanvas, self).__init__(*args, **kwargs)

        # hide debug messages about font finding from MPL
        logging.getLogger('matplotlib.font_manager').disabled = True

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.sc = MplCanvas(self, width=8, height=5, dpi=100)

        # plot the pandas DataFrame, passing in the
        # matplotlib Canvas axes.
        # df.plot(ax=sc.axes)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)
        toolbar.setIconSize(QtCore.QSize(22,22))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()
    
    def set_data(self, meta_df, metapath):

        path = os.path.dirname(metapath)
        df, title = csv.merge_dataframes(meta_df, path)
        df.plot(ax=self.sc.axes,
                title=title,
                x='wavelength', 
                xlabel = 'Wavelength (nm)',
                ylabel = 'Transmission (%)')

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    plot = PlotCanvas()

    meta_tbox = './imported/index.tsv'

    meta_df = csv.read_metadata(meta_tbox)
    metapath = os.path.abspath(meta_tbox)
    path = os.path.dirname(metapath)
    selection_df = csv.filter_by_metadata('element', '01', meta_df)
    selection_df = csv.filter_by_metadata('fluid', 'Beer', selection_df)

    plot.set_data(selection_df, path)


    plot.resize(1024, 768)
    plot.show()
    sys.exit(app.exec())


