# vim: set expandtab shiftwidth=4 softtabstop=4:
from typing import List, Dict

from chimerax.atomic import selected_atoms
from chimerax.core.colors import Color
from chimerax.core.commands import CmdDesc, OpenFileNameArg, StringArg, IntArg, BoolArg, ColorArg
from chimerax.core.errors import UserError
from chimerax.markers import MarkerSet, create_link
from .OverlapRule import OverlapRule
from .enums import BedColourMode, BedSelectMode

# import line_profiler

from .util import get_model_by_id, all_atoms_in

# prof = line_profiler.LineProfiler()

import re

import numpy as np

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


def inspect_beads(session):
    from chimerax.core.commands import all_objects
    atoms = all_objects(session).atoms
    for a in atoms[atoms.selected]:
        session.logger.info(str(a) + ": xyz:" + str(a.coord) + ", " + str(a.marker_extra_attributes))


inspect_beads_desc = CmdDesc()


def bead_select_2(from_val, to_val, bead_list, select_mode):
    if(select_mode == BedSelectMode.RANGE):
        start_index = None
        for bead_index in range(len(bead_list)):
            if(from_val < bead_list[bead_index].bead_end):
                start_index = bead_index
                break
        if start_index is None:
            return []
        end_index = None
        for bead_index in range(start_index, len(bead_list)):
            if(to_val <= bead_list[bead_index].bead_end):
                end_index = bead_index
                break
        if end_index is None:
            end_index = len(bead_list)-1

        return bead_list[start_index:(end_index + 1)]

    if(select_mode == BedSelectMode.RANGE_STRICT):
        start_index = None
        for bead_index in range(len(bead_list)):
            if (from_val < bead_list[bead_index].bead_start+1):
                start_index = bead_index
                break
        if start_index is None:
            return []
        end_index = None
        for bead_index in range(start_index, len(bead_list)):
            if (to_val < bead_list[bead_index].bead_end):
                end_index = bead_index-1
                break
        if end_index is None:
            end_index = len(bead_list) - 1
        return bead_list[start_index:(end_index + 1)]

    if(select_mode == BedSelectMode.START):
        for bead in bead_list:
            if(bead.bead_start < from_val < bead.bead_end):
                return [bead]

    if (select_mode == BedSelectMode.END):
        for bead in bead_list:
            if(bead.bead_start < to_val < bead.bead_end):
                return [bead]

    if (select_mode == BedSelectMode.MIDDLE):
        for bead in bead_list:
            if(bead.bead_start < (from_val + (to_val - from_val) / 2) < bead.bead_end):
                return [bead]
    return []


def get_colour_between(colour_1, colour_2, percent):
    """Get colour between two colours"""
    return [x*(1-percent)+y*percent for x, y in zip(colour_1, colour_2)]


def get_score_based_colour(score_mode,
                           items,
                           start_percentile,
                           end_percentile,
                           gradient_start,
                           gradient_end,
                           gradient_colour_1,
                           gradient_colour_2):

    if (score_mode == 1):  # Use Percentile
        colour_percent = max(0, min(1, (float(items[4]) - start_percentile) / (
                end_percentile - start_percentile)))  # TODO division by 0 possible
    else:  # Use Score
        colour_percent = max(0, min(1, (float(items[4]) - gradient_start) / (
                gradient_end - gradient_start)))
    return get_colour_between(gradient_colour_1.uint8x4(), gradient_colour_2.uint8x4(), colour_percent)


# @prof
def make_bed_model(session,  # TODO session not used
                   new_model,
                   items,
                   select_mode,
                   colour_mode,
                   colour,
                   conflict_colour,
                   hide_org,
                   marker_seen,
                   colour_blend,
                   marker_set,
                   gradient_colour_1,
                   gradient_colour_2,
                   score_mode,
                   gradient_start,
                   gradient_end,
                   start_percentile,
                   end_percentile,
                   correspondence_dict
                   ):

    # Find all markers in the range from the BED file line

    # Find the matching beads

    selection = []  # This selection is continuous and in order
    for key in marker_set.bead_dict:
        if(key.startswith(items[0])):
            selection.extend(bead_select_2(int(items[1]), int(items[2]), marker_set.bead_dict[key], select_mode))
    for m in selection:
        if(m in marker_seen):
            if(colour_mode == BedColourMode.SINGLE):
                continue

            bead = marker_seen[m][0]
            if(colour_blend):
                # Apply blend colour

                # Get blend factor
                blend_factor = marker_seen[m][1]

                if(colour_mode == BedColourMode.SCORE):
                    rgba = get_score_based_colour(score_mode,
                                                  items,
                                                  start_percentile,
                                                  end_percentile,
                                                  gradient_start,
                                                  gradient_end,
                                                  gradient_colour_1,
                                                  gradient_colour_2)

                else:
                    r, g, b = items[8].split(",")
                    rgba = np.array([int(r), int(g), int(b), 255], dtype=np.ubyte)

                bead.color = get_colour_between(bead.color, rgba, 1/(blend_factor+1))
                # Update blend factor:
                marker_seen[m][1] += 1

            else:
                # Apply conflict colour
                bead.color = conflict_colour.uint8x4()

        # Hide beads on main model
        if(hide_org):
            m.display = False  # Use display instead of hide attribute because that is what other tools use

        # Decide bead colour
        if (colour_mode == BedColourMode.SINGLE):
            rgba = colour.uint8x4()

        elif (colour_mode == BedColourMode.SCORE):
            rgba = get_score_based_colour(score_mode,
                       items,
                       start_percentile,
                       end_percentile,
                       gradient_start,
                       gradient_end,
                       gradient_colour_1,
                       gradient_colour_2)

        elif (colour_mode == BedColourMode.COLOUR):
            r, g, b = items[8].split(",")
            rgba = np.array([int(r), int(g), int(b), 255], dtype=np.ubyte)

        else:
            print("Invalid colour mode")
            return  # TODO exception?

        # Make new bead
        new_marker = new_model.create_marker(m.scene_coord, rgba, m.radius, m.residue.number)
        # Add marker as seen
        marker_seen[m] = [new_marker, 1]
        # Add to correspondence dict
        correspondence_dict[m] = new_marker

        



def numbered_naming(existing_name, new_name):
    numbered_ending = re.compile("_([0-9]*)$")
    if (existing_name == new_name):
        match = re.search(numbered_ending, new_name)
        if (match):
            suffix = match.group(1)
            new_name = new_name[:-len(suffix)]
            new_name += str(int(suffix) + 1)
        else:
            new_name += "_1"
    return new_name


def prepare_model(marker_set):
    bd = marker_set.bead_dict = {}  # TODO Doesnt need to be dict? (because loop through keys anyways)
    #cpil= marker_set.chr_pos_index_list = []

    for m in all_atoms_in(marker_set):
        ea = getattr(m, 'marker_extra_attributes', {})
        bead_info = re.split(":|-", ea["beadID"])
        chr_info = ea["chrID"]
        bead_start = int(bead_info[1])
        bead_end = int(bead_info[2])
        m.bead_start = bead_start
        m.bead_end = bead_end
        if(chr_info not in bd):
            bd[chr_info] = []
        bd[chr_info].append(m)
    for key in bd:
        bd[key].sort(key=lambda x: x.bead_start)


def visualise_bed(session,
                  bed_file,
                  select_mode=BedSelectMode.RANGE,
                  colour_mode=BedColourMode.SINGLE,
                  hide_org=True,
                  colour=Color((0.5, 0.5, 0.5, 1)),
                  conflict_colour=Color((0.5, 0.5, 0.5, 1)),
                  colour_blend=False,
                  main_model_id="1",
                  new_model_name="BED",
                  gradient_colour_1=Color((0, 0, 0, 1)),
                  gradient_colour_2=Color((1, 1, 1, 1)),
                  score_mode=0,
                  gradient_start=0.0,
                  gradient_end=0.0):

    marker_set = None
    for model in session.models.list():
        # Check new name against existing names:
        new_model_name = numbered_naming(model.name, new_model_name)
        # Get main model
        if (model.id_string == main_model_id):
            marker_set = model
    if (marker_set is None):
        raise UserError("Main model not found. Model ID: \"" + main_model_id + "\"")

    # Prepare model (if not already prepared)
    if(not hasattr(marker_set, "bead_dict")):
        prepare_model(marker_set)

    try:
        reader = open(bed_file, "r")
    except FileNotFoundError:
        raise UserError("File not found: \"" + bed_file + "\"")

    # Prepare percentiles
    start_percentile = None
    end_percentile = None
    if (colour_mode == BedColourMode.SCORE and score_mode == 1):
        if(not (0 <= gradient_start <= 100) or not (0 <= gradient_end <= 100)):
            UserError("Percentiles must be in the range 0-100")

        with reader:
            scores = []
            # Skip meta lines:  TODO maybe use some of this information to display names and such
            line = skip_meta_lines(reader)
            while (True):
                items = line.strip().split()
                if(len(items) < 5):
                    raise UserError("Failed to colour by score as score data was missing in one or more lines in the file")
                scores.append(float(items[4]))

                line = reader.readline()
                if (line == ""):  # EOF reached
                    break

        start_percentile = np.percentile(scores, gradient_start)
        end_percentile = np.percentile(scores, gradient_end)
        print(f"Percentile colouring is using range:{start_percentile} - {end_percentile}")
        reader = open(bed_file, "r")

    # Build the model
    with reader:
        # Skip meta lines:  TODO maybe use some of this information to display names and such
        line = skip_meta_lines(reader)

        from chimerax.markers import MarkerSet

        new_model = MarkerSet(session)
        new_model.name = new_model_name
        marker_seen = {}  # TODO Dict orig marker as key, new marker and blend factors as value?
        correspondence_dict = {}
        # blend_factors = []
        while(True):
            items = line.strip().split()
            # print("len(items):", len(items))
            if(len(items) < 3):
                # Invalid bed file line
                # skip the line
                line = reader.readline()
                if (line == ""):
                    break
                continue

            if (colour_mode == BedColourMode.COLOUR and len(items) < 9):
                raise UserError("Failed to use colour from file as colour data is missing in one or more lines in the file")

            if(colour_mode == BedColourMode.SCORE and len(items) < 5):
                raise UserError("Failed to colour by score as score data was missing in one or more lines in the file")



            make_bed_model(session,
                           new_model,
                           items,
                           select_mode,
                           colour_mode,
                           colour,
                           conflict_colour,
                           hide_org,
                           marker_seen,
                           colour_blend,
                           marker_set,
                           gradient_colour_1,
                           gradient_colour_2,
                           score_mode,
                           gradient_start,
                           gradient_end,
                           start_percentile,
                           end_percentile,
                           correspondence_dict)

            line = reader.readline()
            if(line == ""):  # EOF reached
                break
        # TODO copy links
        copy_links(marker_set, correspondence_dict)
        session.models.add([new_model])


def skip_meta_lines(reader):
    while (True):
        line = reader.readline()
        if (line.startswith("#") or line.startswith("browser") or line.startswith("track") or line.startswith("\n")):
            continue
        else:
            break
    return line


visualise_bed_desc = CmdDesc(required=[("bed_file", OpenFileNameArg)],
                             optional=[("select_mode", IntArg),
                                       ("colour_mode", IntArg),
                                       ("hide_org", BoolArg),
                                       ("colour", ColorArg),
                                       ("conflict_colour", ColorArg),
                                       ("colour_blend", BoolArg),
                                       ("main_model_id", StringArg),
                                       ("new_model_name", StringArg)])


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


def copy_bead(bead, new_model, main_model):
    new_marker = new_model.create_marker(bead.scene_coord, bead.color, bead.radius, bead.residue.number)
    new_marker.marker_extra_attributes = bead.marker_extra_attributes
    return new_marker
    # TODO add other things to be copied if any


def copy_links(main_model, correspondence_dict):
    original_bonds = main_model.bonds.unique()
    neighbours = original_bonds.atoms

    for a, b, orig in zip(neighbours[0], neighbours[1], original_bonds):
        if(a not in correspondence_dict or b not in correspondence_dict):  # Skip
            continue
        create_link(correspondence_dict[a], correspondence_dict[b], orig.color, orig.radius)


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
                new_bead = copy_bead(m, submodels[chr_id], main_model)
                correspondence_dict[m] = new_bead
            else:
                new_sub = MarkerSet(session, chr_id)
                submodels[chr_id] = new_sub
                new_bead = copy_bead(m, new_sub, main_model)
                correspondence_dict[m] = new_bead
                parent.add([new_sub])

        # Copy links:
        copy_links(main_model, correspondence_dict)

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


def make_model_from_selection(session, new_model_name):  # TODO preserve links
    new_model = MarkerSet(session, new_model_name)
    seen_ids = []
    for bead in selected_atoms(session):
        if (bead.residue.number in seen_ids):
            continue
        seen_ids.append(bead.residue.number)
        new_model.create_marker(bead.scene_coord, bead.color, bead.radius, bead.residue.number)
    session.models.add([new_model])


make_model_from_selection_desc = CmdDesc(required=[("new_model_name", StringArg)])


# TODO make callable as a command in chimerax OR move to separate file?
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
                if(rule.not_include):
                    break
                new_model.create_marker(all_involved_beads[bead_id][1].scene_coord,
                                        rule.colour.uint8x4(),
                                        all_involved_beads[bead_id][1].radius,
                                        all_involved_beads[bead_id][1].residue.number)
                break
    session.models.add([new_model])


def select_beads(session, chr_id, from_val, to_val, model_id, select_mode=BedSelectMode.RANGE):
    model = get_model_by_id(session, model_id)
    # Prepare model (if not already prepared)
    if (not hasattr(model, "bead_dict")):
        prepare_model(model)

    selection = []
    for key in model.bead_dict:
        if(key.startswith(chr_id)):
            selection.extend(bead_select_2(from_val, to_val, model.bead_dict[key], select_mode))

    for bead in selection:
        bead.selected = True


select_beads_desc = CmdDesc(required=[("chr_id", StringArg),
                                      ("from_val", IntArg),
                                      ("to_val", IntArg),
                                      ("model_id", StringArg)],
                            optional=[("select_mode", IntArg)])


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
