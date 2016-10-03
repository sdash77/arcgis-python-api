__all__ = ["gis"]
__version__ = '0.3'


#from . import _impl
from .gis import GIS

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'widgets',
        'dest': 'arcgis',
        'require': 'arcgis/mapview'
    }]

