__version__ = '1.2.0'

from . import features, geoanalytics, geocoding, geometry, geoprocessing, network, raster, realtime, schematics, mapping

from .gis import GIS

from .geocoding import geocode

__all__ = ['GIS', 'geocode', 'features',  'geoanalytics', 'geocoding', 'geometry', 'geoprocessing', 'network', 'raster',
           'realtime', 'schematics', 'mapping']

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'widgets',
        'dest': 'arcgis',
        'require': 'arcgis/mapview'
    }]

