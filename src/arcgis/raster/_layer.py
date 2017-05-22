import json

from arcgis._impl.common._utils import _date_handler
from arcgis.gis import Layer
from arcgis.geometry import Geometry
from ..features import FeatureSet
import datetime

class ImageryLayer(Layer):
    def __init__(self, url, gis=None):
        super(ImageryLayer, self).__init__(url, gis)
        self._spatial_filter = None
        self._temporal_filter = None
        self._where_clause = '1=1'
        self._fn = None
        self._fnra = None
        self._filtered = False
        self._mosaic_rule = None
        self._extent = None
        # self._extent = self.properties.initialExtent

    @property
    def _lyr_json(self):
        url = self.url
        if self._token is not None:  # causing geoanalytics Invalid URL error
            url += '?token=' + self._token

        lyr_dict = {'type': type(self).__name__, 'url': url}

        options_dict = {
            "imageServiceParameters": {
            }
        }

        if self._fn is not None or self._mosaic_rule is not None:
            if self._fn is not None:
                options_dict["imageServiceParameters"]["renderingRule"] = self._fn

            if self._mosaic_rule is not None:
                options_dict["imageServiceParameters"]["mosaicRule"] = self._mosaic_rule

            lyr_dict.update({
                "options": json.dumps(options_dict)
            })

        return lyr_dict

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Image Service':
            raise TypeError("item must be a type of Image Service, not " + item.type)

        return cls(item.url, item._gis)

    @property
    def extent(self):
        """Area of interest. Used for displaying the imagery layer when queried"""
        if self._extent is None:
            self._extent = self.properties.initialExtent

        return self._extent

    @extent.setter
    def extent(self, value):
        self._extent = value

    def set_filter(self, where=None, geometry=None, time=None, lock_rasters=False, clear_filters=False):
        """
        Filters the rasters that will be used for applying raster functions.

        If lock_rasters is set True, the LockRaster mosaic rule will be applied to the layer, unless overridden

        :param where: a where clause on this layer to filter the imagery layer by the selection sql statement.
                Any legal SQL where clause operating on the fields in the raster
        :param geometry: the spatial filter on this layer to spatially filter the imagery layer by the specified arcgis.geometry.filter
        :param time: a temporal filter to this layer to filter the imagery layer by time using the specified time instant or the time extent.
                Time instant specified as datetime.date, datetime.datetime or timestamp in milliseconds since epoch
                Syntax: time_filter=<timeInstant>

                Time extent specified as list of [<startTime>, <endTime>]
                For time extents one of <startTime> or <endTime> could be None. A None value specified for
                start time or end time will represent infinity for start or end time respectively.
                Syntax: time_filter=[<startTime>, <endTime>] ; specified as datetime.date, datetime.datetime or
                timestamp in milliseconds
        :param lock_rasters: if True, the LockRaster mosaic rule will be applied to the layer, unless overridden
        :param clear_filters: if True, the applied filters are cleared
        :return:

        """
        if clear_filters:
            self._filtered = False
            self._where_clause = None
            self._temporal_filter = None
            self._spatial_filter = None
            self._mosaic_rule = None
        else:
            self._filtered = True
            if where is not None:
                self._where_clause = where

            if geometry is not None:
                self._spatial_filter = geometry

            if time is not None:
                self._temporal_filter = time

            if lock_rasters:
                oids = self.query(where=self._where_clause,
                      time_filter=self._temporal_filter,
                      geometry_filter=self._spatial_filter,
                      return_ids_only=True)['objectIds']
                self._mosaic_rule = {
                      "mosaicMethod" : "esriMosaicLockRaster",
                      "lockRasterIds": oids,
                      "ascending" : True,
                      "mosaicOperation" : "MT_FIRST"
                    }


    def filter_by(self, where=None, geometry=None, time=None, lock_rasters=True):
        """
        Filters the layer by where clause, geometry and temporal filters



        :param where: a where clause on this layer to filter the imagery layer by the selection sql statement.
                Any legal SQL where clause operating on the fields in the raster
        :param geometry: the spatial filter on this layer to spatially filter the imagery layer by the specified arcgis.geometry.filter
        :param time: a temporal filter to this layer to filter the imagery layer by time using the specified time instant or the time extent.
                Time instant specified as datetime.date, datetime.datetime or timestamp in milliseconds since epoch
                Syntax: time_filter=<timeInstant>

                Time extent specified as list of [<startTime>, <endTime>]
                For time extents one of <startTime> or <endTime> could be None. A None value specified for
                start time or end time will represent infinity for start or end time respectively.
                Syntax: time_filter=[<startTime>, <endTime>] ; specified as datetime.date, datetime.datetime or
                timestamp in milliseconds
        :param lock_rasters: bool If True, the LockRaster mosaic rule is applied to the layer, using the filtered objectids
        :return: ImageryLayer with filtered images meeting the filter criteria

        """
        newlyr = self._clone_layer()

        newlyr._where_clause = where
        newlyr._spatial_filter = geometry
        newlyr._temporal_filter = time

        if lock_rasters:
            oids = self.query(where=where,
                  time_filter=time,
                  geometry_filter=geometry,
                  return_ids_only=True)['objectIds']
            newlyr._mosaic_rule = {
                "mosaicMethod": "esriMosaicLockRaster",
                "lockRasterIds": oids,
                "ascending": True,
                "mosaicOperation": "MT_FIRST"
            }

        newlyr._filtered = True

        return newlyr

    def _clone_layer(self):
        newlyr = ImageryLayer(self._url, self._gis)
        newlyr._lazy_properties = self.properties
        newlyr._hydrated = True
        newlyr._lazy_token = self._token

        newlyr._fn = self._fn
        newlyr._fnra = self._fnra
        newlyr._mosaic_rule = self._mosaic_rule
        newlyr._extent = self._extent

        # newlyr._where_clause = self._where_clause
        # newlyr._spatial_filter = self._spatial_filter
        # newlyr._temporal_filter = self._temporal_filter
        # newlyr._filtered = self._filtered

        return newlyr

    def filtered_rasters(self):
        """The object ids of the filtered rasters in this imagery layer, by applying the where clause, spatial and
        temporal filters. If no rasters are filtered, returns None. If all rasters are filtered, returns empty list"""
        if self._filtered:
            oids = self.query(where=self._where_clause,
                  time_filter=self._temporal_filter,
                  geometry_filter=self._spatial_filter,
                  return_ids_only=True)['objectIds']
            return oids #['$' + str(x) for x in oids]
        else:
            return None # return '$$'

    def export_image(self,
                     bbox=None,
                     image_sr=None,
                     bbox_sr=None,
                     size=None,
                     time=None,
                     export_format="jpgpng",
                     pixel_type=None,
                     no_data=None,
                     no_data_interpretation="esriNoDataMatchAny",
                     interpolation=None,
                     compression=None,
                     compression_quality=None,
                     band_ids=None,
                     mosaic_rule=None,
                     rendering_rule=None,
                     f="json",
                     save_folder=None,
                     save_file=None,
                     compression_tolerance=None,
                     adjust_aspect_ratio=None
                     ):
        """
        The export_image operation is performed on an imagery layer.
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
           bbox - Optional. The extent (bounding box) of the exported image. Unless
                  the bbox_sr parameter has been specified, the bbox is
                  assumed to be in the spatial reference of the imagery
                  layer.

                  The bbox should be specified as an arcgis.geometry.Envelope object, it's json representation or as
                  a list or string with this format: '<xmin>, <ymin>, <xmax>, <ymax>'

                  If omitted, the extent of the imagery layer is used

           image_sr - The spatial reference of the exported image.
                  The spatial reference can be specified as either a well-known ID, it's json representation or as an
                  arcgis.geometry.SpatialReference object.
                  If the image_sr is not specified, the image will be exported in the spatial reference of the imagery layer.

           bbox_sr - The spatial reference of the bbox.
                  The spatial reference can be specified as either a well-known ID, it's json representation or as an
                  arcgis.geometry.SpatialReference object.
                  If the image_sr is not specified, bbox is assumed to be in the spatial reference of the imagery layer.

           size - The size (width * height) of the exported image in
                  pixels. If size is not specified, an image with a default
                  size of 400 * 400 will be exported.
                  Format: list of [width, height]

           time - The time instant or the time extent of the exported image.
                    Time instant specified as datetime.date, datetime.datetime or timestamp in milliseconds since epoch
                    Syntax: time=<timeInstant>

                    Time extent specified as list of [<startTime>, <endTime>]
                    For time extents one of <startTime> or <endTime> could be None. A None value specified for
                    start time or end time will represent infinity for start or end time respectively.
                    Syntax: time=[<startTime>, <endTime>] ; specified as datetime.date, datetime.datetime or timestamp

           export_format - The format of the exported image. The default format is jpgpng.
                    The jpgpng format returns a JPG if there are no transparent pixels in the requested extent;
                    otherwise, it returns a PNG (png32).

                    Values: jpgpng | png | png8 | png24 | jpg | bmp | gif | tiff | png32 | bip | bsq | lerc

           pixel_type - The pixel type, also known as data type, pertains to
                       the type of values stored in the raster, such as
                       signed integer, unsigned integer, or floating point.
                       Integers are whole numbers, whereas floating points
                       have decimals.

           no_data - The pixel value representing no information.

           no_data_interpretation - Interpretation of the no_data setting. The
                               default is esriNoDataMatchAny when no_data is
                               a number, and esriNoDataMatchAll when no_data
                               is a comma-delimited string:
                               esriNoDataMatchAny | esriNoDataMatchAll.

           interpolation - The resampling process of extrapolating the
                           pixel values while transforming the raster
                           dataset when it undergoes warping or when it
                           changes coordinate space.

           compression - Controls how to compress the image when exporting
                         to TIFF format: None, JPEG, LZ77. It does not
                         control compression on other formats.

           compression_quality - Controls how much loss the image will be
                                subjected to by the compression algorithm.
                                Valid value ranges of compression quality
                                are from 0 to 100.

           band_ids - If there are multiple bands, you can specify a single
                     band to export, or you can change the band combination
                     (red, green, blue) by specifying the band number. Band
                     number is 0 based. Specified as list of ints, eg [2,1,0]

           mosaic_rule - Specifies the mosaic rule when defining how
                        individual images should be mosaicked. When a mosaic
                        rule is not specified, the default mosaic rule of
                        the image service will be used (as advertised in
                        the root resource: defaultMosaicMethod,
                        mosaicOperator, sortField, sortValue).

           rendering_rule - Specifies the rendering rule for how the
                           requested image should be rendered.

           f - The response format.  default is json
               Values: json | image | kmz
               If image format is chosen, the bytes of the exported image are returned unless save_folder and save_file
               parameters are also passed, in which case the image is written to the specified file

           save_folder - the folder in which the exported image is saved when f=image

           save_file - the file in which the exported image is saved when f=image

           compression_tolerance - Controls the tolerance of the lerc compression algorithm. The tolerance defines the
               maximum possible error of pixel values in the compressed image. It's a double value.
               Example: compression_tolerance=0.5 is loseless for 8 and 16 bit images, but has an accuracy of +-0.5 for
               floating point data. The compression tolerance works for the LERC format only.

            adjust_aspect_ratio -  indicates whether to adjust the aspect ratio or not. By default adjust_aspect_ratio is
            true, that means the actual bbox will be adjusted to match the width/height ratio of size paramter, and the
            response image has square pixels. Values: True | False
        """
        import datetime

        if size is None:
            size = [400, 400]

        params = {
            "size": "%s,%s" % (size[0], size[1]),
        }

        if bbox is not None:
            if type(bbox) == str:
                params['bbox'] = bbox
            elif type(bbox) == list:
                params['bbox'] = "%s,%s,%s,%s" % (bbox[0], bbox[1], bbox[2], bbox[3])
            else: # json dict or Geometry Envelope object
                bbox = "%s,%s,%s,%s" % (bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax'])
                params['bbox'] = bbox
        else:
            params['bbox'] = self.extent # properties.initialExtent

        if image_sr is not None:
            params['imageSR'] = image_sr
        if bbox_sr is not None:
            params['bboxSR'] = bbox_sr
        if pixel_type is not None:
            params['pixelType'] = pixel_type

        url = self._url + "/exportImage"
        __allowedFormat = ["jpgpng", "png",
                           "png8", "png24",
                           "jpg", "bmp",
                           "gif", "tiff",
                           "png32", "bip", "bsq", "lerc"]
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
        if mosaic_rule is not None:
            params["mosaicRule"] = mosaic_rule
        elif self._mosaic_rule is not None:
            params["mosaicRule"] = self._mosaic_rule

        if export_format in __allowedFormat:
            params['format'] = export_format

        if self._temporal_filter is not None:
            time = self._temporal_filter

        if time is not None:
            if type(time) is list:
                starttime = _date_handler(time[0])
                endtime = _date_handler(time[1])
                if starttime is None:
                    starttime = 'null'
                if endtime is None:
                    endtime = 'null'
                params['time'] = "%s,%s" % (starttime, endtime)
            else:
                params['time'] = _date_handler(time)

        if interpolation is not None and \
                        interpolation in __allowedInterpolation and \
                isinstance(interpolation, str):
            params['interpolation'] = interpolation

        if pixel_type is not None and \
                        pixel_type in __allowedPixelTypes:
            params['pixelType'] = pixel_type

        if no_data_interpretation in __allowedInterpolation:
            params['noDataInterpretation'] = no_data_interpretation

        if no_data is not None:
            params['noData'] = no_data

        if compression is not None and \
                        compression in __allowedCompression:
            params['compression'] = compression

        if band_ids is not None and \
                isinstance(band_ids, list):
            params['bandIds'] = ",".join([str(x) for x in band_ids])

        if rendering_rule is not None:
            if 'function_chain' in rendering_rule:
                params['renderingRule'] = rendering_rule['function_chain']
            else:
                params['renderingRule'] = rendering_rule
        elif self._fn is not None:
            params['renderingRule'] = self._fn

        if compression_tolerance is not None:
            params['compressionTolerance'] = compression_tolerance

        if compression_quality is not None:
            params['compressionQuality'] = compression_quality

        if adjust_aspect_ratio is not None:
            if adjust_aspect_ratio is True:
                params['adjustAspectRatio'] = 'true'
            else:
                params['adjustAspectRatio'] = 'false'

        params["f"] = f

        if f == "json":
            return self._con.post(url, params, token=self._token)
        elif f == "image":
            if save_folder is not None and save_file is not None:
                return self._con.post(url, params,
                                   out_folder=save_folder, try_json=False,
                                   file_name=save_file, token=self._token)
            else:
                return self._con.post(url, params,
                                     try_json=False, force_bytes=True,
                                     token=self._token)
        elif f == "kmz":
            return self._con.post(url, params,
                                 out_folder=save_folder,
                                 file_name=save_file, token=self._token)
        else:
            print('Unsupported output format')

    # ----------------------------------------------------------------------
    def query(self,
              where=None,
              out_fields="*",
              time_filter=None,
              geometry_filter=None,
              return_geometry=True,
              return_ids_only=False,
              return_count_only=False,
              pixel_size=None,
              order_by_fields=None,
              return_distinct_values=None,
              out_statistics=None,
              group_by_fields_for_statistics=None,
              out_sr=None
              ):
        """ queries an imagery layer by applying the filter specified by the user. The result of this operation is
         either a set of features or an array of raster IDs (if return_ids_only is set to True),
         count (if return_count_only is set to True), or a set of field statistics (if out_statistics is used).

            Inputs:
               where - the selection sql statement. Any legal SQL where clause operating on the fields in the raster
                        catalog is allowed.
               out_fields - the attribute fields to return, comma-delimited list of field names.
               time_filter - The time instant or the time extent of the exported image.
                    Time instant specified as datetime.date, datetime.datetime or timestamp in milliseconds since epoch
                    Syntax: time_filter=<timeInstant>

                    Time extent specified as list of [<startTime>, <endTime>]
                    For time extents one of <startTime> or <endTime> could be None. A None value specified for
                    start time or end time will represent infinity for start or end time respectively.
                    Syntax: time_filter=[<startTime>, <endTime>] ; specified as datetime.date, datetime.datetime or
                    timestamp in milliseconds
               geometry_filter - arcgis.geometry.filter to filter results by a spatial relationship
                                with another geometry
               return_geometry - true means a geometry will be returned,
                                else just the attributes
               return_ids_only - false is default.  True means only OBJECTIDs
                               will be returned
               return_count_only - if True, then an integer is returned only
                                 based on the sql statement
               pixel_size-Query visible rasters at a given pixel size. If
                         pixel_size is not specified, rasters at all
                         resolutions can be queried.
               order_by_fields-Order results by one or more field names. Use
                             ASC or DESC for ascending or descending order,
                             respectively
               return_distinct_values-  If true, returns distinct values
                                    based on the fields specified in
                                    outFields. This parameter applies only
                                    if the supportsAdvancedQueries property
                                    of the image service is true.
               out_statistics- the definitions for one or more field-based
                              statistics to be calculated.
               group_by_fields_for_statistics-One or more field names using the
                                         values that need to be grouped for
                                         calculating the statistics.
               out_sr - if the returning geometry needs to be in a different
                        spatial reference, provide the function with the
                        desired WKID.
            Output:
               A FeatureSet containing the footprints (features) matching the query when return_geometry is True,
               else a dictionary containing the expected return type
         """
        params = {"f": "json",
                  "outFields": out_fields,
                  "returnGeometry": return_geometry,
                  "returnIdsOnly": return_ids_only,
                  "returnCountOnly": return_count_only,
                  }

        if where is not None:
            params['where'] = where
        elif self._where_clause is not None:
            params['where'] = self._where_clause
        else:
            params['where'] = '1=1'

        if not group_by_fields_for_statistics is None:
            params['groupByFieldsForStatistics'] = group_by_fields_for_statistics
        if not out_statistics is None:
            params['outStatistics'] = out_statistics


        if self._temporal_filter is not None:
            time_filter = self._temporal_filter

        if time_filter is not None:
            if type(time_filter) is list:
                starttime = _date_handler(time_filter[0])
                endtime = _date_handler(time_filter[1])
                if starttime is None:
                    starttime = 'null'
                if endtime is None:
                    endtime = 'null'
                params['time'] = "%s,%s" % (starttime, endtime)
            else:
                params['time'] = _date_handler(time_filter)


        if self._spatial_filter is not None:
            geometry_filter = self._spatial_filter

        if not geometry_filter is None and \
                isinstance(geometry_filter, dict):
            gf = geometry_filter
            params['geometry'] = gf['geometry']
            params['geometryType'] = gf['geometryType']
            params['spatialRel'] = gf['spatialRel']
            if 'inSR' in gf:
                params['inSR'] = gf['inSR']

        if pixel_size is not None:
            params['pixelSize'] = pixel_size
        if order_by_fields is not None:
            params['orderByFields'] = order_by_fields
        if return_distinct_values is not None:
            params['returnDistinctValues'] = return_distinct_values
        if out_sr is not None:
            params['outSR'] = out_sr
        url = self._url + "/query"
        result = self._con.post(path=url, postdata=params, token=self._token)

        if 'error' in result:
            raise ValueError(result)

        if return_count_only:
            return result['count']
        elif return_ids_only:
            return result
        elif return_geometry:
            return FeatureSet.from_dict(result)
        else:
            return result

    # ----------------------------------------------------------------------
    def add_rasters(self,
                    raster_type,
                    item_ids=None,
                    service_url=None,
                    compute_statistics=False,
                    build_pyramids=False,
                    build_thumbnail=False,
                    minimum_cell_size_factor=None,
                    maximum_cell_size_factor=None,
                    attributes=None,
                    geodata_transforms=None,
                    geodata_transform_apply_method="esriGeodataTransformApplyAppend"
                    ):
        """
        This operation is supported at 10.1 and later.
        The Add Rasters operation is performed on an image service resource.
        The Add Rasters operation adds new rasters to an image service
        (POST only).
        The added rasters can either be uploaded items, using the item_ids
        parameter, or published services, using the service_url parameter.
        If item_ids is specified, uploaded rasters are copied to the image
        service's dynamic image workspace location; if the service_url is
        specified, the image service adds the URL to the mosaic dataset no
        raster files are copied. The service_url is required input for the
        following raster types: Image Service, Map Service, WCS, and WMS.

        Inputs:

        item_ids - The upload items (raster files) to be added. Either
         item_ids or service_url is needed to perform this operation.
            Syntax: item_ids=<itemId1>,<itemId2>
            Example: item_ids=ib740c7bb-e5d0-4156-9cea-12fa7d3a472c,
                             ib740c7bb-e2d0-4106-9fea-12fa7d3a482c
        service_url - The URL of the service to be added. The image service
         will add this URL to the mosaic dataset. Either item_ids or
         service_url is needed to perform this operation. The service URL is
         required for the following raster types: Image Service, Map
         Service, WCS, and WMS.
            Example: service_url=http://myserver/arcgis/services/Portland/ImageServer
        raster_type - The type of raster files being added. Raster types
         define the metadata and processing template for raster files to be
         added. Allowed values are listed in image service resource.
            Example: Raster Dataset | CADRG/ECRG | CIB | DTED | Image Service | Map Service | NITF | WCS | WMS
        compute_statistics - If true, statistics for the rasters will be
         computed. The default is false.
            Values: false | true
        build_pyramids - If true, builds pyramids for the rasters. The
         default is false.
                Values: false | true
        build_thumbnail	 - If true, generates a thumbnail for the rasters.
         The default is false.
                Values: false | true
        minimum_cell_size_factor - The factor (times raster resolution) used
         to populate the MinPS field (maximum cell size above which the
         raster is visible).
                Syntax: minimum_cell_size_factor=<minimum_cell_size_factor>
                Example: minimum_cell_size_factor=0.1
        maximum_cell_size_factor - The factor (times raster resolution) used
         to populate MaxPS field (maximum cell size below which raster is
         visible).
                Syntax: maximum_cell_size_factor=<maximum_cell_size_factor>
                Example: maximum_cell_size_factor=10
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
        geodata_transforms - The geodata transformations applied on the
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
        geodata_transform_apply_method - This parameter defines how to apply
         the provided geodataTransform. The default is
         esriGeodataTransformApplyAppend.
                Values: esriGeodataTransformApplyAppend |
                esriGeodataTransformApplyReplace |
                esriGeodataTransformApplyOverwrite
        """
        url = self._url + "/add"
        params = {
            "f": "json"
        }
        if item_ids is None and service_url is None:
            raise Exception("An itemId or service_url must be provided")
        if isinstance(item_ids, str):
            item_ids = [item_ids]
        if isinstance(service_url, str):
            service_url = [service_url]
        params['geodataTransformApplyMethod'] = geodata_transform_apply_method
        params['rasterType'] = raster_type
        params['buildPyramids'] = build_pyramids
        params['buildThumbnail'] = build_thumbnail
        params['minimumCellSizeFactor'] = minimum_cell_size_factor
        params['computeStatistics'] = compute_statistics
        params['maximumCellSizeFactor'] = maximum_cell_size_factor
        params['attributes'] = attributes
        params['geodataTransforms'] = geodata_transforms
        if not item_ids is None:
            params['itemIds'] = item_ids
        if not service_url is None:
            params['serviceUrl'] = service_url
        return self._con.post(url, params, token=self._token)

    # ----------------------------------------------------------------------
    def colormap(self):
        """
        The colormap resource returns RGB color representation of pixel
        values. This resource is supported if the hasColormap property of
        the service is true.
        """
        if self.properties.hasColormap:
            url = self._url + "/colormap"
            params = {
                "f": "json"
            }
            return self._con.get(url, params, token=self._token)
        else:
            return None


            # ----------------------------------------------------------------------

    def compute_histograms(self, geometry, mosaic_rule=None,
                                      rendering_rule=None, pixel_size=None):
        """
        The compute_histograms operation is performed on an imagery layer
        resource. This operation is supported by any imagery layer published with
        mosaic datasets or a raster dataset. The result of this operation contains
        both statistics and histograms computed from the given extent.
        Inputs:
        geometry - A geometry that defines the geometry within which the histogram
         is computed. The geometry can be an envelope or a polygon. The structure of
         the geometry is the same as the structure of the JSON geometry objects
         returned by the ArcGIS REST API, or an arcgis.geometry Geometry object
        mosaic_rule - Specifies the mosaic rule when defining how individual
         images should be mosaicked. When a mosaic rule is not specified, the
         default mosaic rule of the image service will be used (as advertised
         in the root resource: defaultMosaicMethod, mosaicOperator, sortField,
         sortValue).
        rendering_rule - Specifies the rendering rule for how the requested
         image should be rendered.
        pixel_size - The pixel level being used (or the resolution being looked at).
         If pixel size is not specified, then pixel_size will default to the base
         resolution of the dataset. The raster at the specified pixel size in the
         mosaic dataset will be used for histogram calculation.
         The structure of the pixel_size parameter is the same as the structure of
         the point object returned by the ArcGIS REST API. In addition to the JSON
         structure, you can specify the pixel size with a simple comma-separated syntax.
        """

        url = self._url + "/computeHistograms"
        params = {
            "f": "json",
            "geometry": geometry,
        }

        if 'xmin' in geometry:
            params["geometryType"] = 'esriGeometryEnvelope'
        else:
            params["geometryType"] = 'esriGeometryPolygon'


        if mosaic_rule is not None:
            params["moasiacRule"] = mosaic_rule
        elif self._mosaic_rule is not None:
            params["moasiacRule"] = self._mosaic_rule

        if not rendering_rule is None:
            params["renderingRule"] = rendering_rule
        elif self._fn is not None:
            params['renderingRule'] = self._fn

        if not pixel_size is None:
            params["pixelSize"] = pixel_size

        return self._con.get(url, params, token=self._token)

        # ----------------------------------------------------------------------

    def get_samples(self, geometry, geometry_type=None,
                   sample_distance=None, sample_count=None, mosaic_rule=None,
                   pixel_size=None, return_first_value_only=None, interpolation=None,
                   out_fields=None):
        """
        The get_samples operation is supported by both mosaic dataset and raster
        dataset imagery layers.
        The result of this operation includes sample point locations, pixel
        values, and corresponding spatial resolutions of the source data for a
        given geometry. When the input geometry is a polyline, envelope, or
        polygon, sampling is based on sample_count or sample_distance; when the
        input geometry is a point or multipoint, the point or points are used
        directly.
        The number of sample locations in the response is based on the
        sample_distance or sample_count parameter and cannot exceed the limit of
        the image service (the default is 1000, which is an approximate limit).
        Inputs:
        geometry - A geometry that defines the location(s) to be sampled. The
         structure of the geometry is the same as the structure of the JSON
         geometry objects returned by the ArcGIS REST API. Applicable geometry
         types are point, multipoint, polyline, polygon, and envelope. When
         spatialReference is omitted in the input geometry, it will be assumed
         to be the spatial reference of the image service.
        geometry_type - The type of geometry specified by the geometry parameter.
         The geometry type can be point, multipoint, polyline, polygon, or envelope.
         Values: esriGeometryPoint | esriGeometryMultipoint | esriGeometryPolyline |
         esriGeometryPolygon | esriGeometryEnvelope
        sample_distance - The distance interval used to sample points from the
         provided path. The unit is the same as the input geometry. If neither
         sample_count nor sample_distance is provided, no densification can be done
         for paths (polylines), and a default sample_count (100) is used for areas
         (polygons or envelopes).
        sample_count - The approximate number of sample locations from the provided
         path. If neither sample_count nor sample_distance is provided, no
         densification can be done for paths (polylines), and a default
         sample_count (100) is used for areas (polygons or envelopes).
        mosaic_rule - Specifies the mosaic rule defining the image sort order.
         Additional filtering can be applied to the where clause and FIDs of a
         mosaic rule.
        pixel_size - The raster that is visible at the specified pixel size in the
         mosaic dataset will be used for sampling. If pixel_size is not specified,
         the service's pixel size is used.
         The structure of the esri_codephpixelSize parameter is the same as the
         structure of the point object returned by the ArcGIS REST API. In addition
         to the JSON structure, you can specify the pixel size with a simple
         comma-separated syntax.
        return_first_value_only - Indicates whether to return all values at a point,
         or return the first non-NoData value based on the current mosaic rule.
         The default is true.
        interpolation - The resampling method. Default is nearest neighbor.
         Values: RSP_BilinearInterpolation | RSP_CubicConvolution | RSP_Majority | RSP_NearestNeighbor
        out_fields - The list of fields to be
         included in the response. This list is a comma-delimited list of field
         names. You can also specify the wildcard character (*) as the value of
         this parameter to include all the field values in the results.
        """

        if not isinstance(geometry, Geometry):
            geometry = Geometry(geometry)

        if geometry_type is None:
            geometry_type = 'esriGeometry' + geometry.type

        url = self._url + "/getSamples"
        params = {
            "f": "json",
            "geometry": geometry,
            "geometryType": geometry_type
        }

        if not sample_distance is None:
            params["sampleDistance"] = sample_distance
        if not sample_count is None:
            params["sampleCount"] = sample_count
        if not mosaic_rule is None:
            params["mosaicRule"] = mosaic_rule
        elif self._mosaic_rule is not None:
            params["moasiacRule"] = self._mosaic_rule
        if not pixel_size is None:
            params["pixelSize"] = pixel_size
        if not return_first_value_only is None:
            params["returnFirstValueOnly"] = return_first_value_only
        if not interpolation is None:
            params["interpolation"] = interpolation
        if not out_fields is None:
            params["outFields"] = out_fields

        return self._con.get(url, params, token=self._token)['samples']

    def key_properties(self, rendering_rule=None):
        """
        returns key properties of the imagery layer, such as band properties
        :param rendering_rule: Specifies the rendering rule for how the requested image should be processed.
        The response contains updated service information that reflects a custom processing as defined
         by the rendering rule. For example, if renderingRule contains an attributeTable function,
         the response will indicate "hasRasterAttributeTable": true; if the renderingRule contains
          functions that alter the number of bands, the response will indicate correct bandCount.
        :return: key properties of the imagery layer
        """
        url = self._url + "/keyProperties"
        params = {
            "f": "json"
        }

        if rendering_rule is not None:
            params['renderingRule'] = rendering_rule
        elif self._fn is not None:
            params['renderingRule'] = self._fn

        return self._con.get(url, params, token=self._token)



    def mosaic_by(self, method=None, sort_by=None, sort_val=None, lock_rasters=None, viewpt=None, asc=True, where=None, fids=None,
           muldidef=None, op="first"):
        """
        Defines how individual images in this layer should be mosaicked. It specifies selection,
        mosaic method, sort order, overlapping pixel resolution, etc. Mosaic rules are for mosaicking rasters in
        the mosaic dataset. A mosaic rule is used to define:

        * The selection of rasters that will participate in the mosaic (using where clause).
        * The mosaic method, e.g. how the selected rasters are ordered.
        * The mosaic operation, e.g. how overlapping pixels at the same location are resolved.

        :param method:  determines how the selected rasters are ordered.
            str, can be none | center | nadir | northwest | seamline | viewpoint | attribute | lock-raster
            required if method is: center | nadir | northwest | seamline,
            optional otherwise. If no method is passed "none" method is used, which uses the order of records to sort
            If sort_by and optionally sort_val parameters are specified, "attribute" method is used
            If lock_rasters are specified, "lock-raster" method is used
            If a viewpt parameter is passed, "viewpoint" method is used.
        :param sort_by: optional str, field name when sorting by attributes
        :param sort_val: optional, a constant value defining a reference or base value for the sort field when sorting by
            attributes
        :param lock_rasters: optional, an array of raster Ids. All the rasters with the given list of raster Ids are selected
            to participate in the mosaic. The rasters will be visible at all pixel sizes regardless of the minimum and
            maximum pixel size range of the locked rasters.
        :param viewpt: optional point, used as view point for viewpoint mosaicking method
        :param asc: optional bool, indicate whether to use ascending or descending order. Default is ascending order.
        :param where: optional str, where clause to define a subset of rasters used in the mosaic, be aware that the rasters
            may not be visible at all scales
        :param fids: optional list of objectids, use the raster id list to define a subset of rasters used in the mosaic, be
            aware that the rasters may not be visible at all scales.
        :param muldidef: optional dict, multidemensional definition used for filtering by variable/dimensions.
            See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r300000290000000
        :param op: optional string, first | last | min | max | mean | blend | sum
            mosaic operation to resolve overlap pixel values: from first or last raster, use the min, max or mean of the
            pixel values, or blend them.
        :return: a mosaic rule defined in the format at
            http://resources.arcgis.com/en/help/arcgis-rest-api/#/Mosaic_rule_objects/02r3000000s4000000/
        Also see http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/understanding-the-mosaicking-rules-for-a-mosaic-dataset.htm#ESRI_SECTION1_ABDC9F3F6F724A4F8079051565DC59E
        """
        mosaic_rule = {
            "mosaicMethod": "esriMosaicNone",
            "ascending": asc,
            "mosaicOperation": 'MT_' + op.upper()
        }

        if where is not None:
            mosaic_rule['where'] = where

        if fids is not None:
            mosaic_rule['fids'] = fids

        if muldidef is not None:
            mosaic_rule['multidimensionalDefinition'] = muldidef

        if method in [ 'none', 'center', 'nadir', 'northwest', 'seamline']:
            mosaic_rule['mosaicMethod'] = 'esriMosaic' + method.title()

        if viewpt is not None:
            if not isinstance(viewpt, Geometry):
                viewpt = Geometry(viewpt)
            mosaic_rule['mosaicMethod'] = 'esriMosaicViewpoint'
            mosaic_rule['viewpt'] = viewpt

        if sort_by is not None:
            mosaic_rule['mosaicMethod'] = 'esriMosaicAttribute'
            mosaic_rule['sortField'] = sort_by
            if sort_val is not None:
                mosaic_rule['sortValue'] = sort_val

        if lock_rasters is not None:
            mosaic_rule['mosaicMethod'] = 'esriMosaicLockRaster'
            mosaic_rule['lockRasterIds'] = lock_rasters

        self._mosaic_rule = mosaic_rule

    @property
    def mosaic_rule(self):
        """The mosaic rule used by the imagery layer to define:
        * The selection of rasters that will participate in the mosaic
        * The mosaic method, e.g. how the selected rasters are ordered.
        * The mosaic operation, e.g. how overlapping pixels at the same location are resolved.

        Set by calling the mosaic_by or filter_by methods on the layer
        """
        return self._mosaic_rule

    @mosaic_rule.setter
    def mosaic_rule(self, value):

        self._mosaic_rule = value

    def _mosaic_operation(self, op):
        """
        Sets how overlapping pixels at the same location are resolved

        :param op: string, one of first | last | min | max | mean | blend | sum

        :return: this imagery layer with mosaic operation set to op
        """
        newlyr = self._clone_layer()
        if self._mosaic_rule is not None:
            newlyr._mosaic_rule["mosaicOperation"] = 'MT_' + op.upper()

        return newlyr

    def first(self):
        """
        overlapping pixels at the same location are resolved by picking the first image
        :return: this imagery layer with mosaic operation set to 'first'
        """
        return self._mosaic_operation('first')

    def last(self):
        """
        overlapping pixels at the same location are resolved by picking the last image
        :return: this imagery layer with mosaic operation set to 'last'
        """
        return self._mosaic_operation('last')

    def min(self):
        """
        overlapping pixels at the same location are resolved by picking the min pixel value
        :return: this imagery layer with mosaic operation set to 'min'
        """
        return self._mosaic_operation('min')

    def max(self):
        """
        overlapping pixels at the same location are resolved by picking the max pixel value
        :return: this imagery layer with mosaic operation set to 'max'
        """
        return self._mosaic_operation('max')

    def mean(self):
        """
        overlapping pixels at the same location are resolved by choosing the mean of all overlapping pixels
        :return: this imagery layer with mosaic operation set to 'mean'
        """
        return self._mosaic_operation('mean')

    def blend(self):
        """
        overlapping pixels at the same location are resolved by blending all overlapping pixels
        :return: this imagery layer with mosaic operation set to 'blend'
        """
        return self._mosaic_operation('blend')

    def sum(self):
        """
        overlapping pixels at the same location are resolved by adding up all overlapping pixel values
        :return: this imagery layer with mosaic operation set to 'sum'
        """
        return self._mosaic_operation('sum')


    def save(self, output_name=None, for_viz=False, gis=None):
        """
        Persists this imagery layer to the GIS as an Imagery Layer item. If for_viz is True, a new Item is created that
        uses the applied raster functions for visualization at display resolution using on-the-fly image processing.
        If for_viz is False, distributed raster analysis is used for generating a new raster information product by
        applying raster functions at source resolution across the extent of the output imagery layer.

        :param output_name: Optional. If not provided, an Imagery Layer item is created by the method and used as the output.
            You can pass in the name of the output Imagery Layer that should be created by this method to
            be used as the output for the tool.
            Alternatively, if for_viz is False, you can pass in an existing Image Service Item from your GIS to use that instead
            A RuntimeError is raised if a service by that name already exists

        :param for_viz: If True, a new Item is created that uses the applied raster functions for visualization at
            display resolution using on-the-fly image processing.
            If for_viz is False, distributed raster analysis is used for generating a new raster information product
            for use in analysis and visualization by applying raster functions at source resolution across the extent of
            the output imagery layer.

        :param gis: The GIS to be used for saving the output

        :return : output_raster - Image layer item
        """
        g = self._gis

        if gis is not None:
            g = gis

        if for_viz:

            if g._con._auth.lower() != 'ANON'.lower() and g._con._auth is not None:
                text_data = {
                    "id": "resultLayer",
                    "visibility": True,
                    "bandIds": [],
                    "opacity": 1,
                    "title": output_name,
                    "timeAnimation": False,
                    "renderingRule": self._fn,
                    "mosaicRule": self._mosaic_rule
                }
                ext = self.properties.initialExtent

                item_properties = {
                    'title': output_name,
                    'type': 'Image Service',
                    'url' : self._url,
                    'description': self.properties.description,
                    'tags': 'imagery',
                    'extent': '{},{},{},{}'.format(ext['xmin'], ext['ymin'], ext['xmax'], ext['ymax']),
                    'spatialReference': self.properties.spatialReference.wkid,
                    'text': json.dumps(text_data)
                }

                return g.content.add(item_properties)
            else:
                raise RuntimeError('You need to be signed in to a GIS to create Items')
        else:
            from .analytics import is_supported, generate_raster
            if is_supported(g):
                return generate_raster(self._fnra, output_name=output_name, gis=g)
            else:
                raise RuntimeError('This GIS does not support raster analysis.')


    def _repr_jpeg_(self):
        return self.export_image(bbox=self._extent, size=[1200, 450], export_format='jpeg', f='image')

    def __sub__(self, other):
        from arcgis.raster.functions import minus
        return minus([self, other])

    def __rsub__(self, other):
        from arcgis.raster.functions import minus
        return minus([other, self])

    def __add__(self, other):
        from arcgis.raster.functions import plus
        return plus([self, other])

    def __radd__(self, other):
        from arcgis.raster.functions import plus
        return plus([other, self])

    def __mul__(self, other):
        from arcgis.raster.functions import times
        return times([self, other])

    def __rmul__(self, other):
        from arcgis.raster.functions import times
        return times([other, self])

    def __div__(self, other):
        from arcgis.raster.functions import divide
        return divide([self, other])

    def __rdiv__(self, other):
        from arcgis.raster.functions import divide
        return divide([other, self])

    def __pow__(self, other):
        from arcgis.raster.functions import power
        return power([self, other])

    def __rpow__(self, other):
        from arcgis.raster.functions import power
        return power([other, self])

    def __abs__(self):
        from arcgis.raster.functions import abs
        return abs([self])

    def __lshift__(self, other):
        from arcgis.raster.functions import bitwise_left_shift
        return bitwise_left_shift([self, other])

    def __rlshift__(self, other):
        from arcgis.raster.functions import bitwise_left_shift
        return bitwise_left_shift([other, self])

    def __rshift__(self, other):
        from arcgis.raster.functions import bitwise_right_shift
        return bitwise_right_shift([self, other])

    def __rrshift__(self, other):
        from arcgis.raster.functions import bitwise_right_shift
        return bitwise_right_shift([other, self])

    def __floordiv__(self, other):
        from arcgis.raster.functions import floor_divide
        return floor_divide([self, other])

    def __rfloordiv__(self, other):
        from arcgis.raster.functions import floor_divide
        return floor_divide([other, self])

    def __truediv__(self, other):
        from arcgis.raster.functions import float_divide
        return float_divide([self, other])

    def __rtruediv__(self, other):
        from arcgis.raster.functions import float_divide
        return float_divide([other, self])

    def __mod__(self, other):
        from arcgis.raster.functions import mod
        return mod([self, other])

    def __rmod__(self, other):
        from arcgis.raster.functions import mod
        return mod([other, self])

    def __neg__(self):
        from arcgis.raster.functions import negate
        return negate([self])

    def __invert__(self):
        from arcgis.raster.functions import boolean_not
        return boolean_not(self)

    def __and__(self, other):
        from arcgis.raster.functions import boolean_and
        return boolean_and([self, other])

    def __rand__(self, other):
        from arcgis.raster.functions import boolean_and
        return boolean_and([other, self])

    def __xor__(self, other):
        from arcgis.raster.functions import boolean_xor
        return boolean_xor([self, other])

    def __rxor__(self, other):
        from arcgis.raster.functions import boolean_xor
        return boolean_xor([other, self])

    def __or__(self, other):
        from arcgis.raster.functions import boolean_or
        return boolean_or([self, other])

    def __ror__(self, other):
        from arcgis.raster.functions import boolean_or
        return boolean_or([other, self])

        # Raster.Raster.__pos__ = unaryPos         # +v
# Raster.Raster.__abs__ = Functions.Abs    # abs(v)
#
# Raster.Raster.__add__  = Functions.Plus  # +
# Raster.Raster.__radd__ = lambda self, lhs: Functions.Plus(lhs, self)
# Raster.Raster.__sub__  = Functions.Minus # -
# # TODO Huh?
# Raster.Raster.__rsub__ = Functions.Minus
# # Raster.Raster.__rsub__ = lambda self, lhs: Functions.Minus(lhs, self)
# Raster.Raster.__mul__  = Functions.Times # *
# Raster.Raster.__rmul__ = lambda self, lhs: Functions.Times(lhs, self)
# Raster.Raster.__pow__  = Functions.Power # **
# Raster.Raster.__rpow__ = lambda self, lhs: Functions.Power(lhs, self)
#
# Raster.Raster.__lshift__  = Functions.BitwiseLeftShift  # <<
# Raster.Raster.__rlshift__ = lambda self, lhs: Functions.BitwiseLeftShift(lhs, self)
# Raster.Raster.__rshift__  = Functions.BitwiseRightShift # >>
# Raster.Raster.__rrshift__ = lambda self, lhs: Functions.BitwiseRightShift(lhs, self)
#
# Raster.Raster.__div__       = Functions.Divide     # /
# Raster.Raster.__rdiv__      = lambda self, lhs: Functions.Divide(lhs, self)

# Raster.Raster.__floordiv__  = Functions.FloorDivide # //
# Raster.Raster.__rfloordiv__ = lambda self, lhs: Functions.FloorDivide(lhs, self)

# Raster.Raster.__truediv__   = Functions.FloatDivide # /
# Raster.Raster.__rtruediv__  = lambda self, lhs: Functions.FloatDivide(lhs, self)



# Raster.Raster.__mod__       = Functions.Mod        # %
# Raster.Raster.__rmod__      = lambda self, lhs: Functions.Mod(lhs, self)
# Raster.Raster.__divmod__    = returnNotImplemented # divmod()
# Raster.Raster.__rdivmod__   = returnNotImplemented
#
# # The Python bitwise operators are used for Raster boolean operators.
# Raster.Raster.__invert__ = Functions.BooleanNot # ~
# Raster.Raster.__and__    = Functions.BooleanAnd # &
# Raster.Raster.__rand__   = lambda self, lhs: Functions.BooleanAnd(lhs, self)
# Raster.Raster.__xor__    = Functions.BooleanXOr # ^
# Raster.Raster.__rxor__   = lambda self, lhs: Functions.BooleanXOr(lhs, self)
# Raster.Raster.__or__     = Functions.BooleanOr  # |
# Raster.Raster.__ror__    = lambda self, lhs: Functions.BooleanOr(lhs, self)
#
# # Python will use the non-augmented versions of these.
# Raster.Raster.__iadd__      = returnNotImplemented # +=
# Raster.Raster.__isub__      = returnNotImplemented # -=
# Raster.Raster.__imul__      = returnNotImplemented # *=
# Raster.Raster.__idiv__      = returnNotImplemented # /=
# Raster.Raster.__itruediv__  = returnNotImplemented # /=
# Raster.Raster.__ifloordiv__ = returnNotImplemented # //=
# Raster.Raster.__imod__      = returnNotImplemented # %=
# Raster.Raster.__ipow__      = returnNotImplemented # **=
# Raster.Raster.__ilshift__   = returnNotImplemented # <<=
# Raster.Raster.__irshift__   = returnNotImplemented # >>=
# Raster.Raster.__iand__      = returnNotImplemented # &=
# Raster.Raster.__ixor__      = returnNotImplemented # ^=
# Raster.Raster.__ior__       = returnNotImplemented # |=