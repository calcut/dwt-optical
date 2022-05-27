import sys
import os
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QWidget, QCheckBox,
    QRadioButton, QVBoxLayout, QFileDialog, QPushButton, QLabel)
import logging
from GUI_commonWidgets import QHLine
import lib.csv_helpers as csv

class ImportWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, setup, input_dir, regex, separator, merge):
        super().__init__()
        self.setup = setup
        self.input_dir = input_dir
        self.regex = regex
        self.separator = separator
        self.merge = merge

    def run(self):
        try:
            csv.import_dir_to_csv(self.setup, self.input_dir, self.regex, 
                                    separator=self.separator, merge=self.merge)
        except Exception as e:
            logging.error(e, exc_info=True)
            logging.error('Check the setup file contains the correct instrument details')
        
        self.finished.emit()

class ImportTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName(u"ImportTab")

        btn_width = 80
        default_regex = '(?P<sensor>.+)_Sensor(?P<element>.+)_(?P<fluid>.+)_Rotation(.+).txt'
        default_input = '/Users/calum/git/Glasgow/sampleData/combined'
        
        # Make a Vertical layout within the new tab
        vbox = QVBoxLayout()

        label_info = QLabel("Import existing csv/tsv files")

        info_tooltip = ("This calls csv.import_dir_to_csv()\n"
                    +"Metadata is populated using setup.json, but overridden for any metadata fields\n"
                    +"identified in the input filenames (using a regular expression)\n\n"
                    +"Regex can identifiy any of:\n"
                    +"date, instrument, sensor, element, surface, fluid, repeats, comment\n\n"
                    +"Output files are named based on the 'primary_metadata' and 'subdirs' in setup.json\n"
                    +"Files and metadata can be optionally merged with existing data\n\n"
                    +"Currently assumes tab separated values (tsv)\n"
                    +"Does not import subdirectories of the input dir\n"
                    )

        label_info.setToolTip(info_tooltip)
        
        label_input = QLabel("Input")
        label_input.setStyleSheet("font-weight: bold")
        label_output = QLabel("Output")
        label_output.setStyleSheet("font-weight: bold")
        label_regex = QLabel("Regular expression to extract metadata from filenames:")
        
        label_inpath = QLabel("Input Directory:")
        self.tbox_input = QLineEdit()
        self.tbox_input.setText(default_input)
        label_outpath = QLabel("Output Directory Structure:")
        self.tbox_outpath = QLineEdit()
        self.tbox_outpath.setReadOnly(True)

        label_merge = QLabel('Merge into existing files')
        self.cbox_merge = QCheckBox()
        self.cbox_merge.setChecked(True)
        
        self.tbox_regex = QLineEdit()
        self.tbox_regex.setText(default_regex)

        browse_input = QPushButton("Browse")
        browse_input.clicked.connect(self.get_input_dir)
        browse_input.setFixedWidth(btn_width)

        label_separator = QLabel("Separator:")
        self.separator = '\t'
        rb_tab = QRadioButton("Tab")
        rb_tab.setChecked(True)
        rb_tab.toggled.connect(self.update_separator)
        rb_comma = QRadioButton("Comma")
        rb_comma.setChecked(False)
        rb_comma.toggled.connect(self.update_separator)

        hbox_separator = QHBoxLayout()
        hbox_separator.addWidget(rb_tab)
        hbox_separator.addWidget(rb_comma)
        hbox_separator.addStretch()

        self.btn_import = QPushButton("Import")
        self.btn_import.clicked.connect(self.run_import)
        self.btn_import.setFixedWidth(btn_width)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.tbox_input)
        hbox_input.addWidget(browse_input)

        hbox_merge = QHBoxLayout()
        hbox_merge.addWidget(self.cbox_merge)
        hbox_merge.addWidget(label_merge)
        hbox_merge.addStretch()

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_import)

        vbox.addWidget(label_info)
        vbox.addWidget(QHLine())
        vbox.addWidget(label_input)


        vbox_input = QVBoxLayout()
        vbox_input.addWidget(label_inpath)
        vbox_input.addLayout(hbox_input)
        vbox_input.addWidget(label_separator)
        vbox_input.addLayout(hbox_separator)
        vbox_input.addWidget(label_regex)
        vbox_input.addWidget(self.tbox_regex)

        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox_input, stretch=10)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        vbox.addWidget(QHLine())
        vbox.addWidget(label_output)
        vbox_output = QVBoxLayout()

        vbox_output.addWidget(label_outpath)
        vbox_output.addWidget(self.tbox_outpath)
        vbox_output.addLayout(hbox_merge)
        vbox_output.addLayout(hbox_run)
        vbox_output.addStretch()

        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox_output, stretch=10)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def update_separator(self, value):
        rb = self.sender()

        if rb.isChecked():
            if rb.text() == 'Comma':
                self.separator = ','
            if rb.text() == 'Tab':
                self.separator = '\t'

    def setup_changed(self, setup):
        logging.debug(f"importTab: got new setup {setup['name']}")
        self.setup = setup

        outpath = os.path.abspath(self.setup['datadir'])
        for dir in self.setup['subdirs']:
            outpath = os.path.join(outpath, f"<{dir}>")

        filename = '-'.join(f'<{p}>' for p in self.setup['primary_metadata'])+".txt"
        outpath = os.path.join(outpath, filename)
        self.tbox_outpath.setText(outpath)

    def get_input_dir(self):
        dirname = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        self.tbox_input.setText(dirname)

    def run_import(self):

        regex = self.tbox_regex.text()
        input_dir = self.tbox_input.text()
        merge = self.cbox_merge.isChecked()
        separator = self.separator

        # csv.import_dir_to_csv(setup, input_dir, regex, 
        #                         separator=separator, merge=merge)

        self.thread = QThread()
        self.worker = ImportWorker(self.setup, input_dir, regex, separator, merge)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btn_import.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.btn_import.setEnabled(True)
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    window = ImportTab()
    setup = csv.get_default_setup()
    window.setup_changed(setup)
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())


