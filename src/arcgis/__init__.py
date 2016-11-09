__version__ = '0.3'

from . import features, geoanalytics, geocoding, geometry, geoprocessing, network, raster, realtime, schematics, mapping

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'widgets',
        'dest': 'arcgis',
        'require': 'arcgis/mapview'
    }]

