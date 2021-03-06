from src.geo_const import BEARING_NORTH
from src.model.geo_point import GeoPoint
from test.my_test_case import MyTestCase

ab_dist = 1
a = GeoPoint(10, -2)
b = a.translate_km(ab_dist, BEARING_NORTH)


class TestGeoPoint(MyTestCase):
    def test_translate_km(self):
        # Coordinate value tested using google maps measure functionality
        self.assertEqual(b.lon_lat(), (a.lon(), -1.9910067966450713))

    def test_distance_km(self):
        self.assertAlmostEqual(ab_dist, a.distance_km(b), delta=0.01)
