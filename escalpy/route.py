from graphics.map import draw_map
from waypoint import Waypoint
import uuid


class Route:
    def __init__(self):
        self.name = None
        self.description = None
        self.waypoints = []
        self.geo_path = None
        self.duration = None
        self.pt_stops = []
        self.pt_connections = {}
        self.pt_duration = None
        self.dangers = {}
        self.uid = uuid.uuid4()
        self.c2c_data = None
        self.level = None

    def get_name(self):
        return self.name

    def get_waypoints(self, type=None):
        """
        :param type: access, summit,...
        :return:
        """
        if type is None:
            return self.waypoints
        else:
            return [w for w in self.waypoints if w.type == type]

    def get_duration(self):
        return int(self.duration)

    def set_pt_stops(self, pt_stops):
        self.pt_stops = pt_stops

    def get_pt_stops(self):
        return sorted(self.pt_stops, key=lambda x: x.distance)

    def set_connections(self, from_station, connections):
        self.pt_connections[from_station] = connections

    def get_connections(self, from_station):
        if from_station not in self.pt_connections:
            return []
        return self.pt_connections[from_station]

    def draw(self):
        m = draw_map([self])
        return m

    def get_connection(self, from_station):
        connections = self.get_connections(from_station=from_station)
        if len(connections) == 0:
            return None
        return connections[0]

    def get_pt_duration(self, from_station):
        connection = self.get_connection(from_station=from_station)
        if connection is None:
            return None

        def to_minutes(txt):
            a = txt.split("d")[1]
            b = a.split(":")
            h = int(b[0])
            m = int(b[1])
            return h * 60 + m

        return to_minutes(connection.data["duration"])

    def get_pt_stop(self):
        stops = self.get_pt_stops()
        if len(stops) == 0:
            return None
        stop = stops[0]
        return stop.name

    def get_geo_path(self):
        return self.geo_path

    def set_geo_path(self, path):
        self.geo_path = path

    def get_danger(self):
        if len(self.dangers) == 0:
            return None

        key = self.dangers.keys()[-1]
        return self.dangers[key]["dangerlevel"]

    @staticmethod
    def from_c2c(data):
        route = Route()
        route.name = data[u'locales'][0]["title_prefix"] + ": " + data[u'locales'][0]["title"]
        route.description = data["locales"][0]["description"]
        try:
            route.duration = int(data["durations"][0])
        except:
            pass

        route.height_diff_up = data["height_diff_up"]
        route.elevation_min = data["elevation_min"]
        route.elevation_max = data["elevation_max"]

        if "ski_rating" in data:
            route.level = data["ski_rating"]

        route.waypoints = [Waypoint.from_c2c(d) for d in data["associations"]["waypoints"]]
        route.uid = data["document_id"]
        route.c2c_data = data
        return route

    def to_json(self):
        pass
