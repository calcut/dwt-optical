import sys
import os
from PySide6.QtWidgets import QLabel
import matplotlib
import mplcursors
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
        self.canvas = MplCanvas(self, width=8, height=5, dpi=100)
        self.plot_visible = False
        # plot the pandas DataFrame, passing in the
        # matplotlib Canvas axes.
        # df.plot(ax=sc.axes)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setIconSize(QtCore.QSize(22,22))

        self.common_info = QLabel('')
        self.process_info = QLabel('')
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.common_info)
        hbox.addWidget(self.process_info)


        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas, stretch = 1)
        layout.addLayout(hbox)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        self.plot_visible = False
        event.accept()

    def onpick(self, event):
        line = event.artist
        print(line)
        if not isinstance(line, matplotlib.lines.Line2D):
            print(line)
        else:

            label = line.get_label()
            color = line.get_color()
            RGB = color[:-2]
            button = event.mouseevent.button
            if button == 1:
                #  Left click shows the line and adds it to legend
                line.set_color(RGB+'ff')
                if label[0] == '_':
                    line.set_label(label[1:])
            if button == 3:
                #  Right click grays out the line and hides from legend
                line.set_color(RGB+'20')
                if label[0] != '_':
                    line.set_label('_'+label)

            # Refresh the legend and canvas
            # legend = self.ax.legend()
            for legline in self.ax.legend().get_lines():
                legline.set_picker(True)  # Enable picking on the legend lines.
            self.canvas.draw_idle()

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            # cont, ind = span.contains(event)
            # if cont:
            self.annot.xy = (event.xdata, event.ydata)
            self.annot.set_visible(True)
            self.canvas.draw_idle()
            # else:
            if vis:
                self.annot.set_visible(False)
                self.canvas.draw_idle()
    
    def set_data(self, df, title=None, info=None):
        lines = len(df.columns) -1
        if lines > 15:
            legend = False
        else:
            legend = True

        if lines > 100:
            msg = QtWidgets.QMessageBox()
            ret = msg.information(self,'', (f"This will plot {lines} lines,"
             +" which may take some time.\n\nContinue?"), msg.Yes | msg.No)

            if ret == msg.No:
                return

        if title is not None:
            self.common_info.setText(title)

        if info is not None:
            self.process_info.setText(info)

        logging.info(f'Plotting {lines} lines')
        self.canvas.axes.cla()
        df.plot(ax=self.canvas.axes,
                title=title,
                x='wavelength', 
                xlabel = 'Wavelength (nm)',
                ylabel = 'Transmission (%)',
                legend = legend)
        self.canvas.draw()
        self.canvas.mpl_connect('pick_event', self.onpick)
        # self.canvas.mpl_connect("motion_notify_event", self.hover)
        self.show()
        self.plot_visible = True


        lines = plot.canvas.axes.get_lines()
        for line in lines:
            print(line)
            line.set_picker(True)
            line.pickradius=1
            color = line.get_color()
            line.set_color(color+'ff')

        self.ax = plot.canvas.axes
        

        for legline in self.ax.legend().get_lines():
            legline.set_picker(True)  # Enable picking on the legend lines.




        crs = mplcursors.cursor(plot.canvas.axes, hover=True)
        crs.connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))

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
    df, title = csv.merge_dataframes(selection_df, path)

    plot.set_data(df, title)
    plot.update()


    



    plot.resize(1024, 768)
    plot.show()

    sys.exit(app.exec())


