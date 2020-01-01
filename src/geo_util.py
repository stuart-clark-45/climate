from typing import Tuple, List

from src.geo_const import BEARING_EAST, BEARING_NORTH
from src.model.geo_point import GeoPoint


def geo_sample_grid(lim_longitude: Tuple[float, float], lim_latitude: Tuple[float, float], resolution: float):
    """
    :param lim_longitude: (min, max) longitude coordinates
    :param lim_latitude: (min, max) latitude coordinates
    :param resolution: grid resolution in km
    """

    point = GeoPoint(lim_longitude[0], lim_latitude[0])
    sample_grid: List[List[GeoPoint]] = []

    while point.lat() < lim_latitude[1]:
        row = []
        while point.lon() < lim_longitude[1]:
            row.append(point)
            point = point.translate_km(resolution, BEARING_EAST)

        sample_grid.append(row)
        point = row[0].translate_km(resolution, BEARING_NORTH)

    return sample_grid
