from chimerax.core.commands import CmdDesc, StringArg, IntArg

from Genometools.src.BedModelsTool.cmd import bead_select
from Genometools.src.enums import SelectMode
from Genometools.src.util import get_model_by_id, prepare_model


def select_beads(session, chr_id, from_val, to_val, model_id, select_mode=SelectMode.RANGE):
    model = get_model_by_id(session, model_id)
    # Prepare model (if not already prepared)
    if (not hasattr(model, "bead_dict")):
        prepare_model(model)

    selection = []
    for key in model.bead_dict:
        if(key.startswith(chr_id)):
            selection.extend(bead_select(from_val, to_val, model.bead_dict[key], select_mode))

    for bead in selection:
        bead.selected = True


select_beads_desc = CmdDesc(required=[("chr_id", StringArg),
                                      ("from_val", IntArg),
                                      ("to_val", IntArg),
                                      ("model_id", StringArg)],
                            optional=[("select_mode", IntArg)])