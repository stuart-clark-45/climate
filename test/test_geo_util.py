import logging

from src.geo_util import geo_sample_grid
from test.my_test_case import MyTestCase


class TestGeoUtil(MyTestCase):
    def test_geo_sample_grid(self):
        lim_lon = (-12, 5)
        lim_lat = (45, 65)
        resolution = 200.0
        grid = geo_sample_grid(lim_lon, lim_lat, resolution)
        max_abs_err = 0
        total_abs_err = 0
        count = 0.0

        for i in range(len(grid)):
            row = grid[i]

            len_row = len(row)
            for j in range(len_row):
                point = row[j]
                count += 1

                # If not first element in row
                if j > 0:
                    # Test the distance to the previous element in the row
                    distance_km = point.distance_km(row[j - 1])
                    abs_err = abs(distance_km - resolution)
                    total_abs_err += abs_err
                    max_abs_err = max(max_abs_err, abs_err)

                # If not first row
                if i > 0:
                    prev_row = grid[i - 1]

                    # And the previous row has an element j
                    if len(prev_row) > j:

                        # Test the distance to the same element in the row above
                        distance_km = point.distance_km(prev_row[j])
                        abs_err = abs(distance_km - resolution)
                        total_abs_err += abs_err
                        max_abs_err = max(max_abs_err, abs_err)

        relative_mean_abs_error = (total_abs_err / count) / resolution
        relative_max_abs_error = max_abs_err / resolution

        logging.info("geo_sample_grid(..) accuracy:")
        logging.info(f"relative mean abs error: {relative_mean_abs_error}")
        logging.info(f"relative max abs error: {relative_max_abs_error}")

        self.assertLess(relative_mean_abs_error, 0.01)
        self.assertLess(relative_max_abs_error, 0.03)
