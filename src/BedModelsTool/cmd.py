import numpy as np
from chimerax.core.colors import Color
from chimerax.core.commands import CmdDesc, OpenFileNameArg, IntArg, BoolArg, ColorArg, StringArg
from chimerax.core.errors import UserError

from ..util import get_colour_between, numbered_naming, prepare_model, copy_links
from ..enums import SelectMode, BedColourMode


def visualise_bed(session,
                  bed_file,
                  select_mode=SelectMode.RANGE,
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
                  gradient_end=0.0,
                  enable_cutoff=False,
                  cutoff_mode=0,
                  cutoff_start=0.0,
                  cutoff_end=0.0
                  ):
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
    if (not hasattr(marker_set, "bead_dict")):
        prepare_model(marker_set)

    try:
        reader = open(bed_file, "r")
    except FileNotFoundError:
        raise UserError("File not found: \"" + bed_file + "\"")

    # Prepare percentiles
    start_percentile = None
    end_percentile = None
    start_cutoff_percentile = None
    end_cutoff_percentile = None
    gradient_percentile_enabled = (colour_mode == BedColourMode.SCORE and score_mode == 1)
    cutoff_percentile_enabled = (enable_cutoff and cutoff_mode == 1)

    if (gradient_percentile_enabled or cutoff_percentile_enabled):
        if (gradient_percentile_enabled and (not (0 <= gradient_start <= 100) or not (0 <= gradient_end <= 100))):
            UserError("Percentiles must be in the range 0-100")
        if (cutoff_percentile_enabled and (not (0 <= cutoff_start <= 100) or not (0 <= cutoff_end <= 100))):
            UserError("Percentiles must be in the range 0-100")

        with reader:
            scores = []
            # Skip meta lines:
            line = skip_meta_lines(reader)
            while (True):
                items = line.strip().split()
                if (len(items) < 5):
                    raise UserError(
                        "Failed to calculate percentiles as score data was missing in one or more lines in the file")
                scores.append(float(items[4]))

                line = reader.readline()
                if (line == ""):  # EOF reached
                    break

        if (gradient_percentile_enabled):
            start_percentile = np.percentile(scores, gradient_start)
            end_percentile = np.percentile(scores, gradient_end)
            print(f"Percentile colouring is using range:{start_percentile} - {end_percentile}")
        if (cutoff_percentile_enabled):
            start_cutoff_percentile = np.percentile(scores, cutoff_start)
            end_cutoff_percentile = np.percentile(scores, cutoff_end)
            print(f"Percentile cutoff is using range:{start_cutoff_percentile} - {end_cutoff_percentile}")

        reader = open(bed_file, "r")

    # Build the model
    with reader:
        # Skip meta lines:
        line = skip_meta_lines(reader)

        from chimerax.markers import MarkerSet

        new_model = MarkerSet(session)
        new_model.name = new_model_name
        marker_seen = {}
        correspondence_dict = {}
        # blend_factors = []
        while (True):
            items = line.strip().split()
            # print("len(items):", len(items))
            if (len(items) < 3):
                # Invalid bed file line
                # skip the line
                line = reader.readline()
                if (line == ""):
                    break
                continue

            if (colour_mode == BedColourMode.COLOUR and len(items) < 9):
                raise UserError(
                    "Failed to use colour from file as colour data is missing in one or more lines in the file")

            if (colour_mode == BedColourMode.SCORE and len(items) < 5):
                raise UserError("Failed to colour by score as score data was missing in one or more lines in the file")

            make_bed_model(new_model,
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
                           correspondence_dict,
                           enable_cutoff,
                           cutoff_mode,
                           cutoff_start,
                           cutoff_end,
                           start_cutoff_percentile,
                           end_cutoff_percentile
                           )

            line = reader.readline()
            if (line == ""):  # EOF reached
                break

        copy_links([marker_set], correspondence_dict)
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


def make_bed_model(new_model,
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
                   correspondence_dict,
                   enable_cutoff,
                   cutoff_mode,
                   cutoff_start,
                   cutoff_end,
                   start_cutoff_percentile,
                   end_cutoff_percentile
                   ):
    # Find all markers in the range from the BED file line

    # Find the matching beads

    selection = []  # This selection is continuous and in order
    for key in marker_set.bead_dict:
        if (key.startswith(items[0])):
            selection.extend(bead_select(int(items[1]), int(items[2]), marker_set.bead_dict[key], select_mode))
    for m in selection:
        # Ignore scores outside of cutoff range:
        if (enable_cutoff):
            if (cutoff_mode == 1):  # Use Percentile
                if (not (start_cutoff_percentile <= float(items[4]) <= end_cutoff_percentile)):
                    continue
            else:  # Use Score
                if (not (cutoff_start <= float(items[4]) <= cutoff_end)):
                    continue

        # Handle multiple entries on a single bead:
        if (m in marker_seen):
            if (colour_mode == BedColourMode.SINGLE or colour_mode == BedColourMode.RETAIN):
                continue

            bead = marker_seen[m][0]
            if (colour_blend):
                # Apply blend colour

                # Get blend factor
                blend_factor = marker_seen[m][1]

                if (colour_mode == BedColourMode.SCORE):
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

                bead.color = get_colour_between(bead.color, rgba, 1 / (blend_factor + 1))
                # Update blend factor:
                marker_seen[m][1] += 1

            else:
                # Apply conflict colour
                bead.color = conflict_colour.uint8x4()
            continue

        # Hide beads on main model
        if (hide_org):
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

        elif (colour_mode == BedColourMode.RETAIN):
            rgba = m.color

        else:
            print("Invalid colour mode")
            return  # TODO exception?

        # Make new bead
        new_marker = new_model.create_marker(m.scene_coord, rgba, m.radius, m.residue.number)
        # Add marker as seen
        marker_seen[m] = [new_marker, 1]
        # Add to correspondence dict
        correspondence_dict[m] = new_marker


def bead_select(from_val, to_val, bead_list, select_mode):
    if(select_mode == SelectMode.RANGE):
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

    if(select_mode == SelectMode.RANGE_STRICT):
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

    if(select_mode == SelectMode.START):
        for bead in bead_list:
            if(bead.bead_start < from_val < bead.bead_end):
                return [bead]

    if (select_mode == SelectMode.END):
        for bead in bead_list:
            if(bead.bead_start < to_val < bead.bead_end):
                return [bead]

    if (select_mode == SelectMode.MIDDLE):
        for bead in bead_list:
            if(bead.bead_start < (from_val + (to_val - from_val) / 2) < bead.bead_end):
                return [bead]
    return []


def get_score_based_colour(score_mode,
                           items,
                           start_percentile,
                           end_percentile,
                           gradient_start,
                           gradient_end,
                           gradient_colour_1,
                           gradient_colour_2):

    if (score_mode == 1):  # Use Percentile
        try:
            colour_percent = max(0, min(1, (float(items[4]) - start_percentile) / (
                    end_percentile - start_percentile)))
        except ZeroDivisionError:
            colour_percent = 0
    else:  # Use Score
        colour_percent = max(0, min(1, (float(items[4]) - gradient_start) / (
                gradient_end - gradient_start)))
    return get_colour_between(gradient_colour_1.uint8x4(), gradient_colour_2.uint8x4(), colour_percent)


def skip_meta_lines(reader):
    while (True):
        line = reader.readline()
        if (line.startswith("#") or line.startswith("browser") or line.startswith("track") or line.startswith("\n")):
            continue
        else:
            break
    return line
