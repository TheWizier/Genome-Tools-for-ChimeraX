# vim: set expandtab shiftwidth=4 softtabstop=4:
from pathlib import Path
from typing import List

import numpy as np
from PyQt5 import QtWidgets
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar)

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QColor, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QDialog, QFileDialog
from matplotlib.figure import Figure

from chimerax.core.errors import UserError
from chimerax.core.tools import ToolInstance
from . import distanceTool
from .enums import BedColourMode


class GenometoolsBedModels(ToolInstance):


    # Inheriting from ToolInstance makes us known to the ChimeraX tool mangager,
    # so we can be notified and take appropriate action when sessions are closed,
    # saved, or restored, and we will be listed among running tools and so on.
    #
    # If cleaning up is needed on finish, override the 'delete' method
    # but be sure to call 'delete' from the superclass at the end.

    SESSION_ENDURING = False    # Does this instance persist when session closes
    SESSION_SAVE = True         # We do save/restore in sessions
    #help = "help:user/tools/tutorial.html"# TODO add help screen for tool
                                # Let ChimeraX know about our help page

    def __init__(self, session, tool_name):
        # 'session'   - chimerax.core.session.Session instance
        # 'tool_name' - string

        # Initialize base class.
        super().__init__(session, tool_name)

        self.score_field_values = ["0", "1000", "0", "100"]

        # Set name displayed on title bar (defaults to tool_name)
        # Must be after the superclass init, which would override it.
        self.display_name = "GenomeTools BED Models"

        # Create the main window for our tool.  The window object will have
        # a 'ui_area' where we place the widgets composing our interface.
        # The window isn't shown until we call its 'manage' method.
        #
        # Note that by default, tool windows are only hidden rather than
        # destroyed when the user clicks the window's close button.  To change
        # this behavior, specify 'close_destroys=True' in the MainToolWindow
        # constructor.
        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)

        # We will be adding an item to the tool's context menu, so override
        # the default MainToolWindow fill_context_menu method
        # self.tool_window.fill_context_menu = self.fill_context_menu

        # Our user interface is simple enough that we could probably inline
        # the code right here, but for any kind of even moderately complex
        # interface, it is probably better to put the code in a method so
        # that this __init__ method remains readable.
        self._build_ui()



    def _build_ui(self):
        # Put our widgets in the tool window
        from . import bedFileForm
        self.bf = bedFileForm.Ui_Form()
        self.bf.setupUi(self.tool_window.ui_area)

        # Set radio button group ids
        # Used to set select and colour mode
        self.bf.colourButtonGroup.setId(self.bf.radioSingleColor, 0)
        self.bf.colourButtonGroup.setId(self.bf.radioScoreColor, 1)
        self.bf.colourButtonGroup.setId(self.bf.radioColorColor, 2)

        self.bf.beadSelectionModeGroup.setId(self.bf.radioInRange, 0)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioInRangeStrict, 1)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioStart, 2)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioMiddle, 3)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioEnd, 4)

        # Hide context options
        self.bf.scoreColourWidget.setVisible(False)
        self.bf.fileColourWidget.setVisible(False)

        # Set default colours
        self.bf.colorPickerStartGradient.set_color(QColor(255, 255, 255))
        self.bf.colorPickerEndGradient.set_color(QColor(0, 0, 0))
        self.bf.conflictColorPicker.set_color(QColor(255, 0, 0))
        self.bf.conflictColorPicker_2.set_color(QColor(255, 0, 0))

        # Set validators
        self.double_only_validator = QDoubleValidator()
        self.bf.startGradient.setValidator(self.double_only_validator)
        self.bf.endGradient.setValidator(self.double_only_validator)

        self.bf.mainModelId.setValidator(QRegExpValidator(QRegExp("[0-9.]*"), self.bf.mainModelId))

        # Connect functions
        self.bf.generateModelButton.clicked.connect(self.generate_model_from_bed)

        self.bf.scoreOrPercentile.currentIndexChanged[int].connect(self.score_field_update)

        # Set filetypes for browse widget
        self.bf.browseWidget.set_file_types("BED-files (*.bed *.bed3 *.bed4 *.bed5 *.bed6 *.bed7 *.bed8 *.bed9 *.bed10 *.bed11 *.bed12);;All files (*.*)")

        # Show the window on the user-preferred side of the ChimeraX
        # main window
        self.tool_window.manage('side')

    def score_field_update(self, index):
        if (index == 0):
            self.score_field_values[2] = self.bf.startGradient.text()
            self.score_field_values[3] = self.bf.endGradient.text()
            self.bf.startGradient.setText(self.score_field_values[0])
            self.bf.endGradient.setText(self.score_field_values[1])
        else:
            self.score_field_values[0] = self.bf.startGradient.text()
            self.score_field_values[1] = self.bf.endGradient.text()
            self.bf.startGradient.setText(self.score_field_values[2])
            self.bf.endGradient.setText(self.score_field_values[3])

    def generate_model_from_bed(self):  # TODO this function should call the corresponding command!
        filepath = self.bf.browseWidget.get_file_path()
        select_mode = self.bf.beadSelectionModeGroup.checkedId()
        colour_mode = self.bf.colourButtonGroup.checkedId()
        hide_org = self.bf.hideOrg.isChecked()
        main_model_id = self.bf.mainModelId.text()
        new_model_name = self.bf.modelName.text()
        colour_1 = self.bf.colorPicker.get_color()

        if(colour_mode == BedColourMode.COLOUR):
            colour_blend = self.bf.colourBlendCheckBox.isChecked()
            colour_2 = self.bf.conflictColorPicker.get_color()
        else:
            colour_blend = self.bf.colourBlendCheckBox_2.isChecked()
            colour_2 = self.bf.conflictColorPicker_2.get_color()

        gradient_colour_1 = self.bf.colorPickerStartGradient.get_color()
        gradient_colour_2 = self.bf.colorPickerEndGradient.get_color()
        score_mode = self.bf.scoreOrPercentile.currentIndex()
        gradient_start = float(self.bf.startGradient.text())
        gradient_end = float(self.bf.endGradient.text())

        from . import cmd

        import cProfile  # TODO remove profiling code

        pr = cProfile.Profile()
        pr.enable()
        cmd.visualise_bed(self.session,
                          filepath,
                          select_mode,
                          colour_mode,
                          hide_org,
                          colour_1,
                          colour_2,
                          colour_blend,
                          main_model_id,
                          new_model_name,
                          gradient_colour_1,
                          gradient_colour_2,
                          score_mode,
                          gradient_start,
                          gradient_end)
        pr.disable()
        pr.dump_stats("bed_performance_dump.prof")


    # TODO if I want a right click menu this is how to do it
    # def fill_context_menu(self, menu, x, y):
    #     # Add any tool-specific items to the given context menu (a QMenu instance).
    #     # The menu will then be automatically filled out with generic tool-related actions
    #     # (e.g. Hide Tool, Help, Dockable Tool, etc.)
    #     #
    #     # The x,y args are the x() and y() values of QContextMenuEvent, in the rare case
    #     # where the items put in the menu depends on where in the tool interface the menu
    #     # was raised.
    #     from PyQt5.QtWidgets import QAction
    #     clear_action = QAction("Clear", menu)
    #     clear_action.triggered.connect(lambda *args: self.line_edit.clear())
    #     menu.addAction(clear_action)


class OverlapTool(ToolInstance):  # TODO maybe add help button for information on how it works???

    def __init__(self, session, tool_name):
        # 'session'   - chimerax.core.session.Session instance
        # 'tool_name' - string

        # Initialize base class.
        super().__init__(session, tool_name)

        self.display_name = "GenomeTools Bead Overlap"

        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)

        from .qcolourrule import QColourRule
        self.colour_rules: List[QColourRule] = []

        # Build UI
        from . import beadOverlap
        self.bof = beadOverlap.Ui_Form()
        self.bof.setupUi(self.tool_window.ui_area)
        self.tool_window.manage('side')
        self.bof.addRule.clicked.connect(self.add_rule)
        self.bof.scrollAreaWidgetContents.layout()
        self.bof.createModel.clicked.connect(self.create_model)

    def create_model(self):  # TODO the backend wants a prioritised list of rules and the selected only flag
        from.OverlapRule import OverlapRule
        import re
        overlap_rules = []

        for rule in self.colour_rules:
            model_ids_string = rule.form.modelIDs.text()
            model_ids_items = re.split(", |,", model_ids_string.strip())
            if(len(model_ids_items) == 1 and model_ids_items[0] == ""):
                model_ids = set()
            else:
                model_ids = set(model_ids_items)
            not_include = rule.form.action.currentIndex() == 1
            if(not_include):
                new_overlap_rule = OverlapRule(self.session, model_ids, not_include)
            else:
                colour = rule.form.colorPicker.get_color()
                new_overlap_rule = OverlapRule(self.session, model_ids, not_include, colour)
            overlap_rules.append(new_overlap_rule)

        from . import cmd
        cmd.make_overlap_model(self.session, overlap_rules, self.bof.newModelName.text())

    def add_rule(self):
        from .qcolourrule import QColourRule
        new_colour_rule = QColourRule(self.bof.scrollAreaWidgetContents)
        self.bof.scrollAreaWidgetContentsLayout.insertWidget(self.bof.scrollAreaWidgetContentsLayout.count()-1, new_colour_rule)
        new_colour_rule.remove_rule_clicked.connect(self.remove_rule)
        new_colour_rule.move_up_clicked.connect(self.move_rule_up)
        new_colour_rule.move_down_clicked.connect(self.move_rule_down)
        self.colour_rules.append(new_colour_rule)
        new_colour_rule.show()

    def remove_rule(self, rule):
        self.bof.scrollAreaWidgetContentsLayout.removeWidget(rule)
        rule.close()
        self.colour_rules.remove(rule)

    def move_rule_up(self, rule):
        index = self.bof.scrollAreaWidgetContentsLayout.indexOf(rule)
        if(index == 0):
            return  # Already at the top
        self.bof.scrollAreaWidgetContentsLayout.removeWidget(rule)
        self.bof.scrollAreaWidgetContentsLayout.insertWidget(index-1, rule)
        self.colour_rules[index-1], self.colour_rules[index] = self.colour_rules[index], self.colour_rules[index-1]

    def move_rule_down(self, rule):
        index = self.bof.scrollAreaWidgetContentsLayout.indexOf(rule)
        if (index == len(self.colour_rules)-1):
            return  # Already at the bottom
        self.bof.scrollAreaWidgetContentsLayout.removeWidget(rule)
        self.bof.scrollAreaWidgetContentsLayout.insertWidget(index + 1, rule)
        self.colour_rules[index + 1], self.colour_rules[index] = self.colour_rules[index], self.colour_rules[index + 1]


class DistanceTool(ToolInstance):

    def __init__(self, session, tool_name):
        super().__init__(session, tool_name)
        self.display_name = "GenomeTools Distances"

        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        self._build_ui()

        self.distances = np.empty((0))
        self.last_filepath = None

    def _build_ui(self):
        from . import distances
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
        self.model_id_validator = QRegExpValidator(QRegExp("[0-9.]*"))
        self.df.pairwiseModelId.setValidator(self.model_id_validator)
        self.int_only_validator = QIntValidator()
        self.double_only_validator = QDoubleValidator()
        self.df.binCount.setValidator(self.int_only_validator)
        self.df.cutoffMin.setValidator(self.double_only_validator)
        self.df.cutoffMax.setValidator(self.double_only_validator)
        self.df.point_X.setValidator(self.double_only_validator)
        self.df.point_Y.setValidator(self.double_only_validator)
        self.df.point_Z.setValidator(self.double_only_validator)

        # Setup result dialog
        from . import distanceResults
        self.result_dialog = QDialog(self.tool_window.ui_area)
        self.drd = distanceResults.Ui_Dialog()
        self.drd.setupUi(self.result_dialog)
        self.drd.textEdit.setReadOnly(True)

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
        # formatted_distances = ", ".join([str(dist) for dist in distances])  # TODO this crashes chimerax OoM?
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
        points = np.array([[float(self.df.point_X.text()), float(self.df.point_Y.text()), float(self.df.point_Z.text())]])
        self.distances = distanceTool.calculate_point(self.session, self.df.pointDistanceModelId.text(), points, metric)
        self._show_distances_dialog()

    def _show_histogram(self):
        bin_count = int(self.df.binCount.text())
        if (self.df.binCount.text() == ""):
            bin_count = 10

        if (self.df.cutoffCheckBox.isChecked()):
            if (self.df.cutoffMin.text() == "" or self.df.cutoffMax.text() == ""):
                raise UserError("Empty cutoff values")
            cutoff_range = (int(self.df.cutoffMin.text()), int(self.df.cutoffMax.text()))
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


class SelectionTool(ToolInstance):

    def __init__(self, session, tool_name):
        super().__init__(session, tool_name)
        self.display_name = "GenomeTools Selector"

        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        self._build_ui()

    def _build_ui(self):
        from . import selection
        self.sf = selection.Ui_Form()
        self.sf.setupUi(self.tool_window.ui_area)
        self.tool_window.manage('side')

        self.sf.beadSelectionModeGroup.setId(self.sf.radioInRange, 0)
        self.sf.beadSelectionModeGroup.setId(self.sf.radioInRangeStrict, 1)

        self.int_only_validator = QIntValidator()
        self.sf.fromField.setValidator(self.int_only_validator)
        self.sf.toField.setValidator(self.int_only_validator)

        self.sf.selectButton.clicked.connect(self.select)

    def select(self):
        chr_id = self.sf.chr_idField.text()
        from_val = int(self.sf.fromField.text())
        to_val = int(self.sf.toField.text())
        model_id = self.sf.model_idField.text()
        select_mode = self.sf.beadSelectionModeGroup.checkedId()

        from . import cmd
        cmd.select_beads(self.session, chr_id, from_val, to_val, model_id, select_mode)
