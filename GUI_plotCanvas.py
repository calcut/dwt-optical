import sys
import os
from PySide6.QtWidgets import QLabel, QWidget
import matplotlib
from matplotlib.pyplot import xlabel
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
        self.legend_visible = True
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

        self.pltline_dict = {} # Will map plot lines to legend lines.
        self.legline_dict = {} # Will map legend lines to plot lines.

    def closeEvent(self, event):
        self.plot_visible = False
        event.accept()

    def onpick(self, event):
        picked_line = event.artist
        if isinstance(picked_line, matplotlib.lines.Line2D):
            # logging.debug(f'picked line object: {picked_line}')
            # Convert a legend line to the original line

            if self.legend_visible:
                # Want to find both the plotline and associated legend line
                # This is done by trying to lookup in both dictionaries
                try: 
                    legline = self.pltline_dict[picked_line]
                    pltline = picked_line
                    # logging.debug(f'got {legline} from plotline')
                except KeyError:
                    pltline = self.legline_dict[picked_line]
                    legline = picked_line
                    # logging.debug(f'got {pltline} from legline')
                except Exception as e:
                    print(e)
                    print('dict lookup failed')



                button = event.mouseevent.button
                if button == 1:
                    #  Left click shows the line
                    pltline.set_alpha(1)
                    legline.set_alpha(1)
                if button == 3:
                    #  Right click grays out the line
                    pltline.set_alpha(0.1)
                    legline.set_alpha(0.1)
            
            else: 
                button = event.mouseevent.button
                if button == 1:
                    #  Left click shows the line
                    picked_line.set_alpha(1)

                if button == 3:
                    #  Right click grays out the line
                    picked_line.set_alpha(0.1)

            self.canvas.draw_idle()

    # def hover(self, event):
    #     vis = self.annot.get_visible()
    #     if event.inaxes == self.ax:
    #         # cont, ind = span.contains(event)
    #         # if cont:
    #         self.annot.xy = (event.xdata, event.ydata)
    #         self.annot.set_visible(True)
    #         self.canvas.draw_idle()
    #         # else:
    #         if vis:
    #             self.annot.set_visible(False)
    #             self.canvas.draw_idle()
    
    def set_data(self, df, title=None, info=None, legend_limit=15):
        lines = len(df.columns) -1

        if lines > legend_limit:
            self.legend_visible = False
        else:
            self.legend_visible = True

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
                legend = self.legend_visible)
        self.canvas.draw()
        self.canvas.mpl_connect('pick_event', self.onpick)
        # self.canvas.mpl_connect("motion_notify_event", self.hover)
        self.show()
        self.plot_visible = True


        lines = self.canvas.axes.get_lines()
        for line in lines:
            line.set_picker(True)
            line.pickradius=1
            color = line.get_color()
            line.set_color(color+'ff')

        self.ax = self.canvas.axes
        
        if self.legend_visible:
            for legline, pltline in zip(self.ax.legend().get_lines(), lines):
                legline.set_picker(True)  # Enable picking on the legend lines.
                legline.pickradius=5
                # Keep 2 dictionaries to be able to identify  plot lines from their
                # legend lines and vice versa
                self.pltline_dict[pltline] = legline
                self.legline_dict[legline] = pltline

        # crs = mplcursors.cursor(self.canvas.axes, hover=True)
        crs = mplcursors.cursor(self.canvas.axes)
        
        # Uncomment to only print the label (not the XY values)
        # crs.connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))

class PlotCanvasBasic(QWidget):
    #Simple version for checking light / dark references

    def __init__(self, ylabel='Transmission (%)', xlabel='Wavelength (nm)'):
        QWidget.__init__(self)

        self.xlabel = xlabel
        self.ylabel = ylabel

        # hide debug messages about font finding from MPL
        logging.getLogger('matplotlib.font_manager').disabled = True

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.canvas = MplCanvas(self, width=8, height=5, dpi=80)
        self.plot_visible = False
        self.legend_visible = True

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)

    def set_data(self, df, title=None):
        self.canvas.axes.cla()
        df.plot(ax=self.canvas.axes,
                x='wavelength', 
                title = title,
                xlabel = self.xlabel,
                ylabel = self.ylabel,
                legend = self.legend_visible)
        self.canvas.draw()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    plot = PlotCanvas()

    meta_tbox = './imported/index.txt'

    meta_df = csv.read_metadata(meta_tbox)
    metapath = os.path.abspath(meta_tbox)
    path = os.path.dirname(metapath)
    selection_df = csv.select_from_metadata('element', '01', meta_df)
    selection_df = csv.select_from_metadata('fluid', 'Beer', selection_df)
    df, title = csv.merge_dataframes(selection_df, path)

    plot.set_data(df, title)
    plot.update()


    



    plot.resize(1024, 768)
    plot.show()

    sys.exit(app.exec())


