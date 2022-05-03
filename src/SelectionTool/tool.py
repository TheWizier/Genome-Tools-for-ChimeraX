from Qt.QtGui import QIntValidator
from Qt.QtWidgets import QStyle
from chimerax.core.tools import ToolInstance

from ..util import get_locale, show_info


class SelectionTool(ToolInstance):

    help = "help:user/tools/Genome_Selection.html"

    def __init__(self, session, tool_name):
        super().__init__(session, tool_name)
        self.display_name = "GenomeTools Genome Selection"

        self.ql = get_locale()

        from chimerax.ui import MainToolWindow
        self.tool_window = MainToolWindow(self)
        self._build_ui(session)

    def _build_ui(self, session):
        from ..gui import selection
        self.sf = selection.Ui_Form()
        self.sf.setupUi(self.tool_window.ui_area)
        self.tool_window.manage('side')

        self.sf.beadSelectionModeGroup.setId(self.sf.radioInRange, 0)
        self.sf.beadSelectionModeGroup.setId(self.sf.radioInRangeStrict, 1)

        self.int_only_validator = QIntValidator()  # TODO accept MB and M and other SI prefixes
        self.sf.fromField.setValidator(self.int_only_validator)
        self.sf.toField.setValidator(self.int_only_validator)

        self.sf.selectButton.clicked.connect(self.select)

        # Set up help button
        self.sf.infoButton.setIcon(self.sf.infoButton.style().standardIcon(getattr(QStyle, "SP_MessageBoxQuestion")))
        self.sf.infoButton.clicked.connect(lambda: show_info(session, self.help))

    def select(self):
        chr_id = self.sf.chr_idField.text()
        from_val, _ = self.ql.toInt(self.sf.fromField.text())
        to_val, _ = self.ql.toInt(self.sf.toField.text())
        model_id = self.sf.model_idField.text()
        select_mode = self.sf.beadSelectionModeGroup.checkedId()

        from .cmd import select_beads
        select_beads(self.session, chr_id, from_val, to_val, model_id, select_mode)
