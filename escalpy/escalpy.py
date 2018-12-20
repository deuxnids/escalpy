from api.camptocamp import Camptocamp
from api.transport import Transport
from api.mailchimp import Mailchimp
from pt import Stop
from api.firebase import to_firebase, from_firebase
from api.weather import get_route_weather
from api.firebase import to_json, from_json

from shapely.ops import nearest_points
from route import Route
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import logging
from api.slf import SLF
import sys
import numpy as np
import pyrebase


def start_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


class Escalpy:
    def __init__(self, mailchimp, activity="skitouring"):
        """
        acts = ["skitouring", "mountain_climbing", "rock_climbing"]
        """
        self.routes = []
        self.c2c = Camptocamp()
        self.transport = Transport()
        self.mailchimp = Mailchimp(mailchimp["key"], mailchimp["usr"])
        self.slf = SLF()
        self.activity = activity

        self.stations_df = None

    def save_to_firebase(self, config, user, pw):
        to_firebase(self, user=user, pw=pw, config=config)

    def load_from_firebase(self, config, user, pw, n=None):
        self.routes = from_firebase(user=user, pw=pw, config=config, n=n)

    def fetch_routes(self, n=-1):
        bbox = [
            [2554732.4, 1188200.8],
            [2664894.8, 1209773.1],
            [2661453.5, 1088834.6],
            [2547806.3, 1082701.6]]

        _routes = self.c2c.get_routes(bbox, activity=self.activity)
        routes = []
        try:
            for _route in _routes[:n]:
                data, url = self.c2c.get_route(_route)
                route = Route.from_c2c(data)
                route.c2c_url = url
                logging.info(route.get_name())
                routes.append(route)
        except Exception as e:
            logging.info(e)
            self.routes = routes
        self.routes = routes

    def search_pt_stops(self):
        for route in self.routes:
            _pt_stops = []
            waypoints = route.get_waypoints("access")
            if len(waypoints) == 0:
                waypoints = route.get_waypoints()

            for access in waypoints:
                pt_stop = self.nearest_pt_stop(access.point)
                stop = Stop.from_sbb(pt_stop)
                distance = access.point.distance(stop.point) / 10.0
                stop.distance = distance
                _pt_stops.append(stop)

            txt = ",".join(map(lambda x: x.name.encode("ascii", "ignore"), _pt_stops))
            logging.info(route.get_name() + ": %s" % txt)
            route.set_pt_stops(_pt_stops)

    def search_connections(self, from_station):
        pt_stops = []

        for route in self.routes:
            for pt_stop in route.get_pt_stops():
                pt_stops.append(pt_stop.name)
        pt_stops = {k: None for k in set(pt_stops)}
        for pt_stop_name in pt_stops.keys():
            logging.info(pt_stop_name)
            cs = self.transport.get_connections(from_station=from_station, to_station=pt_stop_name)
            pt_stops[pt_stop_name] = cs

        for route in self.routes:
            connections = []
            for pt_stop in route.get_pt_stops():
                connections += pt_stops[pt_stop.name]
            route.set_connections(from_station=from_station, connections=connections)

    def nearest_pt_stop(self, point):
        pts = self.stations_df.geometry.unary_union
        # find the nearest point and return the corresponding Place value
        nearest = self.stations_df.geometry == nearest_points(point, pts)[1]
        return self.stations_df[nearest].iloc[0]

    def fetch_stops(self):
        if self.stations_df is None:
            stations = self.transport.get_all_stations()
            stations_df = pd.DataFrame.from_dict([r["fields"] for r in stations["records"]])

            stations_df = stations_df[stations_df.koordx < 300000]
            stations_df['Coordinates'] = list(zip(stations_df.koordy, stations_df.koordx))
            stations_df['Coordinates'] = stations_df['Coordinates'].apply(Point)
            stations_df = gpd.GeoDataFrame(stations_df, geometry='Coordinates')

            stations_df.crs = {'init': 'EPSG:21781'}
            stations_df = stations_df.to_crs({'init': 'EPSG:2056'})

            self.stations_df = stations_df

    def assign_weather(self, route):
        get_route_weather(route)

    def assign_avalanche(self, route):
        waypoints = route.get_waypoints("summit")
        if len(waypoints) == 0:
            waypoints = route.get_waypoints()

        if len(waypoints) > 0:
            waypoint = waypoints[0]
            p = waypoint.point
            danger = self.slf.get_danger_by_coord(p.x, p.y)
            route.dangers[self.slf.date] = danger

    def update_conditions(self, config, user, pw):
        firebase = pyrebase.initialize_app(config)
        auth = firebase.auth()

        user = auth.sign_in_with_email_and_password(user, pw)
        auth.get_account_info(user['idToken'])
        db = firebase.database()

        self.slf = SLF()

        for route_id in db.child("outings").shallow().get().each():
            data = db.child("outings/" + route_id).get(user['idToken']).val()
            route = Route()
            route = from_json(data, route)

            self.assign_avalanche(route)
            self.assign_weather(route)

            data = to_json(route)
            db.child("outings/" + route_id).update(data, user['idToken'])
            logging.info("%s processed" % route_id)

    def get_df(self, from_station):
        data = []
        for route in self.routes:
            # danger = None
            # if len(route.get_waypoints("summit")) > 0:
            #     waypoint = route.get_waypoints("summit")[0]
            #     p = waypoints2chpoint(waypoint)
            #     danger = self.slf.get_danger_by_coord(p.x, p.y)

            _data = [
                route.get_name(),
                route.get_pt_stop(),
                route.get_pt_duration(from_station=from_station),
                route.height_diff_up,
                route.elevation_min,
                route.elevation_max,
                route.get_danger(),
            ]

            data.append(_data)

        return pd.DataFrame(data, columns=["title", "pt_stop", "pt_duration",
                                           "height_diff_up", "elevation_min", "elevation_max",
                                           "danger"])

    def get_route(self, name):
        for route in self.routes:
            if route.get_name() == name:
                return route

    def send_emails(self):
        listname = "Escalp"
        template = "escalp_weekly"

        list_id = self.mailchimp.get_list_id(listname)

        members = []
        for m in self.mailchimp.client.lists.members.all(list_id=list_id)["members"]:
            members.append(m)

        user_data = {}
        for m in members:
            r_data = []
            for r in np.random.choice(self.routes, 2):
                link = 'http://www.nest-or.ch/outings/view/' + str(r.uid)
                txt = r.description
                title = r.name
                r_data.append({"link": link, "txt": txt, "title": title})
            user_data[m["email_address"]] = r_data

        self.mailchimp.update_member(data=user_data, list_id=list_id)
        self.mailchimp.send_emails(listname=listname, template=template)
