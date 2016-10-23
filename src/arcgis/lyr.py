"""
The arcgis.lyr module is used for accessing layers exposed from ArcGIS Online
or Portal.
"""
from __future__ import absolute_import

from re import search

import arcgis.gis
from arcgis._impl.common._filters import *
from arcgis._impl.common._mixins import PropertyMap
from arcgis._impl.common._utils import _DisableLogger
from arcgis._impl.common._utils import local_time_to_online
import arcgis.features # import Table, FeatureLayer, FeatureDataset
from arcgis.geom import SpatialReference

#noinspection PyUnresolvedReferences
from six.moves.urllib.error import HTTPError

from ._impl import *

__all__ = ['GISService', 'ImageLayer', 'Layer', 'MapService', 'NetworkLayer', 'NetworkService', 'SchematicsService', 'VectorTileLayer']

_log = logging.getLogger(__name__)


class Layer(object):
    """ a GIS layer """

    def __init__(self, url, gis=None):
        self._token = None
        
        self.url = url
        self._url = url
        
        err = None

        if gis is None:
            gis = arcgis.gis.GIS()
            self._gis = gis
            self._con = gis._con
            self._token = None
        else:
            self._gis = gis
            self._con = gis._con
            with _DisableLogger():
                try:
                    # try as a federated server
                    self._token = self._con.generate_portal_server_token(url)
                    self._refresh()
                except RuntimeError as e:
                    try:
                        # try as a public server
                        self._token = None
                        self._refresh()
                    except HTTPError as httperror:
                        _log.error(httperror)
                        err = httperror
                    except RuntimeError as e:
                        if 'Token Required' in e.args[0]:
                            # try token in the provided gis
                            self._token = self._con.token
                            self._refresh()
                    """
                    if 'Unable to generate token' in e.args[0]:
                        try:
                            # try as a public server
                            self._token = None
                            self._refresh()
                        except HTTPError as httperror:
                            _log.error(httperror)
                            err = httperror
                        except RuntimeError as e:
                            if 'Token Required' in e.args[0]:
                                # try token in the provided gis
                                self._token = self._con.token
                                self._refresh()
                    elif 'invalid token' in e.args[0].lower(): # Image Services http://landsat2.arcgis.com/arcgis/rest/services/Landsat8_Views/ImageServer
                        try:
                            # try as a public server
                            self._token = None
                            self._refresh()
                        except RuntimeError as e:
                            if 'Token Required' in e.args[0]:
                                # try token in the provided gis
                                self._token = self._con.token
                                self._refresh()
                    else:
                        raise e
                    """
        if err is not None:
            raise RuntimeError('HTTPError: this service url encountered an HTTP Error: ' + self.url)

    def _refresh(self):
        params = {"f": "json"}
        dictdata = self._con.post(self.url, params, token=self._token)
        self.properties = PropertyMap(dictdata)

    def __str__(self):
        return '<%s url:"%s">' % (type(self).__name__, self.url)
    
    def __repr__(self):
        return '<%s url:"%s">' % (type(self).__name__, self.url)
    
    @property
    def _js_lyr(self):
        return { 'type' : type(self).__name__, 'url' : self.url }


    @property
    def properties(self):
        """
        Returns the properties of this layer. The properties are returned using a mutable mapping that allows attribute
        access as well as dict-style access. It can be converted to a dict using dict(properties) if required.
        """
        return self.properties

    def invoke(self, method, **kwargs):
        """Invokes the specified method on this service passing in parameters from the kwargs name-value pairs"""
        url = self._url + "/" + method
        params = { "f" : "json"}
        if len(kwargs) > 0:
            for k,v in kwargs.items():
                params[k] = v
                del k,v
        return self._con.post(path=url, postdata=params, token=self._token)

class GISService(object):
    """ a GIS service
    """
    def __init__(self, url, gis=None):
        self._token = None
        
        self.url = url
        self._url = url
        
        err = None

        if gis is None:
            gis = arcgis.gis.GIS()
            self._gis = gis
            self._con = gis._con
            self._token = None
        else:
            self._gis = gis
            self._con = gis._con
            
            with _DisableLogger():
                try:
                    # try as a federated server
                    self._token = self._con.generate_portal_server_token(url)
                    self._refresh()
                except RuntimeError as e:
                    try:
                        # try as a public server
                        self._token = None
                        self._refresh()
                    except HTTPError as httperror:
                        _log.error(httperror)
                        err = httperror
                    except RuntimeError as e:
                        if 'Token Required' in e.args[0]:
                            # try token in the provided gis
                            self._token = self._con.token
                            self._refresh()
                    """
                    if 'Unable to generate token' in e.args[0] or 'Internal Server Error' in e.args[0]:
                        try:
                            # try as a public server
                            self._token = None
                            self._refresh()
                        except HTTPError as httperror:
                            _log.error(httperror)
                            err = httperror
                        except RuntimeError as e:
                            if 'Token Required' in e.args[0]:
                                # try token in the provided gis
                                self._token = self._con.token
                                self._refresh()
                    elif 'invalid token' in e.args[0].lower(): # Image Services http://landsat2.arcgis.com/arcgis/rest/services/Landsat8_Views/ImageServer
                        try:
                            # try as a public server
                            self._token = None
                            self._refresh()
                        except RuntimeError as e:
                            if 'Token Required' in e.args[0]:
                                # try token in the provided gis
                                self._token = self._con.token
                                self._refresh()
                    else:
                        raise e
                    """
        if err is not None:
            raise RuntimeError('HTTPError: this service url encountered an HTTP Error: ' + self.url)

    def _refresh(self):
        params = {"f": "json"}
        dictdata = self._con.post(self.url, params, token=self._token)
        self.properties = PropertyMap(dictdata)
        

    @classmethod
    def fromitem(cls, item):
        if not item.type.lower().endswith('service'):
            raise TypeError("item must be a type of service, not " + item.type)
        return cls(item.url, item._gis)

    def __str__(self):
        return '<%s url:"%s">' % (type(self).__name__, self.url)
    
    def __repr__(self):
        return '<%s url:"%s">' % (type(self).__name__, self.url)

    def invoke(self, method, **kwargs):
        """Invokes the specified method on this service passing in parameters from the kwargs name-value pairs"""
        url = self._url + "/" + method
        params = { "f" : "json"}
        if len(kwargs) > 0:
            for k,v in kwargs.items():
                params[k] = v
                del k,v
        return self._con.post(path=url, postdata=params, token=self._token)

class VectorTileLayer(Layer):
    def __init__(self, url, gis=None):
        self._token = None
        
        self.url = url
        self._url = url
        
        err = None

        if gis is None:
            gis = arcgis.gis.GIS()
            self._gis = gis
            self._con = gis._con
            self._token = None
        else:
            self._gis = gis
            self._con = gis._con
            try:
                # try as a federated server
                self._token = self._con.generate_portal_server_token(url)
                self._refresh()
            except RuntimeError as e:
                if 'Unable to generate token' in e.args[0]:
                    try:
                        # try as a public server
                        self._token = None
                        self._refresh()
                    except HTTPError as httperror:
                        _log.error(httperror)
                        err = httperror
                    except RuntimeError as e:
                        if 'Token Required' in e.args[0]:
                            # try token in the provided gis
                            self._token = self._con.token
                            self._refresh()

        if err is not None:
            raise RuntimeError('HTTPError: this service url encountered an HTTP Error: ' + self.url)

    def _refresh(self):
        params = {"f": "json"}
        dictdata = self._con.get(self.url, params, token=self._token)
        self.properties = PropertyMap(dictdata)

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Vector Tile Service':
            raise TypeError("item must be a type of Vector Tile Service, not " + item.type)
        
        return cls(item.url, item._gis)

    @property
    def styles(self):
        url = "{url}/styles".format(url=self._url)
        params = {"f" : "json"}
        return self._con.get(path=url, params=params, token=self._token)
    #----------------------------------------------------------------------
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
    #----------------------------------------------------------------------
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
    #----------------------------------------------------------------------
    def tile_sprite(self, out_format="sprite.json"):
        """
        This resource returns sprite image and metadata
        """
        url = "{url}/resources/sprites/{f}".format(url=self._url,
                                                   f=out_format)
        return self._con.get(path=url,
                             params={}, token=self._token)
    #----------------------------------------------------------------------
    @property
    def info(self):
        """This returns relative paths to a list of resource files"""
        url = "{url}/resources/info".format(url=self._url)
        params = {"f" : "json"}
        return self._con.get(path=url,
                             params=params, token=self._token)

class ImageLayer(Layer):
    def __init__(self, url, gis=None):
        super(ImageLayer, self).__init__(url, gis)

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Image Service':
            raise TypeError("item must be a type of Image Service, not " + item.type)

        return cls(item.url, item._gis)

    def export_image(self,
                    bbox,
                    imageSR,
                    bboxSR,
                    size=None,
                    time=None,
                    export_format="jpgpng",
                    pixelType="UNKNOWN",
                    noData=None,
                    noDataInterpretation="esriNoDataMatchAny",
                    interpolation=None,
                    compression=None,
                    compressionQuality=75,
                    bandIds=None,
                    moasiacRule=None,
                    renderingRule="",
                    f="json",
                    saveFolder=None,
                    saveFile=None
                    ):
        """
        The exportImage operation is performed on an image service resource
        The result of this operation is an image resource. This resource
        provides information about the exported image, such as its URL,
        extent, width, and height.
        In addition to the usual response formats of HTML and JSON, you can
        also request the image format while performing this operation. When
        you perform an export with the image format , the server responds
        by directly streaming the image bytes to the client. With this
        approach, you don't get any information associated with the
        exported image other than the image itself.

        Inputs:
           bbox - The extent (bounding box) of the exported image. Unless
                  the bboxSR parameter has been specified, the bbox is
                  assumed to be in the spatial reference of the image
                  service.
           imageSR - The spatial reference of the exported image.
           bboxSR - The spatial reference of the bbox.
           size - The size (width * height) of the exported image in
                  pixels. If size is not specified, an image with a default
                  size of 400 * 400 will be exported.
           time - The time instant or the time extent of the exported image.
           export_format - The format of the exported image. The default format is
                    jpgpng.
                    Values: jpgpng | png | png8 | png24 | jpg | bmp | gif |
                            tiff | png32
           pixelType - The pixel type, also known as data type, pertains to
                       the type of values stored in the raster, such as
                       signed integer, unsigned integer, or floating point.
                       Integers are whole numbers, whereas floating points
                       have decimals.
           noDate - The pixel value representing no information.
           noDataInterpretation - Interpretation of the noData setting. The
                               default is esriNoDataMatchAny when noData is
                               a number, and esriNoDataMatchAll when noData
                               is a comma-delimited string:
                               esriNoDataMatchAny | esriNoDataMatchAll.
           interpolation - The resampling process of extrapolating the
                           pixel values while transforming the raster
                           dataset when it undergoes warping or when it
                           changes coordinate space.
           compression - Controls how to compress the image when exporting
                         to TIFF format: None, JPEG, LZ77. It does not
                         control compression on other formats.
           compressionQuality - Controls how much loss the image will be
                                subjected to by the compression algorithm.
                                Valid value ranges of compression quality
                                are from 0 to 100.
           bandIds - If there are multiple bands, you can specify a single
                     band to export, or you can change the band combination
                     (red, green, blue) by specifying the band number. Band
                     number is 0 based.
           mosaicRule - Specifies the mosaic rule when defining how
                        individual images should be mosaicked. When a mosaic
                        rule is not specified, the default mosaic rule of
                        the image service will be used (as advertised in
                        the root resource: defaultMosaicMethod,
                        mosaicOperator, sortField, sortValue).
           renderingRule - Specifies the rendering rule for how the
                           requested image should be rendered.
           f - The response format.  default is json
               Values: json | image | kmz
        """
        import datetime
        
        params = {
            "bbox" : bbox,
            "imageSR": imageSR,
            "bboxSR": bboxSR,
            "size" : "%s %s" % (size[0], size[1]),
            "pixelType" : pixelType,
            "compressionQuality" : compressionQuality,

        }
        if size is None:
            size = [400,400]
        url = self._url + "/exportImage"
        __allowedFormat = ["jpgpng", "png",
                           "png8", "png24",
                           "jpg", "bmp",
                           "gif", "tiff",
                           "png32"]
        __allowedPixelTypes = [
            "C128", "C64", "F32",
            "F64", "S16", "S32",
            "S8", "U1", "U16",
            "U2", "U32", "U4",
            "U8", "UNKNOWN"
        ]
        __allowednoDataInt = [
            "esriNoDataMatchAny",
            "esriNoDataMatchAll"
        ]
        __allowedInterpolation = [
            "RSP_BilinearInterpolation",
            "RSP_CubicConvolution",
            "RSP_Majority",
            "RSP_NearestNeighbor"
        ]
        __allowedCompression = [
            "JPEG", "LZ77"
        ]
        if isinstance(moasiacRule, dict):
            params["moasiacRule"] = moasiacRule
        if export_format in __allowedFormat:
            params['format'] = export_format
        if isinstance(time, datetime.datetime):
            params['time'] = local_time_to_online(time)
        if interpolation is not None and \
           interpolation in __allowedInterpolation and \
           isinstance(interpolation, str):
            params['interpolation'] = interpolation
        if pixelType is not None and \
           pixelType in __allowedPixelTypes:
            params['pixelType'] = pixelType
        if noDataInterpretation in __allowedInterpolation:
            params['noDataInterpretation']  = noDataInterpretation
        if noData is not None:
            params['noData'] = noData
        if compression is not None and \
           compression in __allowedCompression:
            params['compression'] = compression
        if bandIds is not None and \
           isinstance(bandIds, list):
            params['bandIds'] = ",".join(bandIds)
        if renderingRule is not None:
            params['renderingRule'] = renderingRule
        params["f" ] = f
        if f == "json":
            return self._con.get(url, params, token=self._token)
        elif f == "image":
            result = self._con.get(url, params,
                               out_folder=saveFolder,
                               file_name=saveFile, token=self._token)
            return result
        elif f == "kmz":
            return self._con.get(url, params,
                             out_folder=saveFolder,
                             file_name=saveFile, token=self._token)
    #----------------------------------------------------------------------
    def query(self,
              where="1=1",
              out_fields="*",
              timeFilter=None,
              geometryFilter=None,
              returnGeometry=True,
              returnIdsOnly=False,
              returnCountOnly=False,
              pixelSize=None,
              orderByFields=None,
              returnDistinctValues=True,
              outStatistics=None,
              groupByFieldsForStatistics=None
              ):
        """ queries a feature service based on a sql statement
            Inputs:
               where - the selection sql statement
               out_fields - the attribute fields to return
               timeFilter - a TimeFilter object where either the start time
                            or start and end time are defined to limit the
                            search results for a given time.  The values in
                            the timeFilter should be as UTC timestampes in
                            milliseconds.  No checking occurs to see if they
                            are in the right format.
               geometryFilter - a GeometryFilter object to parse down a given
                               query by another spatial dataset.
               returnGeometry - true means a geometry will be returned,
                                else just the attributes
               returnIdsOnly - false is default.  True means only OBJECTIDs
                               will be returned
               returnCountOnly - if True, then an integer is returned only
                                 based on the sql statement
               pixelSize-Query visible rasters at a given pixel size. If
                         pixelSize is not specified, rasters at all
                         resolutions can be queried.
               orderByFields-Order results by one or more field names. Use
                             ASC or DESC for ascending or descending order,
                             respectively
               returnDistinctValues-  If true, returns distinct values
                                    based on the fields specified in
                                    outFields. This parameter applies only
                                    if the supportsAdvancedQueries property
                                    of the image service is true.
               outStatistics- the definitions for one or more field-based
                              statistics to be calculated.
               groupByFieldsForStatistics-One or more field names using the
                                         values that need to be grouped for
                                         calculating the statistics.
            Output:
               A list of Feature Objects (default) or a path to the output featureclass if
               returnFeatureClass is set to True.
         """
        params = {"f": "json",
                  "where": where,
                  "outFields": out_fields,
                  "returnGeometry" : returnGeometry,
                  "returnIdsOnly" : returnIdsOnly,
                  "returnCountOnly" : returnCountOnly,
                  }
        if not groupByFieldsForStatistics is None:
            params['groupByFieldsForStatistics'] = groupByFieldsForStatistics
        if not outStatistics is None:
            params['outStatistics'] = outStatistics
        if not timeFilter is None and \
           isinstance(timeFilter, dict):
            params['time'] = timeFilter
        if not geometryFilter is None and \
           isinstance(geometryFilter, dict):
            gf = geometryFilter
            params['geometry'] = gf['geometry']
            params['geometryType'] = gf['geometryType']
            params['spatialRelationship'] = gf['spatialRel']
            params['inSR'] = gf['inSR']
        if pixelSize is not None:
            params['pixelSize'] = pixelSize
        if orderByFields is not None:
            params['orderByFields'] = orderByFields
        if returnDistinctValues is not None:
            params['returnDistinctValues'] = returnDistinctValues

        url = self._url + "/query"
        return self._con.get(url, params, token=self._token)
    #----------------------------------------------------------------------
    def add_rasters(self,
            rasterType,
            itemIds=None,
            serviceUrl=None,
            computeStatistics=False,
            buildPyramids=False,
            buildThumbnail=False,
            minimumCellSizeFactor=None,
            maximumCellSizeFactor=None,
            attributes=None,
            geodataTransforms=None,
            geodataTransformApplyMethod="esriGeodataTransformApplyAppend"
            ):
        """
        This operation is supported at 10.1 and later.
        The Add Rasters operation is performed on an image service resource.
        The Add Rasters operation adds new rasters to an image service
        (POST only).
        The added rasters can either be uploaded items, using the itemIds
        parameter, or published services, using the serviceUrl parameter.
        If itemIds is specified, uploaded rasters are copied to the image
        service's dynamic image workspace location; if the serviceUrl is
        specified, the image service adds the URL to the mosaic dataset no
        raster files are copied. The serviceUrl is required input for the
        following raster types: Image Service, Map Service, WCS, and WMS.

        Inputs:

        itemIds - The upload items (raster files) to be added. Either
         itemIds or serviceUrl is needed to perform this operation.
            Syntax: itemIds=<itemId1>,<itemId2>
            Example: itemIds=ib740c7bb-e5d0-4156-9cea-12fa7d3a472c,
                             ib740c7bb-e2d0-4106-9fea-12fa7d3a482c
        serviceUrl - The URL of the service to be added. The image service
         will add this URL to the mosaic dataset. Either itemIds or
         serviceUrl is needed to perform this operation. The service URL is
         required for the following raster types: Image Service, Map
         Service, WCS, and WMS.
            Example: serviceUrl=http://myserver/arcgis/services/Portland/ImageServer
        rasterType - The type of raster files being added. Raster types
         define the metadata and processing template for raster files to be
         added. Allowed values are listed in image service resource.
            Example: Raster Dataset | CADRG/ECRG | CIB | DTED | Image Service | Map Service | NITF | WCS | WMS
        computeStatistics - If true, statistics for the rasters will be
         computed. The default is false.
            Values: false | true
        buildPyramids - If true, builds pyramids for the rasters. The
         default is false.
                Values: false | true
        buildThumbnail	 - If true, generates a thumbnail for the rasters.
         The default is false.
                Values: false | true
        minimumCellSizeFactor - The factor (times raster resolution) used
         to populate the MinPS field (maximum cell size above which the
         raster is visible).
                Syntax: minimumCellSizeFactor=<minimumCellSizeFactor>
                Example: minimumCellSizeFactor=0.1
        maximumCellSizeFactor - The factor (times raster resolution) used
         to populate MaxPS field (maximum cell size below which raster is
         visible).
                Syntax: maximumCellSizeFactor=<maximumCellSizeFactor>
                Example: maximumCellSizeFactor=10
        attributes - Any attribute for the added rasters.
                Syntax:
                {
                  "<name1>" : <value1>,
                  "<name2>" : <value2>
                }
                Example:
                {
                  "MinPS": 0,
                  "MaxPS": 20;
                  "Year" : 2002,
                  "State" : "Florida"
                }
        geodataTransforms - The geodata transformations applied on the
         added rasters. A geodata transformation is a mathematical model
         that performs a geometric transformation on a raster; it defines
         how the pixels will be transformed when displayed or accessed.
         Polynomial, projective, identity, and other transformations are
         available. The geodata transformations are applied to the dataset
         that is added.
                Syntax:
                [
                {
                  "geodataTransform" : "<geodataTransformName1>",
                  "geodataTransformArguments" : {<geodataTransformArguments1>}
                  },
                  {
                  "geodataTransform" : "<geodataTransformName2>",
                  "geodataTransformArguments" : {<geodataTransformArguments2>}
                  }
                ]
         The syntax of the geodataTransformArguments property varies based
         on the specified geodataTransform name. See Geodata Transformations
         documentation for more details.
        geodataTransformApplyMethod - This parameter defines how to apply
         the provided geodataTransform. The default is
         esriGeodataTransformApplyAppend.
                Values: esriGeodataTransformApplyAppend |
                esriGeodataTransformApplyReplace |
                esriGeodataTransformApplyOverwrite
        """
        url = self._url + "/add"
        params = {
            "f" : "json"
        }
        if itemIds is None and serviceUrl is None:
            raise Exception("An itemId or serviceUrl must be provided")
        if isinstance(itemIds, str):
            itemIds = [itemIds]
        if isinstance(serviceUrl, str):
            serviceUrl = [serviceUrl]
        params['geodataTransformApplyMethod'] = geodataTransformApplyMethod
        params['rasterType'] = rasterType
        params['buildPyramids'] = buildPyramids
        params['buildThumbnail'] = buildThumbnail
        params['minimumCellSizeFactor'] = minimumCellSizeFactor
        params['computeStatistics'] = computeStatistics
        params['maximumCellSizeFactor'] = maximumCellSizeFactor
        params['attributes'] = attributes
        params['geodataTransforms'] = geodataTransforms
        if not itemIds is None:
            params['itemIds'] = itemIds
        if not serviceUrl is None:
            params['serviceUrl'] = serviceUrl
        return self._con.post(url, params, token=self._token)
    #----------------------------------------------------------------------
    def colormap(self):
        """
        The colormap resource returns RGB color representation of pixel
        values. This resource is supported if the hasColormap property of
        the service is true.
        """
        if self.hasColormap:
            url = self._url + "/colormap"
            params = {
                "f" : "json"
            }
            return self._con.get(url, params, token=self._token)
        else:
            return None

class NetworkService(GISService):
    def __init__(self, url, gis=None):
        super(NetworkService, self).__init__(url, gis)
        self._load_layers()

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Network Analysis Service':
            raise TypeError("item must be a type of Network Analysis Service, not " + item.type)
        
        return cls(item.url, item._gis)

    #----------------------------------------------------------------------
    def _load_layers(self):
        """loads the various layer types"""
        self._closestFacilityLayers = []
        self._routeLayers = []
        self._serviceAreaLayers = []
        params = {
            "f" : "json",
        }
        json_dict = self._con.get(path=self._url, params=params, token=self._token)
        for k,v in json_dict.items():
            if k == "routeLayers" and json_dict[k]:
                self._routeLayers = []
                for rl in v:
                    self._routeLayers.append(
                        RouteNetworkLayer(url=self._url + "/%s" % rl,
                                          gis=self._gis))
            elif k == "serviceAreaLayers" and json_dict[k]:
                self._serviceAreaLayers = []
                for sal in v:
                    self._serviceAreaLayers.append(
                        ServiceAreaNetworkLayer(url=self._url + "/%s" % sal,
                                                gis=self._gis))
            elif k == "closestFacilityLayers" and json_dict[k]:
                self._closestFacilityLayers = []
                for cf in v:
                    self._closestFacilityLayers.append(
                        ClosestFacilityNetworkLayer(url=self._url + "/%s" % cf,
                                                    gis=self._gis))
    #----------------------------------------------------------------------
    @property
    def route_layers(self):
        if self._routeLayers is None:
            self._load_layers()
        return self._routeLayers
    #----------------------------------------------------------------------
    @property
    def service_area_layers(self):
        if self._serviceAreaLayers is None:
            self._load_layers()
        return self._serviceAreaLayers
    #----------------------------------------------------------------------
    @property
    def closest_facility_layers(self):
        if self._closestFacilityLayers is None:
            self._load_layers()
        return self._closestFacilityLayers

class SchematicsService(GISService):
    def __init__(self, url, gis=None):
        super(SchematicsService, self).__init__(url, gis)

    @property
    def diagrams(self):
        """
        The Schematic Diagrams resource represents all the schematic diagrams
        under a schematic service. It is returned as an array of Schematic
        Diagram resource by the REST API.
        """
        params = {"f" : "json"}
        exportURL = self._url + "/diagrams"
        return self._con.get(path=exportURL,
                             params=params, token=self._token)
    #----------------------------------------------------------------------
    @property
    def folders(self):
        """
        The Schematic Folders resource represents the set of schematic folders
        in the schematic dataset(s) related to the schematic layers under a
        schematic service. It is returned as an array of <Schematic Folder Object>
        by the REST API.
        """
        params = {"f" : "json"}
        exportURL = self._url + "/folders"
        return self._con.get(path=exportURL,
                         params=params, token=self._token)
    #----------------------------------------------------------------------
    @property
    def schematic_layers(self):
        """
        The Schematic Layers resource represents all the schematic layers
        under a schematic service published by ArcGIS Server. It is returned
        as an array of Schematic Layer resources by the REST API.
        """
        params = {"f" : "json"}
        exportURL = self._url + "/schematicLayers"
        return self._con.get(path=exportURL,
                         params=params, token=self._token)
    #----------------------------------------------------------------------
    @property
    def templates(self):
        """
        The Schematic Diagram Templates represents all the schematic diagram
        templates related to the published schematic layers under a schematic
        service. It is returned as an array of Schematic Diagram Template
        resources by the REST API.
        """
        params = {"f" : "json"}
        exportURL = self._url + "/templates"
        return self._con.get(path=exportURL,
                                 params=params, token=self._token)
    #----------------------------------------------------------------------
    def search_diagrams(self,whereClause=None,relatedObjects=None,
                       relatedSchematicObjects=None):
        """
        The Schematic Search Diagrams operation is performed on the schematic
        service resource. The result of this operation is an array of Schematic
        Diagram Information Object.

        It is used to search diagrams in the schematic service by criteria;
        that is, diagrams filtered out via a where clause on any schematic
        diagram class table field, diagrams that contain schematic features
        associated with a specific set of GIS features/objects, or diagrams
        that contain schematic features associated with the same GIS features/
        objects related to another set of schematic features.

        Inputs:
            whereClause - A where clause for the query filter. Any legal SQL
                          where clause operating on the fields in the schematic
                          diagram class table is allowed. See the Schematic
                          diagram class table fields section below to know the
                          exact list of field names that can be used in this
                          where clause.
            relatedObjects - An array containing the list of the GIS features/
                             objects IDs per feature class/table name that are in
                             relation with schematic features in the resulting
                             queried diagrams. Each GIS feature/object ID
                             corresponds to a value of the OBJECTID field in the
                             GIS feature class/table.
            relatedSchematicObjects - An array containing the list of the
                                      schematic feature names per schematic
                                      feature class ID that have the same
                                      associated GIS features/objects with
                                      schematic features in the resulting
                                      queried diagrams. Each schematic feature
                                      name corresponds to a value of the
                                      SCHEMATICTID field in the schematic
                                      feature class.
        """
        params = {"f" : "json"}
        if whereClause:
            params["where"] = whereClause
        if relatedObjects:
            params["relatedObjects"] = relatedObjects
        if relatedSchematicObjects:
            params["relatedSchematicObjects"] = relatedSchematicObjects

        exportURL = self._url + "/searchDiagrams"
        return self._con.get(path=exportURL,
                             params=params, token=self._token)

class NetworkLayer(Layer):
    """
    The network layer resource represents a single network layer in
    a network analysis service published by ArcGIS Server. It provides basic
    information about the network layer such as its name, type, and network
    classes. Additionally, depending on the layer type, it provides different
    pieces of information.

    It is a base class for RouteNetworkLayer, ServiceAreaNetworkLayer, and
    ClosestFacilityNetworkLayer.
    """
    def retrieve_travel_modes(self):
        """identify all the valid travel modes that have been defined on the
        network dataset or in the portal if the GIS server is federated"""
        url = self._url + "/retrieveTravelModes"
        params = {"f":"json"}
        return self._con.get(path=url,
                         params=params, token=self._token)

class RouteNetworkLayer(NetworkLayer):
    """
    The Route Network Layer which has common properties of Network Layer
    as well as some attributes unique to Route Network Layer only.
    """
    def solve(self,stops,
              barriers=None,
              polylineBarriers=None,
              polygonBarriers=None,
              travelMode=None,
              attributeParameterValues=None,
              returnDirections=None,
              returnRoutes=True,
              returnStops=False,
              returnBarriers=False,
              returnPolylineBarriers=True,
              returnPolygonBarriers=True,
              outSR=None,
              ignoreInvalidLocations=True,
              outputLines=None,
              findBestSequence=False,
              preserveFirstStop=True,
              preserveLastStop=True,
              useTimeWindows=False,
              startTime=None,
              startTimeIsUTC=False,
              accumulateAttributeNames=None,
              impedanceAttributeName=None,
              restrictionAttributeNames=None,
              restrictUTurns=None,
              useHierarchy=True,
              directionsLanguage=None,
              directionsOutputType=None,
              directionsStyleName=None,
              directionsLengthUnits=None,
              directionsTimeAttributeName=None,
              outputGeometryPrecision=None,
              outputGeometryPrecisionUnits=None,
              returnZ=False
              ):
        """The solve operation is performed on a network layer resource.
        The solve operation is supported on a network layer whose layerType
        is esriNAServerRouteLayer. You can provide arguments to the solve
        route operation as query parameters.
        Inputs:
            stops - The set of stops loaded as network locations during analysis.
                    Stops can be specified using a simple comma / semi-colon
                    based syntax or as a JSON structure. If stops are not
                    specified, preloaded stops from the map document are used in
                    the analysis.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple comma
                       / semi-colon based syntax or as a JSON structure. If
                       barriers are not specified, preloaded barriers from the
                       map document are used in the analysis. If an empty json
                       object is passed ('{}') preloaded barriers are ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}')
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}') preloaded
                              polygon barriers are ignored.

            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the routing
                         service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            returnDirections - If true, directions will be generated and returned
                               with the analysis results. Default is true.
            returnRoutes - If true, routes will be returned with the analysis
                           results. Default is true.
            returnStops -  If true, stops will be returned with the analysis
                           results. Default is false.
            returnBarriers -  If true, barriers will be returned with the analysis
                              results. Default is false.
            returnPolylineBarriers -  If true, polyline barriers will be returned
                                      with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned with
                                    the analysis results. Default is false.
            outSR - The spatial reference of the geometries returned with the
                    analysis results.
            ignoreInvalidLocations - If true, the solver will ignore invalid
                                     locations. Otherwise, it will raise an error.
                                     The default is as defined in the network layer.
            outputLines - The type of output lines to be generated in the result.
                          The default is as defined in the network layer.
            findBestSequence - If true, the solver should re-sequence the route in
                               the optimal order. The default is as defined in the
                               network layer.
            preserveFirstStop - If true, the solver should keep the first stop
                                fixed in the sequence. The default is as defined
                                in the network layer.
            preserveLastStop - If true, the solver should keep the last stop fixed
                               in the sequence. The default is as defined in the
                               network layer.
            useTimeWindows - If true, the solver should consider time windows.
                             The default is as defined in the network layer.
            startTime - The time the route begins. If not specified, the solver
                        will use the default as defined in the network layer.
            startTimeIsUTC - The time zone of the startTime parameter.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default is
                                       as defined in the network layer. The value
                                       should be specified as a comma separated list
                                       of attribute names. You can also specify a
                                       value of none to indicate that no network
                                       attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default is
                                     as defined in the network layer.
            restrictionAttributeNames -The list of network attribute names to be
                                       used as restrictions with the analysis. The
                                       default is as defined in the network layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be used as
                                       restrictions.
            restrictUTurns -  Specifies how U-Turns should be restricted in the
                              analysis. The default is as defined in the network
                              layer. Values: esriNFSBAllowBacktrack |
                              esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                              esriNFSBAtDeadEndsAndIntersections
            useHierarchy -  If true, the hierarchy attribute for the network should
                            be used in analysis. The default is as defined in the
                            network layer.
            directionsLanguage - The language to be used when computing directions.
                                 The default is as defined in the network layer. The
                                 list of supported languages can be found in REST
                                 layer description.
            directionsOutputType -  Defines content, verbosity of returned
                                    directions. The default is esriDOTStandard.
                                    Values: esriDOTComplete | esriDOTCompleteNoEvents
                                    | esriDOTInstructionsOnly | esriDOTStandard |
                                    esriDOTSummaryOnly
            directionsStyleName - The style to be used when returning the directions.
                                  The default is as defined in the network layer. The
                                  list of supported styles can be found in REST
                                  layer description.
            directionsLengthUnits - The length units to use when computing directions.
                                    The default is as defined in the network layer.
                                    Values: esriNAUFeet | esriNAUKilometers |
                                    esriNAUMeters | esriNAUMiles |
                                    esriNAUNauticalMiles | esriNAUYards |
                                    esriNAUUnknown
            directionsTimeAttributeName - The name of network attribute to use for
                                          the drive time when computing directions.
                                          The default is as defined in the network
                                          layer.
            outputGeometryPrecision -  The precision of the output geometry after
                                       generalization. If 0, no generalization of
                                       output geometry is performed. The default is
                                       as defined in the network service
                                       configuration.
            outputGeometryPrecisionUnits - The units of the output geometry
                                           precision. The default value is
                                           esriUnknownUnits. Values: esriUnknownUnits
                                           | esriCentimeters | esriDecimalDegrees |
                                           esriDecimeters | esriFeet | esriInches |
                                           esriKilometers | esriMeters | esriMiles |
                                           esriMillimeters | esriNauticalMiles |
                                           esriPoints | esriYards
            returnZ - If true, Z values will be included in the returned routes and
                       compressed geometry if the network dataset is Z-aware.
                       The default is false.
        """

        if not self.properties.layerType == "esriNAServerRouteLayer":
            raise ValueError("The solve operation is supported on a network "
                             "layer of Route type only")

        url = self._url + "/solve"
        params = {
                    "f" : "json",
                    "stops": stops
                 }

        if not barriers is None:
            params['barriers'] = barriers
        if not polylineBarriers is None:
            params['polylineBarriers'] = polylineBarriers
        if not polygonBarriers is None:
            params['polygonBarriers'] = polygonBarriers
        if not travelMode is None:
            params['travelMode'] = travelMode
        if not attributeParameterValues is None:
            params['attributeParameterValues'] = attributeParameterValues
        if not returnDirections is None:
            params['returnDirections'] = returnDirections
        if not returnRoutes is None:
            params['returnRoutes'] = returnRoutes
        if not returnStops is None:
            params['returnStops'] = returnStops
        if not returnBarriers is None:
            params['returnBarriers'] = returnBarriers
        if not returnPolylineBarriers is None:
            params['returnPolylineBarriers'] = returnPolylineBarriers
        if not returnPolygonBarriers is None:
            params['returnPolygonBarriers'] = returnPolygonBarriers
        if not outSR is None:
            params['outSR'] = outSR
        if not ignoreInvalidLocations is None:
            params['ignoreInvalidLocations'] = ignoreInvalidLocations
        if not outputLines is None:
            params['outputLines'] = outputLines
        if not findBestSequence is None:
            params['findBestSequence'] = findBestSequence
        if not preserveFirstStop is None:
            params['preserveFirstStop'] = preserveFirstStop
        if not preserveLastStop is None:
            params['preserveLastStop'] = preserveLastStop
        if not useTimeWindows is None:
            params['useTimeWindows'] = useTimeWindows
        if not startTime is None:
            params['startTime'] = startTime
        if not startTimeIsUTC is None:
            params['startTimeIsUTC'] = startTimeIsUTC
        if not accumulateAttributeNames is None:
            params['accumulateAttributeNames'] = accumulateAttributeNames
        if not impedanceAttributeName is None:
            params['impedanceAttributeName'] = impedanceAttributeName
        if not restrictionAttributeNames is None:
            params['restrictionAttributeNames'] = restrictionAttributeNames
        if not restrictUTurns is None:
            params['restrictUTurns'] = restrictUTurns
        if not useHierarchy is None:
            params['useHierarchy'] = useHierarchy
        if not directionsLanguage is None:
            params['directionsLanguage'] = directionsLanguage
        if not directionsOutputType is None:
            params['directionsOutputType'] = directionsOutputType
        if not directionsStyleName is None:
            params['directionsStyleName'] = directionsStyleName
        if not directionsLengthUnits is None:
            params['directionsLengthUnits'] = directionsLengthUnits
        if not directionsTimeAttributeName is None:
            params['directionsTimeAttributeName'] = directionsTimeAttributeName
        if not outputGeometryPrecision is None:
            params['outputGeometryPrecision'] = outputGeometryPrecision
        if not outputGeometryPrecisionUnits is None:
            params['outputGeometryPrecisionUnits'] = outputGeometryPrecisionUnits
        if not returnZ is None:
            params['returnZ'] = returnZ

        return self._con.post(path=url,
                              postdata=params, token=self._token)

class ServiceAreaNetworkLayer(NetworkLayer):
    """
    The Service Area Network Layer which has common properties of Network
    Layer as well as some attributes unique to Service Area Network Layer
    only.
    """
    def solve_service_area(self,facilities,
                         barriers=None,
                         polylineBarriers=None,
                         polygonBarriers=None,
                         travelMode=None,
                         attributeParameterValues=None,
                         defaultBreaks=None,
                         excludeSourcesFromPolygons=None,
                         mergeSimilarPolygonRanges=None,
                         outputLines=None,
                         outputPolygons=None,
                         overlapLines=None,
                         overlapPolygons=None,
                         splitLinesAtBreaks=None,
                         splitPolygonsAtBreaks=None,
                         trimOuterPolygon=None,
                         trimPolygonDistance=None,
                         trimPolygonDistanceUnits=None,
                         returnFacilities=False,
                         returnBarriers=False,
                         returnPolylineBarriers=False,
                         returnPolygonBarriers=False,
                         outSR=None,
                         accumulateAttributeNames=None,
                         impedanceAttributeName=None,
                         restrictionAttributeNames=None,
                         restrictUTurns=None,
                         outputGeometryPrecision=None,
                         outputGeometryPrecisionUnits='esriUnknownUnits',
                         useHierarchy=None,
                         timeOfDay=None,
                         timeOfDayIsUTC=None,
                         travelDirection=None,
                         returnZ=False):
        """ The solve service area operation is performed on a network layer
        resource of type service area (layerType is esriNAServerServiceArea).
        You can provide arguments to the solve service area operation as
        query parameters.
        Inputs:
            facilities - The set of facilities loaded as network locations
                         during analysis. Facilities can be specified using
                         a simple comma / semi-colon based syntax or as a
                         JSON structure. If facilities are not specified,
                         preloaded facilities from the map document are used
                         in the analysis. If an empty json object is passed
                         ('{}') preloaded facilities are ignored.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple
                       comma/semicolon-based syntax or as a JSON structure.
                       If barriers are not specified, preloaded barriers from
                       the map document are used in the analysis. If an empty
                       json object is passed ('{}'), preloaded barriers are
                       ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}'),
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}'),
                              preloaded polygon barriers are ignored.
            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the
                         service area service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            defaultBreaks - A comma-separated list of doubles. The default is
                            defined in the network analysis layer.
            excludeSourcesFromPolygons - A comma-separated list of string names.
                                         The default is defined in the network
                                         analysis layer.

            mergeSimilarPolygonRanges - If true, similar ranges will be merged
                                        in the result polygons. The default is
                                        defined in the network analysis layer.
            outputLines - The type of lines(s) generated. The default is as
                          defined in the network analysis layer.
            outputPolygons - The type of polygon(s) generated. The default is
                             as defined in the network analysis layer.
            overlapLines - Indicates if the lines should overlap from multiple
                           facilities. The default is defined in the network
                           analysis layer.
            overlapPolygons - Indicates if the polygons for all facilities
                              should overlap. The default is defined in the
                              network analysis layer.
            splitLinesAtBreaks - If true, lines will be split at breaks. The
                                 default is defined in the network analysis
                                 layer.
            splitPolygonsAtBreaks - If true, polygons will be split at breaks.
                                    The default is defined in the network
                                    analysis layer.
            trimOuterPolygon -  If true, the outermost polygon (at the maximum
                                break value) will be trimmed. The default is
                                defined in the network analysis layer.
            trimPolygonDistance -  If polygons are being trimmed, provides the
                                   distance to trim. The default is defined in
                                   the network analysis layer.
            trimPolygonDistanceUnits - If polygons are being trimmed, specifies
                                       the units of the trimPolygonDistance. The
                                       default is defined in the network analysis
                                       layer.
            returnFacilities - If true, facilities will be returned with the
                               analysis results. Default is false.
            returnBarriers - If true, barriers will be returned with the analysis
                             results. Default is false.
            returnPolylineBarriers - If true, polyline barriers will be returned
                                     with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned
                                    with the analysis results. Default is false.
            outSR - The well-known ID of the spatial reference for the geometries
                    returned with the analysis results. If outSR is not specified,
                    the geometries are returned in the spatial reference of the map.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default
                                       is as defined in the network analysis layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default
                                     is as defined in the network analysis layer.
            restrictionAttributeNames - The list of network attribute names to be
                                        used as restrictions with the analysis. The
                                        default is as defined in the network analysis
                                        layer. The value should be specified as a
                                        comma separated list of attribute names.
                                        You can also specify a value of none to
                                        indicate that no network attributes should
                                        be used as restrictions.
            restrictUTurns - Specifies how U-Turns should be restricted in the
                             analysis. The default is as defined in the network
                             analysis layer. Values: esriNFSBAllowBacktrack |
                             esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                             esriNFSBAtDeadEndsAndIntersections
            outputGeometryPrecision - The precision of the output geometry after
                                      generalization. If 0, no generalization of
                                      output geometry is performed. The default is
                                      as defined in the network service configuration.
            outputGeometryPrecisionUnits - The units of the output geometry precision.
                                           The default value is esriUnknownUnits.
                                           Values: esriUnknownUnits | esriCentimeters |
                                           esriDecimalDegrees | esriDecimeters |
                                           esriFeet | esriInches | esriKilometers |
                                           esriMeters | esriMiles | esriMillimeters |
                                           esriNauticalMiles | esriPoints | esriYards
            useHierarchy - If true, the hierarchy attribute for the network should be
                           used in analysis. The default is as defined in the network
                           layer. This cannot be used in conjunction with outputLines.
            timeOfDay - The date and time at the facility. If travelDirection is set
                        to esriNATravelDirectionToFacility, the timeOfDay value
                        specifies the arrival time at the facility. if travelDirection
                        is set to esriNATravelDirectionFromFacility, the timeOfDay
                        value is the departure time from the facility. The time zone
                        for timeOfDay is specified by timeOfDayIsUTC.
            timeOfDayIsUTC - The time zone or zones of the timeOfDay parameter. When
                             set to false, which is the default value, the timeOfDay
                             parameter refers to the time zone or zones in which the
                             facilities are located. Therefore, the start or end times
                             of the service areas are staggered by time zone.
            travelDirection - Options for traveling to or from the facility. The
                              default is defined in the network analysis layer.
            returnZ - If true, Z values will be included in saPolygons and saPolylines
                      geometry if the network dataset is Z-aware.
    """
        if not self.properties.layerType == "esriNAServerServiceAreaLayer":
            raise TypeError("The solveServiceArea operation is supported on a network "
                             "layer of Service Area type only")

        url = self._url + "/solveServiceArea"
        params = {
                "f" : "json",
                "facilities": facilities
                }

        if not barriers is None:
            params['barriers'] = barriers
        if not polylineBarriers is None:
            params['polylineBarriers'] = polylineBarriers
        if not polygonBarriers is None:
            params['polygonBarriers'] = polygonBarriers
        if not travelMode is None:
            params['travelMode'] = travelMode
        if not attributeParameterValues is None:
            params['attributeParameterValues'] = attributeParameterValues
        if not defaultBreaks is None:
            params['defaultBreaks'] = defaultBreaks
        if not excludeSourcesFromPolygons is None:
            params['excludeSourcesFromPolygons'] = excludeSourcesFromPolygons
        if not mergeSimilarPolygonRanges is None:
            params['mergeSimilarPolygonRanges'] = mergeSimilarPolygonRanges
        if not outputLines is None:
            params['outputLines'] = outputLines
        if not outputPolygons is None:
            params['outputPolygons'] = outputPolygons
        if not overlapLines is None:
            params['overlapLines'] = overlapLines
        if not overlapPolygons is None:
            params['overlapPolygons'] = overlapPolygons
        if not splitLinesAtBreaks is None:
            params['splitLinesAtBreaks'] = splitLinesAtBreaks
        if not splitPolygonsAtBreaks is None:
            params['splitPolygonsAtBreaks'] = splitPolygonsAtBreaks
        if not trimOuterPolygon is None:
            params['trimOuterPolygon'] = trimOuterPolygon
        if not trimPolygonDistance is None:
            params['trimPolygonDistance'] = trimPolygonDistance
        if not trimPolygonDistanceUnits is None:
            params['trimPolygonDistanceUnits'] = trimPolygonDistanceUnits
        if not returnFacilities is None:
            params['returnFacilities'] = returnFacilities
        if not returnBarriers is None:
            params['returnBarriers'] = returnBarriers
        if not returnPolylineBarriers is None:
            params['returnPolylineBarriers'] = returnPolylineBarriers
        if not returnPolygonBarriers is None:
            params['returnPolygonBarriers'] = returnPolygonBarriers
        if not outSR is None:
            params['outSR'] = outSR
        if not accumulateAttributeNames is None:
            params['accumulateAttributeNames'] = accumulateAttributeNames
        if not impedanceAttributeName is None:
            params['impedanceAttributeName'] = impedanceAttributeName
        if not restrictionAttributeNames is None:
            params['restrictionAttributeNames'] = restrictionAttributeNames
        if not restrictUTurns is None:
            params['restrictUTurns'] = restrictUTurns
        if not outputGeometryPrecision is None:
            params['outputGeometryPrecision'] = outputGeometryPrecision
        if not outputGeometryPrecisionUnits is None:
            params['outputGeometryPrecisionUnits'] = outputGeometryPrecisionUnits
        if not useHierarchy is None:
            params['useHierarchy'] = useHierarchy
        if not timeOfDay is None:
            params['timeOfDay'] = timeOfDay
        if not timeOfDayIsUTC is None:
            params['timeOfDayIsUTC'] = timeOfDayIsUTC
        if not travelDirection is None:
            params['travelDirection'] = travelDirection
        if not returnZ is None:
            params['returnZ'] = returnZ

        return self._con.post(path=url,
                              postdata=params, token=self._token)

class ClosestFacilityNetworkLayer(NetworkLayer):
    """
    The Closest Facility Network Layer which has common properties of Network
    Layer as well as some attributes unique to Closest Facility Network Layer
    only.
    """
    def solve_closest_facility(self,incidents,facilities,
                             barriers=None,
                             polylineBarriers=None,
                             polygonBarriers=None,
                             travelMode=None,
                             attributeParameterValues=None,
                             returnDirections=None,
                             directionsLanguage=None,
                             directionsStyleName=None,
                             directionsLengthUnits=None,
                             directionsTimeAttributeName=None,
                             returnCFRoutes=True,
                             returnFacilities=False,
                             returnIncidents=False,
                             returnBarriers=False,
                             returnPolylineBarriers=False,
                             returnPolygonBarriers=False,
                             outputLines=None,
                             defaultCutoff=None,
                             defaultTargetFacilityCount=None,
                             travelDirection=None,
                             outSR=None,
                             accumulateAttributeNames=None,
                             impedanceAttributeName=None,
                             restrictionAttributeNames=None,
                             restrictUTurns=None,
                             useHierarchy=True,
                             outputGeometryPrecision=None,
                             outputGeometryPrecisionUnits=None,
                             timeOfDay=None,
                             timeOfDayIsUTC=None,
                             timeOfDayUsage=None,
                             returnZ=False):
        """The solve operation is performed on a network layer resource of
        type closest facility (layerType is esriNAServerClosestFacilityLayer).
        You can provide arguments to the solve route operation as query
        parameters.
        Inputs:
            facilities  - The set of facilities loaded as network locations
                          during analysis. Facilities can be specified using
                          a simple comma / semi-colon based syntax or as a
                          JSON structure. If facilities are not specified,
                          preloaded facilities from the map document are used
                          in the analysis.
            incidents - The set of incidents loaded as network locations
                        during analysis. Incidents can be specified using
                        a simple comma / semi-colon based syntax or as a
                        JSON structure. If incidents are not specified,
                        preloaded incidents from the map document are used
                        in the analysis.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple comma
                       / semi-colon based syntax or as a JSON structure. If
                       barriers are not specified, preloaded barriers from the
                       map document are used in the analysis. If an empty json
                       object is passed ('{}') preloaded barriers are ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}')
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}') preloaded
                              polygon barriers are ignored.
            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the routing
                         service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            returnDirections - If true, directions will be generated and returned
                               with the analysis results. Default is true.
            directionsLanguage - The language to be used when computing directions.
                                 The default is as defined in the network layer. The
                                 list of supported languages can be found in REST
                                 layer description.
            directionsOutputType -  Defines content, verbosity of returned
                                    directions. The default is esriDOTStandard.
                                    Values: esriDOTComplete | esriDOTCompleteNoEvents
                                    | esriDOTInstructionsOnly | esriDOTStandard |
                                    esriDOTSummaryOnly
            directionsStyleName - The style to be used when returning the directions.
                                  The default is as defined in the network layer. The
                                  list of supported styles can be found in REST
                                  layer description.
            directionsLengthUnits - The length units to use when computing directions.
                                    The default is as defined in the network layer.
                                    Values: esriNAUFeet | esriNAUKilometers |
                                    esriNAUMeters | esriNAUMiles |
                                    esriNAUNauticalMiles | esriNAUYards |
                                    esriNAUUnknown
            directionsTimeAttributeName - The name of network attribute to use for
                                          the drive time when computing directions.
                                          The default is as defined in the network
                                          layer.
            returnCFRoutes - If true, closest facilities routes will be returned
                             with the analysis results. Default is true.
            returnFacilities -  If true, facilities  will be returned with the
                                analysis results. Default is false.
            returnIncidents - If true, incidents will be returned with the
                              analysis results. Default is false.
            returnBarriers -  If true, barriers will be returned with the analysis
                              results. Default is false.
            returnPolylineBarriers -  If true, polyline barriers will be returned
                                      with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned with
                                    the analysis results. Default is false.
            outputLines - The type of output lines to be generated in the result.
                          The default is as defined in the network layer.
            defaultCutoff - The default cutoff value to stop traversing.
            defaultTargetFacilityCount - The default number of facilities to find.
            travelDirection - Options for traveling to or from the facility.
                              The default is defined in the network layer.
                              Values: esriNATravelDirectionFromFacility |
                              esriNATravelDirectionToFacility
            outSR - The spatial reference of the geometries returned with the
                    analysis results.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default is
                                       as defined in the network layer. The value
                                       should be specified as a comma separated list
                                       of attribute names. You can also specify a
                                       value of none to indicate that no network
                                       attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default is
                                     as defined in the network layer.
            restrictionAttributeNames -The list of network attribute names to be
                                       used as restrictions with the analysis. The
                                       default is as defined in the network layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be used as
                                       restrictions.
            restrictUTurns -  Specifies how U-Turns should be restricted in the
                              analysis. The default is as defined in the network
                              layer. Values: esriNFSBAllowBacktrack |
                              esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                              esriNFSBAtDeadEndsAndIntersections
            useHierarchy -  If true, the hierarchy attribute for the network should
                            be used in analysis. The default is as defined in the
                            network layer.
            outputGeometryPrecision -  The precision of the output geometry after
                                       generalization. If 0, no generalization of
                                       output geometry is performed. The default is
                                       as defined in the network service
                                       configuration.
            outputGeometryPrecisionUnits - The units of the output geometry
                                           precision. The default value is
                                           esriUnknownUnits. Values: esriUnknownUnits
                                           | esriCentimeters | esriDecimalDegrees |
                                           esriDecimeters | esriFeet | esriInches |
                                           esriKilometers | esriMeters | esriMiles |
                                           esriMillimeters | esriNauticalMiles |
                                           esriPoints | esriYards
            timeOfDay - Arrival or departure date and time. Values: specified by
                        number of milliseconds since midnight Jan 1st, 1970, UTC.
            timeOfDayIsUTC - The time zone of the timeOfDay parameter. By setting
                             timeOfDayIsUTC to true, the timeOfDay parameter refers
                             to Coordinated Universal Time (UTC). Choose this option
                             if you want to find what's nearest for a specific time,
                             such as now, but aren't certain in which time zone the
                             facilities or incidents will be located.
            timeOfDayUsage - Defines the way timeOfDay value is used. The default
                             is as defined in the network layer.
                             Values: esriNATimeOfDayUseAsStartTime |
                             esriNATimeOfDayUseAsEndTime
            returnZ - If true, Z values will be included in the returned routes and
                       compressed geometry if the network dataset is Z-aware.
                       The default is false.
    """

        if not self.properties.layerType == "esriNAServerClosestFacilityLayer":
            raise TypeError("The solveClosestFacility operation is supported on a network "
                             "layer of Closest Facility type only")

        url = self._url + "/solveClosestFacility"
        params = {
                "f" : "json",
                "facilities": facilities,
                "incidents": incidents
                }

        if not barriers is None:
            params['barriers'] = barriers
        if not polylineBarriers is None:
            params['polylineBarriers'] = polylineBarriers
        if not polygonBarriers is None:
            params['polygonBarriers'] = polygonBarriers
        if not travelMode is None:
            params['travelMode'] = travelMode
        if not attributeParameterValues is None:
            params['attributeParameterValues'] = attributeParameterValues
        if not returnDirections is None:
            params['returnDirections'] = returnDirections
        if not directionsLanguage is None:
            params['directionsLanguage'] = directionsLanguage
        if not directionsStyleName is None:
            params['directionsStyleName'] = directionsStyleName
        if not directionsLengthUnits is None:
            params['directionsLengthUnits'] = directionsLengthUnits
        if not directionsTimeAttributeName is None:
            params['directionsTimeAttributeName'] = directionsTimeAttributeName
        if not returnCFRoutes is None:
            params['returnCFRoutes'] = returnCFRoutes
        if not returnFacilities is None:
            params['returnFacilities'] = returnFacilities
        if not returnIncidents is None:
            params['returnIncidents'] = returnIncidents
        if not returnBarriers is None:
            params['returnBarriers'] = returnBarriers
        if not returnPolylineBarriers is None:
            params['returnPolylineBarriers'] = returnPolylineBarriers
        if not returnPolygonBarriers is None:
            params['returnPolygonBarriers'] = returnPolygonBarriers
        if not outputLines is None:
            params['outputLines'] = outputLines
        if not defaultCutoff is None:
            params['defaultCutoff'] = defaultCutoff
        if not defaultTargetFacilityCount is None:
            params['defaultTargetFacilityCount'] = defaultTargetFacilityCount
        if not travelDirection is None:
            params['travelDirection'] = travelDirection
        if not outSR is None:
            params['outSR'] = outSR
        if not accumulateAttributeNames is None:
            params['accumulateAttributeNames'] = accumulateAttributeNames
        if not impedanceAttributeName is None:
            params['impedanceAttributeName'] = impedanceAttributeName
        if not restrictionAttributeNames is None:
            params['restrictionAttributeNames'] = restrictionAttributeNames
        if not restrictUTurns is None:
            params['restrictUTurns'] = restrictUTurns
        if not useHierarchy is None:
            params['useHierarchy'] = useHierarchy
        if not outputGeometryPrecision is None:
            params['outputGeometryPrecision'] = outputGeometryPrecision
        if not outputGeometryPrecisionUnits is None:
            params['outputGeometryPrecisionUnits'] = outputGeometryPrecisionUnits
        if not timeOfDay is None:
            params['timeOfDay'] = timeOfDay
        if not timeOfDayIsUTC is None:
            params['timeOfDayIsUTC'] = timeOfDayIsUTC
        if not timeOfDayUsage is None:
            params['timeOfDayUsage'] = timeOfDayUsage
        if not returnZ is None:
            params['returnZ'] = returnZ

        return self._con.post(path=url, postdata=params, token=self._token)


class AdminMapService(GISService):
    """ allows administration (if access permits) of an ArcGIS Online hosted map service 
    A map service offer access to map and layer content.

       The REST API administrative map service resource represents a map
       service. This resource provides basic information about the map,
       including the layers that it contains, whether the map is cached or
       not, its spatial reference, initial and full extents, etc...  The
       administrative map service resource maintains a set of operations
       that manage the state and contents of the service.
    """
    def __init__(self, url, gis=None, ms=None):
        super(AdminMapService, self).__init__(url, gis)
        self._ms = ms
    
    #----------------------------------------------------------------------
    def refresh(self, serviceDefinition=True):
        """
        The refresh operation refreshes a service, which clears the web
        server cache for the service.
        """
        url = self._url + "/MapServer/refresh"
        params = {
            "f" : "json",
            "serviceDefinition" : serviceDefinition
        }

        res =  self._con.post(self._url, params)

        super(AdminMapService, self)._refresh()
        
        self._ms._refresh()

        return res
    #----------------------------------------------------------------------
    def cancel_job(self, jobId):
        """
        The cancel job operation supports cancelling a job while update
        tiles is running from a hosted feature service. The result of this
        operation is a response indicating success or failure with error
        code and description.

        Inputs:
           jobId - jobId to cancel
        """
        url = self._url + "/jobs/%s/cancel" % jobId
        params = {
            "f" : "json"
        }
        return self._con.post(url, params)
    #----------------------------------------------------------------------
    def job_statistics(self, jobId):
        """
        Returns the job statistics for the given jobId

        """
        url = self._url + "/jobs/%s" % jobId
        params = {
            "f" : "json"
        }
        return self._post(url, params)
    #----------------------------------------------------------------------
    def edit_tile_service(self,
                        serviceDefinition=None,
                        minScale=None,
                        maxScale=None,
                        sourceItemId=None,
                        exportTilesAllowed=False,
                        maxExportTileCount=100000):
        """
        This operation updates a Tile Service's properties

        Inputs:
           serviceDefinition - updates a service definition
           minScale - sets the services minimum scale for caching
           maxScale - sets the service's maximum scale for caching
           sourceItemId - The Source Item ID is the GeoWarehouse Item ID of the map service
           exportTilesAllowed - sets the value to let users export tiles
           maxExportTileCount - sets the maximum amount of tiles to be exported
             from a single call.
        """
        params = {
            "f" : "json",
        }
        if not serviceDefinition is None:
            params["serviceDefinition"] = serviceDefinition
        if not minScale is None:
            params['minScale'] = float(minScale)
        if not maxScale is None:
            params['maxScale'] = float(maxScale)
        if not sourceItemId is None:
            params["sourceItemId"] = sourceItemId
        if not exportTilesAllowed is None:
            params["exportTilesAllowed"] = exportTilesAllowed
        if not maxExportTileCount is None:
            params["maxExportTileCount"] = int(maxExportTileCount)
        url = self._url + "/edit"
        return self._con.post(url, params)

class MapService(GISService):
    """ allows use and administration (if access permits) of a feature service """

    def __init__(self, url, gis=None):
        super(MapService, self).__init__(url, gis)
    
        self._populate_layers()
        self._admin = None

    def _populate_layers(self):        
        layers = []
        tables = []
        
        for lyr in self.properties.layers:
            lyr = arcgis.features.FeatureLayer(self.url + '/' + str(lyr.id), self._gis, arcgis.features.FeatureDataset(self.url, self._gis))
            layers.append(lyr)

        for lyr in self.properties.tables:
            lyr = arcgis.features.Table(self.url + '/' + str(lyr.id), self._gis, arcgis.features.FeatureDataset(self.url, self._gis))
            tables.append(lyr)

        #fsurl = self.url + '/layers'
        #params = { "f" : "json" }
        #allayers = self._con.post(fsurl, params, token=self._token)
        
        #for layer in allayers['layers']:
        #    layers.append(FeatureLayer(self.url + '/' + str(layer['id']), self._gis))
                    
        #for table in allayers['tables']:
        #    tables.append(FeatureLayer(self.url + '/' + str(table['id']), self._gis))

        self.layers = layers
        self.tables = tables

    @property
    def admin(self):
        if self._admin is None:
            """accesses the administration service"""
            url = self._url
            res = search("/rest/", url).span()
            addText = "admin/"
            part1 = url[:res[1]]
            part2 = url[res[1]:]
            adminURL = "%s%s%s" % (part1, addText, part2)

            self._admin = AdminMapService(adminURL, self._gis, self)
        return self._admin

    #----------------------------------------------------------------------
    @property
    def kml(self):
        url = "{url}/kml/mapImage.kmz".format(url=self._url)
        return self._con.get(url, {"f" : 'json'},
                             file_name="mapImage.kmz",
                             out_folder=tempfile.gettempdir(), token=self._token)
    #----------------------------------------------------------------------
    @property
    def itemInfo(self):
        """returns the service's item's infomation"""
        url = "{url}/info/iteminfo".format(url=self._url)
        params = {"f" : "json"}
        return self._con.get(url, params, token=self._token)
    #----------------------------------------------------------------------
    @property
    def metadata(self):
        """returns the service's XML metadata file"""
        url = "{url}/info/metadata".format(url=self._url)
        params = {"f" : "json"}
        return self._con.get(url, params, token=self._token)
    #----------------------------------------------------------------------
    def thumbnail(self, out_path=None):
        """"""
        if out_path is None:
            out_path = tempfile.gettempdir()
        url = "{url}/info/thumbnail".format(url=self._url)
        params = {"f" : "json"}
        if out_path is None:
            out_path = tempfile.gettempdir()
        return self._con.get(url,
                             params,
                             out_folder=out_path,
                             file_name="thumbnail.png", token=self._token)
    #----------------------------------------------------------------------
    def identify(self,
                 geometry,
                 mapExtent,
                 imageDisplay,
                 tolerance,
                 geometryType="esriGeometryPoint",
                 sr=None,
                 layerDefs=None,
                 time_value=None,
                 layerTimeOptions=None,
                 layers="top",
                 returnGeometry=True,
                 maxAllowableOffset=None,
                 geometryPrecision=None,
                 dynamicLayers=None,
                 returnZ=False,
                 returnM=False,
                 gdbVersion=None):

        """
            The identify operation is performed on a map service resource
            to discover features at a geographic location. The result of this
            operation is an identify results resource. Each identified result
            includes its name, layer ID, layer name, geometry and geometry type,
            and other attributes of that result as name-value pairs.

            Inputs:
            geometry - The geometry to identify on. The type of the geometry is
                       specified by the geometryType parameter. The structure of
                       the geometries is same as the structure of the JSON geometry
                       objects returned by the ArcGIS REST API. In addition to the
                       JSON structures, for points and envelopes, you can specify
                       the geometries with a simpler comma-separated syntax.
                       Syntax:
                       JSON structures:
                       <geometryType>&geometry={ geometry}
                       Point simple syntax:
                       esriGeometryPoint&geometry=<x>,<y>
                       Envelope simple syntax:
                       esriGeometryEnvelope&geometry=<xmin>,<ymin>,<xmax>,<ymax>

            geometryType - The type of geometry specified by the geometry parameter.
                           The geometry type could be a point, line, polygon, or
                           an envelope.
                           Values:
                           esriGeometryPoint | esriGeometryMultipoint |
                           esriGeometryPolyline | esriGeometryPolygon |
                           esriGeometryEnvelope

            sr - The well-known ID of the spatial reference of the input and
                 output geometries as well as the mapExtent. If sr is not specified,
                 the geometry and the mapExtent are assumed to be in the spatial
                 reference of the map, and the output geometries are also in the
                 spatial reference of the map.

            layerDefs - Allows you to filter the features of individual layers in
                        the exported map by specifying definition expressions for
                        those layers. Definition expression for a layer that is
                        published with the service will be always honored.

            time_value - The time instant or the time extent of the features to be
            identified.

            layerTimeOptions - The time options per layer. Users can indicate
                               whether or not the layer should use the time extent
                               specified by the time parameter or not, whether to
                               draw the layer features cumulatively or not and the
                               time offsets for the layer.

            layers - The layers to perform the identify operation on. There are
                     three ways to specify which layers to identify on:
                     top: Only the top-most layer at the specified location.
                     visible: All visible layers at the specified location.
                     all: All layers at the specified location.

            tolerance - The distance in screen pixels from the specified geometry
                        within which the identify should be performed. The value for
                        the tolerance is an integer.

            mapExtent - The extent or bounding box of the map currently being viewed.
                        Unless the sr parameter has been specified, the mapExtent is
                        assumed to be in the spatial reference of the map.
                        Syntax: <xmin>, <ymin>, <xmax>, <ymax>
                        The mapExtent and the imageDisplay parameters are used by the
                        server to determine the layers visible in the current extent.
                        They are also used to calculate the distance on the map to
                        search based on the tolerance in screen pixels.

            imageDisplay - The screen image display parameters (width, height, and DPI)
                           of the map being currently viewed. The mapExtent and the
                           imageDisplay parameters are used by the server to determine
                           the layers visible in the current extent. They are also used
                           to calculate the distance on the map to search based on the
                           tolerance in screen pixels.
                           Syntax: <width>, <height>, <dpi>

            returnGeometry - If true, the resultset will include the geometries
                             associated with each result. The default is true.

            maxAllowableOffset - This option can be used to specify the maximum allowable
                                 offset to be used for generalizing geometries returned by
                                 the identify operation. The maxAllowableOffset is in the units
                                 of the sr. If sr is not specified, maxAllowableOffset is
                                 assumed to be in the unit of the spatial reference of the map.

            geometryPrecision - This option can be used to specify the number of decimal places
                                in the response geometries returned by the identify operation.
                                This applies to X and Y values only (not m or z-values).

            dynamicLayers - Use dynamicLayers property to reorder layers and change the layer
                            data source. dynamicLayers can also be used to add new layer that
                            was not defined in the map used to create the map service. The new
                            layer should have its source pointing to one of the registered
                            workspaces that was defined at the time the map service was created.
                            The order of dynamicLayers array defines the layer drawing order.
                            The first element of the dynamicLayers is stacked on top of all
                            other layers. When defining a dynamic layer, source is required.

            returnZ - If true, Z values will be included in the results if the features have
                      Z values. Otherwise, Z values are not returned. The default is false.
                      This parameter only applies if returnGeometry=true.

            returnM - If true, M values will be included in the results if the features have
                      M values. Otherwise, M values are not returned. The default is false.
                      This parameter only applies if returnGeometry=true.

            gdbVersion - Switch map layers to point to an alternate geodatabase version.
        """

        params= {'f': 'json',
                 'geometry': geometry,
                 'geometryType': geometryType,
                 'tolerance': tolerance,
                 'mapExtent': mapExtent,
                 'imageDisplay': imageDisplay
                 }
        if not returnGeometry is None:
            params['returnGeometry'] = returnGeometry
        if returnZ:
            params['returnZ'] = returnZ

        if returnM:
            params['returnM'] = returnM
        if layerDefs is not None:
            params['layerDefs'] = layerDefs
        if layers is not None:
            params['layers'] = layers
        if sr is not None:
            params['sr'] = sr
        if time_value is not None:
            params['time'] = time_value
        if layerTimeOptions is not None:
            params['layerTimeOptions'] = layerTimeOptions
        if maxAllowableOffset is not None:
            params['maxAllowableOffset'] = maxAllowableOffset
        if geometryPrecision is not None:
            params['geometryPrecision'] = geometryPrecision
        if dynamicLayers is not None:
            params['dynamicLayers'] = dynamicLayers
        if gdbVersion is not None:
            params['gdbVersion'] = gdbVersion

        identifyURL = "{url}/identify".format(url=self._url)
        return self._con.get(identifyURL, params, token=self._token)
    #----------------------------------------------------------------------
    def find(self, searchText, layers,
             contains=True, searchFields="",
             sr="", layerDefs="",
             returnGeometry=True, maxAllowableOffset="",
             geometryPrecision="", dynamicLayers="",
             returnZ=False, returnM=False, gdbVersion=""):
        """ performs the map service find operation """
        url = "{url}/find".format(url=self._url)
        params = {
            "f" : "json",
            "searchText" : searchText,
            "contains" : contains,
            "searchFields": searchFields,
            "sr" : sr,
            "layerDefs" : layerDefs,
            "returnGeometry" : returnGeometry,
            "maxAllowableOffset" : maxAllowableOffset,
            "geometryPrecision" : geometryPrecision,
            "dynamicLayers" : dynamicLayers,
            "returnZ" : returnZ,
            "returnM" : returnM,
            "gdbVersion" : gdbVersion,
            "layers" : layers
        }
        res = self._con.get(url, params, token=self._token)
        return res
    #----------------------------------------------------------------------
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
        params= {
            "f" : "json",
            'docName' : docName,
            'layers' : layers,
            'layerOptions': layerOptions}
        return self._con.get(kmlURL, params,
                             out_folder=save_location, token=self._token)
    #----------------------------------------------------------------------
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
        params = {
            "f" : "json"
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

    #----------------------------------------------------------------------
    def estimate_export_tiles_size(self,
                                exportBy,
                                levels,
                                tilePackage=False,
                                exportExtent="DEFAULTEXTENT",
                                areaOfInterest=None,
                                async=True):
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
        async - (optional) the estimate function is run asynchronously
         requiring the tool status to be checked manually to force it to
         run synchronously the tool will check the status until the
         estimation completes.  The default is True, which means the status
         of the job and results need to be checked manually.  If the value
         is set to False, the function will wait until the task completes.
           Values: True | False
        """
        import time
        url = self._url + "/estimateExportTilesSize"
        params = {
            "f" : "json",
            "levels" : levels,
            "exportBy" : exportBy,
            "tilePackage" : tilePackage,
            "exportExtent" : exportExtent
        }
        params["levels"] = levels
        if not areaOfInterest is None:
            params['areaOfInterest'] = areaOfInterest
        if async == True:
            return self._con.get(url, params, token=self._token)
        else:
            exportJob = self._con.get(url, params, token=self._token)

            job_id = exportJob['jobId']
            path = "%s/jobs/%s" % (url, exportJob['jobId'])

            params = { "f" : "json" }
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

    #----------------------------------------------------------------------
    def export_tiles(self,
                    levels,
                    exportBy="LevelID",
                    tilePackage=False,
                    exportExtent="DEFAULT",
                    optimizeTilesForSize=True,
                    compressionQuality=0,
                    areaOfInterest=None,
                    async=False
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
        async - default True, this value ensures the returns are returned
         to the user instead of the user having the check the job status
         manually.
        """
        import time
        params = {
            "f" : "json",
            "tilePackage" : tilePackage,
            "exportExtent" : exportExtent,
            "optimizeTilesForSize" : optimizeTilesForSize,
            "compressionQuality" : compressionQuality,
            "exportBy" : exportBy,
            "levels" : levels
        }
        url = self._url + "/exportTiles"
        if isinstance(areaOfInterest, Polygon):
            geom = areaOfInterest.asDictionary()
            template = { "features": [geom]}
            params["areaOfInterest"] = template
        elif isinstance(areaOfInterest, dict):
            params["areaOfInterest"] = { "features": [areaOfInterest]}
        if async == True:
            return self._con.get(path=url, params=params, token=self._token)
        else:
            exportJob = self._con.get(path=url, params=params, token=self._token)
            
            job_id = exportJob['jobId']
            path = "%s/jobs/%s" % (url, exportJob['jobId'])

            params = { "f" : "json" }
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
            
            for k,v in allResults.items():
                if k == "out_service_url":
                    value = v.value
                    params = {
                        "f" : "json"
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

########################################################################
