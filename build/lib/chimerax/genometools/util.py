import numpy as np
from Qt.QtCore import QLocale
from Qt.QtGui import QDoubleValidator


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
