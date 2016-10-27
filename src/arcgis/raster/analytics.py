"""
raster analytics tools
"""


def _create_output_image_service( output_name, task):
    pass
    # ok = self._gis.content.is_service_name_available(output_name, "Image Service")
    # if not ok:
    #     raise RuntimeError("An Image Service by this name already exists: " + output_name)
    #
    # createParameters = {
    #     "name": output_name,
    #     "description": "",
    #     "capabilities": "Image",
    #     "properties": {
    #         "path": "@",
    #         "description": "",
    #         "copyright": ""
    #     }
    # }
    #
    # output_service = self._gis.content.create_service(output_name, create_params=createParameters,
    #                                                   service_type="imageService")
    # description = "Image Service generated from running the " + task + " tool."
    # item_properties = {
    #     "description": description,
    #     "tags": "Analysis Result, " + task,
    #     "snippet": "Analysis Image Service generated from " + task
    # }
    # output_service.update(item_properties)
    # return output_service


def generate_raster(
                    raster_function,
                    function_arguments=None,
                    output_raster=None,
                    output_raster_properties=None,
                    context=None,
                    num_instances=None):
    """


    Parameters
    ----------
    raster_function : Required, see http://resources.arcgis.com/en/help/rest/apiref/israsterfunctions.html

    function_arguments : Optional,  for specifying input Raster alone, portal Item can be passed

    output_raster : Optional. If not provided, an Image Service is created by the method and used as the output raster.
        You can pass in an existing Image Service Item from your GIS to use that instead.
        Alternatively, you can pass in the name of the output Image Service that should be created by this method to be used as the output for the tool.
        A RuntimeError is raised if a service by that name already exists

    output_raster_properties : Optional string

    context : Optional

    num_instances : Optional, number of instances to use


    Returns
    -------
    out_raster : Image Service item
    """
    pass
    #
    # task = "GenerateRaster"
    #
    # output_service = None
    #
    # if output_raster is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_raster, str):
    #     output_service = self._create_output_image_service(output_raster, task)
    # elif isinstance(output_raster, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # if isinstance(function_arguments, arcgis.gis.Item):
    #     if function_arguments.type.lower() == 'image service':
    #         function_arguments = {"Raster": {"itemId": function_arguments.itemid}}
    #     else:
    #         raise TypeError("The item type of function_arguments must be an image service")
    #
    # params = {}
    #
    # params["rasterFunction"] = raster_function
    # params["outputRaster"] = output_raster
    # if function_arguments is not None:
    #     params["functionArguments"] = function_arguments
    # if output_raster_properties is not None:
    #     params["outputRasterProperties"] = output_raster_properties
    # if context is not None:
    #     params["context"] = context
    # if num_instances is not None:
    #     params["numInstances"] = num_instances
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def rasterize(
              input_table,
              output_raster,
              raster_info,
              value_field=None,
              context=None,
              num_instances=None):
    """


    Parameters
    ----------
    input_table : Required string

    output_raster : Required string

    raster_info : Required string

    value_field : Optional string

    context : Optional string

    num_instances : Optional string


    Returns
    -------
    out_raster : layer
    """
    pass
    #
    # task = "Rasterize"
    #
    # output_service = None
    #
    # if output_raster is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_raster, str):
    #     output_service = self._create_output_image_service(output_raster, task)
    # elif isinstance(output_raster, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # params = {}
    #
    # params["inputTable"] = input_table
    # params["outputRaster"] = output_raster
    # params["rasterInfo"] = raster_info
    # if value_field is not None:
    #     params["valueField"] = value_field
    # if context is not None:
    #     params["context"] = context
    # if num_instances is not None:
    #     params["numInstances"] = num_instances
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def interpolate(
                input_table,
                output_raster,
                raster_info,
                value_field=None,
                interpolation_method="Nearest",
                radius=None,
                context=None,
                num_instances=None):
    """


    Parameters
    ----------
    input_table : Required string

    output_raster : Required string

    raster_info : Required string

    value_field : Optional string

    interpolation_method : Optional string
        One of the following: ['Nearest', 'Bilinear', 'Linear', 'NaturalNeighbor']
    radius : Optional float

    context : Optional string

    num_instances : Optional string


    Returns
    -------
    out_raster : layer (Feature Service item)
    """
    pass

    # task = "Interpolate"
    # output_service = None
    #
    # if output_raster is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_raster, str):
    #     output_service = self._create_output_image_service(output_raster, task)
    # elif isinstance(output_raster, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # params = {}
    #
    # params["inputTable"] = input_table
    # params["outputRaster"] = output_raster
    # params["rasterInfo"] = raster_info
    # if value_field is not None:
    #     params["valueField"] = value_field
    # if interpolation_method is not None:
    #     params["interpolationMethod"] = interpolation_method
    # if radius is not None:
    #     params["radius"] = radius
    # if context is not None:
    #     params["context"] = context
    # if num_instances is not None:
    #     params["numInstances"] = num_instances
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def copy_raster(
                input_raster,
                output_raster,
                output_cellsize=None,
                resampling_method="NEAREST",
                clipping_geometry=None,
                context=None,
                num_instances=None):
    """


    Parameters
    ----------
    input_raster : Required string

    output_raster : Required string

    output_cellsize : Optional string

    resampling_method : Optional string
        One of the following: ['NEAREST', 'BILINEAR', 'CUBIC', 'MAJORITY']
    clipping_geometry : Optional string

    context : Optional string

    num_instances : Optional string


    Returns
    -------
    out_raster : layer
    """
    #
    # task = "CopyRaster"
    # output_service = None
    #
    # if output_raster is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_raster, str):
    #     output_service = self._create_output_image_service(output_raster, task)
    # elif isinstance(output_raster, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # params = {}
    #
    # params["inputRaster"] = input_raster
    # params["outputRaster"] = output_raster
    # if output_cellsize is not None:
    #     params["outputCellsize"] = output_cellsize
    # if resampling_method is not None:
    #     params["resamplingMethod"] = resampling_method
    # if clipping_geometry is not None:
    #     params["clippingGeometry"] = clipping_geometry
    # if context is not None:
    #     params["context"] = context
    # if num_instances is not None:
    #     params["numInstances"] = num_instances
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def summarize_raster_within(
                            input_zone_layer,
                            zone_field,
                            input_raster_layerto_summarize,
                            output_name,
                            statistic_type="Mean",
                            ignore_missing_values=True,
                            context=None):
    """


    Parameters
    ----------
    input_zone_layer : Required layer

    zone_field : Required string

    input_raster_layerto_summarize : Required string

    output_name : Required string

    statistic_type : Optional string
        One of the following: ['Mean', 'Majority', 'Maximum', 'Median', 'Minimum', 'Minority', 'Range', 'STD', 'SUM', 'Variety']
    ignore_missing_values : Optional bool

    context : Optional string


    Returns
    -------
    out_raster : layer
    """
    pass
    #
    # task = "Summarize Raster Within"
    #
    # output_service = None
    #
    # if output_name is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_name, str):
    #     output_service = self._create_output_image_service(output_name, task)
    # elif isinstance(output_name, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # params = {}
    #
    # params["inputZoneLayer"] = super()._feature_input(input_zone_layer)
    # params["zoneField"] = zone_field
    # params["inputRasterLayertoSummarize"] = input_raster_layerto_summarize
    #
    # params["outputRaster"] = output_raster
    # params["outputName"] = json.dumps({"serviceProperties": {"name": output_name, "serviceUrl": output_service.url},
    #                                    "itemProperties": {"itemId": output_service.itemid}})
    # if statistic_type is not None:
    #     params["statisticType"] = statistic_type
    # if ignore_missing_values is not None:
    #     params["ignoreMissingValues"] = ignore_missing_values
    # if context is not None:
    #     params["context"] = context
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def density(
            input_feature_class,
            output_raster,
            value_field,
            raster_info=None,
            method="Point_Density",
            neighborhood=None,
            area_units="Square_map_units",
            context=None):
    """


    Parameters
    ----------
    input_feature_class : Required string

    output_raster : Required string

    value_field : Required string

    raster_info : Optional string

    method : Optional string
        One of the following: ['Point_Density', 'Line_Density', 'Kernel_Density_Densities_Planar', 'Kernel_Density_Densities_Geodesic', 'Kernel_Density_Counts_Planar', 'Kernel_Density_Counts_Geodesic']
    neighborhood : Optional string

    area_units : Optional string
        One of the following: ['Square_map_units', 'Square_miles', 'Square_kilometers', 'Arces', 'Hectares', 'Square_yards', 'Square_feet', 'Square_inches', 'Square_meters', 'Square_centimeters', 'Square_millimeters']
    context : Optional string


    Returns
    -------
    out_raster : layer (Feature Service item)
    """
    pass
    #
    # task = "Density"
    # output_service = None
    #
    # if output_raster is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_raster, str):
    #     output_service = self._create_output_image_service(output_raster, task)
    # elif isinstance(output_raster, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # params = {}
    #
    # params["inputFeatureClass"] = input_feature_class
    # params["outputRaster"] = output_raster
    # params["valueField"] = value_field
    # if raster_info is not None:
    #     params["rasterInfo"] = raster_info
    # if method is not None:
    #     params["method"] = method
    # if neighborhood is not None:
    #     params["neighborhood"] = neighborhood
    # if area_units is not None:
    #     params["areaUnits"] = area_units
    # if context is not None:
    #     params["context"] = context
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def classify(
             input_raster,
             input_classifier_definition,
             output_raster,
             additional_input_raster=None,
             number_of_instances="4"):
    """


    Parameters
    ----------
    input_raster : Required string

    input_classifier_definition : Required string

    output_raster : Required string

    additional_input_raster : Optional string

    number_of_instances : Required string


    Returns
    -------
    """
    pass
    #
    # task = "Classify"
    #
    # output_service = None
    #
    # if output_raster is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_raster, str):
    #     output_service = self._create_output_image_service(output_raster, task)
    # elif isinstance(output_raster, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # params = {}
    #
    # params["Input_Raster"] = input_raster
    # params["Input_Classifier_Definition"] = input_classifier_definition
    # params["Output_Classified_Raster"] = output_raster
    # if additional_input_raster is not None:
    #     params["Additional_Input_Raster"] = additional_input_raster
    # params["Number_of_Instances"] = number_of_instances
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def segment_mean_shift(
                       input_raster,
                       output_raster,
                       spectral_detail="15.5",
                       spatial_detail="15",
                       minimum_segment_size_in_pixels="20",
                       band_indexes="1,2,3",
                       remove_tiiling_artifacts="false",
                       number_of_instances="4"):
    """


    Parameters
    ----------
    input_raster : Required string

    output_raster : Required string

    spectral_detail : Required string

    spatial_detail : Required string

    minimum_segment_size_in_pixels : Required string

    band_indexes : Required string

    remove_tiiling_artifacts : Required string

    number_of_instances : Required string


    Returns
    -------
    """
    pass
    #
    # task = "Segment Mean Shift"
    #
    # output_service = None
    #
    # if output_raster is None:
    #     output_ras_name = 'GeneratedRasterProduct' + '_' + _id_generator()
    #     output_service = self._create_output_image_service(output_ras_name, task)
    # elif isinstance(output_raster, str):
    #     output_service = self._create_output_image_service(output_raster, task)
    # elif isinstance(output_raster, Item):
    #     output_service = output_raster
    # else:
    #     raise TypeError("output_raster should be a string (service name) or Item")
    #
    # output_raster = {'itemId': output_service.itemid}
    #
    # params = {}
    #
    # params["Input_Raster"] = input_raster
    # params["Output_Raster_Dataset"] = output_raster
    # params["Spectral_Detail"] = spectral_detail
    # params["Spatial_Detail"] = spatial_detail
    # params["Minimum_Segment_Size_In_Pixels"] = minimum_segment_size_in_pixels
    # params["Band_Indexes"] = band_indexes
    # params["Remove_Tiiling_Artifacts"] = remove_tiiling_artifacts
    # params["Number_of_Instances"] = number_of_instances
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service


def train_classifier(
                     input_raster,
                     input_training_sample_json,
                     segmented_raster,
                     classifier_parameters,
                     segment_attributes="COLOR;MEAN"):
    """


    Parameters
    ----------
    input_raster : Required string

    input_training_sample_json : Required string

    segmented_raster : Required string

    classifier_parameters : Required string

    segment_attributes : Required string


    Returns
    -------
    output_classifier_definition : layer
    """
    pass
    #
    # task = "Train Classifier"
    #
    # params = {}
    #
    # params["Input_Raster"] = input_raster
    # params["Input_Training_Sample_JSON"] = input_training_sample_json
    # params["Segmented_Raster"] = segmented_raster
    # params["Classifier_Parameters"] = classifier_parameters
    # params["Segment_Attributes"] = segment_attributes
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    #
    # return job_values['Output_Classifier_Definition']


def _create_output_feature_service( output_name, task):
    pass
    #
    # ok = self._gis.content.is_service_name_available(output_name, "Feature Service")
    # if not ok:
    #     raise RuntimeError("A Feature Service by this name already exists: " + output_name)
    #
    # createParameters = {
    #     "currentVersion": 10.2,
    #     "serviceDescription": "",
    #     "hasVersionedData": False,
    #     "supportsDisconnectedEditing": False,
    #     "hasStaticData": True,
    #     "maxRecordCount": 2000,
    #     "supportedQueryFormats": "JSON",
    #     "capabilities": "Query",
    #     "description": "",
    #     "copyrightText": "",
    #     "allowGeometryUpdates": False,
    #     "syncEnabled": False,
    #     "editorTrackingInfo": {
    #         "enableEditorTracking": False,
    #         "enableOwnershipAccessControl": False,
    #         "allowOthersToUpdate": True,
    #         "allowOthersToDelete": True
    #     },
    #     "xssPreventionInfo": {
    #         "xssPreventionEnabled": True,
    #         "xssPreventionRule": "InputOnly",
    #         "xssInputRule": "rejectInvalid"
    #     },
    #     "tables": [],
    #     "name": output_name,
    #     "options": {
    #         "dataSourceType": "spatiotemporal"
    #     }
    # }
    #
    # output_service = self._gis.content.create_service(output_name, create_params=createParameters,
    #                                                   service_type="featureService")
    # description = "Feature Service generated from running the " + task + " tool."
    # item_properties = {
    #     "description": description,
    #     "tags": "Analysis Result, " + task,
    #     "snippet": "Analysis Feature Service generated from " + task
    # }
    # output_service.update(item_properties)
    # return output_service


def convert_raster_to_feature(
                              input_raster,
                              output_name,
                              field="Value",
                              output_type="Point",
                              simplify_lines_or_polygons=True,
                              context=None):
    """
    This service tool converts imagery data to feature class vector data.

    Parameters
    ----------
    input_raster : Required string

    output_name : Required string

    field : Optional string

    output_type : Optional string
        One of the following: ['Point', 'Line', 'Polygon']
    simplify_lines_or_polygons : Optional bool

    context : Optional string


    Returns
    -------
    output_feature : layer (Feature Service item)
    """
    pass
    #
    # task = "Convert Raster To Feature"
    #
    # params = {}
    #
    # params["inputRaster"] = input_raster
    #
    # output_service = self._create_output_feature_service(output_name, task)
    #
    # params["outputName"] = json.dumps({"serviceProperties": {"name": output_name, "serviceUrl": output_service.url},
    #                                    "itemProperties": {"itemId": output_service.itemid}})
    # if field is not None:
    #     params["field"] = field
    # if output_type is not None:
    #     params["outputType"] = output_type
    # if simplify_lines_or_polygons is not None:
    #     params["simplifyLinesOrPolygons"] = simplify_lines_or_polygons
    # if context is not None:
    #     params["context"] = context
    #
    # task_url, job_info = super()._analysis_job(task, params)
    #
    # job_info = super()._analysis_job_status(task_url, job_info)
    # job_values = super()._analysis_job_results(task_url, job_info)
    # # print(job_values)
    # item_properties = {
    #     "properties": {
    #         "jobUrl": task_url + '/jobs/' + job_info['jobId'],
    #         "jobType": "GPServer",
    #         "jobId": job_info['jobId'],
    #         "jobStatus": "completed"
    #     }
    # }
    # output_service.update(item_properties)
    # return output_service
