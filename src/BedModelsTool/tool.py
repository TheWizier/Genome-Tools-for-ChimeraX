from os import path

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QColor, QRegularExpressionValidator
from PyQt5.QtWidgets import QStyle
from chimerax.core.tools import ToolInstance

from .cmd import visualise_bed
from ..enums import BedColourMode
from ..util import get_locale, BetterQDoubleValidator, show_info


class BedModelsTool(ToolInstance):
    # Inheriting from ToolInstance makes us known to the ChimeraX tool mangager,
    # so we can be notified and take appropriate action when sessions are closed,
    # saved, or restored, and we will be listed among running tools and so on.
    #
    # If cleaning up is needed on finish, override the 'delete' method
    # but be sure to call 'delete' from the superclass at the end.

    SESSION_ENDURING = False  # Does this instance persist when session closes
    SESSION_SAVE = True  # We do save/restore in sessions

    help = "help:user/tools/Bed_Models.html"
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

        self.ql = get_locale()

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
        self._build_ui(session)

    def _build_ui(self, session):
        # Put our widgets in the tool window
        from ..gui import bedFileForm
        self.bf = bedFileForm.Ui_Form()
        self.bf.setupUi(self.tool_window.ui_area)

        # Set up help button
        self.bf.infoButton.setIcon(self.bf.infoButton.style().standardIcon(getattr(QStyle, "SP_MessageBoxQuestion")))
        self.bf.infoButton.clicked.connect(lambda: show_info(session, self.help))

        # Set radio button group ids
        # Used to set select and colour mode
        self.bf.colourButtonGroup.setId(self.bf.radioSingleColor, 0)
        self.bf.colourButtonGroup.setId(self.bf.radioScoreColor, 1)
        self.bf.colourButtonGroup.setId(self.bf.radioColorColor, 2)
        self.bf.colourButtonGroup.setId(self.bf.radioRetainColor, 3)

        self.bf.beadSelectionModeGroup.setId(self.bf.radioInRange, 0)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioInRangeStrict, 1)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioStart, 2)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioMiddle, 3)
        self.bf.beadSelectionModeGroup.setId(self.bf.radioEnd, 4)

        # Hide context options
        self.bf.scoreColourWidget.setVisible(False)
        self.bf.fileColourWidget.setVisible(False)

        # Disable options disabled by default
        self.bf.cutoffOptions.setEnabled(False)

        # Set default colours
        self.bf.colorPickerStartGradient.set_color(QColor(255, 255, 255))
        self.bf.colorPickerEndGradient.set_color(QColor(0, 0, 0))
        self.bf.conflictColorPicker.set_color(QColor(255, 0, 0))
        self.bf.conflictColorPicker_2.set_color(QColor(255, 0, 0))

        # Set validators
        self.double_only_validator = BetterQDoubleValidator()
        # self.double_only_validator.setLocale(QtCore.QLocale("en_US"))  # TODO or not?
        self.bf.startGradient.setValidator(self.double_only_validator)
        self.bf.endGradient.setValidator(self.double_only_validator)

        self.bf.cutoffFrom.setValidator(self.double_only_validator)
        self.bf.cutoffTo.setValidator(self.double_only_validator)

        self.bf.mainModelId.setValidator(
            QRegularExpressionValidator(QRegularExpression("[0-9.]*"), self.bf.mainModelId))

        # Connect functions
        self.bf.generateModelButton.clicked.connect(self.generate_model_from_bed)

        self.bf.scoreOrPercentile.currentIndexChanged[int].connect(self.score_field_update)

        # Set filetypes for browse widget
        self.bf.browseWidget.set_file_types(
            "BED-files (*.bed *.bed3 *.bed4 *.bed5 *.bed6 *.bed7 *.bed8 *.bed9 *.bed10 *.bed11 *.bed12);;All files (*.*)")

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
        if (new_model_name == ""):  # DEFAULT NAME = FILENAME
            new_model_name = path.splitext(path.basename(filepath))[0]
        colour_1 = self.bf.colorPicker.get_color()

        if (colour_mode == BedColourMode.COLOUR):
            colour_blend = self.bf.colourBlendCheckBox.isChecked()
            colour_2 = self.bf.conflictColorPicker.get_color()
        else:
            colour_blend = self.bf.colourBlendCheckBox_2.isChecked()
            colour_2 = self.bf.conflictColorPicker_2.get_color()

        gradient_colour_1 = self.bf.colorPickerStartGradient.get_color()
        gradient_colour_2 = self.bf.colorPickerEndGradient.get_color()
        score_mode = self.bf.scoreOrPercentile.currentIndex()
        gradient_start, _ = self.ql.toDouble(self.bf.startGradient.text())
        gradient_end, _ = self.ql.toDouble(self.bf.endGradient.text())

        enable_cutoff = self.bf.useCutoff.isChecked()
        cutoff_mode = self.bf.scoreOrPercentileCutoff.currentIndex()
        cutoff_start, _ = self.ql.toDouble(self.bf.cutoffFrom.text())
        cutoff_end, _ = self.ql.toDouble(self.bf.cutoffTo.text())

        from .. import cmd

        #import cProfile  # TODO remove profiling code

        #pr = cProfile.Profile()
        #pr.enable()
        visualise_bed(self.session,
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
                      gradient_end,
                      enable_cutoff,
                      cutoff_mode,
                      cutoff_start,
                      cutoff_end)
        #pr.disable()
        #pr.dump_stats("bed_performance_dump.prof")

    # TODO if I want a right click menu this is how to do it
    # def fill_context_menu(self, menu, x, y):
    #     # Add any tool-specific items to the given context menu (a QMenu instance).
    #     # The menu will then be automatically filled out with generic tool-related actions
    #     # (e.g. Hide Tool, Help, Dockable Tool, etc.)
    #     #
    #     # The x,y args are the x() and y() values of QContextMenuEvent, in the rare case
    #     # where the items put in the menu depends on where in the tool interface the menu
    #     # was raised.
    #     from Qt.QtWidgets import QAction
    #     clear_action = QAction("Clear", menu)
    #     clear_action.triggered.connect(lambda *args: self.line_edit.clear())
    #     menu.addAction(clear_action)
