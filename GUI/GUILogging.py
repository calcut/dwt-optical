import logging
from PySide6.QtCore import QObject, Signal

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
        self.signals.appendLogText.connect(parent.writeLog)
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