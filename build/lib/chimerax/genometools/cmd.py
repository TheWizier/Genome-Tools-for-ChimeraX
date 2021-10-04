# vim: set expandtab shiftwidth=4 softtabstop=4:
import time
from typing import List, Dict

from chimerax.atomic import selected_atoms
from chimerax.core.colors import Color
from chimerax.core.commands import CmdDesc, OpenFileNameArg, StringArg, IntArg, BoolArg, ColorArg
from chimerax.core.errors import UserError
from chimerax.markers import MarkerSet
from .OverlapRule import OverlapRule
from .tool import BedColourMode, BedSelectMode
from chimerax.core.commands import all_objects
import re

import numpy as np

def select_chromosome(session, chr_id):  # Superseded by make_submodels but no reason to remove it
    from chimerax.core.commands import all_objects
    atoms = all_objects(session).atoms
    from chimerax.std_commands.select import select_add
    from chimerax.core.commands import ObjectsArg
    #text = ":"
    count = 0
    for m in atoms:
        ea = getattr(m, 'marker_extra_attributes', {})
        if(ea["chrID"] == chr_id):
            m.selected = True
            count += 1
    session.logger.info("Selected " + str(count) + " markers")
            #text += str(m.residue.number) + ","
    #text = text[:-1]
    #selected, tmp1, tmp2 = ObjectsArg.parse(text, session)
    #select_add(session, selected)


select_chromosome_desc = CmdDesc(required=[("chr_id", StringArg)])


def inspect_beads(session):
    from chimerax.core.commands import all_objects
    atoms = all_objects(session).atoms
    for a in atoms[atoms.selected]:
        session.logger.info(str(a) + ": " + str(a.marker_extra_attributes))


inspect_beads_desc = CmdDesc()


def norm_vector(v):  # TODO check that it works and maybe move elsewhere
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


# TODO NB this is not used and code is outdated:
def cut_bead(session, bead, pos, keep_original=False):  # TODO keep here or move to different file?
    '''
    Split a bead into two new beads while retaining selection and making new bonds.
    The cut is done before the pos index.
    :returns: The two new beads
    '''

    # for var in dir(bead):
    #     print(var, ":")
    #     try:
    #         print(eval("bead." + var))
    #     except NameError:
    #         pass

    # TODO Now adding min size change if neccesary
    minimum_radius = 0.002
    link_to_marker_ratio = 0.25

    if(len(bead.neighbors) > 2 or len(bead.neighbors) < 1):
        print("Invalid number of neighbours for bead in cut_bead:", len(bead.neighbors))
        return None  # TODO or just throw error?

    beadID = re.split(":|-", bead.marker_extra_attributes["beadID"])
    bead_start = int(beadID[1])
    bead_end = int(beadID[2])

    # Find radius of new beads
    print("bead_start:", bead_start, "bead_end:", bead_end)
    print("pos:", pos, "bead.radius:", bead.radius)
    print(((pos - bead_start) / (bead_end - bead_start)))
    print(((bead_end - pos) / (bead_end - bead_start)))  # TODO fix math so radii add up?
    bead1_radius = ((pos - bead_start) / (bead_end - bead_start)) * bead.radius
    bead2_radius = ((bead_end - pos) / (bead_end - bead_start)) * bead.radius
    print("bead1_radius:", bead1_radius)
    print("bead2_radius:", bead2_radius)

    neighbor_a = bead.neighbors[0]
    neighbor_b = bead.neighbors[1]
    neighbor_a_id = re.split(":|-", bead.neighbors[0].marker_extra_attributes["beadID"])
    neighbor_a_start = int(neighbor_a_id[1])

    # Calculate vector to place beads on
    vector = None
    neighbor_first = False
    string_edge = False
    if(len(bead.neighbors) == 1):
        string_edge = True
        # We are at the end of the string of beads
        if(neighbor_a_start < bead_start):
            # neighbour is first -> Vector should point away from neighbour
            vector = bead.scene_coord - neighbor_a.scene_coord
            neighbor_first = True
        else:
            # neighbour is last -> Vector should point towards neighbour
            vector = neighbor_a.scene_coord - bead.scene_coord

    else:
        # We are not at the end of a string of beads
        if (neighbor_a_start < bead_start):
            # neighbour_a is first -> Vector should point away from neighbour_a
            vector = neighbor_b.scene_coord - neighbor_a.scene_coord
            neighbor_first = True
        else:
            # neighbour_a is last -> Vector should point towards neighbour_a
            vector = neighbor_a.scene_coord - neighbor_b.scene_coord

    # Calculate coordinates of new beads
    bead_edge = bead.scene_coord - norm_vector(vector) * bead.radius
    bead1_coord = bead_edge + norm_vector(vector) * bead1_radius
    bead2_coord = bead_edge + norm_vector(vector) * 2 * bead1_radius + norm_vector(vector) * bead2_radius


    from chimerax.markers import MarkerSet
    from chimerax.markers import create_link
    marker_sets = session.models.list(type=MarkerSet)
    m = marker_sets[0]  # TODO this assumes that we are always working on the first one

    if(keep_original):
        m1 = m.create_marker(bead1_coord, bead.color, max(bead1_radius, minimum_radius))
    else:
        m1 = bead  # TODO change size of bonds to neighbors
        bead.scene_coord = bead1_coord
        bead.radius = max(bead1_radius, minimum_radius)
    m2 = m.create_marker(bead2_coord, bead.color, max(bead2_radius, minimum_radius))

    link_radius = max(min(bead1_radius, bead2_radius), minimum_radius) * link_to_marker_ratio

    if(string_edge):
        if(neighbor_first):
            if(keep_original):
                create_link(neighbor_a, m1, bead.color, link_radius)
            else:
                for b in m1.bonds:
                    if(b.other_atom(m1) == neighbor_b):
                        b.delete()
                        print("REM BOND")

        else:
            create_link(m2, neighbor_a, bead.color, link_radius)
            if (not keep_original):
                for b in m1.bonds:
                    if(b.other_atom(m1) == neighbor_a):
                        b.delete()
                        print("REM BOND")
    else:
        if (neighbor_first):
            create_link(m2, neighbor_b, bead.color, link_radius)
            if(keep_original):
                create_link(neighbor_a, m1, bead.color, link_radius)
            else:
                for b in m1.bonds:
                    if(b.other_atom(m1) == neighbor_b):
                        b.delete()
                        print("REM BOND")

        else:
            create_link(m2, neighbor_a, bead.color, link_radius)
            if(keep_original):
                create_link(neighbor_b, m1, bead.color, link_radius)
            else:
                for b in m1.bonds:
                    if(b.other_atom(m1) == neighbor_a):
                        b.delete()
                        print("REM BOND")
    create_link(m1, m2, bead.color, link_radius)


    # Set extra_marker_attributes
    m1.marker_extra_attributes = {"chrID": bead.marker_extra_attributes["chrID"],
                                  "beadID": beadID[0] + ":" + str(bead_start) + "-" + str(pos)}
    m2.marker_extra_attributes = {"chrID": bead.marker_extra_attributes["chrID"],
                                  "beadID": beadID[0] + ":" + str(pos) + "-" + str(bead_end)}
    # Delete old bead  # We change the original to be part of the split instead since deletion breaks indexing
    # if(not keep_original):
    #     for b in bead.bonds:
    #         b.delete()
    #     bead.delete()
    # TODO preserve selection option

    return m1, m2


def bead_select_2(items, bead_list, select_mode):
    if(select_mode == BedSelectMode.RANGE):
        start_index = None
        for bead_index in range(len(bead_list)):
            if(int(items[1]) < bead_list[bead_index].bead_end):
                start_index = bead_index
        if start_index is None:
            return []
        end_index = None
        for bead_index in range(start_index, len(bead_list)):
            if(int(items[2]) < bead_list[bead_index].bead_end):
                end_index = bead_index
        if end_index is None:
            end_index = len(bead_list)-1
        return bead_list[start_index:(end_index + 1)]

    if(select_mode == BedSelectMode.RANGE_STRICT):
        start_index = None
        for bead_index in range(len(bead_list)):
            if (int(items[1]) < bead_list[bead_index].bead_start):
                start_index = bead_index
        if start_index is None:
            return []
        end_index = None
        for bead_index in range(start_index, len(bead_list)):
            if (int(items[2]) < bead_list[bead_index].bead_end):
                end_index = bead_index-1
        if end_index is None:
            end_index = len(bead_list) - 1
        return bead_list[start_index:(end_index + 1)]

    if(select_mode == BedSelectMode.START):
        for bead in bead_list:
            if(bead.bead_start < int(items[1]) < bead.bead_end):
                return [bead]

    if (select_mode == BedSelectMode.END):
        for bead in bead_list:
            if(bead.bead_start < int(items[2]) < bead.bead_end):
                return [bead]

    if (select_mode == BedSelectMode.MIDDLE):
        for bead in bead_list:
            if(bead.bead_start < (int(items[1]) + (int(items[2]) - int(items[1])) / 2) < bead.bead_end):
                return [bead]
    return []


def bead_select(items, bead_start, bead_end, select_mode):
    if(select_mode == BedSelectMode.RANGE):
        return int(items[1]) < bead_end and int(items[2]) >= bead_start
    if(select_mode == BedSelectMode.RANGE_STRICT):
        return int(items[1]) < bead_start and int(items[2]) >= bead_end
    if(select_mode == BedSelectMode.START):
        return bead_start < int(items[1]) < bead_end
    if (select_mode == BedSelectMode.END):
        return bead_start < int(items[2]) < bead_end
    if (select_mode == BedSelectMode.MIDDLE):
        return bead_start < (int(items[1]) + (int(items[2]) - int(items[1])) / 2) < bead_end

# def get_genome_attributes(m): # TODO maybe something like this later
#     ea = getattr(m, 'marker_extra_attributes', {})
#     bead_info = re.split(":|-", ea["beadID"])
#     bead_start = int(bead_info[1])
#     bead_end = int(bead_info[2])

def all_atoms_in(model):
    if(hasattr(model, "atoms")):
        for atom in model.atoms:
            yield atom
    for m in model.child_models():
        yield from all_atoms_in(m)


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
        colour_percent = max(0, min(1, (int(items[4]) - start_percentile) / (
                end_percentile - start_percentile)))  # TODO division by 0 possible
    else:  # Use Score
        colour_percent = max(0, min(1, (int(items[4]) - gradient_start) / (
                gradient_end - gradient_start)))
    return get_colour_between(gradient_colour_1.uint8x4(), gradient_colour_2.uint8x4(), colour_percent)


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
                   blend_factors,
                   gradient_colour_1,
                   gradient_colour_2,
                   score_mode,
                   gradient_start,
                   gradient_end,
                   start_percentile,
                   end_percentile
                   ):


    # Find all markers in the range from the BED file line

    # Find the matching beads

    # TODO TEST NEW CODE
    # selection = []
    # for key in marker_set.bead_dict:
    #     if(key.startswith(items[0])):
    #         selection.append(bead_select_2(items, marker_set.bead_dict[key], select_mode))
    # for m in selection:
    #     pass

    import itertools
    for m in all_atoms_in(marker_set):
        ea = m.marker_extra_attributes
        bead_start = m.bead_start
        bead_end = m.bead_end
        bead_id = m.residue.number  # TODO useful?
        # Currently we are colouring both A and B and others. from inclusive to exclusive
        # TODO be able to specify a or b chromosome
        if (ea["chrID"].startswith(items[0]) and bead_select(items, bead_start, bead_end, select_mode)):
            # Determine what to do if we have seen this marker already
            if(m in marker_seen):
                if(colour_mode == BedColourMode.SINGLE):
                    continue

                if(colour_blend):
                    # Apply blend colour
                    for bead in new_model.atoms:
                        if (bead.residue.number == m.residue.number):
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

                            m_index = marker_seen.index(m)
                            blend_factor = blend_factors[m_index]
                            bead.color = get_colour_between(bead.color, rgba, 1/(blend_factor+1))
                            blend_factors[m_index] += 1

                else:
                    # Apply conflict colour
                    for bead in new_model.atoms:
                        if (bead.residue.number == m.residue.number):
                            bead.color = conflict_colour.uint8x4()
                            break
                continue

            marker_seen.append(m)
            if(colour_blend):
                blend_factors.append(1)  # This relies on the lists being "in sync"

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
            new_model.create_marker(m.scene_coord, rgba, m.radius, bead_id)


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
    # marker_set.save_attribute_in_sessions("bead_dict", dict)  # TODO save?
    starttime = time.clock()  # TODO REMOVE
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
    print("PREPARE:", time.clock()-starttime)  # TODO REMOVE


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
            # Skip meta lines:  TODO maybe use some of this information to display names and such
            line = ""
            scores = []
            while (True):
                line = reader.readline()
                if (line.startswith("#") or line.startswith("browser") or line.startswith("track") or line.startswith(
                        "\n")):
                    continue
                else:
                    break
            while (True):
                items = line.strip().split()
                if(len(items) < 5):
                    raise UserError("Failed to colour by score as score data was missing in one or more lines in the file")
                scores.append(int(items[4]))

                line = reader.readline()
                if (line == ""):  # EOF reached
                    break

        start_percentile = np.percentile(scores, gradient_start)
        end_percentile = np.percentile(scores, gradient_end)
        reader = open(bed_file, "r")

    with reader:
        line = ""

        # Skip meta lines:  TODO maybe use some of this information to display names and such
        while(True):
            line = reader.readline()
            if(line.startswith("#") or line.startswith("browser") or line.startswith("track") or line.startswith("\n")):
                continue
            else:
                break

        from chimerax.markers import MarkerSet

        new_model = MarkerSet(session)
        new_model.name = new_model_name
        marker_seen = []
        blend_factors = []
        while(True):
            items = line.strip().split()
            # print("len(items):", len(items))
            if(len(items) < 3):
                # Invalid bed file line
                # skip the line
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
                           blend_factors,
                           gradient_colour_1,
                           gradient_colour_2,
                           score_mode,
                           gradient_start,
                           gradient_end,
                           start_percentile,
                           end_percentile)

            line = reader.readline()
            if(line == ""):  # EOF reached
                break
        session.models.add([new_model])


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
    from chimerax.core.colors import Color
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
    # TODO add other things to be copied if any

def make_submodels(session, main_model_id="1"):
    # TODO maybe make function for fetching model by id like this
    main_model = None
    for model in session.models.list():
        if (model.id_string == main_model_id):
            main_model = model
            break

    if (main_model is None):
        raise UserError("No model with id: ", main_model_id)

    # To split the model into submodels we actually just make an entirely new model and delete the old one
    # so all the atoms must be "copied" to their new models.
    submodels = {}
    from chimerax.core.models import Model
    parent = Model(main_model.name, session)
    parent.id = main_model.id
    for m in main_model.atoms:
        ea = getattr(m, 'marker_extra_attributes', {})
        if (ea["chrID"] in submodels):
            copy_bead(m, submodels[ea["chrID"]], main_model)
        else:
            new_sub = MarkerSet(session, ea["chrID"])
            submodels[ea["chrID"]] = new_sub
            copy_bead(m, new_sub, main_model)
            parent.add([new_sub])

    session.models.close([main_model])
    session.models.add([parent])


make_submodels_desc = CmdDesc(required=[("main_model_id", StringArg)])

def make_model_from_selection(session, new_model_name):
    new_model = MarkerSet(session, new_model_name)
    seen_ids = []
    for bead in selected_atoms(session):
        if (bead.residue.number in seen_ids):
            continue
        seen_ids.append(bead.residue.number)
        new_model.create_marker(bead.scene_coord, bead.color, bead.radius, bead.residue.number)
    session.models.add([new_model])

make_model_from_selection_desc = CmdDesc(required=[("new_model_name", StringArg)])


def get_model_by_id(session, model_id):
    for model in session.models.list():
        if (model.id_string == model_id):
            return model


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


def save_marker_attributes(session, model_id):  # TODO must apply to submodels as well!
    m_sets = session.models.list(type=MarkerSet)
    print(m_sets)
    for m_set in m_sets:
        if (m_set.id_string == model_id):
            if(hasattr(m_set, "save_marker_attribute_in_sessions")):
                m_set.save_marker_attribute_in_sessions('marker_extra_attributes', Dict)
            else:  # Backwards compatibility
                from chimerax.atomic import Atom
                Atom.register_attr(session, 'marker_extra_attributes', "markers", attr_type=Dict)
            print("SUCCESS")


save_marker_attributes_desc = CmdDesc(required=[("model_id", StringArg)])
