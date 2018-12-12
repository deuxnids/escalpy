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
        data["pt_connections"] = [w.data for w in object.get_connections("Bern")]
        print(object.get_connections("Bern"))
        data["geojson"] = object.geo_path
        # data["danger"] = object.dangers

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

    elif isinstance(object, Route):
        object.name = data["name"]
        object.description = data["description"]
        object.waypoints = [from_json(w, Waypoint()) for w in data["waypoints"]]
        object.pt_stops = [from_json(s, Stop()) for s in data["pt_stops"]]
        if "pt_connections" in data:
            object.pt_connections["Bern"] = [Connection(d) for d in data["pt_connections"]]
        if "geojson" in data:
            object.geo_path = data["geojson"]
        # data["danger"] = object.dangers

    return object


def to_firebase(escalpy, user, pw, config):
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    user = auth.sign_in_with_email_and_password(user, pw)
    auth.get_account_info(user['idToken'])
    db = firebase.database()
    db.child("outings").remove(user['idToken'])
    data = []
    for route in escalpy.routes:
        data.append(to_json(route))
    db.child("outings").set(data, user['idToken'])


def from_firebase(user, pw, config):
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    user = auth.sign_in_with_email_and_password(user, pw)
    auth.get_account_info(user['idToken'])
    db = firebase.database()
    data = db.child("outings").get(user['idToken']).val()
    routes = []
    for d in data:
        route = Route()
        route = from_json(d, route)
        routes.append(route)
    return routes
