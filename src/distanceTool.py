from chimerax.core.errors import UserError
from .util import get_model_by_id
import scipy.spatial.distance


def calculate_pairwise(session, model_id):
    model = get_model_by_id(session, model_id)
    if model is None:
        raise UserError("Could not find model by id: " + model_id)
    coords = model.atoms.coords
    distances = scipy.spatial.distance.pdist(coords)
    return distances


def calculate_between(session):
    pass


def calculate_point(session):
    pass
