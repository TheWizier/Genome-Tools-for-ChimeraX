from typing import Set

from chimerax.core.colors import Color


class OverlapRule():

    def __init__(self, session, model_ids, not_include: bool, colour: Color = None):
        self.model_ids: Set[str] = set()
        for model_id in model_ids:
            if (model_id.startswith("\"") and model_id.endswith("\"")):
                self.model_ids.add(self.model_id_from_model_name(session, model_id.strip('"')))
            else:
                self.model_ids.add(model_id)

        self.not_include: bool = not_include
        self.colour: Color = colour

    def model_id_from_model_name(self, session, model_name):
        for model in session.models.list():
            if (model.name == model_name):
                return model.id_string
