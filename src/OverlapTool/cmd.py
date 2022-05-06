from typing import List

from chimerax.core.errors import UserError
from chimerax.markers import MarkerSet

from .OverlapRule import OverlapRule, OverlapColourMode
from ..util import get_model_by_id, all_atoms_in


def make_overlap_model(session, overlap_rules: List[OverlapRule], model_name: str):
    # Make a list of all involved beads and what models they are in.
    all_involved_model_ids = set()
    for rule in overlap_rules:
        if (len(rule.model_ids) == 0):
            for model in session.models.list():
                all_involved_model_ids.add(model.id_string)
            break
        all_involved_model_ids.update(rule.model_ids)
    all_involved_beads = {}
    for model_id in all_involved_model_ids:
        cur_model = get_model_by_id(session, model_id)
        if cur_model is None:
            raise UserError("Model id not found:" + model_id)
        for bead in all_atoms_in(cur_model):
            if(bead.residue.number not in all_involved_beads):
                all_involved_beads[bead.residue.number] = (set(), bead)
            all_involved_beads[bead.residue.number][0].add(model_id)

    # Go through list and make a bead for the first rule that applies to that list entry
    new_model = MarkerSet(session, name=model_name)
    for bead_id in all_involved_beads:
        for rule in overlap_rules:
            if(rule.model_ids.issubset(all_involved_beads[bead_id][0])):
                # Choose colour:
                if(rule.colour_mode == OverlapColourMode.NOT_INCLUDE):
                    break
                elif(rule.colour_mode == OverlapColourMode.RETAIN_COLOUR):
                    colour = all_involved_beads[bead_id][1].color
                elif(rule.colour_mode == OverlapColourMode.COLOUR):
                    colour = rule.colour.uint8x4()
                else:
                    print("invalid colour mode")  # TODO Exception
                    break

                new_model.create_marker(all_involved_beads[bead_id][1].scene_coord,
                                        colour,
                                        all_involved_beads[bead_id][1].radius,
                                        all_involved_beads[bead_id][1].residue.number)
                break
    session.models.add([new_model])
