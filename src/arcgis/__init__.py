__version__ = '0.3'

from .gis import GIS

from . import features, geoanalytics, geocoding, geometry, geoprocessing, network, raster, realtime, schematics, mapping

__all__ = ['GIS']

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'widgets',
        'dest': 'arcgis',
        'require': 'arcgis/mapview'
    }]

