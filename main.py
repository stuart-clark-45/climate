import json
import logging

import geopandas as gpd
import matplotlib.pyplot as plt

from pandas import DataFrame
from geopandas import GeoDataFrame

from geo_point import GeoPoint
from src.geo_util import geo_sample_grid
from station_data_importer import import_station_data

logging.basicConfig(level=logging.INFO)


def print_json(obj):
    print(json.dumps(obj, indent=2))


def main():
    lim_lon = (-12, 5)
    lim_lat = (45, 65)

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world_ax = world.plot(figsize=(10, 6))
    world_ax.set(xlim=lim_lon, ylim=lim_lat, autoscale_on=False, xlabel="Longitude", ylabel="Latitude")
    # world_ax.set(autoscale_on=False, xlabel="Latitude", ylabel="Longitude")

    sample_grid = geo_sample_grid(lim_lon, lim_lat, 100)

    samples = []
    sample_grid_flat = []
    for row in sample_grid:
        for point in row:
            samples.append({
                "longitude": point.lon(),
                "latitude": point.lat(),
            })
            sample_grid_flat.append(point)
    gdf = GeoDataFrame(DataFrame(samples), geometry=sample_grid_flat)
    gdf.plot(ax=world_ax, markersize=5, color="Red")

    # plt.show()

    # geolocator = Nominatim()
    # location = geolocator.geocode("EX15 3PQ")
    # print(location.address)

    # Plot my house
    # my_house = GeoPoint(-3.198804, 50.925521)
    # forecast_location = my_house
    # gdf = GeoDataFrame(DataFrame([{}]), geometry=[my_house])
    # gdf.plot(ax=world_ax, markersize=15, color="Red")
    # plt.show()
    # plot_points([forecast_location])

    df = import_station_data()

    for date in df.date.unique():
        df_date = df[df.date == date]
        if len(df_date.station.unique()) != len(df_date):
            raise Exception('Multiple data points for same date and station')
        station_points = [GeoPoint(row["longitude"], row["latitude"]) for index, row in df_date.iterrows()]
        gdf = GeoDataFrame(df_date, geometry=station_points)
        gdf.plot(ax=world_ax, marker="x", markersize=15, cmap="Reds", column='value', scheme="BoxPlot")

        plt.show()
        break


main()
print("Done.")
