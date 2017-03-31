__version__ = '1.2.0'

from . import features, geoanalytics, geocoding, geometry, geoprocessing, network, raster, realtime, schematics, mapping
from . import server
from .data.geodataset import SpatialDataFrame, GeoSeries
from .data.geodataset import SpatialDataFrame, GeoSeries

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'widgets',
        'dest': 'arcgis',
        'require': 'arcgis/mapview'
    }]

