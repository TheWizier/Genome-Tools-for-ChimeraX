# vim: set expandtab shiftwidth=4 softtabstop=4:

from chimerax.atomic import selected_atoms
from chimerax.core.commands import CmdDesc, StringArg, IntArg
from chimerax.core.errors import UserError
from chimerax.markers import MarkerSet

# import line_profiler

from .util import copy_bead, copy_links


# prof = line_profiler.LineProfiler()


def select_chromosome(session, chr_id):  # Superseded by make_submodels but no reason to remove it
    from chimerax.core.commands import all_objects
    atoms = all_objects(session).atoms
    count = 0
    for m in atoms:
        ea = getattr(m, 'marker_extra_attributes', {})
        if(ea["chrID"] == chr_id):
            m.selected = True
            count += 1
    session.logger.info("Selected " + str(count) + " markers")


select_chromosome_desc = CmdDesc(required=[("chr_id", StringArg)])


def dump_bead_data(session):
    for a in selected_atoms(session):
        session.logger.info(str(a) + ": xyz:" + str(a.coord) + ", " + str(a.marker_extra_attributes))


dump_bead_data_desc = CmdDesc()


def highlight(session, transparency: int = 30):
    if(not (0 <= transparency <= 255)):
        raise UserError("Transparency value must be in the range 0-255")
    from chimerax.core.commands import all_objects
    atoms = all_objects(session).atoms
    bonds = all_objects(session).bonds

    tmp = bonds.colors
    tmp[:, 3] = transparency
    tmp[bonds.selected, 3] = 255
    bonds.colors = tmp

    # This doesnt work for some reason:
    # atoms.colors[:, 3] = 30  # Make all atoms transparent
    # atoms.colors[atoms.selected, 3] = 255  # Make selection opaque

    tmp = atoms.colors
    tmp[:, 3] = transparency  # Make all atoms transparent
    #tmp[atoms.selected] = np.array([255, 255, 255, 255], dtype=np.ubyte)
    tmp[atoms.selected, 3] = 255  # Make selection opaque
    atoms.colors = tmp


highlight_desc = CmdDesc(optional=[("transparency", IntArg)])


def make_submodels_helper(session, main_model):
    # To split the model into submodels we actually just make an entirely new model and delete the old one
    # so all the atoms must be "copied" to their new models.
    submodels = {}
    correspondence_dict = {}
    from chimerax.core.models import Model
    parent = Model(main_model.name, session)
    parent.id = main_model.id
    try:
        for m in main_model.atoms:
            ea = getattr(m, 'marker_extra_attributes', {})
            if ("chrID" not in ea):
                chr_id = "NO_ID"
            else:
                chr_id = ea["chrID"]

            if (chr_id in submodels):
                new_bead = copy_bead(m, submodels[chr_id])
                correspondence_dict[m] = new_bead
            else:
                new_sub = MarkerSet(session, chr_id)
                submodels[chr_id] = new_sub
                new_bead = copy_bead(m, new_sub)
                correspondence_dict[m] = new_bead
                parent.add([new_sub])

        # Copy links:
        copy_links([main_model], correspondence_dict)

    except AttributeError:
        # Either atoms is missing or extra attributes is missing
        print("Could not split model:", main_model.name)
    else:
        if(len(submodels) <= 1):
            print("Could not split model:", main_model.name)
            return  # Nothing to split
        session.models.close([main_model])
        session.models.add([parent])
        print("Split model", main_model.name, "into", len(submodels), "submodels.")


def make_submodels(session, main_model_id=None):
    if(main_model_id is None):
        # Do all models
        for model in session.models.list():
            make_submodels_helper(session, model)
    else:
        # Do specified model
        from . import util
        main_model = util.get_model_by_id(session, main_model_id)

        if (main_model is None):
            raise UserError("No model with id: ", main_model_id)

        make_submodels_helper(session, main_model)


make_submodels_desc = CmdDesc(optional=[("main_model_id", StringArg)])


def make_model_from_selection(session, new_model_name):
    new_model = MarkerSet(session, new_model_name)
    seen_hash_table = {}
    correspondence_dict = {}
    for bead in selected_atoms(session):
        if(seen_hash_table.get(bead.residue.number, False)):
            continue
        seen_hash_table[bead.residue.number] = True

        new_bead = copy_bead(bead, new_model)
        correspondence_dict[bead] = new_bead

    # TODO The selection is an ordered collection, so this SHOULD work.
    copy_links(session.models, correspondence_dict)
    session.models.add([new_model])


make_model_from_selection_desc = CmdDesc(required=[("new_model_name", StringArg)])


# TODO remove test using ## preferably
# def test(session):
#     print("RUNNING TEST")
#     import time
#     start = time.time_ns()
#     for i in range(4000):
#         for m in all_atoms_in(session.models.list()[0]):
#             m.selected = True
#     print(time.time_ns()-start)
#
#
# test_desc = CmdDesc()
