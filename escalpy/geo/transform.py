import pyproj
from functools import partial

mercator2ch = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:3857'),
    pyproj.Proj(init='epsg:2056'))

mercator2wgs = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:3857'),
    pyproj.Proj(init='epsg:4326'))

ch2mercator = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:2056'),
    pyproj.Proj(init='epsg:3857'))

wgs2ch = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:4326'),
    pyproj.Proj(init='EPSG:2056'))

ch2wgs = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:2056'),
    pyproj.Proj(init='EPSG:4326'))
