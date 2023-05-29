from email.errors import CloseBoundaryNotFoundDefect
import sys
import logging
import os
import signal

from PySide6 import QtGui, QtWidgets, QtCore
from GUI_commonWidgets import SetupBrowse
from GUI_measureTab import MeasureTab
from GUI_episodicTab import EpisodicTab
from GUI_singleMeasureTab import SingleMeasureTab

import lib.csv_helpers as csv
from GUI_Logging import GUILogger
from GUI_importTab import ImportTab
from GUI_exportTab import ExportTab
from GUI_hardwareControl import HardwareControl

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        btn_width = 80
        centralwidget = QtWidgets.QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(1024, 768)

        vbox = QtWidgets.QVBoxLayout(centralwidget)
        vbox.setObjectName(u"verticalLayout")

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)



        self.log = GUILogger(self)
        self.hardwareTab = HardwareControl()
        self.singleMeasureTab = SingleMeasureTab(measure_func=self.hardwareTab.measure)
        self.episodicTab = EpisodicTab(measure_func=self.hardwareTab.measure_no_move)
        self.measureTab = MeasureTab(measure_func=self.hardwareTab.measure)
        self.importTab = ImportTab()
        self.exportTab = ExportTab()

        setupBrowse = SetupBrowse()
        setupBrowse.new_setup.connect(self.singleMeasureTab.setup_changed)
        setupBrowse.new_setup.connect(self.episodicTab.setup_changed)
        setupBrowse.new_setup.connect(self.measureTab.setup_changed)
        setupBrowse.new_setup.connect(self.importTab.setup_changed)
        setupBrowse.new_setup.connect(self.exportTab.setup_changed)
        setupBrowse.new_setup.connect(self.hardwareTab.spectrometerControl.setup_changed)
        setupBrowse.new_setup.connect(self.hardwareTab.stageControl.setup_changed)
        setupBrowse.new_setup.emit(setupBrowse.setup)

        # Allows the output tab to immediately update the combo boxes after a measurement run is complete.
        self.measureTab.run_finished.connect(setupBrowse.update_setup_json)
        self.episodicTab.run_finished.connect(setupBrowse.update_setup_json)

        splitter.addWidget(setupBrowse)
        splitter.addWidget(self.log)
        splitter.setStretchFactor(0,0)
        splitter.setStretchFactor(1,1)

        # Add tab to the main tab widget, and give it a label
        self.tabWidget = QtWidgets.QTabWidget(centralwidget)
        self.tabWidget.addTab(splitter, "Setup and Log")
        self.tabWidget.addTab(self.hardwareTab, "Hardware")
        self.tabWidget.addTab(self.singleMeasureTab, "Single Measure")
        self.tabWidget.addTab(self.episodicTab, "Episodic Measure")
        self.tabWidget.addTab(self.measureTab, "Batch Measure")
        self.tabWidget.addTab(self.importTab, "Import")
        self.tabWidget.addTab(self.exportTab, "Export")

        self.log.new_icon.connect(self.change_log_icon)
        self.change_log_icon()


        vbox.addWidget(self.tabWidget)

        self.setWindowTitle("Optical Tongue Interface")
        self.show()

    def change_log_icon(self):
        self.tabWidget.setTabIcon(0, self.log.pixmap)


if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    app.setWindowIcon(QtGui.QIcon(":/icons/full-spectrum.png"))
    sys.exit(app.exec())

