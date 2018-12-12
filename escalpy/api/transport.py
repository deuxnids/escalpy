import json
import urllib
import urllib2
from escalpy.geo.transform import ch2wgs
from pyproj import transform

from escalpy.pt import Connection


class Transport:
    def __init__(self):
        pass

    def get_station(self, point, distance=1000):
        point2 = transform(ch2wgs, point)

        url = "https://data.sbb.ch/api/records/1.0/search/?dataset=betriebspunkte-didok&rows=10000&geofilter.distance=%f,%f,%i" % (
            point2.y, point2.x, distance)
        stops = json.load(urllib2.urlopen(url))
        return stops

    def get_all_stations(self):
        url = "https://data.sbb.ch/api/records/1.0/search/?dataset=betriebspunkte-didok&rows=10000"
        stops = json.load(urllib2.urlopen(url))
        return stops

    def get_connections(self, from_station, to_station):
        from_station = urllib.quote_plus(from_station.encode('utf-8'))
        to_station = urllib.quote_plus(to_station.encode("utf-8"))
        url = r"http://transport.opendata.ch/v1/connections?from=%s&to=%s" % (from_station, to_station)
        url = url + r"&datetime=2019-02-09T06%3A00"
        print(url)
        connections = json.load(urllib2.urlopen(url))["connections"]
        return map(Connection, connections)
