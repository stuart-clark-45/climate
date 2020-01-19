import json
import logging

import geopandas as gpd
import matplotlib.pyplot as plt

from pandas import DataFrame
from geopandas import GeoDataFrame
from mongoengine import connect

from src.model.geo_point import GeoPoint
from src.station_interpolator import StationInterpolator
from src.geo_util import geo_sample_grid
from src.station_data_importer import import_station_data

logging.basicConfig(level=logging.DEBUG)

connect('climate')


def print_json(obj):
    print(json.dumps(obj, indent=2))


def main():
    # Get the station data and pull out some useful values
    station_data = import_station_data()
    bounds = station_data.bounds
    station_df_series = station_data.station_df_series
    lim_lon = bounds.lon
    lim_lat = bounds.lat

    # Get the samples data frame
    sample_grid = geo_sample_grid(lim_lon, lim_lat, 20)
    samples = []
    sample_grid_flat = []
    for row in sample_grid:
        for point in row:
            samples.append({
                "longitude": point.lon(),
                "latitude": point.lat(),
            })
            sample_grid_flat.append(point)
    samples_df = DataFrame(samples)

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world_ax = world.plot(figsize=(10, 6))
    world_ax.set(xlim=lim_lon, ylim=lim_lat, autoscale_on=False, xlabel="Longitude", ylabel="Latitude")

    # Plot my house
    my_house = GeoPoint(-3.198804, 50.925521)
    forecast_location = my_house
    gdf = GeoDataFrame(DataFrame([{}]), geometry=[forecast_location])
    gdf.plot(ax=world_ax, marker="D", markersize=20, color="Purple")

    StationInterpolator.optimise_params(station_df_series[:5])
    interpolator = StationInterpolator()
    interpolator.interpolate_station_data(station_df_series[0], samples_df)

    # station_points = [GeoPoint(row["longitude"], row["latitude"]) for index, row in date_df.iterrows()]
    # gdf = GeoDataFrame(date_df, geometry=station_points)
    # gdf.plot(
    #     ax=world_ax,
    #     marker="x",
    #     markersize=15,
    #     cmap="Reds",
    #     column='value',
    #     scheme="BoxPlot",
    # )

    gdf = GeoDataFrame(samples_df, geometry=sample_grid_flat)
    gdf.plot(
        ax=world_ax,
        markersize=5,
        cmap="Reds",
        column='value',
        scheme="BoxPlot",
    )

    plt.show()


main()
print("Done.")
