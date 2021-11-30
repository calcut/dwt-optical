import logging
from PySide6.QtGui import QFont
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QHBoxLayout, QPushButton

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
        msg = color + msg + "</font>"
        return msg

class GUILogger():

    def __init__(self, parent):
        self.parent = parent
    # def setupLogging(self):
        # Use the Root Logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # set up log handler for GUI
        gui_logHandler = GUILogHandler(self)
        logger.addHandler(gui_logHandler)
        # gui_logHandler.signals.appendLogText.connect(print('poo'))

        font = QFont()
        font.setStyleHint(QFont.TypeWriter)
        font.setFamily('Monaco')

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clearBox)

        hbox_btn = QHBoxLayout()
        hbox_btn.addStretch()
        hbox_btn.addWidget(self.btn_clear)

        self.logBox = QPlainTextEdit()
        self.logBox.setFont(font)
        self.logBox.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.logVbox = QVBoxLayout()
        self.logVbox.addWidget(self.logBox)
        self.logVbox.addLayout(hbox_btn)




        # This doesn't work, something to do with threads??
        # gui_logHandler.signals.appendLogText.connect(self.writeLog)

        # This does work
        gui_logHandler.signals.appendLogText.connect(parent.writeLog)

        # set up log handler for Console
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.DEBUG)
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)


    # Defines where log messages should be displayed in the GUI.
    # This Doesnt work, something to do with threads? defined in parent instead
    # @Slot(str)
    # def writeLog(self, log_text):
    #     self.logBox.appendHtml(log_text)

    def clearBox(self):
        self.logBox.setPlainText('')