from shapely.ops import transform
from geo.transform import wgs2ch
from shapely.geometry import Point


class Stop:
    def __init__(self):
        self.point = None
        self.name = None
        self.distance = None

    def __repr__(self):
        return self.name

    @staticmethod
    def from_sbb(data):
        stop = Stop()

        stop.name = data["dst_bezeichnung_offiziell"]

        x = data["geopos"][0]
        y = data["geopos"][1]
        p = Point(y, x)
        stop.point = transform(wgs2ch, p)
        return stop


class Connection:
    def __init__(self, data=None):
        self.data = data
        self.duration = 0

    def get_duration(self):
        return self.data["duration"]
