# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\TheWizier\PycharmProjects\ChimeraxBundleTest\genometools\src\beadOverlap.ui'
#
# Created by: Qt UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from Qt import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(394, 517)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.infoButton = QtWidgets.QToolButton(Form)
        self.infoButton.setObjectName("infoButton")
        self.horizontalLayout.addWidget(self.infoButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 354, 352))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContentsLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContentsLayout.setObjectName("scrollAreaWidgetContentsLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.scrollAreaWidgetContentsLayout.addItem(spacerItem1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.addRule = QtWidgets.QToolButton(self.groupBox)
        self.addRule.setStyleSheet("")
        self.addRule.setObjectName("addRule")
        self.verticalLayout_2.addWidget(self.addRule)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.newModelName = QtWidgets.QLineEdit(Form)
        self.newModelName.setObjectName("newModelName")
        self.horizontalLayout_2.addWidget(self.newModelName)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.createModel = QtWidgets.QPushButton(Form)
        self.createModel.setObjectName("createModel")
        self.verticalLayout.addWidget(self.createModel)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Selection Rules"))
        self.addRule.setToolTip(_translate("Form", "Add rule"))
        self.addRule.setText(_translate("Form", "+"))
        self.label_4.setText(_translate("Form", "New model name"))
        self.newModelName.setText(_translate("Form", "overlap_model"))
        self.createModel.setText(_translate("Form", "Create Model"))