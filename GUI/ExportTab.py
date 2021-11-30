from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QWidget,
QVBoxLayout, QFileDialog, QPushButton, QLabel)

# export lib.csv_helpers as csv

class ExportWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, exportFunction, input_dir, selection, output_dir):
        super().__init__()
        self.exportFunction = exportFunction
        self.selection = selection
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        self.exportFunction(self.input_dir, self.selection, self.output_dir, append=False)
        # export_dataframes(meta_df='index.tsv', path='./raw', outfile=None)
        self.finished.emit()

class ExportTab():

    def __init__(self, exportFunction):

        self.exportFunction = exportFunction

        default_meta = '/Users/calum/git/Glasgow/dwt-optical/imported/index.tsv'
        default_outfile = '/Users/calum/git/Glasgow/dwt-optical/export.tsv'
        
        # New Widget (to be used as a tab)
        self.tab = QWidget()
        self.tab.setObjectName(u"ExportTab")

        # Make a Vertical layout within the new tab
        vbox = QVBoxLayout(self.tab)

        label_title = QLabel("Export data to large tsv table, ready for LDA processing")
        label_index = QLabel("Metadata Index File:")
        label_selection = QLabel("Selection to Export:")
        label_output = QLabel("Output File:")
        
        # tooltip_selection = ("Should extract at least [sensor, element, fluid] as in example\n"
        #     +"Other metadata can be captured and will be also be saved")

        self.tbox_meta = QLineEdit()
        self.tbox_meta.setText(default_meta)
        self.tbox_output = QLineEdit()
        self.tbox_output.setText(default_outfile)
        self.tbox_selection = QLineEdit()
        self.tbox_selection.setText('')

        browse_meta = QPushButton("Browse")
        browse_meta.clicked.connect(self.get_meta)

        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.get_output)

        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.run_export)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(label_index)
        hbox_input.addWidget(self.tbox_meta)
        hbox_input.addWidget(browse_meta)

        hbox_output = QHBoxLayout()
        hbox_output.addWidget(label_output)
        hbox_output.addWidget(self.tbox_output)
        hbox_output.addWidget(browse_output)

        hbox_run = QHBoxLayout()
        hbox_run.addStretch()
        hbox_run.addWidget(self.btn_export)

        vbox.addWidget(label_title)
        vbox.addLayout(hbox_input)
        vbox.addLayout(hbox_output)
        vbox.addWidget(label_selection)
        vbox.addWidget(self.tbox_selection)
        vbox.addLayout(hbox_run)
        vbox.addStretch()
        
    def get_meta(self):
        metafile = QFileDialog.getOpenFileName(self.tab, "Select Metadata index.tsv")
        self.tbox_input.setText(metafile)

    def get_output(self):
        outfile = QFileDialog.getSaveFileName(self.tab, "Select Output File")
        self.tbox_output.setText(outfile)

    def run_export(self):

        selection = self.tbox_selection.text()
        input_dir = self.tbox_input.text()
        output_dir = self.tbox_output.text()

        self.thread = QThread()
        self.worker = ExportWorker(self.exportFunction, input_dir, selection, output_dir)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btn_export.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.btn_export.setEnabled(True)
        )




