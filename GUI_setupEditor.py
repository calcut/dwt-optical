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


class TableWidget(QTableWidget):

    request_subtable = Signal(dict)
    request_combo_refresh = Signal(dict)
    # dictionary_changed = Signal

    def __init__(self, path, name):
        super().__init__()

        self.path = path
        self.load_json(path, name)

        self.cellChanged.connect(self.text_field_changed)

    def build_table(self):
        self.clear()
        self.subdict = None
        self.combo_tracker = {}
        self.setColumnCount(2)
        self.setRowCount(len(self.dictionary))
        self.maptable_width = None
        self.subtable_dict = {}

        combo_options_dict = json_setup.get_file_choice(self.path)

        for row, key in enumerate(self.dictionary):
            value = self.dictionary[key]

            if key == 'name':
                self.saveButton = QPushButton('Save')
                self.saveButton.clicked.connect(self.save_json)
                self.setCellWidget(row, 1, self.saveButton)
                if self.dictionary['category'] != 'setup':
                    self.setItem(row, 0, QTableWidgetItem(str(value)))

            if key == 'name' and self.dictionary['category'] == 'setup':
                # A special case where a drop down is provided for the top
                # level 'setup' category
                options = combo_options_dict['setup']

                # Sort in case insensitive alphabetical order
                options.sort(key=str.lower)
                self.setup_combo = QComboBox()
                self.setup_combo.setEditable(True)
                for o in options:
                    self.setup_combo.addItem(o)
                current_index = options.index(self.dictionary['name'])
                self.setup_combo.setCurrentIndex(current_index)
                self.setup_combo.currentIndexChanged.connect(self.setup_changed)
                self.setup_combo.editTextChanged.connect(self.new_setup_name)
                self.setCellWidget(row, 0, self.setup_combo)

            # Check if the field can be expanded (i.e. is effectively a nested dictionary)
            # This is indicated by a string starting with *
            elif type(value) == str and value[0] == '*':
                
                current_name = value[1:]
                options = combo_options_dict[key]
                # Sort in case insensitive alphabetical order
                options.sort(key=str.lower)

                combo = QComboBox()
                for o in options:
                    combo.addItem(o)
                current_index = options.index(current_name)
                combo.setCurrentIndex(current_index)
                combo.key = key
                combo.currentIndexChanged.connect(self.combo_changed)
                self.setCellWidget(row, 0, combo)
                self.combo_tracker[key] = combo

                viewButton = QPushButton('View')
                viewButton.key = key
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
                    maptable.setItem(element_row, 0, QTableWidgetItem(str(element)))
                    maptable.setItem(element_row, 1, QTableWidgetItem(str(detail)))
                maptable.resizeColumnsToContents()
                maptable.resizeRowsToContents()
                
                self.setCellWidget(row, 0, maptable)
                self.maptable_width = (maptable.horizontalHeader().sectionSize(0)
                                     + maptable.horizontalHeader().sectionSize(1))

            else:
                cell_item = QTableWidgetItem(str(value))
                cell_item.key = key
                self.setItem(row, 0, cell_item)
        

        
        self.setHorizontalHeaderLabels([self.dictionary['category'],''])
        self.setVerticalHeaderLabels(self.dictionary.keys())
        self.resizeColumnsToContents()
        if self.maptable_width:
            self.setColumnWidth(0, self.maptable_width)
        self.resizeRowsToContents()
        if self.columnWidth(0) < 200:
            self.setColumnWidth(0, 200)
        self.total_width = self.columnWidth(0) + self.columnWidth(1) + self.verticalHeader().width() + 2
        logging.debug(f'{self.total_width=}')
        self.needs_saved(False)


    # def handleItemClick(self, item):
    #     print(item.text())

    # def handleItemDoubleClick(self, item):
    #     print(f'doubleclick item {item.text()}')

    def view_subtable(self, item):
        self.subtable_dict['path'] = os.path.join(self.path, self.sender().key)
        self.subtable_dict['category'] = self.sender().key
        self.subtable_dict['name'] = self.dictionary[self.sender().key][1:]

        logging.debug(f'{self.subtable_dict=}')
        self.request_subtable.emit(self.subtable_dict)

    def new_setup_name(self, text):
        self.dictionary['name'] = text
        self.needs_saved(True)
        logging.debug(f'New setup name: {text}')

    def setup_changed(self, i):
        name = self.setup_combo.currentText()
        self.load_json(self.path, name)

    def text_field_changed(self, row, col):
        item = self.item(row, col)
        logging.debug(f'field changed {row=} {col=}')
        value = item.text()
        key = item.key
        self.dictionary[key] = value
        self.needs_saved(True)
        logging.debug(f'{key=} {value=}')

    def combo_changed(self, i):
        value = self.sender().currentText()
        key = self.sender().key
        self.dictionary[key] = '*'+value
        self.needs_saved(True)
        logging.debug(f'{key=} {value=}')

        # If a subtable matching this combo is visible, update it
        if 'category' in self.subtable_dict:
            if self.subtable_dict['category'] == key:
                self.subtable_dict['name'] = self.dictionary[key][1:]
                self.request_subtable.emit(self.subtable_dict)

    def refresh_combo(self, refresh_dict):
        key = refresh_dict['category']
        current_name = refresh_dict['name']
        logging.debug(f'refreshing combo {key} == {current_name}')
        combo_options_dict = json_setup.get_file_choice(self.path)
        options = combo_options_dict[key]
        options.sort(key=str.lower)
        logging.debug(options)

        combo = self.combo_tracker[key]
        combo.clear()
        for o in options:
            combo.addItem(o)
        current_index = options.index(current_name)
        combo.setCurrentIndex(current_index)


    # def subtable_changed(self, i):
    #     print(f'{self.sender().currentText()=}')
    #     if self.subdict:
    #         self.subdict['name'] = self.sender().currentText()
    #         self.request_subtable.emit(self.subdict)

    def load_json(self, path, name):
        json_path = os.path.join(path, name+'.json')
        try:
            with open(json_path, 'r') as f:
                self.dictionary = json.load(f)
            logging.debug(f'loaded {json_path}')
            self.build_table()
        except FileNotFoundError:
            logging.warning(f'{json_path} not found')

    def save_json(self):
        name = self.dictionary['name']
        json_path = os.path.join(self.path, name+'.json')
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
        self.needs_saved(False)
        
        self.build_table()

        # Code to prompt a 'parent' table to update itself
        refresh_dict = {}
        refresh_dict['name'] = name
        refresh_dict['category'] = self.dictionary['category']
        self.request_combo_refresh.emit(refresh_dict)

    def needs_saved(self, bool):
        if bool:
            self.saveButton.setStyleSheet("border :2px solid ;" 
                                        "border-color : red")
        else:
            logging.debug('resetting save button style')
            self.saveButton.setStyleSheet("border : none")

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

        path = os.path.join(setup['path'], setup['category'])
        self.table1 = TableWidget(path, setup['name'])
        # table = TableWidget(setup['path'], setup['category'], setup['name'])
        self.table1.request_subtable.connect(self.update_table2)

        
        self.width1 = self.table1.total_width
        self.hbox1.addWidget(self.table1, stretch=self.width1)
        # self.hbox1.addStretch(1)

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


    def update_table2(self, subtable_dict):
        logging.debug('New table2')
        path = subtable_dict['path']
        name = subtable_dict['name']

        while self.hbox1.count() > 1:
            # This also deletes table3 if present
            old_table = self.hbox1.itemAt(1).widget()
            self.hbox1.removeWidget(old_table)
            old_table.deleteLater()

        self.table2 = TableWidget(path, name)
        self.table2.request_subtable.connect(self.update_table3)
        self.table2.request_combo_refresh.connect(self.table1.refresh_combo)
        self.width2 = self.table2.total_width
        self.width3 = 0
        self.hbox1.insertWidget(1, self.table2, stretch=self.width2)

        self.set_window_width()

    def update_table3(self, subtable_dict):
        logging.debug('New table3')

        path = subtable_dict['path']
        name = subtable_dict['name']

        while self.hbox1.count() > 2:
            old_table = self.hbox1.itemAt(2).widget()
            self.hbox1.removeWidget(old_table)
            old_table.deleteLater()

        self.table3 = TableWidget(path, name)
        self.table3.request_subtable.connect(logging.error('further subtables not implemented!'))
        self.table3.request_combo_refresh.connect(self.table2.refresh_combo)
        self.width3 = self.table3.total_width
        self.hbox1.insertWidget(2, self.table3, stretch=self.width3)
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