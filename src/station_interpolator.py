from typing import List

from pandas import DataFrame
from scipy.optimize import basinhopping

from src.model.data.station_interpolator_params import StationInterpolatorParams
from src.model.geo_point import GeoPoint


class StationInterpolator:

    def __init__(self, params: StationInterpolatorParams = None) -> None:
        if not params:
            params = StationInterpolatorParams.objects.first()
        self.params = params

    # TODO this is pretty inefficient because of the use of DataFrame.iterrows()
    # TODO https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    def interpolate_station_data(self, station_df: DataFrame, samples_df: DataFrame):
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

                if distance < self.params.threshold:
                    neighbourhood.append({"distance": distance, "value": station["value"]})

            # Select at most the three closest neighbours
            neighbourhood.sort(key=lambda x: x["distance"])
            neighbourhood = neighbourhood[:self.params.neighbourhood_size]
            # Make sure the sample has a neighborhood
            if not len(neighbourhood):
                raise Exception("Increase threshold at least one sample has no neighbours")

            # Calculate the inverse distance weighted value
            sum_distance = sum(map(lambda n: n["value"], neighbourhood))
            interpolated_value = 0.0
            for neighbour in neighbourhood:
                modifier = sum_distance / neighbour["distance"] ** self.params.distance_exponent
                interpolated_value += neighbour["value"] * modifier

            sample_values.append(interpolated_value)

        # Modify the samples data frame
        samples_df["value"] = sample_values

    @staticmethod
    def optimise_params(station_dfs: List[DataFrame]):
        # TODO actually optimise params
        params = StationInterpolatorParams.objects.first()

        if params:
            params.delete()
        else:
            params = StationInterpolatorParams(threshold=250, neighbourhood_size=3, distance_exponent=2)

        args = {"station_dfs": station_dfs}
        result = basinhopping(StationInterpolator.objective_function,
                              params.to_list(),
                              minimizer_kwargs={"args": args},
                              disp=True)

        params.save()

        print(result)

    @staticmethod
    def objective_function(values_list: List[float], args: dict):
        """
        :param values_list:
        :param args: args["station_dfs"] is a list of station_dfs usually there will be a data frame per unit time for example the
                            the data frame could represent the
        :return:
        """

        print('objective_function(..) hit')

        station_dfs: List[DataFrame] = args["station_dfs"]

        params = StationInterpolatorParams().set_from_list(values_list)
        interpolator = StationInterpolator(params)

        total_error = 0.0
        counter = 0

        # Iterate over each of the station data frames
        for station_df in station_dfs:

            # For each station in the data frame
            for i in range(len(station_df)):
                # Deep copy the station data
                copied_df = station_df.copy()

                # Select a station
                selected_station = copied_df.iloc[i]
                actual_value = selected_station["value"]

                # Removed the selected station from copied_df
                copied_df.drop(i, inplace=True)

                # Run the interpolator
                samples = DataFrame([selected_station])
                interpolator.interpolate_station_data(copied_df, samples)

                # Check to see how accurate the interpolated value is
                interpolated_value = samples.iloc[0]["value"]
                total_error += abs(actual_value - interpolated_value)
                counter += 1

        return total_error / counter
