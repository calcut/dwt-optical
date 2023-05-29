import logging
from PySide6 import QtGui, QtWidgets, QtCore

class Communicate(QtCore.QObject):
    # class to define signals used to communicate between threads
    # Primarily used to catch log messages and print them to the GUI
    # has to inherit from QObject to be able to emit signals
    appendLogText = QtCore.Signal(tuple)

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
        self.signals.appendLogText.emit((msg, record.levelno))


class CustomFormatter(logging.Formatter):

    #Formats log messages as HTML with appropriate colours, for use when
    #redirecting log messages to a GUI PlainTextEdit box

    fmt = '%(levelname)s %(message)s'

    def __init__(self):
        super().__init__()
        self.COLORS = { #Solarized colours
            logging.DEBUG: "<font color=#808080>", #base0
            logging.INFO: "<font color=#0087ff>", # Blue
            logging.WARNING: "<font color=#d75f00>", # Orange
            logging.ERROR: "<font color=#d70000>", #Red
            logging.CRITICAL: "<font color=#af005f>", #Magenta
        }

    def format(self, record):
        formatter = logging.Formatter(self.fmt)
        color = self.COLORS.get(record.levelno)
        msg = formatter.format(record)
        # 'pre' tag signifies pre-formatted text so doesnt remove tabs
        msg = color + "<pre>" + msg + "</pre></font>"
        return msg

class GUILogger(QtWidgets.QWidget):

    new_icon = QtCore.Signal()

    def __init__(self, parent):
        self.parent = parent
        QtWidgets.QWidget.__init__(self)
    # def setupLogging(self):
        # Use the Root Logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # set up log handler for GUI
        self.gui_logHandler = GUILogHandler(self)
        logger.addHandler(self.gui_logHandler)

        font = QtGui.QFont()
        font.setStyleHint(QtGui.QFont.TypeWriter)
        font.setFamily('Monaco')
        font.setPointSize(10)
        font.setBold(True)
        btn_width = 80
        logLabel = QtWidgets.QLabel("Log Output:")
        btn_clear = QtWidgets.QPushButton("Clear")
        btn_clear.clicked.connect(self.clearBox)
        btn_clear.setFixedWidth(btn_width)

        btn_close = QtWidgets.QPushButton('Exit')
        btn_close.clicked.connect(QtCore.QCoreApplication.instance().quit)
        btn_close.setFixedWidth(btn_width)

        hbox_btn = QtWidgets.QHBoxLayout()
        hbox_btn.addStretch()
        hbox_btn.addWidget(btn_clear)
        hbox_btn.addWidget(btn_close)

        self.logBox = QtWidgets.QPlainTextEdit()
        # self.logBox.setStyleSheet("background-color: rgb(0, 43, 54);")
        self.logBox.setFont(font)
        self.logBox.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        self.logVbox = QtWidgets.QVBoxLayout()
        self.logVbox.addWidget(logLabel)
        self.logVbox.addWidget(self.logBox)
        self.logVbox.addLayout(hbox_btn)
        # self.logVbox.addWidget(self.m_label)
        
        self.setLayout(self.logVbox)
        self.log_icon_level = 0
        self.create_pixmap()

        self.gui_logHandler.signals.appendLogText.connect(self.writeLog)
        self.gui_logHandler.signals.appendLogText.connect(self.create_pixmap)

        # set up log handler for Console
        # c_handler = logging.StreamHandler()
        # c_handler.setLevel(logging.DEBUG)
        # c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        # c_handler.setFormatter(c_format)
        # logger.addHandler(c_handler)

    @QtCore.Slot(tuple)
    def create_pixmap(self, log_tuple=None):

        self.COLORS = { #Solarized colours
            logging.DEBUG   : "#808080", # base0
            logging.INFO    : "#0087ff", # Blue
            logging.WARNING : "#d75f00", # Orange
            logging.ERROR   : "#d70000", # Red
            logging.CRITICAL: "#af005f", # Magenta
        }

        if log_tuple is None:
            color = '#000000'
        else:
            levelno = log_tuple[1]
    
            # Don't downgrade the color
            if levelno < self.log_icon_level:
                return
            
            self.log_icon_level = levelno
            color = self.COLORS[self.log_icon_level]

        radius = 6
        rect = QtCore.QRect(QtCore.QPoint(), 2 * radius * QtCore.QSize(1, 1))
        self.pixmap = QtGui.QPixmap(rect.size())
        rect.adjust(1, 1, -1, -1)
        self.pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(self.pixmap)
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing
        )
        pen = painter.pen()
        painter.setPen(QtCore.Qt.NoPen)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        painter.drawEllipse(rect)
        painter.setPen(pen)
        painter.end()

        self.new_icon.emit()


    # Defines where log messages should be displayed in the GUI.
    @QtCore.Slot(tuple)
    def writeLog(self, log_tuple):
        log_text = log_tuple[0]
        self.logBox.appendHtml(log_text)

    def clearBox(self):
        self.logBox.setPlainText('')
        self.create_pixmap()
        self.log_icon_level = 0