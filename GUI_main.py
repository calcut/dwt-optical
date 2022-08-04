from email.errors import CloseBoundaryNotFoundDefect
import sys
import logging
import os

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QCoreApplication, QRect, QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMainWindow, QGridLayout, QApplication, QWidget, QTableView,
QCheckBox, QVBoxLayout, QFileDialog, QPushButton, QLabel, QPlainTextEdit, QTabWidget, QSplitter)
from GUI_commonWidgets import SetupBrowse
from GUI_measureTab import MeasureTab
from GUI_singleMeasureTab import SingleMeasureTab

import lib.csv_helpers as csv
from GUI_Logging import GUILogger
from GUI_importTab import ImportTab
from GUI_exportTab import ExportTab
from GUI_hardwareControl import HardwareControl

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        btn_width = 80
        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(1024, 1024)

        vbox = QVBoxLayout(centralwidget)
        vbox.setObjectName(u"verticalLayout")

        splitter = QSplitter(Qt.Vertical)



        self.log = GUILogger(self)
        self.hardwareTab = HardwareControl()
        self.singleMeasureTab = SingleMeasureTab(measure_func=self.hardwareTab.measure)
        self.measureTab = MeasureTab(measure_func=self.hardwareTab.measure)
        self.importTab = ImportTab()
        self.exportTab = ExportTab()

        setupBrowse = SetupBrowse()
        setupBrowse.new_setup.connect(self.singleMeasureTab.setup_changed)
        setupBrowse.new_setup.connect(self.measureTab.setup_changed)
        setupBrowse.new_setup.connect(self.importTab.setup_changed)
        setupBrowse.new_setup.connect(self.exportTab.setup_changed)
        setupBrowse.new_setup.connect(self.hardwareTab.spectrometerControl.setup_changed)
        setupBrowse.new_setup.emit(setupBrowse.setup)

        # Allows the output tab to immediately update the combo boxes after a measurement run is complete.
        self.measureTab.run_finished.connect(self.exportTab.metaFilter.setup_changed)

        self.setupTab = QWidget()
        self.runTab = QWidget()

        # Add tab to the main tab widget, and give it a label
        tabWidget = QTabWidget(centralwidget)
        tabWidget.addTab(self.hardwareTab, "Hardware")
        tabWidget.addTab(self.singleMeasureTab, "Single Measure")
        tabWidget.addTab(self.measureTab, "Batch Measure")
        tabWidget.addTab(self.importTab, "Import")
        tabWidget.addTab(self.exportTab, "Export")


        splitter.addWidget(tabWidget)
        splitter.addWidget(self.log)
        splitter.setStretchFactor(0,0)
        splitter.setStretchFactor(1,1)

        vbox.addWidget(setupBrowse)
        vbox.addWidget(splitter)

        self.setWindowTitle("Optical Tongue Interface")
        self.show()
 

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    app.setWindowIcon(QtGui.QIcon(":/icons/full-spectrum.png"))
    sys.exit(app.exec())

