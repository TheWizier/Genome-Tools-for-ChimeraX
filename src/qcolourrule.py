from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from . import colourRule


class QColourRule(QWidget):

    remove_rule_clicked = pyqtSignal(object)
    move_up_clicked = pyqtSignal(object)
    move_down_clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.form = colourRule.Ui_Form()
        self.form.setupUi(self)
        self.form.action.currentIndexChanged['int'].connect(self.colour_active)
        self.form.removeRule.clicked.connect(self.trigger_remove_rule_clicked)
        self.form.upButton.clicked.connect(self.trigger_move_up_clicked)
        self.form.downButton.clicked.connect(self.trigger_move_down_clicked)


    def colour_active(self, index):
        if(index == 0):
            self.form.colorPicker.setEnabled(True)
        else:
            self.form.colorPicker.setEnabled(False)

    def trigger_remove_rule_clicked(self):
        self.remove_rule_clicked.emit(self)

    def trigger_move_up_clicked(self):
        self.move_up_clicked.emit(self)

    def trigger_move_down_clicked(self):
        self.move_down_clicked.emit(self)



