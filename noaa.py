from datetime import datetime
import logging

import requests

BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"
MAX_LIMIT = 1000


# TODO need to roll out pagination over all endpoints, and also raise_for_status
class NOAA:
    """
    see https://www.ncdc.noaa.gov/cdo-web/webservices/v2
    """

    def __init__(self, token) -> None:
        self.default_headers = {"token": token}

    def locations_categories(self):
        return requests.get(
            BASE_URL + "locationcategories",
            params={"limit": MAX_LIMIT},
            headers=self.default_headers,
        ).json()

    def locations(self, location_category_id: str = None):
        return requests.get(
            BASE_URL + "locations",
            params={"limit": MAX_LIMIT, "locationcategoryid": location_category_id},
            headers=self.default_headers,
        ).json()

    def stations(self, location_id=None, data_type_id=None):
        return requests.get(
            BASE_URL + "stations",
            params={
                "limit": MAX_LIMIT,
                "locationid": location_id,
                "datatypeid": data_type_id
            },
            headers=self.default_headers,
        ).json()

    def data_set(self, data_set_id: str = None, data_type_id: str = None):
        url = BASE_URL + "datasets"
        if data_set_id:
            url += "/" + data_set_id
        return requests.get(
            url,
            params={
                "limit": MAX_LIMIT,
                'datatypeid': data_type_id
            },
            headers=self.default_headers,
        ).json()

    def data_categories(self):
        return requests.get(
            BASE_URL + "datacategories",
            params={"limit": MAX_LIMIT},
            headers=self.default_headers,
        ).json()

    def data_type(self, data_type_id: str = None, data_category_id: str = None, station_id=None):
        url = BASE_URL + "datatypes"
        if data_type_id:
            url += "/" + data_type_id
        return requests.get(
            url,
            params={
                "limit": MAX_LIMIT,
                "datacategoryid": data_category_id,
                "stationid": station_id
            },
            headers=self.default_headers,
        ).json()

    def data(self,
             data_set_id,
             start_date: datetime,
             end_date: datetime = None,
             data_type_id: str = None,
             station_id: str = None,
             pages: int = None):

        if end_date is None:
            end_date = datetime.now()

        page_count = 0
        page_limit = MAX_LIMIT
        offset = 1
        count = None
        while count is None or offset + page_limit < count:
            response = requests.get(
                BASE_URL + "data",
                params={
                    "limit": page_limit,
                    "offset": offset,
                    "datasetid": data_set_id,
                    "datatypeid": data_type_id,
                    "stationid": station_id,
                    "startdate": start_date.isoformat(),
                    "enddate": end_date.isoformat(),
                },
                headers=self.default_headers,
            )
            response.raise_for_status()

            body = response.json()

            if "metadata" not in body:
                raise Exception(f"No results found.")

            results_set = body["metadata"]["resultset"]
            offset = results_set["offset"]
            count = results_set["count"]

            logging.info(f"{min(offset + page_limit - 1, count)}/{count} data points downloaded...")

            # Just in case the limit is changed by the API
            page_limit = results_set["limit"]

            for result in body["results"]:
                yield result

            page_count += 1
            offset += page_limit
            if pages == page_count:
                return

        logging.info("Finished downloading data.")
