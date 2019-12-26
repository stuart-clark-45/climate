import logging

from datetime import datetime, timedelta
from noaa import NOAA
from pandas import DataFrame


def import_station_data() -> DataFrame:
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

    return df





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
