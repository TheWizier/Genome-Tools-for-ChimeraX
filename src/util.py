import numpy as np


def norm_vector(v):  # TODO check that it works and maybe move elsewhere
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def get_model_by_id(session, model_id):
    for model in session.models.list():
        if (model.id_string == model_id):
            return model