from typing import List

from PyQt5.QtWidgets import QStyle
from chimerax.core.tools import ToolInstance

from .cmd import make_overlap_model
from ..util import show_info


class OverlapTool(ToolInstance):  # TODO maybe add help button for information on how it works???

    help = "help:user/tools/Bead_Overlap.html"

    def __init__(self, session, tool_name):
        # 'session'   - chimerax.core.session.Session instance
        # 'tool_name' - string

        # Initialize base class.
        super().__init__(session, tool_name)

        self.display_name = "GenomeTools Bead Overlap"

        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)

        from ..gui.qcolourrule import QColourRule
        self.colour_rules: List[QColourRule] = []

        # Build UI
        from ..gui import beadOverlap
        self.bof = beadOverlap.Ui_Form()
        self.bof.setupUi(self.tool_window.ui_area)
        self.tool_window.manage('side')
        self.bof.addRule.clicked.connect(self.add_rule)
        self.bof.scrollAreaWidgetContents.layout()
        self.bof.createModel.clicked.connect(self.create_model)

        # Set up info dialog
        # TODO Remove unused files related to this change
        #from ..gui import overlapToolInfo
        #self.info_dialog = QDialog(self.tool_window.ui_area)
        #self.oti = overlapToolInfo.Ui_Dialog()
        #self.oti.setupUi(self.info_dialog)
        self.bof.infoButton.setIcon(self.bof.infoButton.style().standardIcon(getattr(QStyle, "SP_MessageBoxQuestion")))
        self.bof.infoButton.clicked.connect(lambda: show_info(session, self.help))
        #self.info_dialog.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

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

            colour_mode = rule.form.action.currentIndex()
            colour = rule.form.colorPicker.get_color()
            new_overlap_rule = OverlapRule(self.session, model_ids, colour_mode, colour)
            overlap_rules.append(new_overlap_rule)

        make_overlap_model(self.session, overlap_rules, self.bof.newModelName.text())

    def add_rule(self):
        from ..gui.qcolourrule import QColourRule
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