import math

from geopy.distance import geodesic
from shapely.geometry import Point as ShapleyPoint

from src.geo_const import R


class Point(ShapleyPoint):

    def lon(self):
        return self.x

    def lat(self):
        return self.y

    def lon_lat(self):
        return self.lon(), self.lat()

    def lat_lon(self):
        return self.lat(), self.lon()

    def translate_km(self, distance, bearing):
        """
        :param distance: the distance to translate the point in km
        :param bearing: the bearing in degrees where 0 is north
        """
        bearing = math.radians(bearing)

        lat_before = math.radians(self.lat())  # Current lat point converted to radians
        lon_before = math.radians(self.lon())  # Current long point converted to radians

        lat_after = math.asin(math.sin(lat_before) * math.cos(distance / R) +
                              math.cos(lat_before) * math.sin(distance / R) * math.cos(bearing))

        lon_after = lon_before + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat_before),
                                            math.cos(distance / R) - math.sin(lat_before) * math.sin(lat_after))

        return Point(math.degrees(lon_after), math.degrees(lat_after))

    def distance_km(self, other: "Point"):
        """
        :param other: the point you want to know the distance to
        :return: the distance form this point to {@code other} in km
        """
        return geodesic(self.lat_lon(), other.lat_lon()).km



