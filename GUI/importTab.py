from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QWidget,
QVBoxLayout, QFileDialog, QPushButton, QLabel)

# import lib.csv_helpers as csv

class ImportWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, importFunction, input_dir, regex, output_dir):
        super().__init__()
        self.importFunction = importFunction
        self.regex = regex
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        self.importFunction(self.input_dir, self.regex, self.output_dir, append=False)
        # csv.import_dir_to_csv(self.input_dir, self.regex, self.output_dir, append=False)
        self.finished.emit()

class ImportTab():

    def __init__(self, importFunction):

        self.importFunction = importFunction

        default_regex = '(?P<sensor>.+)_Sensor(?P<element>.+)_(?P<fluid>.+)_Rotation(.+).txt'
        default_input = '/Users/calum/git/Glasgow/sampleData/combined'
        default_output = '/Users/calum/git/Glasgow/dwt-optical/imported'
        
        # New Widget (to be used as a tab)
        self.tab = QWidget()
        self.tab.setObjectName(u"ImportTab")

        # Make a Vertical layout within the new tab
        vbox = QVBoxLayout(self.tab)

        label_title = QLabel("Import existing csv/tsv files, extract metadata from filenames")
        label_input = QLabel("Input Directory:")
        label_output = QLabel("Output Directory:")
        label_regex = QLabel("Regular expression to extract metadata from filenames:")
        
        tooltip_regex = ("Should extract at least [sensor, element, fluid] as in example\n"
            +"Other metadata can be captured and will be also be saved")

        self.tbox_input = QLineEdit()
        self.tbox_input.setText(default_input)
        self.tbox_output = QLineEdit()
        self.tbox_output.setText(default_output)
        self.tbox_regex = QLineEdit()
        self.tbox_regex.setText(default_regex)
        self.tbox_regex.setToolTip(tooltip_regex)

        browse_input = QPushButton("Browse")
        browse_input.clicked.connect(self.get_input_dir)

        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output_dir)

        self.btn_import = QPushButton("Import")
        self.btn_import.clicked.connect(self.run_import)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_input)
        hbox_input.addWidget(self.tbox_input)
        hbox_input.addWidget(browse_input)

        hbox_output = QHBoxLayout()
        hbox_output.addWidget(label_output)
        hbox_output.addWidget(self.tbox_output)
        hbox_output.addWidget(browse_output)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_import)

        vbox.addWidget(label_title)
        vbox.addLayout(hbox_input)
        vbox.addLayout(hbox_output)
        vbox.addWidget(label_regex)
        vbox.addWidget(self.tbox_regex)
        vbox.addLayout(hbox_run)
        vbox.addStretch()
        
    def get_input_dir(self):
        dirname = QFileDialog.getExistingDirectory(self.tab, "Select Input Directory")
        self.tbox_input.setText(dirname)

    def get_output_dir(self):
        dirname = QFileDialog.getExistingDirectory(self.tab, "Select Output Directory")
        self.tbox_output.setText(dirname)

    def run_import(self):

        regex = self.tbox_regex.text()
        input_dir = self.tbox_input.text()
        output_dir = self.tbox_output.text()

        self.thread = QThread()
        self.worker = ImportWorker(self.importFunction, input_dir, regex, output_dir)

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




