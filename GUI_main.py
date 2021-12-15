import sys
from time import sleep
import logging
import os

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QCoreApplication, QRect, QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMainWindow, QGridLayout, QApplication, QWidget, QTableView,
QCheckBox, QVBoxLayout, QFileDialog, QPushButton, QLabel, QPlainTextEdit, QTabWidget, QSplitter)
from GUI_surfacesTab import SurfacesTab

import lib.csv_helpers as csv
from GUI_Logging import GUILogger
from GUI_importTab import ImportTab
from GUI_exportTab import ExportTab

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(1024, 900)

        vbox = QVBoxLayout(centralwidget)
        vbox.setObjectName(u"verticalLayout")

        splitter = QSplitter(Qt.Vertical)



        self.log = GUILogger(self)
        self.importTab = ImportTab()
        self.surfacesTab = SurfacesTab()
        self.exportTab = ExportTab()

        self.setupTab = QWidget()
        self.runTab = QWidget()

        # Add tab to the main tab widget, and give it a label
        tabWidget = QTabWidget(centralwidget)
        tabWidget.addTab(self.setupTab, "Setup")
        tabWidget.addTab(self.runTab, "Manual Run")
        tabWidget.addTab(self.importTab, "Import")
        tabWidget.addTab(self.surfacesTab, "Surface Chemistry")
        tabWidget.addTab(self.exportTab, "Export")


        splitter.addWidget(tabWidget)
        splitter.addWidget(self.log)
        vbox.addWidget(splitter)

        self.show()


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

    app = QApplication(sys.argv)
    w = MainWindow()
    app.setWindowIcon(QtGui.QIcon(":/icons/full-spectrum.png"))
    sys.exit(app.exec())

