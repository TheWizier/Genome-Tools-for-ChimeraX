import re

import numpy as np
from Qt.QtCore import QLocale
from Qt.QtGui import QDoubleValidator
from chimerax.atomic import Bonds
from chimerax.markers import create_link


class BetterQDoubleValidator(QDoubleValidator):
    def __init__(self):
        super().__init__()

    # def validate(self, p_str, p_int):
    #     state, str_ret, int_ret = super().validate(p_str, p_int)
    #     #print(state, str_ret, int_ret)
    #     return state, str_ret, int_ret

    def fixup(self, p_str):
        # Try removing group separators:
        if self.locale().groupSeparator() in p_str:
            p_str = p_str.replace(self.locale().groupSeparator(), "")

        # Try removing invalid Scientific notation:
        if(p_str.startswith("E") or p_str.endswith("E") or p_str.endswith("E-")):
            p_str = p_str.replace("E-", "")
            p_str = p_str.replace("E", "")

        # Give up if fix doesn't work
        state, text, _ = self.validate(p_str, len(p_str))
        if (state != QDoubleValidator.Acceptable):
            return "0"

        return p_str


def get_locale():
    """
    :return: The QLocale for this project
    """
    ql = QLocale()
    ql.setNumberOptions(ql.numberOptions() | QLocale.RejectGroupSeparator)
    return ql

def all_atoms_in(model):
    try:
    #if(hasattr(model, "atoms")):
        for atom in model.atoms:
            yield atom
    except AttributeError:
        pass
    for m in model.child_models():
        yield from all_atoms_in(m)


def norm_vector(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def get_model_by_id(session, model_id):
    for model in session.models.list():
        if (model.id_string == model_id):
            return model


def get_models_recursive_by_id(session, model_id):
    root_model = get_model_by_id(session, model_id)
    if root_model is None:
        return []
    model_list = [root_model]
    model_list.extend(get_all_submodels(root_model))
    return model_list


def get_all_submodels(model):
    submodels = []
    for m in model.child_models():
        submodels.append(m)
        submodels.extend(get_all_submodels(m))
    return submodels


def get_colour_between(colour_1, colour_2, percent):
    """
    Get colour between two colours

    :param colour_1: The first colour
    :param colour_2: The second colour
    :param percent: The percentage between the colours to find
    :return: The colour at the percentage between the two colours
    """
    return [x*(1-percent)+y*percent for x, y in zip(colour_1, colour_2)]


def numbered_naming(existing_name, new_name):  # TODO a bit strange but works fine
    """
    Checks for duplicate naming and returns numbered names for duplicates.

    :param existing_name: Name to check against
    :param new_name: The new name
    :return: The new name after check and potential alteration
    """
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
    bead_id_split_pattern = re.compile(":|-")
    for m in all_atoms_in(marker_set):
        ea = getattr(m, 'marker_extra_attributes', {})
        bead_info = bead_id_split_pattern.split(ea["beadID"])
        # bead_info = re.split(":|-", ea["beadID"])
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


def copy_bead(bead, new_model):
    """
    Makes a copy of the specified bead and places it in the new model

    :param bead: Bead to copy
    :param new_model: The model to copy the bead into
    :return: The new bead
    """
    new_marker = new_model.create_marker(bead.scene_coord, bead.color, bead.radius, bead.residue.number)
    new_marker.marker_extra_attributes = bead.marker_extra_attributes
    return new_marker
    # TODO add other things to be copied if any


def copy_links(main_model, correspondence_dict):
    """
    Links beads in the correspondence_dict if they are linked in the main_model.
    The new links retain the colour and radius of the original link.

    :param main_model: The main_model
    :param correspondence_dict: A dictionary with corresponding beads from the new model and the main_model
    """

    # Get all bonds(links) from the main model and its submodels
    models = get_all_submodels(main_model)
    models.append(main_model)
    original_bonds = Bonds()
    for model in models:
        try:
            original_bonds = original_bonds.merge(model.bonds.unique())
        except AttributeError:
            pass

    neighbours = original_bonds.atoms

    # Copy over the required links
    for a, b, orig in zip(neighbours[0], neighbours[1], original_bonds):
        if(a not in correspondence_dict or b not in correspondence_dict):  # Skip
            continue
        create_link(correspondence_dict[a], correspondence_dict[b], orig.color, orig.radius)