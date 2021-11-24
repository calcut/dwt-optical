import sys

from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QMainWindow, QGridLayout, QApplication, QWidget
from layout_colorwidget import Color
import resources_rc

from mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        # self.label_11.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/penguin.png\"/></p></body></html>", None))

        # self.tab = QWidget()
        # self.widget = QWidget(self.tab)
        # self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)

# class MainWindow(QMainWindow):

#     def __init__(self):
#         # super(MainWindow, self).__init__()
#         super().__init__()

#         self.setWindowTitle("My App")

#         layout = QGridLayout()

#         layout.addWidget(Color('red'), 0, 0)
#         layout.addWidget(Color('green'), 1, 0)
#         layout.addWidget(Color('blue'), 1, 1)
#         layout.addWidget(Color('purple'), 0, 1)

#         widget = QWidget()
#         widget.setLayout(layout)
#         self.setCentralWidget(widget)
#         self.show()




app = QApplication(sys.argv)
layout = QGridLayout()

layout.addWidget(Color('red'), 0, 0)
layout.addWidget(Color('green'), 1, 0)
layout.addWidget(Color('blue'), 1, 1)
layout.addWidget(Color('purple'), 0, 1)

widget = QWidget()
widget.setLayout(layout)


w = MainWindow()
# w.setCentralWidget(widget)
w.ui.horizontalLayout.addWidget(widget)
app.setWindowIcon(QtGui.QIcon(":/icons/full-spectrum.png"))
app.exec()
