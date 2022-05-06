from typing import Set
from enum import IntEnum
from chimerax.core.colors import Color

from ..util import model_id_from_model_name


class OverlapColourMode(IntEnum):
    COLOUR, NOT_INCLUDE, RETAIN_COLOUR = range(3)


class OverlapRule():

    def __init__(self, session, model_ids, colour_mode: OverlapColourMode, colour: Color = None):
        self.model_ids: Set[str] = set()
        self.retainer: str = ""

        first = True
        for model_id in model_ids:
            if (model_id.startswith("\"") and model_id.endswith("\"")):
                m_id = model_id_from_model_name(session, model_id.strip('"'))
                self.model_ids.add(m_id)
                if(first):
                    self.retainer = m_id
                    first = False
            else:
                self.model_ids.add(model_id)
                if (first):
                    self.retainer = model_id
                    first = False

        self.colour_mode: OverlapColourMode = colour_mode
        self.colour: Color = colour
