import json
from typing import List

from noaa import NOAA
from geopy.geocoders import Nominatim
from shapely.geometry import Point
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt

import pandas as pd
import geopandas as gpd


def print_json(obj: dict):
    print(json.dumps(obj, indent=2))


world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world_ax = world.plot(figsize=(10, 6))


def plot_points(points: List[Point], color="red"):
    gdf = GeoDataFrame(pd.DataFrame(points), geometry=points)

    # this is a simple map that goes with geopandas
    gdf.plot(ax=world_ax, marker="o", color=color, markersize=15)


# geolocator = Nominatim()
# location = geolocator.geocode("EX15 3PQ")
# print(location.address)


my_house = Point(-3.198804, 50.925521)
forecast_location = my_house
plot_points([forecast_location])

# Init NOAA client
token = "QuhilYMtyPaXXgylTKUwWMUypPOqZZja"
noaa = NOAA(token)

# Get uk stations
uk_location_id = "FIPS:UK"
stations = noaa.stations(uk_location_id)["results"]


station_points = [Point(station["longitude"], station["latitude"]) for station in stations]
plot_points(station_points, "blue")

plt.show()



# # print_json(noaa.locations_categories())
# # print_json(noaa.locations("ST"))
#


# print_json(noaa.data_categories())
# print_json(noaa.data_type(data_category_id="PRCP"))


# yesterday = datetime.now() - timedelta(days=100)
# print_json(noaa.data("GSOM", yesterday, data_type_id="WT21"))
