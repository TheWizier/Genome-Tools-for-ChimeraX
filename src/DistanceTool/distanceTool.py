import numpy as np

from chimerax.core.errors import UserError
from ..util import get_model_by_id, get_models_recursive_by_id
import scipy.spatial.distance


def _get_coords_from_models(model_list):
    coords_list = []
    for m in model_list:
        try:
            coords_list.append(m.atoms.coords)
        except AttributeError:
            pass
    coords = np.concatenate(coords_list)
    return coords



def calculate_pairwise(session, model_id, metric):
    models = get_models_recursive_by_id(session, model_id)
    if not models:
        raise UserError("Could not find model by id: " + model_id)
    coords = _get_coords_from_models(models)

    distances = scipy.spatial.distance.pdist(coords, metric)
    return distances


def calculate_between(session, model_id_a, model_id_b, metric):
    models_a = get_models_recursive_by_id(session, model_id_a)
    if not models_a:
        raise UserError("Could not find model by id: " + model_id_a)
    coords_a = _get_coords_from_models(models_a)

    models_b = get_models_recursive_by_id(session, model_id_b)
    if not models_b:
        raise UserError("Could not find model by id: " + model_id_b)
    coords_b = _get_coords_from_models(models_b)

    distances = scipy.spatial.distance.cdist(coords_a, coords_b, metric)
    return distances


def calculate_point(session, model_id, points, metric):
    models = get_models_recursive_by_id(session, model_id)
    if not models:
        raise UserError("Could not find model by id: " + model_id)
    coords = _get_coords_from_models(models)

    distances = scipy.spatial.distance.cdist(coords, points, metric)
    return distances
