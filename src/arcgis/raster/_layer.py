from arcgis._impl.common._utils import local_time_to_online
from arcgis.gis import Layer


class ImageryLayer(Layer):
    def __init__(self, url, gis=None):
        super(ImageryLayer, self).__init__(url, gis)

    @classmethod
    def fromitem(cls, item):
        if not item.type == 'Image Service':
            raise TypeError("item must be a type of Image Service, not " + item.type)

        return cls(item.url, item._gis)

    def export_image(self,
                     bbox,
                     image_sr=None,
                     bbox_sr=None,
                     size=None,
                     time=None,
                     export_format="jpgpng",
                     pixel_type="UNKNOWN",
                     no_data=None,
                     no_data_interpretation="esriNoDataMatchAny",
                     interpolation=None,
                     compression=None,
                     compression_quality=75,
                     band_ids=None,
                     moasiac_rule=None,
                     rendering_rule="",
                     f="json",
                     save_folder=None,
                     save_file=None,
                     compression_tolerance=None
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
           bbox - The extent (bounding box) of the exported image. Unless
                  the bbox_sr parameter has been specified, the bbox is
                  assumed to be in the spatial reference of the imagery
                  layer.

                  The bbox should be specified as an arcgis.geometry.Envelope object, it's json representation or as
                  a list or string with this format: '<xmin>, <ymin>, <xmax>, <ymax>'

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
           export_format - The format of the exported image. The default format is
                    jpgpng.
                    Values: jpgpng | png | png8 | png24 | jpg | bmp | gif |
                            tiff | png32
           pixel_type - The pixel type, also known as data type, pertains to
                       the type of values stored in the raster, such as
                       signed integer, unsigned integer, or floating point.
                       Integers are whole numbers, whereas floating points
                       have decimals.
           no_date - The pixel value representing no information.
           no_data_interpretation - Interpretation of the noData setting. The
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
           compression_quality - Controls how much loss the image will be
                                subjected to by the compression algorithm.
                                Valid value ranges of compression quality
                                are from 0 to 100.
           band_ids - If there are multiple bands, you can specify a single
                     band to export, or you can change the band combination
                     (red, green, blue) by specifying the band number. Band
                     number is 0 based.
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

           compression_tolerance - Controls the tolerance of the lerc compression algorithm. The tolerance defines the
               maximum possible error of pixel values in the compressed image. It's a double value.
               Example: compression_tolerance=0.5 is loseless for 8 and 16 bit images, but has an accuracy of +-0.5 for
               floating point data. The compression tolerance works for the LERC format only.

        """
        import datetime

        if size is None:
            size = [400, 400]

        params = {
            "size": "%s,%s" % (size[0], size[1]),
            "compressionQuality": compression_quality,
        }

        if type(bbox) == str:
            params['bbox'] = bbox
        elif type(bbox) == list:
            params['bbox'] = "%s,%s,%s,%s" % (bbox[0], bbox[1], bbox[2], bbox[3])
        else: # json dict or Geometry Envelope object
            bbox = "%s,%s,%s,%s" % (bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax'])
            params['bbox'] = bbox

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
        if isinstance(moasiac_rule, dict):
            params["moasiacRule"] = moasiac_rule
        if export_format in __allowedFormat:
            params['format'] = export_format
        if isinstance(time, datetime.datetime):
            params['time'] = local_time_to_online(time)
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
            params['bandIds'] = ",".join(band_ids)
        if rendering_rule is not None:
            params['renderingRule'] = rendering_rule

        if compression_tolerance is not None:
            params['compressionTolerance'] = compression_tolerance
        params["f"] = f
        if f == "json":
            return self._con.get(url, params, token=self._token)
        elif f == "image":
            result = self._con.get(url, params,
                                   out_folder=save_folder, try_json=False,
                                   file_name=save_file, token=self._token)
            return result
        elif f == "kmz":
            return self._con.get(url, params,
                                 out_folder=save_folder,
                                 file_name=save_file, token=self._token)
        else:
            print('Unsupported output format')

    # ----------------------------------------------------------------------
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
                  "returnGeometry": returnGeometry,
                  "returnIdsOnly": returnIdsOnly,
                  "returnCountOnly": returnCountOnly,
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

    # ----------------------------------------------------------------------
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
            "f": "json"
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

    # ----------------------------------------------------------------------
    def colormap(self):
        """
        The colormap resource returns RGB color representation of pixel
        values. This resource is supported if the hasColormap property of
        the service is true.
        """
        if self.hasColormap:
            url = self._url + "/colormap"
            params = {
                "f": "json"
            }
            return self._con.get(url, params, token=self._token)
        else:
            return None