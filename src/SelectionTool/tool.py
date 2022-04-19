from PyQt5.QtGui import QIntValidator
from chimerax.core.tools import ToolInstance

from ..util import get_locale


class SelectionTool(ToolInstance):

    def __init__(self, session, tool_name):
        super().__init__(session, tool_name)
        self.display_name = "GenomeTools Selector"

        self.ql = get_locale()

        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        self._build_ui()

    def _build_ui(self):
        from ..gui import selection
        self.sf = selection.Ui_Form()
        self.sf.setupUi(self.tool_window.ui_area)
        self.tool_window.manage('side')

        self.sf.beadSelectionModeGroup.setId(self.sf.radioInRange, 0)
        self.sf.beadSelectionModeGroup.setId(self.sf.radioInRangeStrict, 1)

        self.int_only_validator = QIntValidator()  # TODO accept MB andM and other SI prefixes
        self.sf.fromField.setValidator(self.int_only_validator)
        self.sf.toField.setValidator(self.int_only_validator)

        self.sf.selectButton.clicked.connect(self.select)

    def select(self):
        chr_id = self.sf.chr_idField.text()
        from_val, _ = self.ql.toInt(self.sf.fromField.text())
        to_val, _ = self.ql.toInt(self.sf.toField.text())
        model_id = self.sf.model_idField.text()
        select_mode = self.sf.beadSelectionModeGroup.checkedId()

        from .. import cmd
        cmd.select_beads(self.session, chr_id, from_val, to_val, model_id, select_mode)