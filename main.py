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


# TODO this is pretty inefficient because of the use of DataFrame.iterrows()
# TODO https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
def interpolate_station_data(
        station_df: DataFrame,
        samples_df: DataFrame,
        threshold=250,
        neighbourhood_size=3,
        distance_exponent=2):

    sample_values = []

    # For each of the samples we are going to find an interpolated value
    for _, sample in samples_df.iterrows():

        # Find the samples neighbours
        neighbourhood = []
        for _, station in station_df.iterrows():

            # Get the distance from the station to the sample
            station_point = GeoPoint(station["longitude"], station["latitude"])
            sample_point = GeoPoint(sample["longitude"], sample["latitude"])
            distance = station_point.distance_km(sample_point)

            if distance < threshold:
                neighbourhood.append({"distance": distance, "value": station["value"]})

        # Select at most the three closest neighbours
        neighbourhood.sort(key=lambda x: x["distance"])
        neighbourhood = neighbourhood[:neighbourhood_size]

        # Make sure the sample has a neighborhood
        if not len(neighbourhood):
            raise Exception("Increase threshold at least one sample has no neighbours")

        # Calculate the inverse distance weighted value
        sum_distance = sum(map(lambda n: n["value"], neighbourhood))
        interpolated_value = 0.0
        for neighbour in neighbourhood:
            modifier = sum_distance / neighbour["distance"] ** distance_exponent
            interpolated_value += neighbour["value"] * modifier

        sample_values.append(interpolated_value)

    # Modify the samples data frame
    samples_df["value"] = sample_values


def main():
    station_df = import_station_data()

    lon_series = station_df['longitude']
    lat_series = station_df['latitude']

    lim_lon = (lon_series.min(), lon_series.max())
    lim_lat = (lat_series.min(), lat_series.max())

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

    for date in station_df.date.unique():
        df_date = station_df[station_df.date == date]
        if len(df_date.station.unique()) != len(df_date):
            raise Exception('Multiple data points for same date and station')

        interpolate_station_data(df_date, samples_df)

        # station_points = [GeoPoint(row["longitude"], row["latitude"]) for index, row in df_date.iterrows()]
        # gdf = GeoDataFrame(df_date, geometry=station_points)
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
        break


main()
print("Done.")
