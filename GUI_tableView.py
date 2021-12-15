
import sys
import pandas as pd
from PySide6.QtWidgets import QLabel, QLineEdit, QMainWindow, QTableView, QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel

class MetaModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[col]
        return None

class ExportModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return (f"{self._data.columns[col][0]}\n"
                   +f"{self._data.columns[col][1]}\n"
                   +f"{self._data.columns[col][2]}"
            )
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[col]
        return None

class MetaTable(QMainWindow):

    def __init__(self, dataframe, title):
        super().__init__()

        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(950, 850)
        self.setWindowTitle(title)

        self.table = QTableView()
        self.model = MetaModel(dataframe)

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)
        self.proxyModel.setFilterKeyColumn(-1) #Use All Columns

        self.table.setSortingEnabled(True)
        self.table.setModel(self.proxyModel)

        self.label_filter = QLabel("Basic Wildcard Filter:")

        self.tbox_filter = QLineEdit()
        self.tbox_filter.textChanged.connect(self.updateFilter)

        self.VBoxTable = QVBoxLayout(centralwidget)
        self.VBoxTable.addWidget(self.table)
        self.VBoxTable.addWidget(self.label_filter)
        self.VBoxTable.addWidget(self.tbox_filter)

    def updateFilter(self, text):
        self.proxyModel.setFilterWildcard(text)



class ExportTable(QMainWindow):

    def __init__(self, dataframe, title):
        super().__init__()

        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(950, 850)
        self.setWindowTitle(title)

        self.table = QTableView()
        self.model = ExportModel(dataframe)

        self.table.setSortingEnabled(True)
        self.table.setModel(self.model)

        self.VBoxTable = QVBoxLayout(centralwidget)
        self.VBoxTable.addWidget(self.table)

class SurfaceModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data.iloc[index.row(),index.column()] = value
            return True

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[col]
        return None

    def flags(self, index):
        if self._data.columns[index.column()] == 'chemistry':
            return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsEditable
        else:
            return Qt.NoItemFlags


class SurfaceTable(QTableView):

    def __init__(self):
        super().__init__()

    def set_data(self, dataframe):
        self.model = SurfaceModel(dataframe)
        self.setModel(self.model)
        # Unsure why sorting doesn't work
        # self.setSortingEnabled(True)

