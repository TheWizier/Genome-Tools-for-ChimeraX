from pathlib import Path

from Qt import QtCore, QtGui, QtWidgets
from Qt.QtWidgets import QWidget, QFileDialog


class BrowseForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.browseButton = QtWidgets.QPushButton(self)
        self.browseButton.setObjectName("browseButton")
        self.horizontalLayout_2.addWidget(self.browseButton)

        self.browseButton.clicked.connect(self.load_file_path)

        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.file_types = "All files (*.*)"

        self.lineEdit.setText(str(Path.home()))

        "BED-files (*.bed *.bed3 *.bed4 *.bed5 *.bed6 *.bed7 *.bed8 *.bed9 *.bed10 *.bed11 *.bed12);;All files (*.*)"

    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("browseForm", "browseForm"))
        self.browseButton.setText(_translate("browseForm", "..."))

    def set_file_types(self, file_types: str):
        self.file_types = file_types

    def load_file_path(self):
        # filepaths, selected_filter = QFileDialog.getOpenFileName(self,
        #                              "Select one or multiple files to open",
        #                              self.lineEdit.text().strip().split(",")[0],
        #                              "bed-files (*.bed)")
        #
        # if(filepaths != ""):
        #     text = ""
        #     for filepath in filepaths:
        #         text += filepath + ", "
        #     text = text[:-2]
        #     self.lineEdit.setText(text)
        try:
            filepath, selected_filter = QFileDialog.getOpenFileName(self,
                                                                    "Select a file to open",
                                                                    self.lineEdit.text(),
                                                                    self.file_types)
        except RuntimeError:
            filepath, selected_filter = QFileDialog.getOpenFileName(self,
                                                                    "Select a file to open",
                                                                    "",
                                                                    self.file_types)
        if(filepath == ""):
            return
        self.lineEdit.setText(filepath)

    def get_file_path(self):
        # return self.lineEdit.text().strip().split(",")
        return self.lineEdit.text()

