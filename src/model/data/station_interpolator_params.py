from typing import List

from mongoengine import Document, LongField, IntField


class StationInterpolatorParams(Document):
    # TODO actual doc string linking
    """
    Collection used to store parameters used by the StationInterpolator
    """
    threshold = LongField(required=True)
    neighbourhood_size = IntField(required=True)
    distance_exponent = LongField(required=True)

    def to_list(self) -> List[float]:
        return [self.threshold, self.neighbourhood_size, self.distance_exponent]

    def set_from_list(self, value_list: List[float]) -> "StationInterpolatorParams":
        self.threshold = value_list[0]
        self.neighbourhood_size = int(value_list[1])
        self.distance_exponent = value_list[2]
        return self
