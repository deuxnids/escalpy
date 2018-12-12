from shapely.geometry import Point
from shapely.ops import transform
from escalpy.geo.transform import ch2mercator
import json
import urllib2
import urllib
import logging


class Camptocamp:
    def __init__(self):
        pass

    def get_route(self, data):
        route_id = data["document_id"]
        url = "https://api.camptocamp.org/routes/" + str(route_id)
        return json.load(urllib2.urlopen(url))

    def get_routes(self, bbox, activity="skitouring"):
        logging.info("Start fetching routes for %s" % activity)
        bbox = self.get_wgs_bbox(bbox)
        total = 1
        n = 0
        routes = []
        while n < total:
            url = "https://api.camptocamp.org/routes?bbox=" + urllib.quote_plus(bbox) + "&act=%s&pl=fr&offset=%i" % (
                activity, n)
            _routes = json.load(urllib2.urlopen(url))
            total = _routes["total"]
            n += len(_routes["documents"])
            routes += _routes["documents"]
        logging.info("Done fetching routes for %s" % activity)
        return routes

    def get_wgs_bbox(self, bbox):
        points = []
        for p in bbox:
            points.append(transform(ch2mercator, Point(p[0], p[1])))

        poly = [min([p.x for p in points]),
                min([p.y for p in points]),
                max([p.x for p in points]),
                max([p.y for p in points])]
        bbox = ",".join(map(str, map(int, poly)))
        return bbox
