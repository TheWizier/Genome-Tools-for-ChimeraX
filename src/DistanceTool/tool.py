from pathlib import Path

import numpy as np
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt5.QtWidgets import QDialog, QFileDialog
from Qt import QtCore, QtWidgets
from chimerax.core.errors import UserError
from chimerax.core.tools import ToolInstance
from matplotlib import pyplot
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from . import distanceTool
from ..util import get_locale, BetterQDoubleValidator


class DistanceTool(ToolInstance):

    def __init__(self, session, tool_name):
        super().__init__(session, tool_name)
        self.display_name = "GenomeTools Distances"

        self.ql = get_locale()

        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        self._build_ui()

        self.distances = np.empty((0))
        self.last_filepath = None



    def _build_ui(self):
        from ..gui import distances
        self.df = distances.Ui_Form()
        self.df.setupUi(self.tool_window.ui_area)
        self.tool_window.manage('side')
        self.df.calculatePairwiseButton.clicked.connect(self.calculate_pairwise)
        self.df.calculateBetweenButton.clicked.connect(self.calculate_between)
        self.df.calculatePointButton.clicked.connect(self.calculate_point)

        # Setup distance metrics
        self.df.metricComboBox.addItems(["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine",
                                        "dice", "euclidean", "hamming", "jaccard", "kulsinski",
                                        "mahalanobis", "matching", "minkowski", "rogerstanimoto", "russellrao",
                                        "seuclidean", "sokalmichener", "sokalsneath", "sqeuclidean"])
        # "wminkowski", "yule", "jensenshannon"
        self.df.metricComboBox.setCurrentIndex(7)  # Euclidean is default

        # Set validators
        self.model_id_validator = QRegularExpressionValidator(QRegularExpression("[0-9.]*"))
        self.df.pairwiseModelId.setValidator(self.model_id_validator)
        self.int_only_validator = QIntValidator()
        self.double_only_validator = BetterQDoubleValidator()
        # self.double_only_validator.setLocale(QtCore.QLocale("en_US")) TODO or not?
        self.df.binCount.setValidator(self.int_only_validator)
        self.df.cutoffMin.setValidator(self.double_only_validator)
        self.df.cutoffMax.setValidator(self.double_only_validator)
        self.df.point_X.setValidator(self.double_only_validator)
        self.df.point_Y.setValidator(self.double_only_validator)
        self.df.point_Z.setValidator(self.double_only_validator)

        # Setup result dialog
        from ..gui import distanceResults
        self.result_dialog = QDialog(self.tool_window.ui_area)
        self.drd = distanceResults.Ui_Dialog()
        self.drd.setupUi(self.result_dialog)
        self.drd.textEdit.setReadOnly(True)
        self.result_dialog.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.verticalLayout_frame_1 = QtWidgets.QVBoxLayout(self.drd.frame)
        self.verticalLayout_frame_1.setObjectName("verticalLayout_frame_1")
        self.matplot_canvas = FigureCanvasQTAgg(Figure())
        self.verticalLayout_frame_1.addWidget(self.matplot_canvas)
        self.matplot_toolbar = NavigationToolbar(self.matplot_canvas, self.drd.frame)
        self.verticalLayout_frame_1.addWidget(self.matplot_toolbar)

        self.drd.saveButton.clicked.connect(self.save_array)

    def save_array(self):
        success = False
        name = ""
        if(self.last_filepath is not None):
            try:
                name, _ = QFileDialog.getSaveFileName(self.result_dialog, "Save File", self.last_filepath,
                                                      "Numpy file (*.npy)")
                success = True
            except RuntimeError:
                pass
        if(not success):
            try:
                name, _ = QFileDialog.getSaveFileName(self.result_dialog, "Save File", str(Path.home()),
                                                      "Numpy file (*.npy)")
            except RuntimeError:
                name, _ = QFileDialog.getSaveFileName(self.result_dialog, "Save File", "", "Numpy file (*.npy)")

        if name == "":
            return
        self.last_filepath = name
        if not name.endswith(".npy"):
            name += ".npy"
        file = open(name, "wb")
        np.save(file, self.distances)
        file.close()

    def _show_distances_dialog(self):
        formatted_distances = str(self.distances)
        self.drd.textEdit.setText("Array of shape " + str(self.distances.shape) + ".\n" + formatted_distances)

        self._show_histogram()

    def calculate_pairwise(self):
        metric = self.df.metricComboBox.currentText()
        self.distances = distanceTool.calculate_pairwise(self.session, self.df.pairwiseModelId.text(), metric)
        self._show_distances_dialog()

    def calculate_between(self):
        metric = self.df.metricComboBox.currentText()
        self.distances = distanceTool.calculate_between(self.session, self.df.ModelAId.text(), self.df.modelBId.text(), metric)

        self._show_distances_dialog()

    def calculate_point(self):
        metric = self.df.metricComboBox.currentText()
        points = np.array([[self.ql.toDouble(self.df.point_X.text())[0], self.ql.toDouble(self.df.point_Y.text())[0], self.ql.toDouble(self.df.point_Z.text())[0]]])
        self.distances = distanceTool.calculate_point(self.session, self.df.pointDistanceModelId.text(), points, metric)
        self._show_distances_dialog()

    def _show_histogram(self):
        bin_count, _ = self.ql.toInt(self.df.binCount.text())
        if (self.df.binCount.text() == ""):
            bin_count = 10

        if (self.df.cutoffCheckBox.isChecked()):
            if (self.df.cutoffMin.text() == "" or self.df.cutoffMax.text() == ""):
                raise UserError("Empty cutoff values")
            cutoff_range = (self.ql.toInt(self.df.cutoffMin.text())[0], self.ql.toInt(self.df.cutoffMax.text())[0])
        else:
            cutoff_range = None
        pyplot.clf()
        try:
            histogram = pyplot.hist(self.distances.flatten(), bin_count, cutoff_range)  # TODO do something with the histogram data?
        except ValueError:
            UserError("The histogram was unable to compute due to unsupported values")
        self.matplot_canvas.figure = pyplot.gcf()
        self.matplot_canvas.draw()
        self.result_dialog.show()