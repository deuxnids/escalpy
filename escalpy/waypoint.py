from shapely.ops import transform
from geo.transform import mercator2ch
from shapely.geometry import Point
import json

TYPE_ACCESS = "access"
TYPE_SUMMIT = "summit"


class Waypoint:
    def __init__(self):
        self.type = ""
        self.name = ""
        self.point = ""

    @staticmethod
    def from_c2c(data):
        geometry = data["geometry"]
        geom = json.loads(geometry["geom"])
        x = geom["coordinates"][0]
        y = geom["coordinates"][1]
        p = Point(x, y)
        p = transform(mercator2ch, p)

        type = data["waypoint_type"]
        name = data["locales"][0]["title"]

        w = Waypoint()
        w.type = type
        w.name = name
        w.point = p
        return w
