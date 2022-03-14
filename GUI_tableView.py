
import sys
import pandas as pd
from PySide6.QtWidgets import QLabel, QLineEdit, QMainWindow, QTableWidget, QTableWidgetItem, QTableView, QWidget, QVBoxLayout, QTextEdit, QHBoxLayout
from PySide6.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel
import os

class SetupTable(QMainWindow):

    def __init__(self, setup, title):
        super().__init__()

        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(960, 480)
        self.setWindowTitle(title)

        setup_table = QTableWidget()
        instrument_table = QTableWidget()
        element_table = QTableWidget()

        # Create the table with necessary properties
        setup_table.setColumnCount(1)
        setup_table.setRowCount(len(setup))

        instrument_table.setColumnCount(1)
        instrument_table.setRowCount(len(setup['instrument']))
        
        element_table.setColumnCount(1)
        element_table.setRowCount(len(setup['instrument']['element_map']))

        for row, key in enumerate(setup):
            if not key == 'instrument':
                value = setup[key]
            else:
                value = '-->'
            setup_table.setItem(row, 0, QTableWidgetItem(str(value)))
        path, filename = os.path.split(title)
        setup_table.setHorizontalHeaderLabels([filename])
        setup_table.setVerticalHeaderLabels(setup.keys())

        instrument = setup['instrument']
        for row, key in enumerate(instrument):
            if not key == 'element_map':
                value = instrument[key]
            else: value = '-->'
            instrument_table.setItem(row, 0, QTableWidgetItem(str(value)))

        instrument_table.setHorizontalHeaderLabels(['instrument'])
        instrument_table.setVerticalHeaderLabels(instrument.keys())

        element_map = instrument['element_map']

        for row, key in enumerate(element_map):
            value = element_map[key]
            element_table.setItem(row, 0, QTableWidgetItem(str(value)))

        element_table.setHorizontalHeaderLabels(['element map'])
        element_table.setVerticalHeaderLabels(element_map.keys())

        setup_table.resizeColumnsToContents()
        setup_table.resizeRowsToContents()
        instrument_table.resizeColumnsToContents()
        instrument_table.resizeRowsToContents()
        element_table.resizeColumnsToContents()
        element_table.resizeRowsToContents()

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(setup_table, stretch=setup_table.columnWidth(0))
        self.hbox.addWidget(instrument_table, stretch=instrument_table.columnWidth(0))
        self.hbox.addWidget(element_table, stretch=element_table.columnWidth(0))

        self.label_filter = QLabel("Test Label")
        self.VBoxTable = QVBoxLayout(centralwidget)
        self.VBoxTable.addWidget(self.label_filter)
        self.VBoxTable.addLayout(self.hbox)
        self.VBoxTable.addWidget(self.label_filter)
        # self.setCentralWidget(setup_table)



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

class PreviewModel(QAbstractTableModel):

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
            return self._data.columns[col].replace('_', '\n')
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[col]
        return None

class PreviewTable(QMainWindow):

    def __init__(self, dataframe, title, common_info='', process_info=''):
        super().__init__()

        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.resize(950, 850)
        self.setWindowTitle(title)

        self.table = QTableView()
        self.model = PreviewModel(dataframe)

        self.table.setSortingEnabled(True)
        self.table.setModel(self.model)

        self.common_info = QLabel(f'Common Metadata:\n{common_info}')
        self.process_info = QLabel(f'Process Info:\n{process_info}')
        hbox = QHBoxLayout()
        hbox.addWidget(self.common_info)
        hbox.addWidget(self.process_info)

        self.VBoxTable = QVBoxLayout(centralwidget)
        self.VBoxTable.addLayout(hbox)
        self.VBoxTable.addWidget(self.table)
