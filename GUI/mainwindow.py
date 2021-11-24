# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.2.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QMenu, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QSpinBox, QStatusBar, QTabWidget,
    QToolButton, QVBoxLayout, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(958, 773)
        self.actionitem_xxx = QAction(MainWindow)
        self.actionitem_xxx.setObjectName(u"actionitem_xxx")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.toolButton = QToolButton(self.tab)
        self.toolButton.setObjectName(u"toolButton")
        self.toolButton.setGeometry(QRect(240, 190, 26, 22))
        self.radioButton = QRadioButton(self.tab)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(100, 190, 99, 20))
        self.widget = QWidget(self.tab)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(-10, 320, 200, 124))
        self.gridLayout_4 = QGridLayout(self.widget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.widget)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)

        self.label_9 = QLabel(self.widget)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_4.addWidget(self.label_9, 0, 5, 2, 1)

        self.label_10 = QLabel(self.widget)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_4.addWidget(self.label_10, 0, 6, 1, 2)

        self.label_8 = QLabel(self.widget)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_4.addWidget(self.label_8, 1, 1, 2, 2)

        self.label_14 = QLabel(self.widget)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_4.addWidget(self.label_14, 1, 6, 2, 2)

        self.label_11 = QLabel(self.widget)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_4.addWidget(self.label_11, 1, 10, 2, 1)

        self.label_12 = QLabel(self.widget)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_4.addWidget(self.label_12, 1, 11, 1, 1)

        self.label_18 = QLabel(self.widget)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_4.addWidget(self.label_18, 2, 2, 2, 2)

        self.label_15 = QLabel(self.widget)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_4.addWidget(self.label_15, 2, 7, 2, 2)

        self.label_13 = QLabel(self.widget)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_4.addWidget(self.label_13, 2, 11, 2, 1)

        self.label_19 = QLabel(self.widget)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_4.addWidget(self.label_19, 3, 3, 2, 2)

        self.label_16 = QLabel(self.widget)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_4.addWidget(self.label_16, 3, 8, 2, 2)

        self.label_20 = QLabel(self.widget)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_4.addWidget(self.label_20, 4, 4, 2, 2)

        self.label_17 = QLabel(self.widget)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_4.addWidget(self.label_17, 4, 9, 2, 2)

        self.label_23 = QLabel(self.widget)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout_4.addWidget(self.label_23, 4, 11, 2, 1)

        self.label_21 = QLabel(self.widget)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_4.addWidget(self.label_21, 5, 5, 2, 2)

        self.label_22 = QLabel(self.widget)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_4.addWidget(self.label_22, 6, 6, 1, 2)

        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 270, 901, 351))
        self.label_3.setPixmap(QPixmap(u":/sensors/wellplate060.png"))
        self.label_3.setScaledContents(True)
        self.widget1 = QWidget(self.tab)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(120, 320, 2083, 639))
        self.gridLayout_3 = QGridLayout(self.widget1)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.checkBox_52 = QCheckBox(self.widget1)
        self.checkBox_52.setObjectName(u"checkBox_52")

        self.gridLayout_3.addWidget(self.checkBox_52, 2, 1, 1, 1)

        self.checkBox_13 = QCheckBox(self.widget1)
        self.checkBox_13.setObjectName(u"checkBox_13")

        self.gridLayout_3.addWidget(self.checkBox_13, 0, 14, 1, 1)

        self.checkBox_36 = QCheckBox(self.widget1)
        self.checkBox_36.setObjectName(u"checkBox_36")

        self.gridLayout_3.addWidget(self.checkBox_36, 1, 1, 1, 1)

        self.checkBox_58 = QCheckBox(self.widget1)
        self.checkBox_58.setObjectName(u"checkBox_58")

        self.gridLayout_3.addWidget(self.checkBox_58, 2, 2, 1, 1)

        self.checkBox_74 = QCheckBox(self.widget1)
        self.checkBox_74.setObjectName(u"checkBox_74")

        self.gridLayout_3.addWidget(self.checkBox_74, 3, 2, 1, 1)

        self.checkBox_59 = QCheckBox(self.widget1)
        self.checkBox_59.setObjectName(u"checkBox_59")

        self.gridLayout_3.addWidget(self.checkBox_59, 2, 11, 1, 1)

        self.checkBox_37 = QCheckBox(self.widget1)
        self.checkBox_37.setObjectName(u"checkBox_37")

        self.gridLayout_3.addWidget(self.checkBox_37, 1, 14, 1, 1)

        self.checkBox_79 = QCheckBox(self.widget1)
        self.checkBox_79.setObjectName(u"checkBox_79")

        self.gridLayout_3.addWidget(self.checkBox_79, 3, 10, 1, 1)

        self.checkBox_49 = QCheckBox(self.widget1)
        self.checkBox_49.setObjectName(u"checkBox_49")

        self.gridLayout_3.addWidget(self.checkBox_49, 2, 13, 1, 1)

        self.checkBox = QCheckBox(self.widget1)
        self.checkBox.setObjectName(u"checkBox")

        self.gridLayout_3.addWidget(self.checkBox, 0, 0, 1, 1)

        self.checkBox_4 = QCheckBox(self.widget1)
        self.checkBox_4.setObjectName(u"checkBox_4")

        self.gridLayout_3.addWidget(self.checkBox_4, 0, 3, 1, 1)

        self.checkBox_55 = QCheckBox(self.widget1)
        self.checkBox_55.setObjectName(u"checkBox_55")

        self.gridLayout_3.addWidget(self.checkBox_55, 2, 7, 1, 1)

        self.checkBox_34 = QCheckBox(self.widget1)
        self.checkBox_34.setObjectName(u"checkBox_34")

        self.gridLayout_3.addWidget(self.checkBox_34, 1, 15, 1, 1)

        self.checkBox_16 = QCheckBox(self.widget1)
        self.checkBox_16.setObjectName(u"checkBox_16")

        self.gridLayout_3.addWidget(self.checkBox_16, 0, 12, 1, 1)

        self.checkBox_9 = QCheckBox(self.widget1)
        self.checkBox_9.setObjectName(u"checkBox_9")

        self.gridLayout_3.addWidget(self.checkBox_9, 0, 10, 1, 1)

        self.checkBox_78 = QCheckBox(self.widget1)
        self.checkBox_78.setObjectName(u"checkBox_78")

        self.gridLayout_3.addWidget(self.checkBox_78, 3, 0, 1, 1)

        self.checkBox_40 = QCheckBox(self.widget1)
        self.checkBox_40.setObjectName(u"checkBox_40")

        self.gridLayout_3.addWidget(self.checkBox_40, 1, 5, 1, 1)

        self.checkBox_70 = QCheckBox(self.widget1)
        self.checkBox_70.setObjectName(u"checkBox_70")

        self.gridLayout_3.addWidget(self.checkBox_70, 3, 12, 1, 1)

        self.checkBox_73 = QCheckBox(self.widget1)
        self.checkBox_73.setObjectName(u"checkBox_73")

        self.gridLayout_3.addWidget(self.checkBox_73, 3, 4, 1, 1)

        self.checkBox_45 = QCheckBox(self.widget1)
        self.checkBox_45.setObjectName(u"checkBox_45")

        self.gridLayout_3.addWidget(self.checkBox_45, 1, 3, 1, 1)

        self.checkBox_62 = QCheckBox(self.widget1)
        self.checkBox_62.setObjectName(u"checkBox_62")

        self.gridLayout_3.addWidget(self.checkBox_62, 2, 0, 1, 1)

        self.checkBox_53 = QCheckBox(self.widget1)
        self.checkBox_53.setObjectName(u"checkBox_53")

        self.gridLayout_3.addWidget(self.checkBox_53, 2, 14, 1, 1)

        self.checkBox_6 = QCheckBox(self.widget1)
        self.checkBox_6.setObjectName(u"checkBox_6")

        self.gridLayout_3.addWidget(self.checkBox_6, 0, 6, 1, 1)

        self.checkBox_41 = QCheckBox(self.widget1)
        self.checkBox_41.setObjectName(u"checkBox_41")

        self.gridLayout_3.addWidget(self.checkBox_41, 1, 4, 1, 1)

        self.checkBox_80 = QCheckBox(self.widget1)
        self.checkBox_80.setObjectName(u"checkBox_80")

        self.gridLayout_3.addWidget(self.checkBox_80, 3, 8, 1, 1)

        self.checkBox_66 = QCheckBox(self.widget1)
        self.checkBox_66.setObjectName(u"checkBox_66")

        self.gridLayout_3.addWidget(self.checkBox_66, 3, 15, 1, 1)

        self.checkBox_71 = QCheckBox(self.widget1)
        self.checkBox_71.setObjectName(u"checkBox_71")

        self.gridLayout_3.addWidget(self.checkBox_71, 3, 7, 1, 1)

        self.checkBox_47 = QCheckBox(self.widget1)
        self.checkBox_47.setObjectName(u"checkBox_47")

        self.gridLayout_3.addWidget(self.checkBox_47, 1, 10, 1, 1)

        self.checkBox_46 = QCheckBox(self.widget1)
        self.checkBox_46.setObjectName(u"checkBox_46")

        self.gridLayout_3.addWidget(self.checkBox_46, 1, 0, 1, 1)

        self.checkBox_56 = QCheckBox(self.widget1)
        self.checkBox_56.setObjectName(u"checkBox_56")

        self.gridLayout_3.addWidget(self.checkBox_56, 2, 5, 1, 1)

        self.checkBox_15 = QCheckBox(self.widget1)
        self.checkBox_15.setObjectName(u"checkBox_15")

        self.gridLayout_3.addWidget(self.checkBox_15, 0, 13, 1, 1)

        self.checkBox_48 = QCheckBox(self.widget1)
        self.checkBox_48.setObjectName(u"checkBox_48")

        self.gridLayout_3.addWidget(self.checkBox_48, 1, 8, 1, 1)

        self.checkBox_75 = QCheckBox(self.widget1)
        self.checkBox_75.setObjectName(u"checkBox_75")

        self.gridLayout_3.addWidget(self.checkBox_75, 3, 11, 1, 1)

        self.checkBox_12 = QCheckBox(self.widget1)
        self.checkBox_12.setObjectName(u"checkBox_12")

        self.gridLayout_3.addWidget(self.checkBox_12, 0, 8, 1, 1)

        self.checkBox_68 = QCheckBox(self.widget1)
        self.checkBox_68.setObjectName(u"checkBox_68")

        self.gridLayout_3.addWidget(self.checkBox_68, 3, 1, 1, 1)

        self.checkBox_38 = QCheckBox(self.widget1)
        self.checkBox_38.setObjectName(u"checkBox_38")

        self.gridLayout_3.addWidget(self.checkBox_38, 1, 12, 1, 1)

        self.checkBox_14 = QCheckBox(self.widget1)
        self.checkBox_14.setObjectName(u"checkBox_14")

        self.gridLayout_3.addWidget(self.checkBox_14, 0, 15, 1, 1)

        self.checkBox_57 = QCheckBox(self.widget1)
        self.checkBox_57.setObjectName(u"checkBox_57")

        self.gridLayout_3.addWidget(self.checkBox_57, 2, 4, 1, 1)

        self.checkBox_63 = QCheckBox(self.widget1)
        self.checkBox_63.setObjectName(u"checkBox_63")

        self.gridLayout_3.addWidget(self.checkBox_63, 2, 10, 1, 1)

        self.checkBox_10 = QCheckBox(self.widget1)
        self.checkBox_10.setObjectName(u"checkBox_10")

        self.gridLayout_3.addWidget(self.checkBox_10, 0, 11, 1, 1)

        self.checkBox_54 = QCheckBox(self.widget1)
        self.checkBox_54.setObjectName(u"checkBox_54")

        self.gridLayout_3.addWidget(self.checkBox_54, 2, 12, 1, 1)

        self.checkBox_76 = QCheckBox(self.widget1)
        self.checkBox_76.setObjectName(u"checkBox_76")

        self.gridLayout_3.addWidget(self.checkBox_76, 3, 9, 1, 1)

        self.checkBox_61 = QCheckBox(self.widget1)
        self.checkBox_61.setObjectName(u"checkBox_61")

        self.gridLayout_3.addWidget(self.checkBox_61, 2, 3, 1, 1)

        self.checkBox_69 = QCheckBox(self.widget1)
        self.checkBox_69.setObjectName(u"checkBox_69")

        self.gridLayout_3.addWidget(self.checkBox_69, 3, 14, 1, 1)

        self.checkBox_43 = QCheckBox(self.widget1)
        self.checkBox_43.setObjectName(u"checkBox_43")

        self.gridLayout_3.addWidget(self.checkBox_43, 1, 11, 1, 1)

        self.checkBox_7 = QCheckBox(self.widget1)
        self.checkBox_7.setObjectName(u"checkBox_7")

        self.gridLayout_3.addWidget(self.checkBox_7, 0, 7, 1, 1)

        self.checkBox_65 = QCheckBox(self.widget1)
        self.checkBox_65.setObjectName(u"checkBox_65")

        self.gridLayout_3.addWidget(self.checkBox_65, 3, 13, 1, 1)

        self.checkBox_8 = QCheckBox(self.widget1)
        self.checkBox_8.setObjectName(u"checkBox_8")

        self.gridLayout_3.addWidget(self.checkBox_8, 0, 4, 1, 1)

        self.checkBox_60 = QCheckBox(self.widget1)
        self.checkBox_60.setObjectName(u"checkBox_60")

        self.gridLayout_3.addWidget(self.checkBox_60, 2, 9, 1, 1)

        self.checkBox_42 = QCheckBox(self.widget1)
        self.checkBox_42.setObjectName(u"checkBox_42")

        self.gridLayout_3.addWidget(self.checkBox_42, 1, 2, 1, 1)

        self.checkBox_2 = QCheckBox(self.widget1)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.gridLayout_3.addWidget(self.checkBox_2, 0, 1, 1, 1)

        self.checkBox_35 = QCheckBox(self.widget1)
        self.checkBox_35.setObjectName(u"checkBox_35")

        self.gridLayout_3.addWidget(self.checkBox_35, 1, 6, 1, 1)

        self.checkBox_72 = QCheckBox(self.widget1)
        self.checkBox_72.setObjectName(u"checkBox_72")

        self.gridLayout_3.addWidget(self.checkBox_72, 3, 5, 1, 1)

        self.checkBox_3 = QCheckBox(self.widget1)
        self.checkBox_3.setObjectName(u"checkBox_3")

        self.gridLayout_3.addWidget(self.checkBox_3, 0, 2, 1, 1)

        self.checkBox_39 = QCheckBox(self.widget1)
        self.checkBox_39.setObjectName(u"checkBox_39")

        self.gridLayout_3.addWidget(self.checkBox_39, 1, 7, 1, 1)

        self.checkBox_77 = QCheckBox(self.widget1)
        self.checkBox_77.setObjectName(u"checkBox_77")

        self.gridLayout_3.addWidget(self.checkBox_77, 3, 3, 1, 1)

        self.checkBox_11 = QCheckBox(self.widget1)
        self.checkBox_11.setObjectName(u"checkBox_11")

        self.gridLayout_3.addWidget(self.checkBox_11, 0, 9, 1, 1)

        self.checkBox_50 = QCheckBox(self.widget1)
        self.checkBox_50.setObjectName(u"checkBox_50")

        self.gridLayout_3.addWidget(self.checkBox_50, 2, 15, 1, 1)

        self.checkBox_33 = QCheckBox(self.widget1)
        self.checkBox_33.setObjectName(u"checkBox_33")

        self.gridLayout_3.addWidget(self.checkBox_33, 1, 13, 1, 1)

        self.checkBox_44 = QCheckBox(self.widget1)
        self.checkBox_44.setObjectName(u"checkBox_44")

        self.gridLayout_3.addWidget(self.checkBox_44, 1, 9, 1, 1)

        self.checkBox_64 = QCheckBox(self.widget1)
        self.checkBox_64.setObjectName(u"checkBox_64")

        self.gridLayout_3.addWidget(self.checkBox_64, 2, 8, 1, 1)

        self.checkBox_67 = QCheckBox(self.widget1)
        self.checkBox_67.setObjectName(u"checkBox_67")

        self.gridLayout_3.addWidget(self.checkBox_67, 3, 6, 1, 1)

        self.checkBox_5 = QCheckBox(self.widget1)
        self.checkBox_5.setObjectName(u"checkBox_5")

        self.gridLayout_3.addWidget(self.checkBox_5, 0, 5, 1, 1)

        self.checkBox_51 = QCheckBox(self.widget1)
        self.checkBox_51.setObjectName(u"checkBox_51")

        self.gridLayout_3.addWidget(self.checkBox_51, 2, 6, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.label_3.raise_()
        self.toolButton.raise_()
        self.radioButton.raise_()
        self.checkBox.raise_()
        self.checkBox_2.raise_()
        self.checkBox_3.raise_()
        self.checkBox_4.raise_()
        self.checkBox_5.raise_()
        self.checkBox_6.raise_()
        self.checkBox_7.raise_()
        self.checkBox_8.raise_()
        self.checkBox_9.raise_()
        self.checkBox_10.raise_()
        self.checkBox_11.raise_()
        self.checkBox_12.raise_()
        self.checkBox_13.raise_()
        self.checkBox_14.raise_()
        self.checkBox_15.raise_()
        self.checkBox_16.raise_()
        self.checkBox_33.raise_()
        self.checkBox_34.raise_()
        self.checkBox_35.raise_()
        self.checkBox_36.raise_()
        self.checkBox_37.raise_()
        self.checkBox_38.raise_()
        self.checkBox_39.raise_()
        self.checkBox_40.raise_()
        self.checkBox_41.raise_()
        self.checkBox_42.raise_()
        self.checkBox_43.raise_()
        self.checkBox_44.raise_()
        self.checkBox_45.raise_()
        self.checkBox_46.raise_()
        self.checkBox_47.raise_()
        self.checkBox_48.raise_()
        self.checkBox_49.raise_()
        self.checkBox_50.raise_()
        self.checkBox_51.raise_()
        self.checkBox_52.raise_()
        self.checkBox_53.raise_()
        self.checkBox_54.raise_()
        self.checkBox_55.raise_()
        self.checkBox_56.raise_()
        self.checkBox_57.raise_()
        self.checkBox_58.raise_()
        self.checkBox_59.raise_()
        self.checkBox_60.raise_()
        self.checkBox_61.raise_()
        self.checkBox_62.raise_()
        self.checkBox_63.raise_()
        self.checkBox_64.raise_()
        self.checkBox_65.raise_()
        self.checkBox_66.raise_()
        self.checkBox_67.raise_()
        self.checkBox_68.raise_()
        self.checkBox_69.raise_()
        self.checkBox_70.raise_()
        self.checkBox_71.raise_()
        self.checkBox_72.raise_()
        self.checkBox_73.raise_()
        self.checkBox_74.raise_()
        self.checkBox_75.raise_()
        self.checkBox_76.raise_()
        self.checkBox_77.raise_()
        self.checkBox_78.raise_()
        self.checkBox_79.raise_()
        self.checkBox_80.raise_()
        self.label_7.raise_()
        self.label_8.raise_()
        self.label_9.raise_()
        self.label_10.raise_()
        self.label_11.raise_()
        self.label_12.raise_()
        self.label_13.raise_()
        self.label_14.raise_()
        self.label_15.raise_()
        self.label_16.raise_()
        self.label_17.raise_()
        self.label_18.raise_()
        self.label_19.raise_()
        self.label_20.raise_()
        self.label_21.raise_()
        self.label_22.raise_()
        self.label_23.raise_()
        self.widget.raise_()
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayoutWidget = QWidget(self.tab_2)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(460, 320, 427, 44))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.radioButton_2 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.gridLayout.addWidget(self.radioButton_2, 0, 1, 1, 1)

        self.radioButton_4 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_4.setObjectName(u"radioButton_4")

        self.gridLayout.addWidget(self.radioButton_4, 0, 3, 1, 1)

        self.radioButton_3 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_3.setObjectName(u"radioButton_3")

        self.gridLayout.addWidget(self.radioButton_3, 0, 2, 1, 1)

        self.radioButton_5 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_5.setObjectName(u"radioButton_5")

        self.gridLayout.addWidget(self.radioButton_5, 0, 0, 1, 1)

        self.radioButton_6 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_6.setObjectName(u"radioButton_6")

        self.gridLayout.addWidget(self.radioButton_6, 1, 1, 1, 1)

        self.radioButton_7 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_7.setObjectName(u"radioButton_7")

        self.gridLayout.addWidget(self.radioButton_7, 1, 0, 1, 1)

        self.radioButton_8 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_8.setObjectName(u"radioButton_8")

        self.gridLayout.addWidget(self.radioButton_8, 1, 2, 1, 1)

        self.radioButton_9 = QRadioButton(self.gridLayoutWidget)
        self.radioButton_9.setObjectName(u"radioButton_9")

        self.gridLayout.addWidget(self.radioButton_9, 1, 3, 1, 1)

        self.verticalLayoutWidget = QWidget(self.tab_2)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(11, 11, 361, 631))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_2 = QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout.addWidget(self.pushButton_2)

        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.spinBox = QSpinBox(self.verticalLayoutWidget)
        self.spinBox.setObjectName(u"spinBox")

        self.verticalLayout.addWidget(self.spinBox)

        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.pushButton = QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout.addWidget(self.pushButton)

        self.listWidget = QListWidget(self.tab_2)
        QListWidgetItem(self.listWidget)
        QListWidgetItem(self.listWidget)
        QListWidgetItem(self.listWidget)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setGeometry(QRect(420, 50, 451, 191))
        self.listWidget.setDragEnabled(True)
        self.tabWidget.addTab(self.tab_2, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 958, 24))
        self.menuMenu_Item = QMenu(self.menubar)
        self.menuMenu_Item.setObjectName(u"menuMenu_Item")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuMenu_Item.menuAction())
        self.menuMenu_Item.addAction(self.actionitem_xxx)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionitem_xxx.setText(QCoreApplication.translate("MainWindow", u"item xxx", None))
        self.toolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/penguin.png\"/></p></body></html>", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/icons/monkey.png\"/></p></body></html>", None))
        self.label_3.setText("")
        self.checkBox_52.setText("")
        self.checkBox_13.setText("")
        self.checkBox_36.setText("")
        self.checkBox_58.setText("")
        self.checkBox_74.setText("")
        self.checkBox_59.setText("")
        self.checkBox_37.setText("")
        self.checkBox_79.setText("")
        self.checkBox_49.setText("")
        self.checkBox.setText("")
        self.checkBox_4.setText("")
        self.checkBox_55.setText("")
        self.checkBox_34.setText("")
        self.checkBox_16.setText("")
        self.checkBox_9.setText("")
        self.checkBox_78.setText("")
        self.checkBox_40.setText("")
        self.checkBox_70.setText("")
        self.checkBox_73.setText("")
        self.checkBox_45.setText("")
        self.checkBox_62.setText("")
        self.checkBox_53.setText("")
        self.checkBox_6.setText("")
        self.checkBox_41.setText("")
        self.checkBox_80.setText("")
        self.checkBox_66.setText("")
        self.checkBox_71.setText("")
        self.checkBox_47.setText("")
        self.checkBox_46.setText("")
        self.checkBox_56.setText("")
        self.checkBox_15.setText("")
        self.checkBox_48.setText("")
        self.checkBox_75.setText("")
        self.checkBox_12.setText("")
        self.checkBox_68.setText("")
        self.checkBox_38.setText("")
        self.checkBox_14.setText("")
        self.checkBox_57.setText("")
        self.checkBox_63.setText("")
        self.checkBox_10.setText("")
        self.checkBox_54.setText("")
        self.checkBox_76.setText("")
        self.checkBox_61.setText("")
        self.checkBox_69.setText("")
        self.checkBox_43.setText("")
        self.checkBox_7.setText("")
        self.checkBox_65.setText("")
        self.checkBox_8.setText("")
        self.checkBox_60.setText("")
        self.checkBox_42.setText("")
        self.checkBox_2.setText("")
        self.checkBox_35.setText("")
        self.checkBox_72.setText("")
        self.checkBox_3.setText("")
        self.checkBox_39.setText("")
        self.checkBox_77.setText("")
        self.checkBox_11.setText("")
        self.checkBox_50.setText("")
        self.checkBox_33.setText("")
        self.checkBox_44.setText("")
        self.checkBox_64.setText("")
        self.checkBox_67.setText("")
        self.checkBox_5.setText("")
        self.checkBox_51.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.radioButton_4.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.radioButton_5.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.radioButton_6.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.radioButton_7.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.radioButton_8.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.radioButton_9.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Label 1", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))

        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"sdfgs", None));
        ___qlistwidgetitem1 = self.listWidget.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"asdfasdf", None));
        ___qlistwidgetitem2 = self.listWidget.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"asdfasdfa", None));
        self.listWidget.setSortingEnabled(__sortingEnabled)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.menuMenu_Item.setTitle(QCoreApplication.translate("MainWindow", u"Menu Item", None))
    # retranslateUi

