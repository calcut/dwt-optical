import os
import sys
import pandas as pd
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLineEdit, QMainWindow, QWidget, QFrame, QMessageBox,
    QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
from GUI_tableView import MetaTable
from GUI_tableView import SetupTable
from GUI_setupEditor import SetupEditor
import lib.csv_helpers as csv
import lib.json_setup as json_setup

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class SetupBrowse(QWidget):

    new_setup = Signal(dict)

    def __init__(self, rootpath=None):
        QWidget.__init__(self)

        try:
            os.chdir(rootpath)
        except FileNotFoundError:
            logging.warning('Working directory not found, please browse and select one')
        self.rootpath = rootpath

        self.setup = csv.get_default_setup()

        btn_width = 80
        btn_browse_setup = QPushButton("Browse")
        btn_browse_setup.clicked.connect(self.browse_path)
        btn_browse_setup.setFixedWidth(btn_width)

        btn_edit_setup = QPushButton("Edit")
        btn_edit_setup.clicked.connect(self.edit_setup)
        btn_edit_setup.setFixedWidth(btn_width)

        label_root = QLabel("Root Path:")
        self.tbox_root = QLineEdit()
        self.tbox_root.setReadOnly(True)
        self.tbox_root.setText(self.rootpath)

        # hbox_root = QHBoxLayout()
        # hbox_root.addWidget(label_root)
        # hbox_root.addWidget(self.tbox_root)

        label_setup = QLabel("Setup File:")
        self.setup_combo = QComboBox()
        self.setup_combo.setEditable(False)
        

        # self.tbox_setup = QLineEdit()
        # self.tbox_setup.setReadOnly(True)
        # self.tbox_setup.setText(self.setuppath)


        label_metapath = QLabel("Data Index:")
        self.tbox_metapath = QLineEdit()
        self.tbox_metapath.setReadOnly(True)

        btn_view_meta = QPushButton("View")
        btn_view_meta.clicked.connect(self.view_meta)
        btn_view_meta.setFixedWidth(btn_width)

        grid = QGridLayout()
        grid.addWidget(label_root, 0, 0)
        grid.addWidget(self.tbox_root, 0, 1)
        grid.addWidget(btn_browse_setup, 0, 2)

        grid.addWidget(label_setup, 1, 0)
        grid.addWidget(self.setup_combo, 1, 1)
        grid.addWidget(btn_edit_setup, 1, 2)

        grid.addWidget(label_metapath, 2, 0)
        grid.addWidget(self.tbox_metapath, 2, 1)
        grid.addWidget(btn_view_meta, 2, 2)

    

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(grid, stretch=10)
        hbox.addStretch(1)
        # hbox_metapath.addWidget(label_metapath)
        # hbox_metapath.addWidget(self.tbox_metapath)

        
        label = QLabel("Common Setup")
        label.setStyleSheet("font-weight: bold")
        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # Populate the fields:
        self.update_setup_combo()
        self.setup_combo.currentIndexChanged.connect(self.update_setup_json)

    def browse_path(self):
        dir = QFileDialog.getExistingDirectory(self, "Root Path:")
        if dir:
            self.rootpath = dir
            self.tbox_root.setText(dir)
            os.chdir(dir)
            self.update_setup_combo()
            logging.debug(f'setting root directory: {dir}')

    def update_setup_combo(self, current_name='default_setup'):
        logging.debug(f"{current_name=}")
        self.setup_combo.clear()
        combo_options_dict = json_setup.get_file_choice('setup')
        logging.debug(f"{combo_options_dict=}")
        if 'setup' in combo_options_dict:
            options = combo_options_dict['setup']
            # Sort in case insensitive alphabetical order
            options.sort(key=str.lower)
        else:
            logging.warning(f'No "setup" folder found in {os.getcwd()}')
            return
        
        for o in options:
            self.setup_combo.addItem(o)

        try:
            current_index = options.index(current_name)
            self.setup_combo.setCurrentIndex(current_index)
        except:
            logging.debug(f'Could not set combo to {current_name}')
        
        self.update_setup_json()

    def update_setup_json(self):
        if self.setup_combo.currentText() == '':
            return
        self.setuppath = os.path.join('setup', self.setup_combo.currentText()+'.json')
        if os.path.isfile(self.setuppath):
            self.setup = json_setup.json_to_dict(self.setuppath)
            self.metapath = os.path.join(self.setup['datadir'], self.setup['metafile'])
            self.tbox_metapath.setText(self.metapath)
            logging.debug(f"New Setup dict: {self.setup['name']}")
            self.new_setup.emit(self.setup)
        else:
            logging.error(f'No Setup File found at {self.setuppath}')

    def edit_setup(self):
        self.setupEditor = SetupEditor(self.setuppath, 'Setup Editor')
        self.setupEditor.new_setup_name.connect(self.update_setup_combo)
        self.setupEditor.show()

    def view_meta(self):
        meta_df = csv.read_metadata(self.setup)
        if meta_df is None:
            logging.debug('No meta_df to diaplay')
            msg = QMessageBox()
            msg.information(self,'', 'Data Index not found', msg.Ok)
        else:
            self.metaTable = MetaTable(meta_df, title=self.metapath)
            self.metaTable.show()


class MetaFilter(QWidget):

    new_selection_df = Signal(pd.DataFrame)

    def __init__(self):
        QWidget.__init__(self)

        self.setObjectName(u"MetaFilter")
        vbox = QVBoxLayout()

        self.meta_df = None
        label = QLabel("Select/Filter from Metadata file:")

        btn_width = 80
        btn_apply_selection = QPushButton("Apply")
        btn_apply_selection.clicked.connect(self.select_meta)
        btn_apply_selection.setFixedWidth(btn_width)

        btn_preview_selection = QPushButton("Preview")
        btn_preview_selection.clicked.connect(self.preview_selection)
        btn_preview_selection.setFixedWidth(btn_width)

        self.grid_sel = QGridLayout()
        self.grid_sel.setContentsMargins(0, 0, 0, 0)
        self.add_sel_row()

        hbox_selection = QHBoxLayout()
        hbox_selection.addStretch()
        hbox_selection.addWidget(btn_apply_selection)
        hbox_selection.addWidget(btn_preview_selection)

        vbox.addWidget(label)
        vbox.addLayout(self.grid_sel)
        vbox.addLayout(hbox_selection)
        self.setLayout(vbox)

    def select_meta(self):

        if self.meta_df is None:
            logging.debug("meta_df is not found")
            return

        self.selection_df = self.meta_df

        rows = self.grid_sel.rowCount()
        for i in range(rows):
            if i == 0:
                # This is the header row
                continue
            try:
                if i == 1:
                    # First filter is effectively an AND with the orginal index
                    logic = 'AND'
                else:
                    logic = self.grid_sel.itemAtPosition(i, 0).widget().currentText()
                
                key = self.grid_sel.itemAtPosition(i, 1).widget().currentText()
                value = self.grid_sel.itemAtPosition(i, 2).widget().currentText()
                wildcard = self.grid_sel.itemAtPosition(i, 3).widget().isChecked()
            except AttributeError:
                # This can happen if rows are deleted then recreated, ghost row
                # indicies still exist.
                continue

            if key == '':
                continue
            if logic == 'AND':
                self.selection_df = csv.select_from_metadata(key, value,
                     self.selection_df,
                     regex=wildcard)
            if logic == 'OR':
                filtered_df = csv.select_from_metadata(key, value,
                     self.meta_df,
                     regex=wildcard)
                self.selection_df.reset_index(inplace=True)
                filtered_df.reset_index(inplace=True)
                self.selection_df = pd.merge(self.selection_df,
                                             filtered_df,
                                             how = 'outer')
                self.selection_df.set_index('index', verify_integrity=True, inplace=True)

        logging.info(f'{len(self.selection_df)} metadata rows in selection, '
            + f'with {self.selection_df["repeats"].sum()} total measurements')
       
        self.new_selection_df.emit(self.selection_df)
        
    def add_sel_row(self):
        
        rows = self.grid_sel.rowCount()
        columns = self.grid_sel.columnCount()
        btn_width = 80

        item = self.grid_sel.itemAtPosition(0, 0)
        if item is None:
            widget = QPushButton('Add Filter')
            widget.clicked.connect(self.add_sel_row)
            widget.setFixedWidth(btn_width)
            self.grid_sel.addWidget(widget, 0, 4, 1, 1, alignment=Qt.AlignRight)

            self.grid_sel.addWidget(QLabel("Metadata Key"), 0, 1, 1, 1)
            self.grid_sel.addWidget(QLabel("Value"), 0, 2, 1, 1)
            self.grid_sel.addWidget(QLabel("Wildcard"), 0, 3, 1, 1)
            self.grid_sel.addWidget(QLabel(""), 0, 0, 1, 1)

        else:
            self.logicCombo = QComboBox()
            self.logicCombo.addItem('AND')
            self.logicCombo.addItem('OR')

            self.keyCombo = QComboBox()
            self.keyCombo.setEditable(True)
            self.keyCombo.addItem('')
            self.keyCombo.currentTextChanged.connect(self.keyChanged)

            if hasattr(self, 'meta_df'):
                if isinstance(self.meta_df, pd.DataFrame):
                    items = self.meta_df.columns.tolist()
                    self.keyCombo.addItems(items)

            self.valCombo = QComboBox()
            self.valCombo.setEditable(True)
            self.valCombo.addItem('')

            if not rows == 1:
                # Logic Operator doesn't make sense on first row
                self.grid_sel.addWidget(self.logicCombo, rows, 0, 1, 1)
            self.grid_sel.addWidget(self.keyCombo, rows, 1, 1, 1)
            self.grid_sel.addWidget(self.valCombo, rows, 2, 1, 1)
            self.grid_sel.addWidget(QCheckBox(), rows, 3, 1, 1)
            widget = QPushButton('Remove')
            widget.clicked.connect(self.remove_sel_row)
            widget.setFixedWidth(btn_width)
            self.grid_sel.addWidget(widget, rows, 4, 1, 1, alignment=Qt.AlignRight)

    def remove_sel_row(self):
            index = self.grid_sel.indexOf(self.sender())
            row = self.grid_sel.getItemPosition(index)[0]
            for column in range(self.grid_sel.columnCount()):
                layout = self.grid_sel.itemAtPosition(row, column)
                if layout is not None:
                    layout.widget().deleteLater()
                    self.grid_sel.removeItem(layout)

    def keyChanged(self, key):
        index = self.grid_sel.indexOf(self.sender())
        row = self.grid_sel.getItemPosition(index)[0]
        valuebox = self.grid_sel.itemAtPosition(row, 2).widget()
        # print(f'sender text = {self.sender.currentText()}')
        valuebox.clear()
        try:
            logging.debug(self.meta_df[key].unique())
            items = sorted(self.meta_df[key].unique())
            items = [str(i) for i in items]
            valuebox.addItem('')
            valuebox.addItems(items)
        except KeyError:
            logging.debug(f'Key "{key}" not found in Metadata index file')

    def setup_changed(self, setup):

        logging.debug(f"MetaFilter : got new setup")
        self.meta_df = csv.read_metadata(setup)


        # Update the 'key' combo boxes with fields from new meta_df 
        rows = self.grid_sel.rowCount()
        for row in range(rows):
            if row == 0:
                # This is the header row
                continue
            # try:
            keyCombo = self.grid_sel.itemAtPosition(row,1).widget()
            keyCombo.clear()
            # except AttributeError as e:
                # logging.debug(e)
                # logging.debug(f"row {row}")
            items = self.meta_df.columns.tolist()
            keyCombo.addItem('')
            keyCombo.addItems(items)

    def preview_selection(self):
        title = 'Selected Data'
        try:
            self.selectedTable = MetaTable(self.selection_df, title)
            self.selectedTable.show()
        except AttributeError:
            logging.error("Please Apply filter first")

if __name__ == "__main__":

    app = QApplication(sys.argv)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    window = QMainWindow()
    centralwidget = QWidget()
    centralwidget.setObjectName(u"centralwidget")
    window.setCentralWidget(centralwidget)

    # metaBrowse = MetaBrowse()
    setupBrowse = SetupBrowse("C:/Users/calum/spectrometer")
    metaFilter = MetaFilter()
    # metaBrowse.new_metapath.connect(metaFilter.metapath_changed)
    # metaBrowse.update_meta_df()
    
    vbox = QVBoxLayout()
    vbox.addWidget(setupBrowse)
    vbox.addStretch()
    # vbox.addWidget(metaBrowse)
    vbox.addWidget(QHLine())
    vbox.addWidget(metaFilter)
    centralwidget.setLayout(vbox)
    window.resize(1024, 400)
    window.show()
    sys.exit(app.exec())
