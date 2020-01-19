import logging

from datetime import datetime, timedelta
from typing import Tuple, List

from src.service.noaa import NOAA
from pandas import DataFrame


class GeoPointBounds:
    def __init__(self, lat: Tuple[float, float], lon: Tuple[float, float]) -> None:
        """
        :param lat: tuple with the following form (<min lat>, <max lat>)
        :param lon:tuple with the following form (<min lon>, <max lon>)
        """
        self.lat = lat
        self.lon = lon


class StationData:
    def __init__(self, station_df_series: List[DataFrame], bounds: GeoPointBounds) -> None:
        self.station_df_series = station_df_series
        self.bounds = bounds


def import_station_data() -> StationData:
    # Init NOAA client
    token = "QuhilYMtyPaXXgylTKUwWMUypPOqZZja"
    noaa = NOAA(token)

    data_type_id = "TAVG"

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

    start_date = datetime.now() - timedelta(days=60)
    df = None
    for station in stations:
        station_id = station["id"]
        try:
            new_df = DataFrame(noaa.data("GHCND", start_date, data_type_id=data_type_id, station_id=station_id))
            new_df["longitude"] = station["longitude"]
            new_df["latitude"] = station["latitude"]
            if df is None:
                df = new_df
            else:
                df = df.append(new_df)

        except Exception as err:
            logging.warning(f"Failed to get data for station id {station_id}: {err}")

    df.sort_values(by=['date'], inplace=True)

    logging.info(f"Obtained data for {len(df.station.unique())} stations")

    # Create bounding box for the data retrieved
    lon_series = df['longitude']
    lat_series = df['latitude']
    lim_lat = (lat_series.min(), lat_series.max())
    lim_lon = (lon_series.min(), lon_series.max())
    bounds = GeoPointBounds(lim_lat, lim_lon)

    # Split data frame into multiple data frames, one each date in the series.
    dates = df.date.unique()
    station_df_series = []
    for date in dates:
        date_df = df[df.date == date]
        if len(date_df.station.unique()) != len(date_df):
            raise Exception('Multiple data points for same date and station')
        date_df.reset_index(inplace=True)
        station_df_series.append(date_df)

    return StationData(station_df_series, bounds)

# TODO This is some code to get hold of meta data
# # plt.show()
#
# # print_json(noaa.locations_categories())
# # print_json(noaa.data_set(data_type_id=data_type_id))
#
#
# # print_json(noaa.data_categories())
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
#
