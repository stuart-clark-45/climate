from mongoengine import Document, IntField, LongField


class StationInterpolatorParams(Document):
    threshold = LongField(required=True)
    neighbourhood_size = IntField(required=True)
    distance_exponent = LongField(required=True)
