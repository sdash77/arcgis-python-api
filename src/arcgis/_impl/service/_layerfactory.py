"""
Generates Layer Types from the given inputs.

"""
from __future__ import absolute_import
import os
import json
from six import add_metaclass
from ._featureservice import FeatureService, FeatureLayer, TableLayer, TiledService
from .geoprocessing import GPService
from ._geocodeservice import GeocodeService
from ._geodataservice import GeoDataService
from ._geometry import GeometryService
from ._globeservice import GlobeService, GlobeServiceLayer
from ._imageservice import ImageService
from ._mapservice import MapService
from ._mobileservice import MobileService
from ._networkservice import NetworkService
from ._sceneservice import SceneService
from ._schematicservice import SchematicsService
from ._vectortile import VectorTileService
class LayerFactory(type):
    """
    Generates a geometry object from a given set of
    JSON (dictionary or iterable)
    """
    def __call__(cls, url, connection=None,
                 item=None, gis=None,
                 initialize=False):
        """generates the proper type of layer from a given url"""
        hasLayer = False
        if url is None:
            url = item.url
        base_name = os.path.basename(url)
        if base_name.isdigit():
            base_name = os.path.basename(url.replace("/" +base_name, ""))
            hasLayer = True
        if base_name.lower() == "mapserver":
            if hasLayer:
                return FeatureLayer(item=item, gis=gis, url=url,
                                   connection=connection,
                                   initialize=initialize)
            else:
                return MapService(item=item, gis=gis, url=url,
                                   connection=connection,
                                   initialize=initialize)
        elif base_name.lower() == "featureserver":
            if hasLayer:
                return FeatureLayer(item=item, gis=gis, url=url,
                                   connection=connection,
                                   initialize=initialize)
            else:
                return FeatureService(item=item, gis=gis, url=url,
                                   connection=connection,
                                   initialize=initialize)
        elif base_name.lower() == "imageserver":
            return ImageService(item=item, gis=gis, url=url,
                                connection=connection,
                                initialize=initialize)
        elif base_name.lower() == "gpserver":
            return GPService(item=item, gis=gis, url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "geometryserver":
            return GeometryService(item=item, gis=gis, url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "mobileserver":
            return MobileService(item=item, gis=gis, url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "geocodeserver":
            return GeocodeService(item=item, gis=gis, url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "globeserver":
            if hasLayer:
                return GlobeServiceLayer(item=item, gis=gis, url=url,
                             connection=connection,
                             initialize=initialize)
            return GlobeService(item=item, gis=gis, url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "geodataserver":
            return GeoDataService(item=item, gis=gis, url=url,
                                  connection=connection,
                                  initialize=initialize)
        elif base_name.lower() == "naserver":
            return NetworkService(item=item, gis=gis, url=url,
                                  connection=connection,
                                  initialize=initialize)
        elif base_name.lower() == "sceneserver":
            return SceneService(item=item, gis=gis, url=url,
                                  connection=connection,
                                  initialize=initialize)
        elif base_name.lower() == "schematicsserver":
            return SchematicsService(item=item, gis=gis, url=url,
                                  connection=connection,
                                  initialize=initialize)
        elif base_name.lower() == "vectortileserver":
            return VectorTileService(item=item, gis=gis, url=url,
                                     connection=connection,
                                     initialize=initialize)
        else:
            print 'not implemented'
            print url, base_name, hasLayer
            return None
        print 'stop'
        return type.__call__(cls,  url, connection, item, gis, initialize)
###########################################################################
@add_metaclass(LayerFactory)
class Layer(object):
    def __init__(self, url, connection=None, item=None, gis=None, initialize=False):
        if iterable is None:
            iterable = ()
        super(Layer, self).__init__( url, connection, item, gis, initialize)
        self.update(kwargs)