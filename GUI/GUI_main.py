import sys

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QCoreApplication, QRect
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMainWindow, QGridLayout, QApplication, QWidget,
    QCheckBox, QVBoxLayout, QFileDialog, QPushButton, QLabel)

from layout_colorwidget import Color
import resources_rc

from mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(958, 773)
        self.generateTab()
        self.importTab()
        # self.assignWidgets()

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

    def importTab(self):

        # New Widget (to be used as a tab)
        self.ui.tab_import = QWidget()
        self.ui.tab_import.setObjectName(u"tab_import")

        # Make a Vertical layout within the new tab
        vbox = QVBoxLayout(self.ui.tab_import)

        label_title = QLabel("Import existing csv/tsv files, extract metadata from filenames")
        label_input = QLabel("Input Directory:")
        label_output = QLabel("Output Directory:")
        self.ui.tbox_input = QLineEdit()
        self.ui.tbox_output = QLineEdit()

        browse_input = QPushButton("Browse")
        browse_input.clicked.connect(self.get_input_dir)

        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output_dir)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_input)
        hbox_input.addWidget(self.ui.tbox_input)
        hbox_input.addWidget(browse_input)

        hbox_output = QHBoxLayout()
        hbox_output.addWidget(label_output)
        hbox_output.addWidget(self.ui.tbox_output)
        hbox_output.addWidget(browse_output)

        vbox.addWidget(label_title)
        vbox.addLayout(hbox_input)
        vbox.addLayout(hbox_output)
        vbox.addStretch()


    
        # self.ui.VLayoutWidget_import = QWidget(self.ui.tab_x)
        # self.ui.VLayoutWidget_import.setObjectName(u"VLayoutWidget_import")
        # self.ui.VLayoutWidget_import.setGeometry(QRect(10, 10, 450, 200))

        # self.ui.gridLayout_x = QGridLayout(self.ui.VLayoutWidget_import)
        # self.ui.gridLayout_x.setObjectName(u"gridLayout_x")
        # self.ui.gridLayout_x.setContentsMargins(0, 0, 0, 0)
        # self.ui.boxes=[]
        # for i in range(4):
        #     self.ui.boxes.append(QCheckBox(self.ui.tab_x))
        #     self.ui.gridLayout_x.addWidget(self.ui.boxes[i], i, i, 1, 1)
        #     self.ui.boxes[i].toggled.connect(self.checkboxSlot)

        # Add tab to the main tab widget, and give it a label
        self.ui.tabWidget.addTab(self.ui.tab_import, "")
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_import), "import")
        
    def get_input_dir(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        self.ui.tbox_input.setText(dirname)

    def get_output_dir(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        self.ui.tbox_output.setText(dirname)

app = QApplication(sys.argv)
w = MainWindow()
app.setWindowIcon(QtGui.QIcon(":/icons/full-spectrum.png"))
app.exec()

