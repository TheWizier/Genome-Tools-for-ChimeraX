# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\TheWizier\PycharmProjects\ChimeraxBundleTest\genometools\src\colourRule.ui'
#
# Created by: Qt UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from Qt import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(452, 25)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(-1, 1, -1, 1)
        self.gridLayout.setObjectName("gridLayout")
        self.downButton = QtWidgets.QToolButton(Form)
        self.downButton.setText("")
        self.downButton.setArrowType(QtCore.Qt.DownArrow)
        self.downButton.setObjectName("downButton")
        self.gridLayout.addWidget(self.downButton, 0, 5, 1, 1)
        self.action = QtWidgets.QComboBox(Form)
        self.action.setObjectName("action")
        self.action.addItem("")
        self.action.addItem("")
        self.gridLayout.addWidget(self.action, 0, 1, 1, 1)
        self.modelIDs = QtWidgets.QLineEdit(Form)
        self.modelIDs.setObjectName("modelIDs")
        self.gridLayout.addWidget(self.modelIDs, 0, 0, 1, 1)
        self.removeRule = QtWidgets.QToolButton(Form)
        self.removeRule.setArrowType(QtCore.Qt.NoArrow)
        self.removeRule.setObjectName("removeRule")
        self.gridLayout.addWidget(self.removeRule, 0, 6, 1, 1)
        self.upButton = QtWidgets.QToolButton(Form)
        self.upButton.setText("")
        self.upButton.setArrowType(QtCore.Qt.UpArrow)
        self.upButton.setObjectName("upButton")
        self.gridLayout.addWidget(self.upButton, 0, 4, 1, 1)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 0, 3, 1, 1)
        self.colorPicker = QColourPicker(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorPicker.sizePolicy().hasHeightForWidth())
        self.colorPicker.setSizePolicy(sizePolicy)
        self.colorPicker.setMinimumSize(QtCore.QSize(23, 23))
        self.colorPicker.setMaximumSize(QtCore.QSize(23, 23))
        self.colorPicker.setBaseSize(QtCore.QSize(23, 23))
        self.colorPicker.setToolTip("")
        self.colorPicker.setStyleSheet("font: 72pt \"Arial\";")
        self.colorPicker.setObjectName("colorPicker")
        self.gridLayout.addWidget(self.colorPicker, 0, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.action.setItemText(0, _translate("Form", "Colour"))
        self.action.setItemText(1, _translate("Form", "Don\'t include"))
        self.modelIDs.setToolTip(_translate("Form", "Comma separated model IDs or names in double quotes. Empty field will select all models."))
        self.removeRule.setToolTip(_translate("Form", "Remove rule"))
        self.removeRule.setText(_translate("Form", "-"))
        self.colorPicker.setText(_translate("Form", "▮"))
from .qcolourpicker import QColourPicker