from datetime import datetime

import requests

BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"
MAX_LIMIT = 1000


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
            params={"limit": MAX_LIMIT},
            headers=self.default_headers,
        ).json()

    def locations(self, location_category_id: str = None):
        return requests.get(
            BASE_URL + "locations",
            params={"limit": MAX_LIMIT, "locationcategoryid": location_category_id},
            headers=self.default_headers,
        ).json()

    def stations(self, location_id=None):
        return requests.get(
            BASE_URL + "stations",
            params={"limit": MAX_LIMIT, "locationid": location_id},
            headers=self.default_headers,
        ).json()

    def data_set(self, data_set_id: str = None):
        url = BASE_URL + "datasets"
        if data_set_id:
            url += "/" + data_set_id
        return requests.get(
            url,
            params={"limit": MAX_LIMIT},
            headers=self.default_headers,
        ).json()

    def data_categories(self):
        return requests.get(
            BASE_URL + "datacategories",
            params={"limit": MAX_LIMIT},
            headers=self.default_headers,
        ).json()

    def data_type(self, data_type_id: str = None, data_category_id: str = None):
        url = BASE_URL + "datatypes"
        if data_type_id:
            url += "/" + data_type_id
        return requests.get(
            url,
            params={"limit": MAX_LIMIT, "datacategoryid": data_category_id},
            headers=self.default_headers,
        ).json()

    def data(self,
             data_set_id,
             start_date: datetime,
             end_date: datetime = None,
             data_type_id: str = None,
             pages: int = None):

        if not end_date:
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
                    "offset": 1,
                    "datasetid": data_set_id,
                    "datatypeid": data_type_id,
                    "startdate": start_date.isoformat(),
                    "enddate": end_date.isoformat(),
                },
                headers=self.default_headers,
            ).json()

            if "metadata" not in response:
                raise Exception(f"Request failed {response}")

            results_set = response["metadata"]["resultset"]
            offset = results_set["offset"]
            count = results_set["count"]
            # Just in case the limit is changed by the API
            page_limit = results_set["limit"]

            for result in response["results"]:
                yield result

            page_count += 1
            if pages == page_count:
                return
