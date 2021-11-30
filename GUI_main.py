import sys
from time import sleep
import logging

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QCoreApplication, QRect, QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMainWindow, QGridLayout, QApplication, QWidget,
QCheckBox, QVBoxLayout, QFileDialog, QPushButton, QLabel, QPlainTextEdit, QTabWidget)

import GUI.resources_rc

from GUI.mainwindow import Ui_MainWindow
import lib.csv_helpers as csv
from GUI.GUILogging import GUILogger
from GUI.importTab import ImportTab
from GUI.ExportTab import ExportTab

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(1024, 768)

        verticalLayout = QVBoxLayout(centralwidget)
        verticalLayout.setObjectName(u"verticalLayout")



        self.log = GUILogger(self)

        importFunction = csv.import_dir_to_csv # A bit awkward to to this way, maybe change?
        importTab = ImportTab(importFunction)

        exportFunction= csv.export_dataframes
        exportTab = ExportTab(exportFunction)

        setupTab = QWidget()
        runTab = QWidget()

        # Add tab to the main tab widget, and give it a label
        tabWidget = QTabWidget(centralwidget)
        tabWidget.addTab(setupTab, "Setup")
        tabWidget.addTab(runTab, "Manual Run")
        tabWidget.addTab(importTab.tab, "Import")
        tabWidget.addTab(exportTab.tab, "Export")


        # tabWidget.setTabText(tabWidget.indexOf(importTab.tab), "Import")

                
        verticalLayout.addWidget(tabWidget)
        verticalLayout.addLayout(self.log.logVbox)


        self.show()

    # This slot seems to work as expected here, but not when placed inside the
    # GUILogger class
    # Defines where log messages should be displayed in the GUI.
    @Slot(str)
    def writeLog(self, log_text):
        self.log.logBox.appendHtml(log_text)



    def generateTab(self):

        # New Widget (to be used as a tab)
        self.ui.tab_x = QWidget()
        self.ui.tab_x.setObjectName(u"tab_x")

        # Make a grid layout and position it within the new tab
        self.ui.gridLayoutWidget_x = QWidget(self.ui.tab_x)
        self.ui.gridLayoutWidget_x.setObjectName(u"gridLayoutWidget_x")
        self.ui.gridLayoutWidget_x.setGeometry(QRect(10, 10, 450, 200))

        self.ui.gridLayout_x = QGridLayout(self.ui.gridLayoutWidget_x)
        self.ui.gridLayout_x.setObjectName(u"gridLayout_x")
        self.ui.gridLayout_x.setContentsMargins(0, 0, 0, 0)
        self.ui.boxes=[]
        for i in range(4):
            self.ui.boxes.append(QCheckBox(self.ui.tab_x))
            self.ui.gridLayout_x.addWidget(self.ui.boxes[i], i, i, 1, 1)
            self.ui.boxes[i].toggled.connect(self.checkboxSlot)

        # Add tab to the main tab widget, and give it a label
        self.ui.tabWidget.addTab(self.ui.tab_x, "")
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_x), "abc")
        
    def checkboxSlot(self):
        cbutton = self.sender()
        print(cbutton.isChecked())

    

if __name__ == "__main__":

    orig_stdout = sys.stdout
    app = QApplication(sys.argv)
    w = MainWindow()
    app.setWindowIcon(QtGui.QIcon(":/icons/full-spectrum.png"))
    app.exec()

