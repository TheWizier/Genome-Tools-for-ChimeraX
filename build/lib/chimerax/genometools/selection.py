# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\TheWizier\PycharmProjects\ChimeraxBundleTest\Genometools\src\selection.ui'
#
# Created by: Qt UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from Qt import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 178)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.chr_idField = QtWidgets.QLineEdit(Form)
        self.chr_idField.setObjectName("chr_idField")
        self.gridLayout.addWidget(self.chr_idField, 1, 0, 1, 1)
        self.fromField = QtWidgets.QLineEdit(Form)
        self.fromField.setObjectName("fromField")
        self.gridLayout.addWidget(self.fromField, 1, 1, 1, 1)
        self.toField = QtWidgets.QLineEdit(Form)
        self.toField.setObjectName("toField")
        self.gridLayout.addWidget(self.toField, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.radioInRange = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioInRange.setChecked(True)
        self.radioInRange.setObjectName("radioInRange")
        self.beadSelectionModeGroup = QtWidgets.QButtonGroup(Form)
        self.beadSelectionModeGroup.setObjectName("beadSelectionModeGroup")
        self.beadSelectionModeGroup.addButton(self.radioInRange)
        self.gridLayout_2.addWidget(self.radioInRange, 0, 0, 1, 1)
        self.radioInRangeStrict = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioInRangeStrict.setObjectName("radioInRangeStrict")
        self.beadSelectionModeGroup.addButton(self.radioInRangeStrict)
        self.gridLayout_2.addWidget(self.radioInRangeStrict, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)
        self.model_idField = QtWidgets.QLineEdit(Form)
        self.model_idField.setObjectName("model_idField")
        self.gridLayout_3.addWidget(self.model_idField, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.selectButton = QtWidgets.QPushButton(Form)
        self.selectButton.setObjectName("selectButton")
        self.verticalLayout.addWidget(self.selectButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "chrID"))
        self.label_2.setText(_translate("Form", "From"))
        self.label_3.setText(_translate("Form", "To"))
        self.groupBox_2.setTitle(_translate("Form", "Bead selection mode"))
        self.radioInRange.setToolTip(_translate("Form", "<html><head/><body><p>Selects all beads that are within or partilally within the range of the sequences</p></body></html>"))
        self.radioInRange.setText(_translate("Form", "In range"))
        self.radioInRangeStrict.setToolTip(_translate("Form", "<html><head/><body><p>Only selects beads that are completely within a sequence range</p></body></html>"))
        self.radioInRangeStrict.setText(_translate("Form", "Strictly in range"))
        self.label_4.setText(_translate("Form", "Model ID"))
        self.model_idField.setText(_translate("Form", "1"))
        self.selectButton.setText(_translate("Form", "Add to selection"))
