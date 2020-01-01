from pandas import DataFrame

from src.model.station_interpolator_params import StationInterpolatorParams
from src.geo_point import GeoPoint


class StationInterpolator:

    def __init__(self) -> None:
        self.optimise_params()

    # TODO this is pretty inefficient because of the use of DataFrame.iterrows()
    # TODO https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    def interpolate_station_data(
            self,
            station_df: DataFrame,
            samples_df: DataFrame):

        params = StationInterpolatorParams.objects.first()

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

                if distance < params.threshold:
                    neighbourhood.append({"distance": distance, "value": station["value"]})

            # Select at most the three closest neighbours
            neighbourhood.sort(key=lambda x: x["distance"])
            neighbourhood = neighbourhood[:params.neighbourhood_size]

            # Make sure the sample has a neighborhood
            if not len(neighbourhood):
                raise Exception("Increase threshold at least one sample has no neighbours")

            # Calculate the inverse distance weighted value
            sum_distance = sum(map(lambda n: n["value"], neighbourhood))
            interpolated_value = 0.0
            for neighbour in neighbourhood:
                modifier = sum_distance / neighbour["distance"] ** params.distance_exponent
                interpolated_value += neighbour["value"] * modifier

            sample_values.append(interpolated_value)

        # Modify the samples data frame
        samples_df["value"] = sample_values

    def optimise_params(self):
        params = StationInterpolatorParams.objects.first()
        if params:
            params.delete()

        StationInterpolatorParams(threshold=250, neighbourhood_size=3, distance_exponent=2).save()
