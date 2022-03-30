import logging
from PySide6.QtGui import QFont
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication
from PySide6.QtWidgets import (QPlainTextEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QWidget)

class Communicate(QObject):
    # class to define signals used to communicate between threads
    # Primarily used to catch log messages and print them to the GUI
    # has to inherit from QObject to be able to emit signals
    appendLogText = Signal(str)


class GUILogHandler(logging.Handler):

    # A log handler to redirect log messages (particularly from worker threads)
    # to the main GUI thread
    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.signals=Communicate()
        # self.signals.appendLogText.connect(parent.writeLog)
        self.setLevel(logging.INFO)
        self.setFormatter(CustomFormatter())

    def emit(self, record):
        # When a new log record is received, send it to the main thread using
        # the appendLogText signal, which will call the write_log() funciton.
        msg = self.format(record)
        self.signals.appendLogText.emit(msg)


class CustomFormatter(logging.Formatter):

    #Formats log messages as HTML with appropriate colours, for use when
    #redirecting log messages to a GUI PlainTextEdit box

    fmt = '%(levelname)s %(message)s'

    def __init__(self):
        super().__init__()
        self.COLORS = {
            logging.DEBUG: "<font color=\"Black\">",
            logging.INFO: "<font color=\"SteelBlue\">",
            logging.WARNING: "<font color=\"Orange\">",
            logging.ERROR: "<font color=\"OrangeRed\">",
            logging.CRITICAL: "<font color=\"Red\">",
        }

    def format(self, record):
        formatter = logging.Formatter(self.fmt)
        color = self.COLORS.get(record.levelno)
        msg = formatter.format(record)
        # 'pre' tag signifies pre-formatted text so doesnt remove tabs
        msg = color + "<pre>" + msg + "</pre></font>"
        return msg

class GUILogger(QWidget):

    def __init__(self, parent):
        self.parent = parent
        QWidget.__init__(self)
    # def setupLogging(self):
        # Use the Root Logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # set up log handler for GUI
        self.gui_logHandler = GUILogHandler(self)
        logger.addHandler(self.gui_logHandler)

        # font = QFont()
        # font.setStyleHint(QFont.TypeWriter)
        # font.setFamily('Monaco')
        btn_width = 80
        logLabel = QLabel("Log Output:")
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clearBox)
        btn_clear.setFixedWidth(btn_width)

        btn_close = QPushButton('Exit')
        btn_close.clicked.connect(QCoreApplication.instance().quit)
        btn_close.setFixedWidth(btn_width)

        hbox_btn = QHBoxLayout()
        hbox_btn.addStretch()
        hbox_btn.addWidget(btn_clear)
        hbox_btn.addWidget(btn_close)

        self.logBox = QPlainTextEdit()
        # self.logBox.setFont(font)
        self.logBox.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.logVbox = QVBoxLayout()
        self.logVbox.addWidget(logLabel)
        self.logVbox.addWidget(self.logBox)
        self.logVbox.addLayout(hbox_btn)
        
        self.setLayout(self.logVbox)

        self.gui_logHandler.signals.appendLogText.connect(self.writeLog)

        # set up log handler for Console
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.DEBUG)
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)


    # Defines where log messages should be displayed in the GUI.
    @Slot(str)
    def writeLog(self, log_text):
        self.logBox.appendHtml(log_text)

    def clearBox(self):
        self.logBox.setPlainText('')