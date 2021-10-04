from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog, QPushButton

from chimerax.core.colors import Color


class QColourPicker(QPushButton):

    def __init__(self, parent=None, default_color=QColor(150, 150, 150)):
        super().__init__(parent)

        self.clicked.connect(self.select_color)
        self.color = default_color
        self.update_color()

    def update_color(self):
        self.setStyleSheet("font: 20pt \"Wingdings\";\ncolor: " + self.color.name())
        self.style().unpolish(self)
        self.style().polish(self)

    def select_color(self):
        color = QColorDialog.getColor(self.color, self.parentWidget())
        if(not QColor.isValid(color)):
            return
        if (color != self.color):
            self.set_color(color)

    def set_color(self, color):
        self.color = color
        self.update_color()

    def get_color(self):
        return Color([self.color.red() / 255, self.color.green() / 255, self.color.blue() / 255, 1])
