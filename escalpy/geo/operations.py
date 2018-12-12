import json
from shapely.geometry import Point
from shapely.ops import transform
from escalpy.geo.transform import mercator2wgs, mercator2ch


def waypoints2wgspoints(waypoint):
    p = Point(json.loads(waypoint['geometry']["geom"])["coordinates"])
    p = transform(mercator2wgs, p)
    return p


def waypoints2chpoint(waypoint):
    p = Point(json.loads(waypoint['geometry']["geom"])["coordinates"])
    p = transform(mercator2ch, p)
    return p


def stop2wgspoints(stop):
    x = stop["geopos"][0]
    y = stop["geopos"][1]
    p = Point(y, x)
    return p
