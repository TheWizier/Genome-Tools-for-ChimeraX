from typing import Set
from enum import IntEnum
from chimerax.core.colors import Color

from ..util import model_id_from_model_name


class OverlapColourMode(IntEnum):
    COLOUR, NOT_INCLUDE, RETAIN_COLOUR = range(3)


class OverlapRule():

    def __init__(self, session, model_ids, colour_mode: OverlapColourMode, colour: Color = None):
        self.model_ids: Set[str] = set()
        for model_id in model_ids:
            if (model_id.startswith("\"") and model_id.endswith("\"")):
                self.model_ids.add(model_id_from_model_name(session, model_id.strip('"')))
            else:
                self.model_ids.add(model_id)

        self.colour_mode: OverlapColourMode = colour_mode
        self.colour: Color = colour
