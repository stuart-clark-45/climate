import json
import logging

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from typing import List
from datetime import datetime, timedelta
from geopandas import GeoDataFrame
from shapely.geometry import Point
from noaa import NOAA

logging.basicConfig(level=logging.INFO)


def print_json(obj):
    print(json.dumps(obj, indent=2))


world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world_ax = world.plot(figsize=(10, 6))
world_ax.set(xlim=(-12, 5), ylim=(45, 65), autoscale_on=False, xlabel="Latitude", ylabel="Longitude")



# geolocator = Nominatim()
# location = geolocator.geocode("EX15 3PQ")
# print(location.address)

# Plot my house
my_house = Point(-3.198804, 50.925521)
forecast_location = my_house
# plot_points([forecast_location])

# Init NOAA client
token = "QuhilYMtyPaXXgylTKUwWMUypPOqZZja"
noaa = NOAA(token)

data_type_id = "PRCP"
# data_type_id = "TMAX"

# Get uk stations
uk_location_id = "FIPS:UK"
stations = noaa.stations(uk_location_id, data_type_id=data_type_id)["results"]
station_id_filter = {
    "GHCND:UK000003005",
    "GHCND:UK000003302",
    "GHCND:UKW00035047",
    "GHCND:UK000003808",
    "GHCND:UK000070765",
    "GHCND:UKM00003917",
    "GHCND:UKM00003017",
    "GHCND:UKM00003066",
    "GHCND:UK000003162",
    "GHCND:UKM00003091",
    "GHCND:UKM00003862",
    "GHCND:UKM00003171",
    "GHCND:UKM00003257",
    "GHCND:UKM00003414",
    "GHCND:UKM00003772",
    "GHCND:UKM00003502",
    "GHCND:UKM00003590",
    "GHCND:UKM00003100",
    "GHCND:UK000003026",
    "GHCND:UKM00003740"
}
stations = list(filter(lambda s: s["id"] in station_id_filter, stations))

# plt.show()

# print_json(noaa.locations_categories())
# print_json(noaa.data_set(data_type_id=data_type_id))


# print_json(noaa.data_categories())
# data_types = {}
# for station in stations:
#     station_id = station["id"]
#     logging.info(f'Getting data types for {station_id}')
#     try:
#         for data_type in noaa.data_type(station_id=station_id)["results"]:
#             dt_id = data_type["id"]
#             if not data_type["id"] in data_types:
#                 data_types[dt_id] = data_type
#
#     except Exception:
#         logging.warning(f"Couldn't get data types for {station_id}")
# print_json(list(data_types.values()))

start_date = datetime.now() - timedelta(days=60)
end_date = start_date - timedelta(days=3)
df = None
for station in stations:
    station_id = station["id"]
    try:
        new_df = pd.DataFrame(noaa.data("GHCND", start_date, data_type_id=data_type_id, station_id=station_id))
        num_rows = len(new_df)
        new_df["longitude"] = station["longitude"]
        new_df["latitude"] = station["latitude"]
        if df is None:
            df = new_df
        else:
            df = df.append(new_df)
        print(2)

    except Exception as err:
        logging.warning(f"Failed to get data for station id {station_id}: {err}")

df.sort_values(by=['date'], inplace=True)

logging.info(f"Obtained data for {len(df.station.unique())} stations")

for date in df.date.unique():
    df_date = df[df.date == date]
    if len(df_date.station.unique()) != len(df_date):
        raise Exception('Multiple data points for same date and station')
    station_points = [Point(row["longitude"], row["latitude"]) for index, row in df_date.iterrows()]

    gdf = GeoDataFrame(df_date, geometry=station_points)
    gdf.plot(ax=world_ax, markersize=15, cmap="Reds", column='value', scheme="BoxPlot")
    plt.show()
    break

print(1)
