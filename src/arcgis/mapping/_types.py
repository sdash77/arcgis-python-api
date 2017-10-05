from __future__ import absolute_import

import collections
import json
import logging
import os
import tempfile
from contextlib import contextmanager
from re import search

import arcgis.features
import arcgis.gis
from arcgis._impl.common._mixins import PropertyMap
from arcgis.geometry import SpatialReference, Polygon
from arcgis.gis import Layer, _GISResource

_log = logging.getLogger(__name__)


@contextmanager
def _tempinput(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write((bytes(data, 'UTF-8')))
    temp.close()
    yield temp.name
    os.unlink(temp.name)

class SceneLayer(Layer):
    """
    The SceneSerice is represents a 3D service published on server.
    """
    def __init__(self, url, gis=None):
        """
        Constructs a feature layer given a feature layer URL
        :param url: feature layer url
        :param gis: optional, the GIS that this layer belongs to. Required for secure feature layers.
        """
        super(SceneLayer, self).__init__(url, gis)

class WebMap(collections.OrderedDict):
    """
    Represents a webmap and provides access to it's basemaps and operational layers as well
    as functionality to visualize and interact with them.
    http://resources.arcgis.com/en/help/arcgis-web-map-json/index.html#/Web_map_format_overview/02qt00000007000000/
    """

    def __init__(self, webmapitem):
        """
        Constructs a Webmap object given it's item from ArcGIS Online or Portal.
        """
        if webmapitem.type.lower() != 'web map':
            raise TypeError("item type must be web map")
        self.item = webmapitem
        self._gis = webmapitem._gis
        self._con = self._gis._con
        webmapdict = self.item.get_data()
        collections.OrderedDict.__init__(self, webmapdict)
        # dict.update(webmapdict)

    # def _repr_html_(self):
    def _ipython_display_(self, **kwargs):
        from arcgis.widgets import MapView
        # return '<iframe width=960 height=600 src="'+self.item._portal.url  + "/home/webmap/viewer.html?webmap=" + self.item.itemid + '"/>'
        mapwidget = MapView(gis=self._gis, item=self.item)
        return mapwidget._ipython_display_(**kwargs)

    def __repr__(self):
        return 'WebMap at ' + self.item._portal.url  + "/home/webmap/viewer.html?webmap=" + self.item.itemid

    def __str__(self):
        return json.dumps(self)

    def update(self):
        # with _tempinput(self.__str__()) as tempfilename:
        self.item.update({'text': self.__str__()})


class WebScene(collections.OrderedDict):
    """
    Represents a web scene and provides access to it's basemaps and operational layers as well
    as functionality to visualize and interact with them.
    """

    def __init__(self, websceneitem):
        """
        Constructs a WebScene object given it's item from ArcGIS Online or Portal.
        """
        if websceneitem.type.lower() != 'web scene':
            raise TypeError("item type must be web scene")
        self.item = websceneitem
        webscenedict = self.item.get_data()
        collections.OrderedDict.__init__(self, webscenedict)

    def _repr_html_(self):
        return '<iframe width=960 height=600 src="' + "https://www.arcgis.com/home/webscene/viewer.html?webscene=" + self.item.itemid + '"/>'

    def __repr__(self):
        return 'WebScene at ' + self.item._portal.url  + "/home/webscene/viewer.html?webscene=" + self.item.itemid

    def __str__(self):
        return json.dumps(self)

    def update(self):
        # with _tempinput(self.__str__()) as tempfilename:
        self.item.update({'text': self.__str__()})


class VectorTileLayer(Layer):

    def __init__(self, url, gis=None):
        super(VectorTileLayer, self).__init__(url, gis)

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Vector Tile Service':
            raise TypeError("item must be a type of Vector Tile Service, not " + item.type)

        return cls(item.url, item._gis)

    @property
    def styles(self):
        url = "{url}/styles".format(url=self._url)
        params = {"f": "json"}
        return self._con.get(path=url, params=params, token=self._token)

    # ----------------------------------------------------------------------
    def tile_fonts(self, fontstack, stack_range):
        """This resource returns glyphs in PBF format. The template url for
        this fonts resource is represented in Vector Tile Style resource."""
        url = "{url}/resources/fonts/{fontstack}/{stack_range}.pbf".format(
            url=self._url,
            fontstack=fontstack,
            stack_range=stack_range)
        params = {}
        return self._con.get(path=url,
                             params=params, force_bytes=True, token=self._token)

    # ----------------------------------------------------------------------
    def vector_tile(self, level, row, column):
        """This resource represents a single vector tile for the map. The
        bytes for the tile at the specified level, row and column are
        returned in PBF format. If a tile is not found, an error is returned."""
        url = "{url}/tile/{level}/{row}/{column}.pbf".format(url=self._url,
                                                             level=level,
                                                             row=row,
                                                             column=column)
        params = {}
        return self._con.get(path=url,
                             params=params, try_json=False, force_bytes=True, token=self._token)

    # ----------------------------------------------------------------------
    def tile_sprite(self, out_format="sprite.json"):
        """
        This resource returns sprite image and metadata
        """
        url = "{url}/resources/sprites/{f}".format(url=self._url,
                                                   f=out_format)
        return self._con.get(path=url,
                             params={}, token=self._token)

    # ----------------------------------------------------------------------
    @property
    def info(self):
        """This returns relative paths to a list of resource files"""
        url = "{url}/resources/info".format(url=self._url)
        params = {"f": "json"}
        return self._con.get(path=url,
                             params=params, token=self._token)


class MapImageLayerManager(_GISResource):
    """ allows administration (if access permits) of ArcGIS Online hosted map image layers.
    A map image layer offers access to map and layer content.
    """

    def __init__(self, url, gis=None, map_img_lyr=None):
        super(MapImageLayerManager, self).__init__(url, gis)
        self._ms = map_img_lyr

    # ----------------------------------------------------------------------
    def refresh(self, service_definition=True):
        """
        The refresh operation refreshes a service, which clears the web
        server cache for the service.
        """
        url = self._url + "/MapServer/refresh"
        params = {
            "f": "json",
            "serviceDefinition": service_definition
        }

        res = self._con.post(self._url, params)

        super(MapImageLayerManager, self)._refresh()

        self._ms._refresh()

        return res

    # ----------------------------------------------------------------------
    def cancel_job(self, job_id):
        """
        The cancel job operation supports cancelling a job while update
        tiles is running from a hosted feature service. The result of this
        operation is a response indicating success or failure with error
        code and description.

        Inputs:
           job_id - job id to cancel
        """
        url = self._url + "/jobs/%s/cancel" % job_id
        params = {
            "f": "json"
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def job_statistics(self, job_id):
        """
        Returns the job statistics for the given jobId

        """
        url = self._url + "/jobs/%s" % job_id
        params = {
            "f": "json"
        }
        return self._con._post(url, params)
    #----------------------------------------------------------------------
    def update_tiles(self, levels=None, extent=None):
        """
        The starts tile generation for ArcGIS Online.  The levels of detail
        and the extent are provided to determine the area where tiles need
        to be rebuilt.


        ..Note: This operation is for ArcGIS Online only.

        ===============     ====================================================
        **Argument**        **Description**
        ---------------     ----------------------------------------------------
        levels              Optional string, The level of details to update
                            example: "1,2,10,20"
        ---------------     ----------------------------------------------------
        extent              Optional string, the area to update as Xmin, YMin, XMax, YMax
                            example: "-100,-50,200,500"
        ===============     ====================================================

        :returns:
           Dictionary. If the product is not ArcGIS Online tile service, the
           result will be None.
        """
        if self._gis._portal.is_arcgisonline:
            url = "%s/updateTiles" % self._url
            params = {
                "f" : "json"
            }
            if levels:
                params['levels'] = levels
            if extent:
                params['extent'] = extent
            return self._con.post(url, params)
        return None
    #----------------------------------------------------------------------
    @property
    def rerun_job(self, job_id, code):
        """
        The rerun job operation supports re-running a canceled job from a
        hosted map service. The result of this operation is a response
        indicating success or failure with error code and description.

        ===============     ====================================================
        **Argument**        **Description**
        ---------------     ----------------------------------------------------
        code                required string, parameter used to re-run a given
                            jobs with a specific error
                            code: ALL | ERROR | CANCELED
        ---------------     ----------------------------------------------------
        job_id              required string, job to reprocess
        ===============     ====================================================

        :returns:
           boolean or dictionary
        """
        url = self._url + "/jobs/%s/rerun" % job_id
        params = {
            "f" : "json",
            "rerun": code
        }
        return self._con._post(url, params)
    # ----------------------------------------------------------------------
    def edit_tile_service(self,
                          service_definition=None,
                          min_scale=None,
                          max_scale=None,
                          source_item_id=None,
                          export_tiles_allowed=False,
                          max_export_tile_count=100000):
        """
        This operation updates a Tile Service's properties

        Inputs:
           service_definition - updates a service definition
           min_scale - sets the services minimum scale for caching
           max_scale - sets the service's maximum scale for caching
           source_item_id - The Source Item ID is the GeoWarehouse Item ID of the map service
           export_tiles_allowed - sets the value to let users export tiles
           max_export_tile_count - sets the maximum amount of tiles to be exported
             from a single call.
        """
        params = {
            "f": "json",
        }
        if not service_definition is None:
            params["serviceDefinition"] = service_definition
        if not min_scale is None:
            params['minScale'] = float(min_scale)
        if not max_scale is None:
            params['maxScale'] = float(max_scale)
        if not source_item_id is None:
            params["sourceItemId"] = source_item_id
        if not export_tiles_allowed is None:
            params["exportTilesAllowed"] = export_tiles_allowed
        if not max_export_tile_count is None:
            params["maxExportTileCount"] = int(max_export_tile_count)
        url = self._url + "/edit"
        return self._con.post(url, params)
    #----------------------------------------------------------------------
    def delete_tiles(self, levels, extent=None ):
        """
        Deletes tiles for the current cache

        ===============     ====================================================
        **Argument**        **Description**
        ---------------     ----------------------------------------------------
        extent              optional dictionary,  If specified, the tiles within
                            this extent will be deleted or will be deleted based
                            on the service's full extent.
                            Example:
                            6224324.092137296,487347.5253569535,
                            11473407.698535524,4239488.369818687
                            the minx, miny, maxx, maxy values or,
                            {"xmin":6224324.092137296,"ymin":487347.5253569535,
                            "xmax":11473407.698535524,"ymax":4239488.369818687,
                            "spatialReference":{"wkid":102100}} the JSON
                            representation of the Extent object.
        ---------------     ----------------------------------------------------
        levels              required string, The level to delete.
                            Example, 0-5,10,11-20 or 1,2,3 or 0-5
        ===============     ====================================================

        :returns:
           dictionary
        """
        params = {
            "f" : "json",
            "levels" : levels,
        }
        if extent:
            params['extent'] = extent
        url = self._url + "/deleteTiles"
        return self._con.post(url, params)



class MapImageLayer(Layer):
    """
    MapImageLayer allows you to display and analyze data from sublayers defined in a map service, exporting images
    instead of features. Map service images are dynamically generated on the server based on a request, which includes
    an LOD (level of detail), a bounding box, dpi, spatial reference and other options. The exported image is of the
    entire map extent specified.

    MapImageLayer does not display tiled images. To display tiled map service layers, see TileLayer.
    """

    def __init__(self, url, gis=None):
        """
        .. Creates a map image layer given a URL. The URL will typically look like the following.

            https://<hostname>/arcgis/rest/services/<service-name>/MapServer

        :param url: the layer location
        :param gis: the GIS to which this layer belongs
        """
        super(MapImageLayer, self).__init__(url, gis)

        self._populate_layers()
        self._admin = None
        try:
            from arcgis.gis.server._service._adminfactory import AdminServiceGen
            self.service = AdminServiceGen(service=self, gis=gis)
        except: pass

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Map Service':
            raise TypeError("item must be a type of Map Service, not " + item.type)
        return cls(item.url, item._gis)

    def _populate_layers(self):
        layers = []
        tables = []

        for lyr in self.properties.layers:
            if 'subLayerIds' in lyr and lyr.subLayerIds is not None: # Group Layer
                lyr = Layer(self.url + '/' + str(lyr.id), self._gis)
            else:
                lyr = arcgis.features.FeatureLayer(self.url + '/' + str(lyr.id), self._gis, self)
            layers.append(lyr)

        for lyr in self.properties.tables:
            lyr = arcgis.features.Table(self.url + '/' + str(lyr.id), self._gis, self)
            tables.append(lyr)

        # fsurl = self.url + '/layers'
        # params = { "f" : "json" }
        # allayers = self._con.post(fsurl, params, token=self._token)

        # for layer in allayers['layers']:
        #    layers.append(FeatureLayer(self.url + '/' + str(layer['id']), self._gis))

        # for table in allayers['tables']:
        #    tables.append(FeatureLayer(self.url + '/' + str(table['id']), self._gis))

        self.layers = layers
        self.tables = tables

    @property
    def manager(self):
        if self._admin is None:
            """accesses the administration service"""
            url = self._url
            res = search("/rest/", url).span()
            addText = "admin/"
            part1 = url[:res[1]]
            part2 = url[res[1]:]
            adminURL = url.replace("/rest/", "/admin/").replace("/MapServer", ".MapServer")#"%s%s%s" % (part1, addText, part2)

            self._admin = MapImageLayerManager(adminURL, self._gis, self)
        return self._admin

    #----------------------------------------------------------------------
    def create_dynamic_layer(self, layer):
        """
        A dynamic layer / table method represents a single layer / table
        of a map service published by ArcGIS Server or of a registered
        workspace. This resource is supported only when the map image layer
        supports dynamic layers, as indicated by supportsDynamicLayers on
        the map image layer properties.

        =================     ====================================================================
        **Argument**          **Description**
        -----------------     --------------------------------------------------------------------
        layer                 required dict.  Dynamic layer/table source definition.
                              Syntax:
                              {
                                "id": <layerOrTableId>,
                                "source": <layer source>, //required
                                "definitionExpression": "<definitionExpression>",
                                "drawingInfo":
                                {
                                  "renderer": <renderer>,
                                  "transparency": <transparency>,
                                  "scaleSymbols": <true,false>,
                                  "showLabels": <true,false>,
                                  "labelingInfo": <labeling info>
                                },
                                "layerTimeOptions": //supported only for time enabled map layers
                                {
                                  "useTime" : <true,false>,
                                  "timeDataCumulative" : <true,false>,
                                  "timeOffset" : <timeOffset>,
                                  "timeOffsetUnits" : "<esriTimeUnitsCenturies,esriTimeUnitsDays,
                                                    esriTimeUnitsDecades,esriTimeUnitsHours,
                                                    esriTimeUnitsMilliseconds,esriTimeUnitsMinutes,
                                                    esriTimeUnitsMonths,esriTimeUnitsSeconds,
                                                    esriTimeUnitsWeeks,esriTimeUnitsYears |
                                                    esriTimeUnitsUnknown>"
                                }
                              }
        =================     ====================================================================

        :returns: arcgis.features.FeatureLayer or None (if not enabled)

        """
        if "supportsDynamicLayers" in self.properties and \
           self.properties["supportsDynamicLayers"]:
            from urllib.parse import urlencode
            url = "%s/dynamicLayer" % self._url
            d = urlencode(layer)
            url += "?layer=%s" % d
            return arcgis.features.FeatureLayer(url=url, gis=self._gis, dynamic_layer=layer)
        return None
    # ----------------------------------------------------------------------
    @property
    def kml(self):
        """returns the KML file for the layer"""
        url = "{url}/kml/mapImage.kmz".format(url=self._url)
        return self._con.get(url, {"f": 'json'},
                             file_name="mapImage.kmz",
                             out_folder=tempfile.gettempdir(), token=self._token)

    # ----------------------------------------------------------------------
    @property
    def item_info(self):
        """returns the service's item's infomation"""
        url = "{url}/info/iteminfo".format(url=self._url)
        params = {"f": "json"}
        return self._con.get(url, params, token=self._token)

    #----------------------------------------------------------------------
    @property
    def legend(self):
        """
        The legend resource represents a map service's legend. It returns
        the legend information for all layers in the service. Each layer's
        legend information includes the symbol images and labels for each
        symbol. Each symbol is an image of size 20 x 20 pixels at 96 DPI.
        Additional information for each layer such as the layer ID, name,
        and min and max scales are also included.

        The legend symbols include the base64 encoded imageData as well as
        a url that could be used to retrieve the image from the server.
        """
        url = "%s/legend" % self._url
        return self._con.get(path=url, params={'f': 'json'})

    # ----------------------------------------------------------------------
    @property
    def metadata(self):
        """returns the service's XML metadata file"""
        url = "{url}/info/metadata".format(url=self._url)
        params = {"f": "json"}
        return self._con.get(url, params, token=self._token)

    # ----------------------------------------------------------------------
    def thumbnail(self, out_path=None):
        """if present, this operation will download the image to local disk"""
        if out_path is None:
            out_path = tempfile.gettempdir()
        url = "{url}/info/thumbnail".format(url=self._url)
        params = {"f": "json"}
        if out_path is None:
            out_path = tempfile.gettempdir()
        return self._con.get(url,
                             params,
                             out_folder=out_path,
                             file_name="thumbnail.png", token=self._token)

    # ----------------------------------------------------------------------
    def identify(self,
                 geometry,
                 map_extent,
                 image_display,
                 geometry_type="Point",
                 sr=None,
                 layer_defs=None,
                 time_value=None,
                 time_options=None,
                 layers="all",
                 tolerance=None,
                 return_geometry=True,
                 max_offset=None,
                 precision=4,
                 dynamic_layers=None,
                 return_z=False,
                 return_m=False,
                 gdb_version=None,
                 return_unformatted=False,
                 return_field_name=False,
                 transformations=None,
                 map_range_values=None,
                 layer_range_values=None,
                 layer_parameters=None,
                 **kwargs):

        """
        The identify operation is performed on a map service resource
        to discover features at a geographic location. The result of this
        operation is an identify results resource. Each identified result
        includes its name, layer ID, layer name, geometry and geometry type,
        and other attributes of that result as name-value pairs.

        ==================    ====================================================================
        **Argument**          **Description**
        ------------------    --------------------------------------------------------------------
        geometry              required Geometry or list. The geometry to identify on. The type of
                              the geometry is specified by the geometryType parameter. The
                              structure of the geometries is same as the structure of the JSON
                              geometry objects returned by the API. In addition to the JSON
                              structures, for points and envelopes, you can specify the geometries
                              with a simpler comma-separated syntax.
        ------------------    --------------------------------------------------------------------
        geometry_type         required string.The type of geometry specified by the geometry
                              parameter. The geometry type could be a point, line, polygon, or an
                              envelope.
                              Values: Point,Multipoint,Polyline,Polygon,Envelope
        ------------------    --------------------------------------------------------------------
        sr                    optional dict, string, or SpatialReference. The well-known ID of the
                              spatial reference of the input and output geometries as well as the
                              map_extent. If sr is not specified, the geometry and the map_extent
                              are assumed to be in the spatial reference of the map, and the
                              output geometries are also in the spatial reference of the map.
        ------------------    --------------------------------------------------------------------
        layer_defs            optional dict. Allows you to filter the features of individual
                              layers in the exported map by specifying definition expressions for
                              those layers. Definition expression for a layer that is
                              published with the service will be always honored.
        ------------------    --------------------------------------------------------------------
        time_value            optional list. The time instant or the time extent of the features
                              to be identified.
        ------------------    --------------------------------------------------------------------
        time_options          optional dict. The time options per layer. Users can indicate
                              whether or not the layer should use the time extent specified by the
                              time parameter or not, whether to draw the layer features
                              cumulatively or not and the time offsets for the layer.
        ------------------    --------------------------------------------------------------------
        layers                optional string. The layers to perform the identify operation on.
                              There are three ways to specify which layers to identify on:
                               - top: Only the top-most layer at the specified location.
                               - visible: All visible layers at the specified location.
                               - all: All layers at the specified location.
        ------------------    --------------------------------------------------------------------
        tolerance             optional integer. The distance in screen pixels from the specified
                              geometry within which the identify should be performed. The value for
                              the tolerance is an integer.
        ------------------    --------------------------------------------------------------------
        map_extent            required string. The extent or bounding box of the map currently
                              being viewed.
        ------------------    --------------------------------------------------------------------
        image_display         optional string. The screen image display parameters (width, height,
                              and DPI) of the map being currently viewed. The mapExtent and the
                              image_display parameters are used by the server to determine the
                              layers visible in the current extent. They are also used to
                              calculate the distance on the map to search based on the tolerance
                              in screen pixels.
                              Syntax: <width>, <height>, <dpi>
        ------------------    --------------------------------------------------------------------
        return_geometry       optional boolean. If true, the resultset will include the geometries
                              associated with each result. The default is true.
        ------------------    --------------------------------------------------------------------
        max_offset            optional integer. This option can be used to specify the maximum
                              allowable offset to be used for generalizing geometries returned by
                              the identify operation.
        ------------------    --------------------------------------------------------------------
        precision             optional integer. This option can be used to specify the number of
                              decimal places in the response geometries returned by the identify
                              operation. This applies to X and Y values only (not m or z-values).
        ------------------    --------------------------------------------------------------------
        dynamic_layers        optional dict. Use dynamicLayers property to reorder layers and
                              change the layer data source. dynamicLayers can also be used to add
                              new layer that was not defined in the map used to create the map
                              service. The new layer should have its source pointing to one of the
                              registered workspaces that was defined at the time the map service
                              was created.
                              The order of dynamicLayers array defines the layer drawing order.
                              The first element of the dynamicLayers is stacked on top of all
                              other layers. When defining a dynamic layer, source is required.
        ------------------    --------------------------------------------------------------------
        return_z              optional boolean. If true, Z values will be included in the results
                              if the features have Z values. Otherwise, Z values are not returned.
                              The default is false.
        ------------------    --------------------------------------------------------------------
        return_m              optional boolean.If true, M values will be included in the results
                              if the features have M values. Otherwise, M values are not returned.
                              The default is false.
        ------------------    --------------------------------------------------------------------
        gdb_version           optional string. Switch map layers to point to an alternate
                              geodatabase version.
        ------------------    --------------------------------------------------------------------
        return_unformatted    optional boolean. If true, the values in the result will not be
                              formatted i.e. numbers will returned as is and dates will be
                              returned as epoch values. The default is False.
        ------------------    --------------------------------------------------------------------
        return_field_name     optional boolean. Default is False. If true, field names will be
                              returned instead of field aliases.
        ------------------    --------------------------------------------------------------------
        transformations       optional list. Use this parameter to apply one or more datum
                              transformations to the map when sr is different than the map
                              service's spatial reference. It is an array of transformation
                              elements.
                              Transformations specified here are used to project features from
                              layers within a map service to sr.
        ------------------    --------------------------------------------------------------------
        map_range_values      optional list. Allows for the filtering features in the exported map
                              from all layer that are within the specified range instant or extent.
        ------------------    --------------------------------------------------------------------
        layer_range_values    optional list. Allows for the filtering of features for each
                              individual layer that are within the specified range instant or
                              extent.
        ------------------    --------------------------------------------------------------------
        layer_parameters      optional list. Allows for the filtering of the features of
                              individual layers in the exported map by specifying value(s) to an
                              array of pre-authored parameterized filters for those layers. When
                              value is not specified for any parameter in a request, the default
                              value, that is assigned during authoring time, gets used instead.
        ==================    ====================================================================

        :returns: dictionary
        """

        if geometry_type.find("esriGeometry") == -1:
            geometry_type = "esriGeometry" + geometry_type
        if sr is None:
            sr = kwargs.pop('sr', None)
        if layer_defs is None:
            layer_defs = kwargs.pop('layerDefs', None)
        if time_value is None:
            time_value = kwargs.pop('layerTimeOptions', None)
        if return_geometry is None:
            return_geometry = kwargs.pop('returnGeometry', True)
        if return_m is None:
            return_m = kwargs.pop('returnM', False)
        if return_z is None:
            return_z = kwargs.pop('returnZ', False)
        if max_offset is None:
            max_offset = kwargs.pop('maxAllowableOffset', None)
        if precision is None:
            precision = kwargs.pop('geometryPrecision', None)
        if dynamic_layers is None:
            dynamic_layers = kwargs.pop('dynamicLayers', None)
        if gdb_version is None:
            gdb_version = kwargs.pop('gdbVersion', None)

        params = {'f': 'json',
                  'geometry': geometry,
                  'geometryType': geometry_type,
                  'tolerance': tolerance,
                  'mapExtent': map_extent,
                  'imageDisplay': image_display
                  }
        if sr:
            params['sr'] = sr
        if layer_defs:
            params['layerDefs'] = layer_defs
        if time_value:
            params['time'] = time_value
        if time_options:
            params['layerTimeOptions'] = time_options
        if layers:
            params['layers'] = layers
        if tolerance:
            params['tolerance'] = tolerance
        if return_geometry is not None:
            params['returnGeometry'] = return_geometry
        if max_offset:
            params['maxAllowableOffset'] = max_offset
        if precision:
            params['geometryPrecision'] = precision
        if dynamic_layers:
            params['dynamicLayers'] = dynamic_layers
        if return_m is not None:
            params['returnM'] = return_m
        if return_z is not None:
            params['returnZ'] = return_z
        if gdb_version:
            params['gdbVersion'] = gdb_version
        if return_unformatted is not None:
            params['returnUnformattedValues'] = return_unformatted
        if return_field_name is not None:
            params['returnFieldName'] = return_field_name
        if transformations:
            params['datumTransformations'] = transformations
        if map_range_values:
            params['mapRangeValues'] = map_range_values
        if layer_range_values:
            params['layerRangeValues'] = layer_range_values
        if layer_parameters:
            params['layerParameterValues'] = layer_parameters
        identifyURL = "{url}/identify".format(url=self._url)
        return self._con.post(identifyURL, params, token=self._token)

    # ----------------------------------------------------------------------
    def find(self,
             search_text,
             layers,
             contains=True,
             search_fields=None,
             sr=None,
             layer_defs=None,
             return_geometry=True,
             max_offset=None,
             precision=None,
             dynamic_layers=None,
             return_z=False,
             return_m=False,
             gdb_version=None):
        """
        performs the map service find operation

        =================     ====================================================================
        **Argument**          **Description**
        -----------------     --------------------------------------------------------------------
        search_text           required string.The search string. This is the text that is searched
                              across the layers and fields the user specifies.
        -----------------     --------------------------------------------------------------------
        layers                optional string. The layers to perform the identify operation on.
                              There are three ways to specify which layers to identify on:
                               - top: Only the top-most layer at the specified location.
                               - visible: All visible layers at the specified location.
                               - all: All layers at the specified location.
        -----------------     --------------------------------------------------------------------
        contains              optional boolean. If false, the operation searches for an exact
                              match of the search_text string. An exact match is case sensitive.
                              Otherwise, it searches for a value that contains the search_text
                              provided. This search is not case sensitive. The default is true.
        -----------------     --------------------------------------------------------------------
        search_fields         optional string. List of field names to look in.
        -----------------     --------------------------------------------------------------------
        sr                    optional dict, string, or SpatialReference. The well-known ID of the
                              spatial reference of the input and output geometries as well as the
                              map_extent. If sr is not specified, the geometry and the map_extent
                              are assumed to be in the spatial reference of the map, and the
                              output geometries are also in the spatial reference of the map.
        -----------------     --------------------------------------------------------------------
        layer_defs            optional dict. Allows you to filter the features of individual
                              layers in the exported map by specifying definition expressions for
                              those layers. Definition expression for a layer that is
                              published with the service will be always honored.
        -----------------     --------------------------------------------------------------------
        return_geometry       optional boolean. If true, the resultset will include the geometries
                              associated with each result. The default is true.
        -----------------     --------------------------------------------------------------------
        max_offset            optional integer. This option can be used to specify the maximum
                              allowable offset to be used for generalizing geometries returned by
                              the identify operation.
        -----------------     --------------------------------------------------------------------
        precision             optional integer. This option can be used to specify the number of
                              decimal places in the response geometries returned by the identify
                              operation. This applies to X and Y values only (not m or z-values).
        -----------------     --------------------------------------------------------------------
        dynamic_layers        optional dict. Use dynamicLayers property to reorder layers and
                              change the layer data source. dynamicLayers can also be used to add
                              new layer that was not defined in the map used to create the map
                              service. The new layer should have its source pointing to one of the
                              registered workspaces that was defined at the time the map service
                              was created.
                              The order of dynamicLayers array defines the layer drawing order.
                              The first element of the dynamicLayers is stacked on top of all
                              other layers. When defining a dynamic layer, source is required.
        -----------------     --------------------------------------------------------------------
        return_z              optional boolean. If true, Z values will be included in the results
                              if the features have Z values. Otherwise, Z values are not returned.
                              The default is false.
        -----------------     --------------------------------------------------------------------
        return_m              optional boolean.If true, M values will be included in the results
                              if the features have M values. Otherwise, M values are not returned.
                              The default is false.
        -----------------     --------------------------------------------------------------------
        gdb_version           optional string. Switch map layers to point to an alternate
                              geodatabase version.
        =================     ====================================================================

        :returns: dictionary
        """
        url = "{url}/find".format(url=self._url)
        params = {
            "f": "json",
            "searchText": search_text,
            "contains": contains,
        }
        if search_fields:
            params['searchFields'] = search_fields
        if sr:
            params['sr'] = sr
        if layer_defs:
            params['layerDefs'] = layer_defs
        if return_geometry is not None:
            params['returnGeometry'] = return_geometry
        if max_offset:
            params['maxAllowableOffset'] = max_offset
        if precision:
            params['geometryPrecision'] = precision
        if dynamic_layers:
            params['dynamicLayers'] = dynamic_layers
        if return_z is not None:
            params['returnZ'] = return_z
        if return_m is not None:
            params['returnM'] = return_m
        if gdb_version:
            params['gdbVersion'] = gdb_version
        if layers:
            params['layers'] = layers
        res = self._con.get(url, params, token=self._token)
        return res

    # ----------------------------------------------------------------------
    def generate_kml(self, save_location, docName, layers, layerOptions="composite"):
        """
           The generateKml operation is performed on a map service resource.
           The result of this operation is a KML document wrapped in a KMZ
           file. The document contains a network link to the KML Service
           endpoint with properties and parameters you specify.
           Inputs:
              docName - The name of the resulting KML document. This is the
                        name that appears in the Places panel of Google
                        Earth.
              layers - the layers to perform the generateKML operation on.
                       The layers are specified as a comma-separated list
                       of layer ids.
              layerOptions - The layer drawing options. Based on the option
                             chosen, the layers are drawn as one composite
                             image, as separate images, or as vectors. When
                             the KML capability is enabled, the ArcGIS
                             Server administrator has the option of setting
                             the layer operations allowed. If vectors are
                             not allowed, then the caller will not be able
                             to get vectors. Instead, the caller receives a
                             single composite image.
                             values: composite | separateImage |
                                     nonComposite
        """
        kmlURL = self._url + "/generateKml"
        params = {
            "f": "json",
            'docName': docName,
            'layers': layers,
            'layerOptions': layerOptions}
        return self._con.get(kmlURL, params,
                             out_folder=save_location, token=self._token)

    # ----------------------------------------------------------------------
    def export_map(self,
                   bbox,
                   bboxSR=None,
                   size="600,550",
                   dpi=200,
                   imageSR=None,
                   image_format="png",
                   layerDefFilter=None,
                   layers=None,
                   transparent=False,
                   timeFilter=None,
                   layerTimeOptions=None,
                   dynamicLayers=None,
                   mapScale=None
                   ):
        """
           The export operation is performed on a map service resource.
           The result of this operation is a map image resource. This
           resource provides information about the exported map image such
           as its URL, its width and height, extent and scale.
           Inputs:
            bbox - (Required) The extent (bounding box) of the exported
             image. Unless the bboxSR parameter has been specified, the bbox
             is assumed to be in the spatial reference of the map.
             Example: bbox="-104,35.6,-94.32,41"
            size - size of image in pixels
            dpi - dots per inch
            imageSR - spatial reference of the output image
            image_format - Description: The format of the exported image.
                             The default format is .png.
                             Values: png | png8 | png24 | jpg | pdf | bmp | gif
                                     | svg | svgz | emf | ps | png32
            layerDefFilter - Description: Allows you to filter the
                             features of individual layers in the exported
                             map by specifying definition expressions for
                             those layers. Definition expression for a
                             layer that is published with the service will
                             be always honored.
            layers - Determines which layers appear on the exported map.
                     There are four ways to specify which layers are shown:
                        show: Only the layers specified in this list will
                              be exported.
                        hide: All layers except those specified in this
                              list will be exported.
                        include: In addition to the layers exported by
                                 default, the layers specified in this list
                                 will be exported.
                        exclude: The layers exported by default excluding
                                 those specified in this list will be
                                 exported.
            transparent - If true, the image will be exported with the
                          background color of the map set as its
                          transparent color. The default is false. Only
                          the .png and .gif formats support transparency.
                          Internet Explorer 6 does not display transparency
                          correctly for png24 image formats.
            timeFilter - The time instant or time extent of the exported
                         map image.
            layerTimeOptions - The time options per layer. Users can
                               indicate whether or not the layer should use
                               the time extent specified by the time
                               parameter or not, whether to draw the layer
                               features cumulatively or not and the time
                               offsets for the layer.
                               see: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Export_Map/02r3000000v7000000/
            dynamicLayers - Use dynamicLayers parameter to modify the layer
                            drawing order, change layer drawing info, and
                            change layer data source version for this request.
                            New layers (dataLayer) can also be added to the
                            dynamicLayers based on the map service registered
                            workspaces.
            mapScale - Use this parameter to export a map image at a specific
                       scale, with the map centered around the center of the
                       specified bounding box (bbox).
         Output:
           Image of the map.
        """
        if self.properties['exportTilesAllowed'] == False:
            return
        params = {
            "f": "json"
        }
        params['bbox'] = bbox
        if bboxSR:
            params['bboxSR'] = bboxSR
        if dpi is not None:
            params['dpi'] = dpi
        if size is not None:
            params['size'] = size
        if imageSR is not None and \
                isinstance(imageSR, SpatialReference):
            params['imageSR'] = {'wkid': imageSR.wkid}
        if image_format is not None:
            params['format'] = image_format
        if layerDefFilter is not None:
            params['layerDefs'] = layerDefFilter
        if layers is not None:
            params['layers'] = layers
        if transparent is not None:
            params['transparent'] = transparent
        if timeFilter is not None:
            params['time'] = timeFilter
        if layerTimeOptions is not None:
            params['layerTimeOptions'] = layerTimeOptions
        if dynamicLayers is not None:
            params['dynamicLayers'] = dynamicLayers
        if mapScale is not None:
            params['mapScale'] = mapScale
        exportURL = self._url + "/export"
        return self._con.get(exportURL, params, token=self._token)

    # ----------------------------------------------------------------------
    def estimate_export_tiles_size(self,
                                   exportBy,
                                   levels,
                                   tilePackage=False,
                                   exportExtent="DEFAULTEXTENT",
                                   areaOfInterest=None,
                                   asynchronous=True):
        """
        The estimateExportTilesSize operation is an asynchronous task that
        allows estimation of the size of the tile package or the cache data
        set that you download using the Export Tiles operation. This
        operation can also be used to estimate the tile count in a tile
        package and determine if it will exceced the maxExportTileCount
        limit set by the administrator of the service. The result of this
        operation is Map Service Job. This job response contains reference
        to Map Service Result resource that returns the total size of the
        cache to be exported (in bytes) and the number of tiles that will
        be exported.

        Inputs:

        tilePackage - Allows estimating the size for either a tile package
         or a cache raster data set. Specify the value true for tile
         packages format and false for Cache Raster data set. The default
         value is False
           Values: True | False
        exportExtent - The extent (bounding box) of the tile package or the
         cache dataset to be exported. If extent does not include a spatial
         reference, the extent values are assumed to be in the spatial
         reference of the map. The default value is full extent of the
         tiled map service.
        Syntax: <xmin>, <ymin>, <xmax>, <ymax>
           Example 1: -104,35.6,-94.32,41
        exportBy - The criteria that will be used to select the tile
         service levels to export. The values can be Level IDs, cache scales
         or the Resolution (in the case of image services).
        Values: LevelID | Resolution | Scale
        levels - Specify the tiled service levels for which you want to get
         the estimates. The values should correspond to Level IDs, cache
         scales or the Resolution as specified in exportBy parameter. The
         values can be comma separated values or a range.
        Example 1: 1,2,3,4,5,6,7,8,9
        Example 2: 1-4,7-9
        areaOfInterest - (Optional) The areaOfInterest polygon allows
         exporting tiles within the specified polygon areas. This parameter
         supersedes exportExtent parameter. Also excepts geometry.Polygon.
        Example: { "features": [{"geometry":{"rings":[[[-100,35],
             [-100,45],[-90,45],[-90,35],[-100,35]]],
             "spatialReference":{"wkid":4326}}}]}
        asynchronous - (optional) the estimate function is run asynchronously
         requiring the tool status to be checked manually to force it to
         run synchronously the tool will check the status until the
         estimation completes.  The default is True, which means the status
         of the job and results need to be checked manually.  If the value
         is set to False, the function will wait until the task completes.
           Values: True | False
        """
        if self.properties['exportTilesAllowed'] == False:
            return
        import time
        url = self._url + "/estimateExportTilesSize"
        params = {
            "f": "json",
            "levels": levels,
            "exportBy": exportBy,
            "tilePackage": tilePackage,
            "exportExtent": exportExtent
        }
        params["levels"] = levels
        if not areaOfInterest is None:
            params['areaOfInterest'] = areaOfInterest
        if asynchronous == True:
            return self._con.get(url, params, token=self._token)
        else:
            exportJob = self._con.get(url, params, token=self._token)

            job_id = exportJob['jobId']
            path = "%s/jobs/%s" % (url, exportJob['jobId'])

            params = {"f": "json"}
            job_response = self._con.post(path, params, token=self._token)

            if "status" in job_response:
                status = job_response.get("status")
                while not status == "esriJobSucceeded":
                    time.sleep(5)

                    job_response = self._con.post(path, params, token=self._token)
                    status = job_response.get("status")
                    if status in ['esriJobFailed',
                                  'esriJobCancelling',
                                  'esriJobCancelled',
                                  'esriJobTimedOut']:
                        print(str(job_response['messages']))
                        raise Exception('Job Failed with status ' + status)
            else:
                raise Exception("No job results.")

            return job_response['results']

    # ----------------------------------------------------------------------
    def export_tiles(self,
                     levels,
                     exportBy="LevelID",
                     tilePackage=False,
                     exportExtent="DEFAULT",
                     optimizeTilesForSize=True,
                     compressionQuality=0,
                     areaOfInterest=None,
                     asynchronous=False
                     ):
        """
        The exportTiles operation is performed as an asynchronous task and
        allows client applications to download map tiles from a server for
        offline use. This operation is performed on a Map Service that
        allows clients to export cache tiles. The result of this operation
        is Map Service Job. This job response contains a reference to the
        Map Service Result resource, which returns a URL to the resulting
        tile package (.tpk) or a cache raster dataset.
        exportTiles can be enabled in a service by using ArcGIS for Desktop
        or the ArcGIS Server Administrator Directory. In ArcGIS for Desktop
        make an admin or publisher connection to the server, go to service
        properties, and enable Allow Clients to Export Cache Tiles in the
        advanced caching page of the Service Editor. You can also specify
        the maximum tiles clients will be allowed to download. The default
        maximum allowed tile count is 100,000. To enable this capability
        using the Administrator Directory, edit the service, and set the
        properties exportTilesAllowed=true and maxExportTilesCount=100000.

        At 10.2.2 and later versions, exportTiles is supported as an
        operation of the Map Server. The use of the
        http://Map Service/exportTiles/submitJob operation is deprecated.
        You can provide arguments to the exportTiles operation as defined
        in the following parameters table:

        Inputs:
         exportBy - The criteria that will be used to select the tile
           service levels to export. The values can be Level IDs, cache
           scales. or the resolution (in the case of image services).
        Values: LevelID | Resolution | Scale
        levels - Specifies the tiled service levels to export. The values
          should correspond to Level IDs, cache scales. or the resolution
          as specified in exportBy parameter. The values can be comma
          separated values or a range. Make sure tiles are present at the
          levels where you attempt to export tiles.
        Example 1: 1,2,3,4,5,6,7,8,9
        Example 2: 1-4,7-9
        tilePackage - Allows exporting either a tile package or a cache
          raster data set. If the value is true, output will be in tile
          package format, and if the value is false, a cache raster data
          set is returned. The default value is false
        Values: true | false
        exportExtent - The extent (bounding box) of the tile package or the
          cache dataset to be exported. If extent does not include a
          spatial reference, the extent values are assumed to be in the
          spatial reference of the map. The default value is full extent of
          the tiled map service.
                       Syntax: <xmin>, <ymin>, <xmax>, <ymax>
                       Example 1: -104,35.6,-94.32,41
                       Example 2: {"xmin" : -109.55, "ymin" : 25.76,
                        "xmax" : -86.39, "ymax" : 49.94,
                        "spatialReference" : {"wkid" : 4326}}
        optimizeTilesForSize - (Optional) Use this parameter to enable
          compression of JPEG tiles and reduce the size of the downloaded
          tile package or the cache raster data set. Compressing tiles
          slightly compromises the quality of tiles but helps reduce the
          size of the download. Try sample compressions to determine the
          optimal compression before using this feature.
        Values: true | false
        compressionQuality - (Optional) When optimizeTilesForSize=true, you
         can specify a compression factor. The value must be between 0 and
         100. The value cannot be greater than the default compression
         already set on the original tile. For example, if the default
         value is 75, the value of compressionQuality must be between 0 and
         75. A value greater than 75 in this example will attempt to up
         sample an already compressed tile and will further degrade the
         quality of tiles.
        areaOfInterest - (Optional) The areaOfInterest polygon allows
         exporting tiles within the specified polygon areas. This parameter
         supersedes the exportExtent parameter. Must be geometry.Polygon
         object.
        Example: { "features": [{"geometry":{"rings":[[[-100,35],
         [-100,45],[-90,45],[-90,35],[-100,35]]],
         "spatialReference":{"wkid":4326}}}]}
        asynchronous - default True, this value ensures the returns are returned
         to the user instead of the user having the check the job status
         manually.
        """
        import time
        params = {
            "f": "json",
            "tilePackage": tilePackage,
            "exportExtent": exportExtent,
            "optimizeTilesForSize": optimizeTilesForSize,
            "compressionQuality": compressionQuality,
            "exportBy": exportBy,
            "levels": levels
        }
        url = self._url + "/exportTiles"
        if isinstance(areaOfInterest, Polygon):
            geom = areaOfInterest.asDictionary()
            template = {"features": [geom]}
            params["areaOfInterest"] = template
        elif isinstance(areaOfInterest, dict):
            params["areaOfInterest"] = {"features": [areaOfInterest]}
        if asynchronous == True:
            return self._con.get(path=url, params=params, token=self._token)
        else:
            exportJob = self._con.get(path=url, params=params, token=self._token)

            job_id = exportJob['jobId']
            path = "%s/jobs/%s" % (url, exportJob['jobId'])

            params = {"f": "json"}
            job_response = self._con.post(path, params, token=self._token)

            if "status" in job_response:
                status = job_response.get("status")
                while not status == 'esriJobSucceeded':
                    time.sleep(5)

                    job_response = self._con.post(path, params, token=self._token)
                    status = job_response.get("status")
                    if status in ['esriJobFailed',
                                  'esriJobCancelling',
                                  'esriJobCancelled',
                                  'esriJobTimedOut']:
                        print(str(job_response['messages']))
                        raise Exception('Job Failed with status ' + status)
            else:
                raise Exception("No job results.")

            allResults = job_response['results']

            for k, v in allResults.items():
                if k == "out_service_url":
                    value = v.value
                    params = {
                        "f": "json"
                    }
                    gpRes = self._con.get(path=value, params=params, token=self._token)
                    if tilePackage == True:
                        files = []
                        for f in gpRes['files']:
                            name = f['name']
                            dlURL = f['url']
                            files.append(
                                self._con.get(dlURL, params,
                                              out_folder=tempfile.gettempdir(),
                                              file_name=name), token=self._token)
                        return files
                    else:
                        return gpRes['folders']
                else:
                    return None

