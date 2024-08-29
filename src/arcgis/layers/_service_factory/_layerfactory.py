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
import requests

_arcgis = LazyLoader("arcgis")


###########################################################################
class _DataServiceUrlFactory(type):
    """
    A factory that handles URLs that endwith /data.  This would normally be Item
    urls where the Item type is not known coming from the webmap.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    url                    Required string, specify the url ending in /data
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS`  object. If not specified, the active GIS connection is
                           used.
    ==================     ====================================================================

    """

    def __call__(cls, url, gis=None):
        if hasattr(url, "url") and getattr(url, "url"):
            #  item object is given for some reason
            url = url.url
        if url.lower().endswith("/data"):
            item_url: str = url.replace("/data", "")
            resp: requests.Response = gis.session.get(
                item_url,
                params={
                    "f": "json",
                },
            )
            data: dict = resp.json()
            if data["type"] in ["KML", "KML Collection"]:
                from .._ogc import KMLLayer

                return KMLLayer(url=url, gis=gis)
            elif data["type"] in ["GeoJSON", "GeoJson"]:
                from .._ogc import GeoJSONLayer

                return GeoJSONLayer(url=url, gis=gis)
            elif data["type"] == "CSV":
                from .._ogc import CSVLayer

                return CSVLayer(url_or_item=url, gis=gis)
        else:
            raise ValueError("Invalid URL. The URL for this factory must end in /data")


###########################################################################
class DataServiceLayer(Layer, metaclass=_DataServiceUrlFactory):
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
        >> arcgis.layers.PointCloudLayer

        print(s_layer.properties.layers[0].name)
        >> 'your layer name'
    """

    def __init__(self, url: str, gis=None):
        """
        Constructs a SceneLayer given a web scene layer URL
        """
        super().__init__(url=url, gis=gis)


###########################################################################
class _FeatureServiceLayerFactory(type):
    """
    Factory that generates the Scene Layers

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    url                    Required string, specify the url ending in /FeatureServer/
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS`  object. If not specified, the active GIS connection is
                           used.
    ==================     ====================================================================

    .. code-block:: python

        # USAGE EXAMPLE 1: Instantiating a SceneLayer object

        from arcgis.layers import SceneLayer
        s_layer = FeatureServiceLayer(url='https://your_portal.com/arcgis/rest/services/service_name/FeatureServer')

        type(s_layer)
        >> arcgis.layers.PointCloudLayer

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
        >> arcgis.layers.PointCloudLayer

        print(s_layer.properties.layers[0].name)
        >> 'your layer name'
    """

    def __init__(self, url: str, gis=None):
        """
        Constructs a SceneLayer given a web scene layer URL
        """
        super(SceneLayer, self).__init__(url, gis)


def _item_properties(itemid: str, gis: "GIS") -> tuple[dict, str]:
    url: str = f"{gis.resturl}content/items/{itemid}"
    return gis.session.get(url, params={"f": "json"}).json(), url


def _layer_type_from_url(url: str):
    """Returns a tuple of the layer type and a lambda to create the layer"""
    base_name = os.path.basename(url)
    hasLayer = False
    if url.lower().find("sceneserver/layers") > -1:
        # special case for scene layers
        base_name = "sceneserver"
        hasLayer = True
    elif base_name.isdigit():
        # special case for services with a layer index
        base_name = os.path.basename(url.replace("/" + base_name, ""))
        hasLayer = True
    base_name_lower = base_name.lower()

    if base_name_lower == "mapserver":
        if hasLayer:
            return MapServiceLayer, lambda url, gis: MapServiceLayer(url=url, gis=gis)
        return MapImageLayer, lambda url, gis: MapImageLayer(url=url, gis=gis)
    if base_name_lower == "featureserver":
        if hasLayer:
            return FeatureServiceLayer, lambda url, gis: FeatureServiceLayer(
                url=url, gis=gis
            )
        return FeatureLayerCollection, lambda url, gis: FeatureLayerCollection(
            url=url, gis=gis
        )
    if base_name_lower == "imageserver":
        return ImageryLayer, lambda url, gis: ImageryLayer(url=url, gis=gis)
    if base_name_lower == "gpserver":
        from arcgis.geoprocessing import (
            import_toolbox as _import_toolbox,
        )

        return "GeoprocessingToolbox", lambda url, gis: _import_toolbox(url, gis)
    if base_name_lower == "geometryserver":
        return GeometryService, lambda url, gis: GeometryService(url=url, gis=gis)
    if base_name_lower == "geocodeserver":
        return Geocoder, lambda url, gis: Geocoder(location=url, gis=gis)
    if base_name_lower == "geodataserver":
        return GeoData, lambda url, connection: GeoData(url=url, connection=connection)
    if base_name_lower == "naserver":
        return NetworkDataset, lambda url, gis: NetworkDataset(url=url, gis=gis)
    if base_name_lower == "sceneserver":
        return SceneLayer, lambda url, gis: SceneLayer(url=url, gis=gis)
    if base_name_lower == "schematicsserver":
        return SchematicLayers, lambda url, gis: SchematicLayers(url=url, gis=gis)
    if base_name_lower == "vectortileserver":
        return VectorTileLayer, lambda url, gis: VectorTileLayer(url=url, gis=gis)
    if base_name.find(".geojson") > -1:
        from .._ogc import GeoJSONLayer

        return GeoJSONLayer, lambda url, gis: GeoJSONLayer(url=url, gis=gis)
    if base_name.find(".csv") > -1:
        from .._ogc import CSVLayer

        return CSVLayer, lambda url, gis: CSVLayer(url_or_item=url, gis=gis)
    if base_name.find(".kml") > -1 or base_name.find(".kmz") > -1:
        from .._ogc import KMLLayer

        return KMLLayer, lambda url, gis: KMLLayer(url=url, gis=gis)
    if base_name_lower == "ogcfeatureserver":
        from .._ogc._service import OGCFeatureService

        return OGCFeatureService, lambda url, gis: OGCFeatureService(url, gis=gis)
    if base_name_lower == "data":
        return DataServiceLayer, lambda url, gis: DataServiceLayer(url=url, gis=gis)
    if base_name_lower == "wmts":
        from .._ogc import WMTSLayer

        return WMTSLayer, lambda url, gis: WMTSLayer(url=url, gis=gis)
    # GlobeServer and MobileServer use generic Layer
    # Fall back to Layer for all other services
    return Layer, lambda url, gis: Layer(url=url, gis=gis)


def _get_url_for_item(item_url: str, item_props: dict):
    if item_props["type"] not in [
        "KML",
        "KML Collection",
        "CSV",
        "GeoJSON",
        "GeoJson",
    ]:
        raise ValueError(
            "Item type not supported, must be KML, KML Collection, CSV, or GeoJSON"
        )
    if not item_url.endswith("/data"):
        item_url = item_url + "/data"
    return item_url


def _get_url_from_item(item: _arcgis.gis.Item, gis: _arcgis.gis.GIS) -> str:
    props: dict
    item_url: str
    props, item_url = _item_properties(item.id, gis=gis)
    return _get_url_for_item(item_url, props)


class ServiceFactory(type):
    """
    Generates a Service object for a given url and
    item configuration
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
        server = server or _arcgis.env.active_gis
        if isinstance(url_or_item, _arcgis.gis.Item):
            url = _get_url_from_item(url_or_item, gis=server)
        elif isinstance(url_or_item, str):
            url = url_or_item
        else:
            raise ValueError("A URL to the service or an arcgis.Item is required.")
        parsed_url = urlparse(url)

        _, layer_lambda = _layer_type_from_url(url)
        # GeoData is a legacy edge case that needs a Connection instead of GIS
        if _ == GeoData:
            if isinstance(server, Connection) or hasattr(server, "token"):
                connection = server
            elif isinstance(server, (ServicesDirectory)):
                connection = server._con
            elif isinstance(server, GIS):
                ...
            else:
                try:
                    site_url = "{scheme}://{nl}/{wa}".format(
                        scheme=parsed_url.scheme,
                        nl=parsed_url.netloc,
                        wa=parsed_url.path[1:].split("/")[0],
                    )
                    connection = Connection(baseurl=site_url)  # anonymous connection
                    server = ServicesDirectory(url=site_url)
                except:
                    site_url = "https://{nl}/rest/services".format(
                        scheme=parsed_url.scheme, nl=parsed_url.netloc
                    )
                    connection = Connection(
                        baseurl=site_url, all_ssl=parsed_url.scheme == "https"
                    )  # anonymous connection
                    server = ServicesDirectory(url=site_url)
            return layer_lambda(url, connection)
        return layer_lambda(url, server)


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
