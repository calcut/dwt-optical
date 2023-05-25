import sys
import os
from PySide6.QtWidgets import QLabel, QWidget
import matplotlib
from matplotlib.pyplot import xlabel
import mplcursors
matplotlib.use('Qt5Agg')

import pandas as pd
import logging

from PySide6 import QtCore, QtWidgets
import pyqtgraph as pg


import signal
import numpy as np

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
    
    def set_data(self, df, title=None, info=None, legend_limit=15, stats_df=None):
        numlines = len(df.columns)

        if numlines > legend_limit:
            self.legend_visible = False
        else:
            self.legend_visible = True

        if numlines > 500:
            msg = QtWidgets.QMessageBox()
            ret = msg.information(self,'', (f"This will plot {numlines} lines,"
             +" which may take some time.\n\nContinue?"), msg.Yes | msg.No)

            if ret == msg.No:
                return

        if title is not None:
            self.common_info.setText(title)

        if info is not None:
            self.process_info.setText(info)

        logging.debug(f'Plotting {numlines} lines')
        self.canvas.axes.cla()
        df.plot(ax=self.canvas.axes,
                title=title,
                # x='wavelength', 
                xlabel = 'Wavelength (nm)',
                ylabel = 'Transmission (%)',
                legend = self.legend_visible)

        self.canvas.draw()
        self.canvas.mpl_connect('pick_event', self.onpick)
        # self.canvas.mpl_connect("motion_notify_event", self.hover)



        lines = self.canvas.axes.get_lines()
        for line in lines:
            line.set_picker(True)
            line.pickradius=1
            color = line.get_color()
            line.set_color(color+'ff')

        self.ax = self.canvas.axes

        if stats_df is not None:
            try:
                trans = df[df.columns[0]]
                row = stats_df.index[0]
                inflection_min = stats_df.loc[row]['Infl_L']
                inflection_max = stats_df.loc[row]['Infl_R']
                fwhm = stats_df.loc[row]['FWHM']
                peak = stats_df.loc[row]['Peak']
                height = stats_df.loc[row]['Height']

                # Recalculate some FWHM details to position lines on plot
                min = trans.min()
                half_max=min+height/2
                hm_range = trans[trans <= half_max].index
                
                self.ax.axvline(x=peak, label=f"Peak={peak}nm", color='r')
                self.ax.axvline(x=inflection_min, label=f"Infl_L={inflection_min}nm", color='c')
                self.ax.axvline(x=inflection_max, label=f"Infl_R={inflection_max}nm", color='c')
                self.ax.hlines(y=half_max, xmin=hm_range[0], xmax=hm_range[-1], label=f"FWHM={fwhm}nm", color='m')
                self.ax.axhline(y=min+height, label=f"Height={height}%", color='g')
                # self.canvas.draw()
            except Exception as e:
                logging.warning(f'Could not plot stats: {e}') 

        if self.legend_visible:
            for legline, pltline in zip(self.ax.legend().get_lines(), lines):
                legline.set_picker(True)  # Enable picking on the legend lines.
                legline.pickradius=5
                # Keep 2 dictionaries to be able to identify  plot lines from their
                # legend lines and vice versa
                self.pltline_dict[pltline] = legline
                self.legline_dict[legline] = pltline

        self.canvas.draw()
        self.show()
        self.plot_visible = True

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

    def set_data(self, df, title=None, ylim=None, xlim=None):
        self.canvas.axes.cla()
        df.plot(ax=self.canvas.axes,
                # x='wavelength', 
                title = title,
                xlabel = self.xlabel,
                ylabel = self.ylabel,
                legend = self.legend_visible)

        if xlim:
            self.canvas.axes.set_xlim(xlim)
        if ylim:
            self.canvas.axes.set_ylim(ylim)
        self.canvas.draw()

class Pyqtgraph_canvas(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        axis = pg.DateAxisItem(orientation='bottom')

        self.line = pg.PlotCurveItem(clear=True, pen="g")

        self.xData = np.array([])
        self.yData = np.array([])

        self.graphWidget = pg.PlotWidget(
            labels={'left': 'Peak Wavelength (nm)'},
            axisItems={'bottom': axis}
        )
        self.graphWidget.addItem(self.line)
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.graphWidget)

        self.setLayout(vbox)
        self.resize(1000,400)

    def append_datapoint(self, x, y):

        self.yData = np.append(self.yData, y)
        self.xData = np.append(self.xData, x)
        self.line.setData(x=self.xData, y=self.yData)


if __name__ == "__main__":

    import lib.json_setup as json_setup
    import lib.data_process

    with open('rootpath_cache', 'r') as f:
        rootpath = f.readline().strip()
    os.chdir(rootpath)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    setup_path = "setup/20220818_s44076.json"
    setup = json_setup.json_to_dict(setup_path)
    meta_df = csv.read_metadata(setup)
    selection_df = csv.select_from_metadata('fluid', 'Air', meta_df)
    selection_df = csv.select_from_metadata('element', 'A01', meta_df)
    
    df, title = csv.merge_dataframes(setup, selection_df)

    dp = lib.data_process.DataProcessor()
    dp.apply_avg_repeats = True
    dp.apply_normalise = False
    dp.apply_smooth = False
    dp.apply_trim = True
    dp.apply_interpolate = False
    dp.apply_round = False
    df = dp.process_dataframe(df)
    stats_df = dp.get_stats(df)
    # stats_df = None
    # plot.set_data(df, title, stats_df=stats_df)
    # plot.update()

   
    plot = Pyqtgraph_canvas()

    plot.show()

    print(f'{stats_df=}')

    sys.exit(app.exec())


