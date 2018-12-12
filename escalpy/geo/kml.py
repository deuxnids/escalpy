from fastkml import kml
import geopandas as gpd
import fiona

doc = file("/Users/denism/Downloads/map.geo.admin.ch_KML_20181202030734.kml").read()
k = kml.KML()
k.from_string(doc)
for feature in k.features():
    print
    feature.name

fiona.drvsupport.supported_drivers['kml'] = 'rw'  # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw'  # enable KML support which is disabled by default

gpd.read_file("/Users/denism/Downloads/map.geo.admin.ch_KML_20181202030734.kml")
