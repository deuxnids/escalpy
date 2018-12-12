from ipyleaflet import Map, basemaps, basemap_to_tiles, Marker, DrawControl, CircleMarker, GeoJSON
from ipywidgets import HTML, Layout
from escalpy.geo.transform import ch2wgs, wgs2ch
from shapely.ops import transform
from shapely.geometry import Point
import copy


def create_dummy():
    tiles = basemaps.NASAGIBS.ModisTerraTrueColorCR
    tiles[
        "url"] = 'https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe-winter/default/current/3857/{z}/{x}/{y}.png'
    tiles["url"] = 'https://wmts20.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg'
    tiles["attribution"] = "swissgeo"
    tiles["max_zoom"] = 50

    return tiles


def draw_map(routes):
    tiles = create_dummy()
    m = Map(
        layers=(basemap_to_tiles(tiles, "2017-04-08"),),
        zoom=12, layout=Layout(width='100%', height='600px')
    )

    tiles30 = create_dummy()
    tiles30[
        "url"] = 'https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.hangneigung-ueber_30/default/current/3857/{z}/{x}/{y}.png'
    tiles["opacity"] = .0
    layer = basemap_to_tiles(tiles30, "adad")

    layer.opacity = 0.2
    m.add_layer(layer)

    tiles30 = create_dummy()
    tiles30[
        "url"] = 'https://wmts.geo.admin.ch/1.0.0/ch.swisstopo-karto.skitouren/default/current/3857/{z}/{x}/{y}.png'
    tiles["opacity"] = .0
    layer = basemap_to_tiles(tiles30, "adad")

    layer.opacity = 0.9
    m.add_layer(layer)



    # layer = ipyl.GeoJSON(data=geojson, hover_style={'fillColor': 'red'})

    # def hover_handler(event=None, id=None, properties=None):
    #    label.value = properties['geounit']

    # layer.on_hover(hover_handler)
    draw_control = DrawControl()
    draw_control.polyline = {
        "shapeOptions": {
            "color": "#6bc2e5",
            "weight": 8,
            "opacity": 1.0
        }
    }
    draw_control.polygon = {
        "shapeOptions": {
            "fillColor": "#6be5c3",
            "color": "#6be5c3",
            "fillOpacity": 1.0
        },
        "drawError": {
            "color": "#dd253b",
            "message": "Oups!"
        },
        "allowIntersection": False
    }
    draw_control.circle = {
        "shapeOptions": {
            "fillColor": "#efed69",
            "color": "#efed69",
            "fillOpacity": 1.0
        }
    }
    draw_control.rectangle = {
        "shapeOptions": {
            "fillColor": "#fca45d",
            "color": "#fca45d",
            "fillOpacity": 1.0
        }
    }

    def on_draw(x, geo_json, action):
        route = routes[0]
        cs_ch = []
        for ps in geo_json["geometry"]["coordinates"]:
            p = Point(ps[0], ps[1])
            p = transform(wgs2ch, p)
            cs_ch.append([p.x, p.y])

        geo_json["geometry"]["coordinates"] = cs_ch

        route.geo_path = geo_json

    draw_control.on_draw(on_draw)

    m.add_control(draw_control)

    for route in routes:

        if route.geo_path is not None:
            geo_json = copy.deepcopy(route.geo_path)
            cs_ch = []
            for ps in geo_json["geometry"]["coordinates"]:
                p = Point(ps[0], ps[1])
                p = transform(ch2wgs, p)
                cs_ch.append([p.x, p.y])

            geo_json["geometry"]["coordinates"] = cs_ch

            geo_json = GeoJSON(data=geo_json)
            m.add_layer(geo_json)

        points = []
        labels = []
        points += [transform(ch2wgs, w.point) for w in route.get_waypoints()]
        labels += [route.get_name() for p in route.get_waypoints()]
        for p, label in zip(points, labels):
            marker = CircleMarker()
            marker.location = (p.y, p.x)
            marker.color = "blue"
            marker.title = label

            m.add_layer(marker)

        points = []
        labels = []
        points += [transform(ch2wgs, stop.point) for stop in route.get_pt_stops()]
        labels += [route.get_name() for p in route.get_pt_stops()]
        for p, label in zip(points, labels):
            marker = CircleMarker()
            marker.location = (p.y, p.x)
            marker.color = "red"
            marker.title = label

            m.add_layer(marker)
    p = points[0]
    m.center = (p.y, p.x)
    return m
