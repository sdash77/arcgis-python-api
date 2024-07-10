"""
Generates Layer Types from the given inputs.

"""

from __future__ import absolute_import
import os
from arcgis.auth.tools import LazyLoader

from urllib.parse import urlparse
from arcgis.gis import GIS
from arcgis.features.layer import (
    FeatureLayer,
    FeatureLayerCollection,
    OrientedImageryLayer,
    Table,
)
from arcgis.geocoding import Geocoder
from arcgis.geoprocessing._tool import Toolbox
from arcgis.geoprocessing import import_toolbox as _import_toolbox
from arcgis._impl.tools import _GeometryService as GeometryService
from arcgis.network import NetworkDataset
from arcgis.gis import Layer
from arcgis.layers import VectorTileLayer
from arcgis.layers import MapImageLayer, MapServiceLayer
from arcgis.raster import ImageryLayer
from arcgis.schematics import SchematicLayers
from arcgis.layers._scenelyrs import SceneLayer
from ...gis._impl._con import Connection
from ...gis.server._service._geodataservice import GeoData

_arcgis = LazyLoader("arcgis")


###########################################################################
class _FeatureServiceLayerFactory(type):
    """
    Factory that generates the Scene Layers

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    url                    Required string, specify the url ending in /SceneServer/
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS`  object. If not specified, the active GIS connection is
                           used.
    ==================     ====================================================================

    .. code-block:: python

        # USAGE EXAMPLE 1: Instantiating a SceneLayer object

        from arcgis.layers import SceneLayer
        s_layer = SceneLayer(url='https://your_portal.com/arcgis/rest/services/service_name/SceneServer/')

        type(s_layer)
        >> arcgis.layers._types.PointCloudLayer

        print(s_layer.properties.layers[0].name)
        >> 'your layer name'
    """

    def __call__(cls, url, gis=None):
        lyr = Layer(url=url, gis=gis)
        props = lyr.properties
        if props["type"] in ["Feature Layer", "Catalog Layer"]:
            return FeatureLayer(url, gis=gis)
        elif props["type"] == "Oriented Imagery Layer":
            return OrientedImageryLayer(url, gis=gis)
        elif props["type"] == "Table":
            return Table(url, gis=gis)

        return lyr


###########################################################################
class FeatureServiceLayer(Layer, metaclass=_FeatureServiceLayerFactory):
    """
    The ``SceneLayer`` class represents a Web scene layer.

    .. note::
        Web scene layers are cached web layers that are optimized for displaying a large amount of 2D and 3D features.

    .. note::
        Web scene layers can be used to represent 3D points, point clouds, 3D objects and
        integrated mesh layers.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    url                    Required string, specify the url ending in /SceneServer/
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS`  object. If not specified, the active GIS connection is
                           used.
    ==================     ====================================================================

    .. code-block:: python

        # USAGE EXAMPLE 1: Instantiating a SceneLayer object

        from arcgis.layers import SceneLayer
        s_layer = SceneLayer(url='https://your_portal.com/arcgis/rest/services/service_name/SceneServer/')

        type(s_layer)
        >> arcgis.layers._types.PointCloudLayer

        print(s_layer.properties.layers[0].name)
        >> 'your layer name'
    """

    def __init__(self, url: str, gis=None):
        """
        Constructs a SceneLayer given a web scene layer URL
        """
        super(SceneLayer, self).__init__(url, gis)


class ServiceFactory(type):
    """
    Generates a geometry object from a given set of
    JSON (dictionary or iterable)
    """

    def __call__(
        cls,
        url_or_item: _arcgis.gis.Item | str = None,
        server=None,
        initialize=False,
    ):
        """generates the proper type of layer from a given url"""
        from ...gis.server import ServicesDirectory

        url: str

        if server is None:

            server = _arcgis.env.active_gis
        hasLayer = False
        if isinstance(url_or_item, _arcgis.gis.Item):
            url = url_or_item.url
        elif isinstance(url_or_item, str):
            url = url_or_item
        else:

            raise ValueError("A URL to the service or an arcgis.Item is required.")

        if isinstance(server, Connection) or hasattr(server, "token"):
            connection = server

        elif isinstance(server, (ServicesDirectory)):
            connection = server._con
        elif isinstance(server, GIS):
            ...
        else:
            try:
                parsed = urlparse(url)
                site_url = "{scheme}://{nl}/{wa}".format(
                    scheme=parsed.scheme,
                    nl=parsed.netloc,
                    wa=parsed.path[1:].split("/")[0],
                )
                connection = Connection(baseurl=site_url)  # anonymous connection
                server = ServicesDirectory(url=site_url)
            except:
                parsed = urlparse(url)
                site_url = "https://{nl}/rest/services".format(
                    scheme=parsed.scheme, nl=parsed.netloc
                )
                connection = Connection(
                    baseurl=site_url, all_ssl=parsed.scheme == "https"
                )  # anonymous connection
                server = ServicesDirectory(url=site_url)
        base_name = os.path.basename(url)
        if base_name.isdigit():
            base_name = os.path.basename(url.replace("/" + base_name, ""))
            hasLayer = True
        if base_name.lower() == "mapserver":
            if hasLayer:
                return MapServiceLayer(url=url, gis=server)
            else:
                return MapImageLayer(url=url, gis=server)
        elif base_name.lower() == "featureserver":
            if hasLayer:
                return FeatureServiceLayer(url=url, gis=server)
            else:
                return FeatureLayerCollection(url=url, gis=server)
        elif base_name.lower() == "imageserver":
            return ImageryLayer(url=url, gis=server)
        elif base_name.lower() == "gpserver":
            from arcgis.geoprocessing import (
                import_toolbox as _import_toolbox,
            )

            res = _import_toolbox(url, server)
            return res
        elif base_name.lower() == "geometryserver":
            return GeometryService(url=url, gis=server)
        elif base_name.lower() == "mobileserver":
            return Layer(url=url, gis=server)
        elif base_name.lower() == "geocodeserver":
            return Geocoder(location=url, gis=server)
        elif base_name.lower() == "globeserver":
            if hasLayer:
                return Layer(url=url, gis=server)
            return Layer(url=url, gis=server)
        elif base_name.lower() == "geodataserver":
            return GeoData(url=url, connection=connection)
        elif base_name.lower() == "naserver":
            return NetworkDataset(url=url, gis=server)
        elif base_name.lower() == "sceneserver":
            return SceneLayer(url=url, gis=server)
        elif base_name.lower() == "schematicsserver":
            return SchematicLayers(url=url, gis=server)
        elif base_name.lower() == "vectortileserver":
            return VectorTileLayer(url=url, gis=server)
        elif base_name.find(".geojson") > -1:
            from .._ogc import GeoJSONLayer

            return GeoJSONLayer(url=url, gis=server)
        elif base_name.find(".csv") > -1:
            from .._ogc import CSVLayer

            return CSVLayer(url_or_item=url, gis=server)
        elif base_name.find(".kml") > -1 or base_name.find(".kmz") > -1:
            from .._ogc import KMLLayer

            return KMLLayer(url=url, gis=server)
        elif base_name.lower() == "ogcfeatureserver":
            from .._ogc._service import OGCFeatureService

            return OGCFeatureService(url, gis=server)
        else:
            return Layer(url=url, gis=server)
        return type.__call__(cls, url, server, initialize)


###########################################################################
class Service(object, metaclass=ServiceFactory):
    """
    The Layer class allows users to pass a url, connection or other object
    to the class and get back properties and functions specifically related
    to the service.

    Inputs:
       url - internet address to the service
       server - Server class
       item - Portal or AGOL Item class
    """

    def __init__(self, url, item=None, server=None):
        if iterable is None:
            iterable = ()
        super(Layer, self).__init__(url, item, server)
