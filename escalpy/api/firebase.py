import pyrebase
from escalpy.waypoint import Waypoint
from escalpy.pt import Stop, Connection
from escalpy.route import Route
from shapely.geometry import Point
import json


def to_json(object):
    data = {}
    if isinstance(object, Waypoint):
        data["name"] = object.name
        data["type"] = object.type
        data["x"] = object.point.x
        data["y"] = object.point.y

    elif isinstance(object, Stop):
        data["name"] = object.name
        data["distance"] = object.distance
        data["x"] = object.point.x
        data["y"] = object.point.y

    elif isinstance(object, Route):
        data["name"] = object.get_name()
        data["description"] = object.description
        data["waypoints"] = [to_json(w) for w in object.get_waypoints()]
        data["pt_stops"] = [to_json(w) for w in object.get_pt_stops()]
        data["pt_connections"] = {}
        for from_station in object.pt_connections.keys():
            data["pt_connections"][from_station] = [w.data for w in object.get_connections(from_station)]
        data["geojson"] = object.geo_path
        data["dangers"] = object.dangers

        data["height_diff_up"] = object.height_diff_up
        data["elevation_min"] = object.elevation_min
        data["elevation_max"] = object.elevation_max
        data["c2c_url"] = object.c2c_url
        data["c2c_data"] = object.c2c_data
        data["level"] = object.level
        data["weather"] = object.weather

    else:
        raise Exception("not yet implemented")

    return data


def from_json(data, object):
    if isinstance(object, Waypoint):
        object.name = data["name"]
        object.type = data["type"]
        object.point = Point(data["x"], data["y"])

    elif isinstance(object, Stop):
        object.name = data["name"]
        object.distance = data["distance"]
        object.point = Point(data["x"], data["y"])

    elif isinstance(object, Connection):
        object.data = data
        object.duration = data["duration"]

    elif isinstance(object, Route):
        object.name = data["name"]
        if "description" in data:
            object.description = data["description"]
        object.waypoints = [from_json(w, Waypoint()) for w in data["waypoints"]]
        object.pt_stops = [from_json(s, Stop()) for s in data["pt_stops"]]
        if "pt_connections" in data:
            for from_station in data["pt_connections"].keys():
                object.pt_connections[from_station] = [from_json(d, Connection()) for d in
                                                       data["pt_connections"][from_station]]
        if "geojson" in data:
            object.geo_path = data["geojson"]

        try:
            object.dangers = data["dangers"]
        except:
            object.dangers = {}
        try:
            object.height_diff_up = data["height_diff_up"]
        except:
            object.height_diff_up = None
        try:
            object.elevation_min = data["elevation_min"]
        except:
            object.elevation_min = None
        try:
            object.elevation_max = data["elevation_max"]
        except:
            object.elevation_max = None

        try:
            object.level = data["level"]
        except:
            object.level = None


        try:
            object.weather = data["weatehr"]
        except:
            object.weather = []

        object.c2c_url = data["c2c_url"]
        object.c2c_data = data["c2c_data"]

    return object


def to_firebase(escalpy, user, pw, config):
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    user = auth.sign_in_with_email_and_password(user, pw)
    auth.get_account_info(user['idToken'])
    db = firebase.database()
    # db.child("outings").remove(user['idToken'])
    data = {}
    for route in escalpy.routes:
        data[route.uid] = to_json(route)

    db.child("outings").update(data, user['idToken'])


def route_to_firebase(route, user, pw, config):
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    user = auth.sign_in_with_email_and_password(user, pw)
    auth.get_account_info(user['idToken'])
    db = firebase.database()
    data = to_json(route)
    db.child("outings/" + str(route.uid)).update(data, user['idToken'])


def from_firebase(user, pw, config):
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    user = auth.sign_in_with_email_and_password(user, pw)
    auth.get_account_info(user['idToken'])
    db = firebase.database()
    data = db.child("outings").get(user['idToken']).val()
    routes = []
    for d in data.keys():
        route = Route()
        route = from_json(data[d], route)
        route.uid = d
        routes.append(route)
    return routes
