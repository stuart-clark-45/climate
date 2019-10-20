from unittest import TestCase

from src.geo_const import BEARING_NORTH
from src.point import Point

ab_dist = 1
a = Point(10, -2)
b = a.translate_km(ab_dist, BEARING_NORTH)


class TestPoint(TestCase):
    def test_translate_km(self):
        # Coordinate value tested using google maps measure functionality
        self.assertEqual(b.lon_lat(), (a.lon(), -1.9910167950466309))

    def test_distance_km(self):
        # TODO from this test we can see that accuracy of either Point.distance_km(..) or Point.translate_km(..)
        # TODO leaves something to be required
        self.assertAlmostEqual(ab_dist, a.distance_km(b), delta=0.01)
