import json
import urllib2
from escalpy.geo.transform import ch2wgs
from shapely.ops import transform
import dateparser


def get_route_weather(r):
    if len(r.get_waypoints()) == 0:
        r.weather = []
    else:

        w = r.get_waypoints()[0]
        p = transform(ch2wgs, w.point)

        api_key = r"0a3579da59da4f51f7ca483fa7ff1281"

        url = "http://api.openweathermap.org/data/2.5/forecast?lat=%i&lon=%i&APPID=%s" % (p.y, p.x, api_key)
        data = json.load(urllib2.urlopen(url))["list"]
        results = []
        days_to_fr = {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi", 5: "samedi", 6: "dimanche"}
        for d in data:
            date = dateparser.parse(d[u'dt_txt'])
            if date.hour == 9:
                icon = d["weather"][0]["icon"]
                results.append({"day": days_to_fr[date.weekday()], "icon": icon})
        r.weather = results
