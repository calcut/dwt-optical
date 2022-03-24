import json
import os
import sys
from PySide6 import QtWidgets
import pandas as pd
import PySide6.QtWidgets
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QFrame, QTableWidget, QTableWidgetItem, QTableView,
    QVBoxLayout, QFileDialog, QPushButton, QLabel, QSpinBox, QTreeView, QTreeWidget, QTreeWidgetItem)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont
import logging
from GUI_plotCanvas import PlotCanvas
from GUI_tableView import PreviewTable
import lib.csv_helpers as csv
import lib.data_process
import lib.json_setup as json_setup


# class StandardItem(QStandardItem):
#     def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
#         super().__init__()

#         fnt = QFont('Open Sans', font_size)
#         fnt.setBold(set_bold)

#         self.setEditable(False)
#         self.setForeground(color)
#         self.setFont(fnt)
#         self.setText(txt)

class TableWidget(QTableWidget):

    request_subtable = Signal(dict)
    # dictionary_changed = Signal

    def __init__(self, dictionary_in):
        super().__init__()

        self.name = dictionary_in['name']
        self.category = dictionary_in['category']
        self.path = dictionary_in['path']
        self.subdict = None

        self.load_json()

    def build_table(self):
        self.clear()
        self.setColumnCount(2)
        self.setRowCount(len(self.dictionary))
        self.maptable_width = None

        combo_options_dict = json_setup.get_file_choice(self.path)

        for row, key in enumerate(self.dictionary):
            value = self.dictionary[key]
            if key == 'name':
                options = combo_options_dict[self.category]

                # Sort in case insensitive alphabetical order
                options.sort(key=str.lower)
                print(f'{options=}')
                self.combo = QComboBox()
                self.combo.setEditable(True)
                for o in options:
                        self.combo.addItem(o)
                current_index = options.index(self.name)
                self.combo.setCurrentIndex(current_index)
                self.combo.currentIndexChanged.connect(self.dictionary_changed)
                self.setCellWidget(row, 0, self.combo)

                viewButton = QPushButton('Save')
                # viewButton.source = key
                viewButton.clicked.connect(self.save_json)
                self.setCellWidget(row, 1, viewButton)

            # Check if the field can be expanded (i.e. is effectively a nested dictionary)
            # This is indicated by a string starting with *
            elif type(value) == str and value[0] == '*':
                # if 
                button_dict = {}
                button_dict['name'] = value[1:]
                button_dict['category'] = key
                button_dict['path'] = os.path.join(self.path, self.category)
                category = key
                # print(f'{combo_options_dict=}')
                options = combo_options_dict[category]
                # Sort in case insensitive alphabetical order
                options.sort(key=str.lower)
                print(f'{key=}  {options=}')

                combo = QComboBox()
                for o in options:
                    combo.addItem(o)
                current_index = options.index(button_dict['name'])
                combo.setCurrentIndex(current_index)
                self.setCellWidget(row, 0, combo)

                viewButton = QPushButton('View')
                viewButton.dictionary = button_dict
                viewButton.clicked.connect(self.view_subtable)
                self.setCellWidget(row, 1, viewButton)

            elif key == 'map':
                # A special case where we can embed a table within the table

                maptable = QTableWidget()
                maptable.setRowCount(len(value))
                maptable.setColumnCount(2)
                maptable.setHorizontalHeaderLabels(['element', 'detail'])
                # maptable.horizontalHeader().setVisible(False)
                # maptable.setVerticalHeaderLabels(value.keys())
                maptable.verticalHeader().setVisible(False)

                for element_row, element in enumerate(value):
                    detail = value[element]
                    print(f'{element_row=} {detail=}')
                    maptable.setItem(element_row, 0, QTableWidgetItem(str(element)))
                    maptable.setItem(element_row, 1, QTableWidgetItem(str(detail)))
                maptable.resizeColumnsToContents()
                maptable.resizeRowsToContents()
                print(f'{maptable.columnWidth(0)=}')
                print(f'{maptable.horizontalHeader().sectionSize(0)=}')
                print(f'{maptable.horizontalHeader().sectionSize(1)=}')
                
                self.setCellWidget(row, 0, maptable)
                self.maptable_width = (maptable.horizontalHeader().sectionSize(0)
                                     + maptable.horizontalHeader().sectionSize(1))

            else:
                self.setItem(row, 0, QTableWidgetItem(str(value)))

        

        self.itemClicked.connect(self.handleItemClick)
        self.itemDoubleClicked.connect(self.handleItemDoubleClick)
        # self.cellDoubleClicked.connect(self.handleCellDoubleClick)
        self.setHorizontalHeaderLabels([self.dictionary['category'],''])
        self.setVerticalHeaderLabels(self.dictionary.keys())
        self.resizeColumnsToContents()
        if self.maptable_width:
            self.setColumnWidth(0, self.maptable_width)
        self.resizeRowsToContents()
        print(f'{self.columnWidth(0)=}')
        if self.columnWidth(0) < 200:
            self.setColumnWidth(0, 200)
        self.total_width = self.columnWidth(0) + self.columnWidth(1) + self.verticalHeader().width() + 2


    def handleItemClick(self, item):
        print(item.text())

    def view_subtable(self, item):
        # print(self.sender().dictionary)
        self.subdict = self.sender().dictionary
        self.request_subtable.emit(self.subdict)

    def handleItemDoubleClick(self, item):
        print(f'double item {item.text()}')

    def dictionary_changed(self, i):
        self.name = self.combo.currentText()
        self.load_json()
        if self.subdict:
            self.request_subtable.emit(self.subdict)

    def load_json(self):
        json_path = os.path.join(self.path, self.category, self.name+'.json')
        try:
            with open(json_path, 'r') as f:
                self.dictionary = json.load(f)
            self.build_table()
        except FileNotFoundError:
            logging.warning(f'{json_path} not found')

    def save_json(self):
        self.name = self.combo.currentText()
        print(f'{self.name=}')
        json_path = os.path.join(self.path, self.category, self.name+'.json')
        if os.path.exists(json_path):
            logging.warning('file exists, are you sure you want to overwrite')
            msg = QtWidgets.QMessageBox()
            ret = msg.information(self,'Overwrite?',
                 (f'{json_path}\n\nFile exists, overwrite?'),
                  msg.Yes | msg.No)
            if ret == msg.No:
                return

        logging.info(f'writing to {json_path}')
        with open(json_path, 'w') as f:
            json.dump(self.dictionary, f, ensure_ascii=False, indent=3)

        self.build_table()
            

    
    def acceptCombo(self, text):
        print(f'combo {text}')


class SetupEditor(QMainWindow):

    def __init__(self, setup, title):
        QMainWindow.__init__(self)

        centralwidget = QWidget()
        centralwidget.setObjectName(u"centralwidget")
        self.setCentralWidget(centralwidget)
        self.setWindowTitle(title)

        self.width1 = 0
        self.width2 = 0
        self.width3 = 0

        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()

        table = TableWidget(setup)
        table.request_subtable.connect(self.new_subtable)

        
        # self.hbox1.addWidget(table, stretch=table.columnWidth(0))
        # table.horizontalHeader().sectionSizeFromContents()
        # print(f'{table.width()=}')
        # print(f'{table.verticalHeader().height()=}')
        # print(f'{table.verticalHeader().width()=}')
        # print(f'{table.horizontalHeader().height()=}')
        # print(f'{table.horizontalHeader().width()=}')
        # print(f'{table.horizontalHeader().sectionSize(0)=}')
        # print(f'{table.horizontalHeader().sectionSize(1)=}')
        # print(f'{table.horizontalHeader().sectionSize(-1)=}')
        # print(f'{table.columnWidth(-1)=}')
        self.width1 = table.total_width
        self.hbox1.addWidget(table, stretch=self.width1)
        self.hbox1.addStretch(1)

        self.VBoxTable = QVBoxLayout(centralwidget)
        self.VBoxTable.addLayout(self.hbox1, stretch=10)
        # self.VBoxTable.addLayout(self.hbox2)
        # self.VBoxTable.addLayout(self.hbox3)
        self.VBoxTable.addStretch(1)


        self.set_window_width()

        self.show()


    def set_window_width(self):
        self.window_width = self.width1 + self.width2 + self.width3 + 40
        self.resize(self.window_width, 480)


    def new_subtable(self, dict):
        print(f'new subtable!! {dict}')
        try:
            old_table = self.hbox1.itemAt(1).widget()
            self.hbox1.removeWidget(old_table)
            old_table.deleteLater()
        except AttributeError as e:
            # If the subtable doesn't exist yet, ignore this
            # print(e)
            pass
        subtable = TableWidget(dict)
        subtable.request_subtable.connect(self.new_subsubtable)
        # self.hbox1.addWidget(subtable, stretch=10)
        self.width2 = subtable.total_width
        self.hbox1.insertWidget(1, subtable, stretch=self.width2)
        print(f'stretch set to {self.width2}')

        self.set_window_width()



    def new_subsubtable(self, dict):
        print(f'new subsubtable!! {dict}')
        try:
            old_table = self.hbox1.itemAt(2).widget()
            self.hbox1.removeWidget(old_table)
            old_table.deleteLater()
        except AttributeError as e:
            # If the subtable doesn't exist yet, ignore this
            # print(e)
            pass
        subtable = TableWidget(dict)
        subtable.request_subtable.connect(logging.error('not implemented!'))
        self.width3 = subtable.total_width
        self.hbox1.insertWidget(2, subtable, stretch=self.width3)
        print(f'stretch set to {self.width3}')
        # self.hbox1.addWidget(subtable, stretch=10)
        self.set_window_width()


if __name__ == "__main__":
    

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    setup = csv.get_default_setup()
    setup['path'] = '/Users/calum/spectrometer'

    window = SetupEditor(setup, 'Setup Editor')


    d = { 'key1': 'value1', 
    'key2': 'value2',
    'key3': [1,2,3, { 1: 3, 7 : 9}],
    'key4': object(),
    'key5': { 'another key1' : 'another value1',
                'another key2' : 'another value2'} }


    # window.fill_widget(widget, setup)
    # widget.show()

    # meta_df = csv.read_metadata(setup)
    # selection_df = csv.select_from_metadata('element', 'A01', meta_df)
    # selection_df = csv.select_from_metadata('fluid', 'waterA', selection_df)

    # print(selection_df)

    # df, title = csv.merge_dataframes(setup, selection_df)

    # window.set_data(df, title)
    # window.selection_df = selection_df
    # window.setup = setup
    # window.resize(1024, 768)
    # window.show()
    sys.exit(app.exec())