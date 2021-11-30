import sys
from multiprocessing import Process, Queue
from time import sleep
import logging

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QCoreApplication, QRect, QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMainWindow, QGridLayout, QApplication, QWidget,
QCheckBox, QVBoxLayout, QFileDialog, QPushButton, QLabel, QPlainTextEdit)

from GUI.layout_colorwidget import Color
import GUI.resources_rc

from GUI.mainwindow import Ui_MainWindow
import lib.csv_helpers as csv

class MyLog(QObject):
    # create a new Signal
    # - have to be a static element
    # - class  has to inherit from QObject to be able to emit signals
    signal = Signal(str)

    # not sure if it's necessary to implement this
    def __init__(self):
        super().__init__()

class CustomLogHandler(logging.Handler):
    # A log handler to redirect messages to a QT Widget in a thread safe manner
    def __init__(self):
        super().__init__()
        self.log = MyLog()

    
    def emit(self, record):
        msg = self.format(record)
        self.log.signal.emit(msg)

class Worker(QObject):
    finished = Signal()
    progress = Signal(int)

    def setup(self, input_dir, regex, output_dir):
        self.regex = regex
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):

        csv.import_dir_to_csv(self.input_dir, self.regex, self.output_dir, append=False)
        """Long-running task."""
        # for i in range(5):
        #     sleep(1)
        #     self.progress.emit(i + 1)
        #     logging.warning(f"ding {i}")
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(1024, 768)

        # self.logwidget = QPlainTextEdit()
        # self.logwidget.setReadOnly(True)
        # self.logwidget.setGeometry(20,300,800,100)


        # set up log handler
        self.logHandler = CustomLogHandler()
        # self.logHandler.setFormatter(
            # logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'))
        self.logHandler.setFormatter(
            logging.Formatter('%(levelname)s %(message)s'))
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(self.logHandler)


        self.importTab()
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

        default_regex = '(?P<sensor>.+)_Sensor(?P<element>.+)_(?P<fluid>.+)_Rotation(.+).txt'
        default_input = '/Users/calum/git/Glasgow/sampleData/combined'
        default_output = '/Users/calum/git/Glasgow/dwt-optical/imported'
        

        # New Widget (to be used as a tab)
        self.ui.tab_import = QWidget()
        self.ui.tab_import.setObjectName(u"tab_import")

        # Make a Vertical layout within the new tab
        vbox = QVBoxLayout(self.ui.tab_import)

        label_title = QLabel("Import existing csv/tsv files, extract metadata from filenames")
        label_input = QLabel("Input Directory:")
        label_output = QLabel("Output Directory:")
        label_regex = QLabel("Regular expression to extract metadata from filenames:")
        
        tooltip_regex = ("Should extract at least [sensor, element, fluid] as in example\n"
            +"Other metadata can be captured and will be also be saved")

        self.ui.tbox_input = QLineEdit()
        self.ui.tbox_input.setText(default_input)
        self.ui.tbox_output = QLineEdit()
        self.ui.tbox_output.setText(default_output)
        self.ui.tbox_regex = QLineEdit()
        self.ui.tbox_regex.setText(default_regex)
        self.ui.tbox_regex.setToolTip(tooltip_regex)

        font = QtGui.QFont()
        font.setStyleHint(QtGui.QFont.TypeWriter)
        font.setFamily('Monaco')

        self.ui.import_printbox = QPlainTextEdit()
        self.ui.import_printbox.setFont(font)
        self.ui.import_printbox.setLineWrapMode(QPlainTextEdit.NoWrap)

        # logTextBox = QTextEditLogger(self)
        # # log to text box
        # logTextBox.setFormatter(
        #     logging.Formatter('%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
        #     )
        # logging.getLogger().addHandler(logTextBox)
        # logging.getLogger().setLevel(logging.DEBUG)


        browse_input = QPushButton("Browse")
        browse_input.clicked.connect(self.get_input_dir)

        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output_dir)

        self.ui.btn_import = QPushButton("Import")
        self.ui.btn_import.clicked.connect(self.run_import)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_input)
        hbox_input.addWidget(self.ui.tbox_input)
        hbox_input.addWidget(browse_input)

        hbox_output = QHBoxLayout()
        hbox_output.addWidget(label_output)
        hbox_output.addWidget(self.ui.tbox_output)
        hbox_output.addWidget(browse_output)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.ui.btn_import)

        vbox.addWidget(label_title)
        vbox.addLayout(hbox_input)
        vbox.addLayout(hbox_output)
        vbox.addWidget(label_regex)
        vbox.addWidget(self.ui.tbox_regex)
        vbox.addWidget(self.ui.import_printbox)
        vbox.addLayout(hbox_run)
        vbox.addStretch()

        # Add tab to the main tab widget, and give it a label
        self.ui.tabWidget.addTab(self.ui.tab_import, "")
        self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(self.ui.tab_import), "import")
        
    def get_input_dir(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        self.ui.tbox_input.setText(dirname)

    def get_output_dir(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        self.ui.tbox_output.setText(dirname)

    def run_import(self):

        regex = self.ui.tbox_regex.text()
        input_dir = self.ui.tbox_input.text()
        output_dir = self.ui.tbox_output.text()
     
        self.ui.import_printbox.appendPlainText('Running Import')

        self.ui.thread = QThread()
        self.ui.worker = Worker()
        self.ui.worker.setup(input_dir, regex, output_dir)

        self.ui.worker.moveToThread(self.ui.thread)
        self.ui.thread.started.connect(self.ui.worker.run)
        self.ui.worker.finished.connect(self.ui.thread.quit)
        self.ui.worker.finished.connect(self.ui.worker.deleteLater)
        self.ui.thread.finished.connect(self.ui.thread.deleteLater)
        self.ui.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.ui.thread.start()
        self.ui.btn_import.setEnabled(False)
        self.ui.thread.finished.connect(
            lambda: self.ui.btn_import.setEnabled(True)
        )
        # self.ui.worker.logHandler.log.signal.connect(self.write_log)
        self.logHandler.log.signal.connect(self.write_log)
        
        # p = Process(target= csv.import_dir_to_csv, args=(input_dir, regex, output_dir), kwargs = {'append' : False})
        # p.start()
        # p.join()
        # csv.import_dir_to_csv(input_dir, regex, output_dir, append=False)

    def reportProgress(self, n):
        self.ui.import_printbox.appendPlainText(f"Long-Running Step: {n}")
        # self.stepLabel.setText

    # define a new Slot, that receives a string
    @Slot(str)
    def write_log(self, log_text):
        self.ui.import_printbox.appendPlainText(log_text)
        print('wrote log')
        # self.logTextBox.centerCursor()  # scroll to the bottom


    def write(self, message):
        cursor = self.ui.import_printbox.textCursor()
        if cursor.positionInBlock() > 0:
            self.ui.import_printbox.insertPlainText('\n')
        self.ui.import_printbox.insertPlainText(message.rstrip())

    def flush(self):
        # This prevents an error message related to capturing stdout
        pass

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)

    orig_stdout = sys.stdout
    app = QApplication(sys.argv)
    w = MainWindow()
    # sys.stdout = w
    app.setWindowIcon(QtGui.QIcon(":/icons/full-spectrum.png"))
    app.exec()

