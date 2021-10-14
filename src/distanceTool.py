from .util import get_model_by_id
import scipy.spatial.distance

def calculate_pairwise(session):
    model = get_model_by_id(session, "1")
    coords = model.atoms.coords
    distances = scipy.spatial.distance.pdist(coords)
    return distances

def calculate_between(session):
    pass


def calculate_point(session):
    pass
