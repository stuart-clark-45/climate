import requests
from datetime import datetime

BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"


class NOAA:
    """
    see https://www.ncdc.noaa.gov/cdo-web/webservices/v2
    """

    def __init__(self, token) -> None:
        self.token = token
        self.default_headers = {"token": self.token}

    def locations_categories(self):
        return requests.get(
            BASE_URL + "locationcategories",
            params={"limit": 1000},
            headers=self.default_headers,
        ).json()

    def locations(self, location_category_id: str = None):
        return requests.get(
            BASE_URL + "locations",
            params={"limit": 1000, "locationcategoryid": location_category_id},
            headers=self.default_headers,
        ).json()

    def stations(self, location_id=None):
        return requests.get(
            BASE_URL + "stations",
            params={"limit": 1000, "locationid": location_id},
            headers=self.default_headers,
        ).json()

    def data_set(self, data_set_id: str = None):
        url = BASE_URL + "datasets"
        if data_set_id:
            url += "/" + data_set_id
        return requests.get(
            url,
            params={"limit": 1000},
            headers=self.default_headers,
        ).json()

    def data_categories(self):
        return requests.get(
            BASE_URL + "datacategories",
            params={"limit": 1000},
            headers=self.default_headers,
        ).json()

    def data_type(self, data_type_id: str = None, data_category_id: str = None):
        url = BASE_URL + "datatypes"
        if data_type_id:
            url += "/" + data_type_id
        return requests.get(
            url,
            params={"limit": 1000, "datacategoryid": data_category_id},
            headers=self.default_headers,
        ).json()

    def data(self, data_set_id, start_date: datetime, end_date: datetime = None, data_type_id: str = None):
        if not end_date:
            end_date = datetime.now()

        return requests.get(
            BASE_URL + "data",
            params={
                "datasetid": data_set_id,
                "datatypeid": data_type_id,
                "startdate": start_date.isoformat(),
                "enddate": end_date.isoformat(),
            },
            headers=self.default_headers,
        ).json()
