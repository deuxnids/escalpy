from graphics.map import draw_map
from waypoint import Waypoint


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
        """
        TODO: what should we do with the list
        :return:
        """
        return int(self.data["durations"][0])

    def set_pt_stops(self, pt_stops):
        self.pt_stops = pt_stops

    def get_pt_stops(self):
        return self.pt_stops

    def set_connections(self, from_station, connections):
        self.pt_connections[from_station] = connections

    def get_connections(self, from_station):
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
        return connection.duration

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
        return self.dangers[-1]["dangerlevel"]

    @staticmethod
    def from_c2c(data):
        route = Route()
        route.name = data[u'locales'][0]["title_prefix"] + ": " + data[u'locales'][0]["title"]
        route.description = data["locales"][0]["description"]
        try:
            route.duration = int(data["durations"][0])
        except:
            pass

        route.waypoints = [Waypoint.from_c2c(d) for d in data["associations"]["waypoints"]]
        return route

    def to_json(self):
        pass

