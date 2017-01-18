"""
Generates Layer Types from the given inputs.

"""
from __future__ import absolute_import
import os
from six import add_metaclass

from ._featureservice import FeatureService
from ._featureservice import FeatureLayer, TableLayer, RasterLayer, GroupLayer
from ._mapservice import MapService
#from .geoprocessing import GPService
#from ._geocodeservice import GeocodeService
from ._geodataservice import GeoData
from ._geometry import GeometryService
from ._globeservice import Globe, GlobeLayer
from ._imageservice import ImageService

from ._mobileservice import MobileService
from ._networkservice import NetworkService
from ._sceneservice import Scene
from ._schematicservice import Schematics
from ._vectortile import VectorTile
class LayerFactory(type):
    """
    Generates a geometry object from a given set of
    JSON (dictionary or iterable)
    """
    def __call__(cls,
                 connection=None,
                 url=None,
                 item=None,
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
                return FeatureLayer(url=url,
                                   connection=connection,
                                   initialize=initialize)
            else:
                return MapService(url=url,
                              connection=connection,
                              initialize=initialize)
        #elif base_name.lower() == "featureserver":
            #if hasLayer:
                #return FeatureLayer(item=item, url=url,
                                   #connection=connection,
                                   #initialize=initialize)
            #else:
                #return FeatureService(item=item, url=url,
                                   #connection=connection,
                                   #initialize=initialize)
        elif base_name.lower() == "imageserver":
            return ImageService(url=url,
                                connection=connection,
                                initialize=initialize)
        #elif base_name.lower() == "gpserver":
            #return GPService(item=item, url=url,
                             #connection=connection,
                             #initialize=initialize)
        elif base_name.lower() == "geometryserver":
            return GeometryService(url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "mobileserver":
            return MobileService(url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "geocodeserver":
            return GeocodeService(url=url,
                             connection=connection,
                             initialize=initialize)
        elif base_name.lower() == "globeserver":
            if hasLayer:
                return GlobeLayer( url=url,
                             connection=connection,
                             initialize=initialize)
            return Globe( url=url,
                          connection=connection,
                          initialize=initialize)
        elif base_name.lower() == "geodataserver":
            return GeoData(url=url,
                           connection=connection,
                           initialize=initialize)
        elif base_name.lower() == "naserver":
            return NetworkService(url=url,
                                  connection=connection,
                                  initialize=initialize)
        elif base_name.lower() == "sceneserver":
            return Scene(url=url,
                         connection=connection,
                         initialize=initialize)
        elif base_name.lower() == "schematicsserver":
            return Schematics( url=url,
                               connection=connection,
                               initialize=initialize)
        elif base_name.lower() == "vectortileserver":
            return VectorTile( url=url,
                              connection=connection,
                              initialize=initialize)
        else:
            return None
        return type.__call__(cls, url, connection, item, gis, initialize)
###########################################################################
@add_metaclass(LayerFactory)
class Layer(object):
    """
    The Layer class allows users to pass a url, connection or other object
    to the class and get back properties and functions specifically related
    to the service.

    Inputs:
       url - internet address to the service
       connection - connection object that performs the GET and POST calls
       item - Portal or AGOL Item class
       initialize - states if you want to pre-load the service's properties

    Anonymous Example:
       >>> con = ServerConnection()
       >>> service = Layer(
       url="https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/GPServer",
       connection=con)
       >>> print (type(service))
       'GPService'
       >>> service = Layer(
        url="https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer",
        connection=con)
       >>> print (type(service))
       MapService
    """
    def __init__(self, url, connection=None, item=None, initialize=False):
        if iterable is None:
            iterable = ()
        super(Layer, self).__init__(url, connection, item, initialize)