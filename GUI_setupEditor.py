import json
from operator import index
import os
from signal import signal
import sys
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QLabel, QSpinBox, QDialogButtonBox, QDialog)
import logging

from matplotlib.font_manager import json_load
import lib.csv_helpers as csv
import lib.json_setup as json_setup
import string

class TableWidget(QTableWidget):

    request_subtable = Signal(dict)
    request_combo_refresh = Signal(dict)
    new_setup = Signal()

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
        self.setRowCount(len(self.dictionary) + 1)
        maptable_row = None
        self.subtable_dict = {}

        combo_options_dict = json_setup.get_file_choice(self.path)

        self.setHorizontalHeaderLabels([self.dictionary['category'],''])
        self.setVerticalHeaderLabels(self.dictionary.keys())

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


            elif type(value) == str and value[0] == '*':
                # Check if the field can be expanded (i.e. is effectively a nested dictionary)
                # This is indicated by a string starting with *
                
                current_name = value[1:]
                options = combo_options_dict[key]
                # Sort in case insensitive alphabetical order
                options.sort(key=str.lower)
                combo = QComboBox()
                for o in options:
                    combo.addItem(o)
                current_index = options.index(current_name)
                combo.setCurrentIndex(current_index)
                combo.currentIndexChanged.connect(self.combo_changed)
                self.setCellWidget(row, 0, combo)
                self.combo_tracker[key] = combo

                viewButton = QPushButton('View')
                viewButton.clicked.connect(self.view_subtable)
                self.setCellWidget(row, 1, viewButton)

            elif key == 'map':
                # A special case where we can embed a table within the table

                self.maptable = QTableWidget()
                self.maptable.setRowCount(len(value))
                self.maptable.setColumnCount(2)
                self.maptable.setHorizontalHeaderLabels(['element', 'detail'])
                self.maptable.verticalHeader().setVisible(False)

                for element_row, element in enumerate(value):
                    detail = value[element]
                    self.maptable.setItem(element_row, 0, QTableWidgetItem(str(element)))
                    self.maptable.setItem(element_row, 1, QTableWidgetItem(str(detail)))
                self.maptable.resizeColumnsToContents()
                self.maptable.resizeRowsToContents()
                
                self.setCellWidget(row, 0, self.maptable)
                maptable_row = row
                maptable_width = (self.maptable.horizontalHeader().sectionSize(0)
                                     + self.maptable.horizontalHeader().sectionSize(1))
                maptable_height = self.maptable.height()
                self.maptable.cellChanged.connect(self.map_field_changed)


                btn_new_map = QPushButton('New Map')
                btn_new_map.setMaximumHeight(self.saveButton.height())
                btn_new_map.clicked.connect(self.new_map)

                self.setCellWidget(row, 1, btn_new_map)
                
            elif key == 'category':
                # This sets category to read only
                cell_item = QTableWidgetItem(str(value))
                cell_item.setFlags(Qt.ItemIsEnabled)
                self.setItem(row, 0, cell_item)

            else:
                cell_item = QTableWidgetItem(str(value))
                self.setItem(row, 0, cell_item)

        addButton = QPushButton('Add Row')
        addButton.clicked.connect(self.add_row)
        row = self.rowCount() -1
        self.setCellWidget(row, 1, addButton)
        self.setVerticalHeaderItem(row, QTableWidgetItem(''))
        
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        if maptable_row:
            self.setColumnWidth(0, maptable_width)
            self.setRowHeight(maptable_row, maptable_height)
        if self.columnWidth(0) < 200:
            self.setColumnWidth(0, 200)
        self.total_width = self.columnWidth(0) + self.columnWidth(1) + self.verticalHeader().width() + 2
        logging.debug(f'{self.total_width=}')
        self.needs_saved(False)


    def add_row(self):
        dlg = QDialog(self)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(dlg.accept)
        buttonBox.rejected.connect(dlg.reject)
        
        key_box = QLineEdit()
        value_box = QLineEdit()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Setting'))
        hbox.addWidget(key_box)
        hbox.addWidget(QLabel('Value'))
        hbox.addWidget(value_box)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(buttonBox)
        dlg.setWindowTitle("Add new setting")
        dlg.setLayout(vbox)
        if dlg.exec():
            key = key_box.text()
            value = value_box.text()
            row = self.rowCount() - 1
            self.insertRow(row)
            self.setVerticalHeaderItem(row, QTableWidgetItem(key))
            self.setItem(row, 0, QTableWidgetItem(value))
            self.dictionary[key] = value
            self.needs_saved(True)

    def view_subtable(self, item):
        # Slightly convoluted way to get the row of the view button
        row = self.indexAt(self.sender().pos()).row()
        key = self.verticalHeaderItem(row).text()
        self.subtable_dict['path'] = os.path.join(self.path, key)
        self.subtable_dict['category'] = key
        self.subtable_dict['name'] = self.dictionary[key][1:]

        logging.debug(f'{self.subtable_dict=}')
        self.request_subtable.emit(self.subtable_dict)

    def new_setup_name(self, text):
        self.dictionary['name'] = text
        self.needs_saved(True)
        logging.debug(f'New setup name: {text}')

    def setup_changed(self, i):
        name = self.setup_combo.currentText()
        self.load_json(self.path, name)
        self.new_setup.emit()

    def text_field_changed(self, row, col):
        item = self.item(row, col)
        value = item.text()
        key = self.verticalHeaderItem(row).text()
        self.dictionary[key] = value
        self.needs_saved(True)
        logging.debug(f'{key=} {value=}')

    def map_field_changed(self, row, col):
        item = self.maptable.item(row, col)
        logging.debug(f'maptable field changed {row=} {col=}')

        key = self.maptable.item(row, 0).text()
        value = self.maptable.item(row, 1).text()

        self.dictionary['map'][key] = value
        logging.debug(f'maptable set {key=} {value=}')

        self.needs_saved(True)

    def new_map(self):
        dlg = QDialog(self)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(dlg.accept)
        buttonBox.rejected.connect(dlg.reject)

        cols = 1
        rows = 1
        try: #Try to get existing element row/col counts
            for e in self.dictionary['map'].keys():
                col_count = int(e[1:])
                if col_count > cols:
                    cols = col_count
                row_count = string.ascii_uppercase.index(e[0])+1
                if  row_count > rows:
                    rows = row_count
        except Exception as e:
            logging.warning(e)

        rows_box = QSpinBox()
        rows_box.setMinimum(1)
        rows_box.setMaximum(26)
        rows_box.setValue(rows)
        cols_box = QSpinBox()
        cols_box.setMinimum(1)
        cols_box.setMaximum(99)
        cols_box.setValue(cols)

        detail_box = QLineEdit()

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Element Rows'))
        hbox.addWidget(rows_box)
        hbox.addWidget(QLabel('Element Columns'))
        hbox.addWidget(cols_box)

        hbox_detail = QHBoxLayout()
        hbox_detail.addWidget(QLabel('Detail (optional)'))
        hbox_detail.addWidget(detail_box)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox_detail)
        vbox.addWidget(buttonBox)
        dlg.setWindowTitle("Define new map")
        dlg.setLayout(vbox)
        if dlg.exec():

            rows = rows_box.value()
            cols = cols_box.value()
            row_list = list(string.ascii_uppercase[:rows])
            col_list = range(1, cols+1)
            map_dict = {}
            for row, col in [(row, col) for row in row_list for col in col_list]:
                map_dict[F"{row}{col:02d}"] = detail_box.text()

            self.dictionary['map'] = map_dict
            self.build_table()
            self.needs_saved(True)

    def combo_changed(self, i):
        # Slightly convoluted way to get the table row of the combo box
        row = self.indexAt(self.sender().pos()).row()
        key = self.verticalHeaderItem(row).text()
        value = self.sender().currentText()
        self.dictionary[key] = '*'+value
        self.needs_saved(True)
        logging.debug(f'{key=} {value=}')

        # If a subtable matching this combo is visible, update it
        if 'category' in self.subtable_dict:
            if self.subtable_dict['category'] == key:
                self.subtable_dict['name'] = self.dictionary[key][1:]
                self.request_subtable.emit(self.subtable_dict)

    def check_valid_layout(self):
        #Try to check valid layout. This might be better in the json lib file.
        try:
            if 'layout' in self.dictionary and self.dictionary['category'] == 'sensor':
                layout = self.dictionary['layout'][1:]

                map_fields = {}
                for key, val in self.dictionary.items():
                    if key.endswith('_map'):
                        map_fields[key] = val[1:]

                for key, file in map_fields.items():
                    json_path = os.path.join(self.path, key, file+'.json')
                    try:
                        with open(json_path, 'r') as f:
                            temp_dict = json.load(f)
                    except FileNotFoundError:
                        logging.warning(f'{json_path} not found')
                    if 'valid_layout' in temp_dict:
                        valid = temp_dict['valid_layout']
                        if valid != layout:
                            text = (f'This {key} may be incompatible with {layout}'
                                    +f', it expects layout:  {valid}')
                            logging.warning(text)
                            msg = QtWidgets.QMessageBox()
                            msg.warning(self,'Warning', text, msg.Ok)
        except Exception as e:
            logging.error(e + "unable to check valid_layout")


    def refresh_combo(self, refresh_dict):
        # A slot typically triggered when a sub table has been updated / saved
        # Ensures the GUI stays in sync
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
        self.check_valid_layout()

        if os.path.exists(json_path):
            logging.warning('file exists, are you sure you want to overwrite')
            msg = QtWidgets.QMessageBox()
            ret = msg.information(self,'Overwrite?',
                 (f'{json_path}\n\nFile exists, overwrite?'),
                  msg.Yes | msg.No)
            if ret == msg.No:
                return

        else:
            logging.warning('file exists, are you sure you want to overwrite')
            msg = QtWidgets.QMessageBox()
            ret = msg.information(self,'',
                  f"Save as new {self.dictionary['category']} file?\n\n{json_path}",
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
            self.saveButton.setEnabled(True)
            # self.saveButton.setStyleSheet("border :2px solid ;" 
                                        # "border-color : red")
        else:
            self.saveButton.setEnabled(False)
            # self.saveButton.setStyleSheet(None)


class SetupEditor(QMainWindow):

    new_setup = Signal(string)

    def __init__(self, filepath, title):
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

        path = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name = os.path.splitext(filename)[0]

        self.table1 = TableWidget(path, name)
        self.table1.request_subtable.connect(self.update_table2)
        self.table1.new_setup.connect(self.remove_subtables)
        # self.table1.new_setup.connect(self.new_setup.emit(self.table1.dictionary['name']))

        self.width1 = self.table1.total_width
        self.hbox1.addWidget(self.table1, stretch=self.width1)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.ok_button_press)
        buttonBox.rejected.connect(self.close)

        self.vbox = QVBoxLayout(centralwidget)
        self.vbox.addLayout(self.hbox1, stretch=10)
        self.vbox.addWidget(buttonBox)
        # self.VBoxTable.addStretch(1)

        self.sensor_layout = None
        self.set_window_width()

        self.show()

    def ok_button_press(self):

        t1 = self.table1.saveButton.isEnabled()
        try:
            t2 = self.table2.saveButton.isEnabled()
        except:
            t2 = False
        try:
            t3 = self.table2.saveButton.isEnabled()
        except:
            t3 = False

        if (t1 or t2 or t3):
            msg = QtWidgets.QMessageBox()
            ret = msg.information(self,'',
                  (f"Unsaved changes\nClose anyway?"),
                  msg.Yes | msg.No)
            if ret == msg.No:
                return
        self.close()



    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            focuswidget = QtWidgets.QApplication.focusWidget()
            try:
                indexes = sorted(focuswidget.selectedIndexes())
                self.copied_cells = []
                for cell in indexes:
                    self.copied_cells.append([cell.row(), cell.column(), QTableWidgetItem(cell.data())])
            except Exception as e:
                logging.error(e)

        elif event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
            focuswidget = QtWidgets.QApplication.focusWidget()

            try:
                r = focuswidget.currentRow() - self.copied_cells[0][0]
                c = focuswidget.currentColumn() - self.copied_cells[0][1]
                print(f'{r=} {c=}')
                for cell in self.copied_cells:
                    focuswidget.setItem(cell[0] + r, cell[1] + c, cell[2])
            except Exception as e:
                logging.error(e)

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
        # self.table3.request_subtable.connect(logging.error('further subtables not implemented!'))
        self.table3.request_combo_refresh.connect(self.table2.refresh_combo)
        self.width3 = self.table3.total_width
        self.hbox1.insertWidget(2, self.table3, stretch=self.width3)
        self.set_window_width()

    def remove_subtables(self):
        while self.hbox1.count() > 1:
            table = self.hbox1.itemAt(1).widget()
            self.hbox1.removeWidget(table)
            table.deleteLater()
        self.width2 = 0
        self.width3 = 0
        self.set_window_width()


if __name__ == "__main__":
    

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # setup = csv.get_default_setup()
    filepath = '/Users/calum/spectrometer/setup/default_setup.json'

    window = SetupEditor(filepath, 'Setup Editor')

    sys.exit(app.exec())