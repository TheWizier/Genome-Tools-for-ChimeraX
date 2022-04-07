import numpy as np
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QDoubleValidator


# class BetterQDoubleValidator(QDoubleValidator):
#     def __init__(self):
#         super().__init__()
#
#     def validate(self, p_str, p_int):
#         ret = super().validate(p_str, p_int)


def get_locale(): #TODO issue with qvalidator giving 0 from , and empty without changing text field
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


def norm_vector(v):  # TODO check that it works and maybe move elsewhere
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
    model_list.extend(get_all_submodels(session, root_model))
    return model_list


def get_all_submodels(session, model):
    submodels = []
    for m in model.child_models():
        submodels.append(m)
        submodels.extend(get_all_submodels(session, m))
    return submodels
