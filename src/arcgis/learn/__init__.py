"Functions for calling the Deep Learning Tools." 

from arcgis.geoprocessing._support import _analysis_job, _analysis_job_results, \
                                          _analysis_job_status, _layer_input
import json as _json
import arcgis as _arcgis
import string as _string
import random as _random
from arcgis.gis import Item
from .models import *


def _set_param(gis, params, param_name, input_param):
    if isinstance(input_param, str):
        if 'http:' in input_param or 'https:' in input_param:
            params[param_name] = _json.dumps({ 'url' : input_param })
        else:
            params[param_name] = _json.dumps({ 'uri' : input_param })

    elif isinstance(input_param, Item):
        params[param_name] = _json.dumps({ "itemId" : input_param.itemid })

    elif isinstance(input_param, dict):
        params[param_name] =  input_param
    elif isinstance(input_param, Model):
        params[param_name] = input_param._model
    else:
        raise TypeError(input_param+" should be a string (service url) or Item")

    return


def _id_generator(size=6, chars=_string.ascii_uppercase + _string.digits):
    return ''.join(_random.choice(chars) for _ in range(size))


def _set_context(params):
    out_sr = _arcgis.env.out_spatial_reference
    process_sr = _arcgis.env.process_spatial_reference
    out_extent = _arcgis.env.analysis_extent

    context = {}
    set_context = False

    if out_sr is not None:
        context['outSR'] = {'wkid': int(out_sr)}
        set_context = True
    if out_extent is not None:
        context['extent'] = out_extent
        set_context = True
    if process_sr is not None:
        context['processSR'] = {'wkid': int(process_sr)}
        set_context = True

    if set_context:
        params["context"] = _json.dumps(context)
        
def _create_output_image_service(gis, output_name, task):
    ok = gis.content.is_service_name_available(output_name, "Image Service")
    if not ok:
        raise RuntimeError("An Image Service by this name already exists: " + output_name)

    create_parameters = {
        "name": output_name,
        "description": "",
        "capabilities": "Image",
        "properties": {
            "path": "@",
            "description": "",
            "copyright": ""
        }
    }

    output_service = gis.content.create_service(output_name, create_params=create_parameters,
                                                      service_type="imageService")
    description = "Image Service generated from running the " + task + " tool."
    item_properties = {
        "description": description,
        "tags": "Analysis Result, " + task,
        "snippet": "Analysis Image Service generated from " + task
    }
    output_service.update(item_properties)
    return output_service

def _create_output_feature_service(gis, output_name, output_service_name='Analysis feature service', task='GeoAnalytics'):
    ok = gis.content.is_service_name_available(output_name, 'Feature Service')
    if not ok:
        raise RuntimeError("A Feature Service by this name already exists: " + output_name)

    createParameters = {
            "currentVersion": 10.2,
            "serviceDescription": "",
            "hasVersionedData": False,
            "supportsDisconnectedEditing": False,
            "hasStaticData": True,
            "maxRecordCount": 2000,
            "supportedQueryFormats": "JSON",
            "capabilities": "Query",
            "description": "",
            "copyrightText": "",
            "allowGeometryUpdates": False,
            "syncEnabled": False,
            "editorTrackingInfo": {
                "enableEditorTracking": False,
                "enableOwnershipAccessControl": False,
                "allowOthersToUpdate": True,
                "allowOthersToDelete": True
            },
            "xssPreventionInfo": {
                "xssPreventionEnabled": True,
                "xssPreventionRule": "InputOnly",
                "xssInputRule": "rejectInvalid"
            },
            "tables": [],
            "name": output_service_name.replace(' ', '_')
        }

    output_service = gis.content.create_service(output_name, create_params=createParameters, service_type="featureService")
    description = "Feature Service generated from running the " + task + " tool."
    item_properties = {
            "description" : description,
            "tags" : "Analysis Result, " + task,
            "snippet": output_service_name
            }
    output_service.update(item_properties)
    return output_service


def detect_objects(input_raster,
                    model,
                    model_arguments=None,
                    output_name=None,
                    context = None,
                    gis=None):

    """
    Function can be used to generate feature service that contains polygons on detected objects 
    found in the imagery data using the designated deep learning model. Note that the deep learning 
    library needs to be installed separately, in addition to the server’s built in Python 3.x library.

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    input_raster           Required. raster layer that contains objects that need to be detected.
    ------------------     --------------------------------------------------------------------
    model                  Required model object. 
    ------------------     --------------------------------------------------------------------
    model_arguments        Optional dictionary. Name-value pairs of arguments and their values that can be customized by the clients.
                           eg: {"name1":"value1", "name2": "value2"}

    ------------------     --------------------------------------------------------------------
    output_name            Optional. If not provided, an Feature layer is created by the method and used as the output .
                           You can pass in an existing Feature Service Item from your GIS to use that instead.
                           Alternatively, you can pass in the name of the output Feature Service that should be created by this method
                           to be used as the output for the tool.
                           A RuntimeError is raised if a service by that name already exists
    ------------------     --------------------------------------------------------------------
    context                Optional. Context contains additional settings that affect task execution. 
                           1. Output Spatial Reference (outSR)—the output features will be projected into 
                           the output spatial reference. 
                           2. Snap Raster 
                           
                           Syntax: {"outSR" : {spatial reference} }

    ------------------     --------------------------------------------------------------------
    gis                    Optional GIS. The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The feature layer

    """


    task = "DetectObjectsUsingDeepLearning"

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.rasterAnalytics.url
    gptool = _arcgis.gis._GISResource(url, gis)
    
    params = {}

    params["inputRaster"] = _layer_input(input_raster)

    if output_name is None:
        output_service_name = 'DetectObjectsUsingDeepLearning_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_feature_service(gis, output_name, output_service_name, 'Convert Raster To Feature')

    params["outputObjects"] = _json.dumps({"serviceProperties": {"name": output_service_name, "serviceUrl": output_service.url},
                                       "itemProperties": {"itemId": output_service.itemid}})

    if model is None:
        raise RuntimeError('model cannot be None')
    else:
        _set_param(gis, params, "model", model)

    if model_arguments:
        params["modelArguments"] = model_arguments

    _set_context(params)

    task_url, job_info, job_id = _analysis_job(gptool, task, params)

    job_info = _analysis_job_status(gptool, task_url, job_info)
    job_values = _analysis_job_results(gptool, task_url, job_info, job_id)
    item_properties = {
        "properties": {
            "jobUrl": task_url + '/jobs/' + job_info['jobId'],
            "jobType": "GPServer",
            "jobId": job_info['jobId'],
            "jobStatus": "completed"
        }
    }
    output_service.update(item_properties)
    return output_service


def classify_pixels(input_raster,
                    model,
                    model_arguments=None,
                    output_name=None,
                    context=None,
                    gis=None):

    """
    Function to classify input imagery data using a deep learning model. 
    Note that the deep learning library needs to be installed separately, 
    in addition to the server’s built in Python 3.x library.

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    input_raster           Required. raster layer that needs to be classified
    ------------------     --------------------------------------------------------------------
    model                  Required model object. 
    ------------------     --------------------------------------------------------------------
    model_arguments        Optional dictionary. Name-value pairs of arguments and their values that can be customized by the clients.
                           eg: {"name1":"value1", "name2": "value2"}

    ------------------     --------------------------------------------------------------------
    output_name            Optional. If not provided, an imagery layer is created by the method and used as the output .
                           You can pass in an existing Image Service Item from your GIS to use that instead.
                           Alternatively, you can pass in the name of the output Image Service that should be created by this method
                           to be used as the output for the tool.
                           A RuntimeError is raised if a service by that name already exists
    ------------------     --------------------------------------------------------------------
    context                Context contains additional settings that affect task execution. 
                           1. Output Spatial Reference (outSR)—the output features will be projected into 
                           the output spatial reference. 
                           2. Snap Raster 
                           
                           Syntax: {"outSR" : {spatial reference} }

    ------------------     --------------------------------------------------------------------
    gis                    Optional GIS. The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The classified imagery layer item

    """


    task = "ClassifyPixelsUsingDeepLearning"

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.rasterAnalytics.url
    gptool = _arcgis.gis._GISResource(url, gis)

    output_service = None

    if output_name is None:
        output_name = task + '_' + _id_generator()
        output_service = _create_output_image_service(gis, output_name, task)
        output_raster = _json.dumps({"serviceProperties": {"name" : output_service.name, "serviceUrl" : output_service.url}, "itemProperties": {"itemId" : output_service.itemid}}) 
    elif isinstance(output_name, str):
        output_service = _create_output_image_service(gis, output_name, task)
        output_raster = _json.dumps({"serviceProperties": {"name" : output_service.name, "serviceUrl" : output_service.url}, "itemProperties": {"itemId" : output_service.itemid}}) 
    elif isinstance(output_name, _arcgis.gis.Item):
        output_service = output_name
        output_raster = _json.dumps({"itemId":output_service.itemid})
    else:
        raise TypeError("output_raster should be a string (service name) or Item")

    params = {}

    params["outputClassifiedRaster"] = output_raster

    params["inputRaster"] = _layer_input(input_raster)

    if model is None:
        raise RuntimeError('model cannot be None')
    else:
        _set_param(gis, params, "model", model)

    if model_arguments:
        params["modelArguments"] = model_arguments

    _set_context(params)
    task_url, job_info, job_id = _analysis_job(gptool, task, params)

    job_info = _analysis_job_status(gptool, task_url, job_info)
    job_values = _analysis_job_results(gptool, task_url, job_info, job_id)
    item_properties = {
        "properties": {
            "jobUrl": task_url + '/jobs/' + job_info['jobId'],
            "jobType": "GPServer",
            "jobId": job_info['jobId'],
            "jobStatus": "completed"
        }
    }
    output_service.update(item_properties)
    return output_service


def export_training_data(input_raster,
                        input_class_data=None,
                        chip_format=None,
                        tile_size=None,
                        stride_size=None,
                        metadata_format = None,
                        classvalue_field = None,
                        buffer_radius = None,
                        output_location = None,
                        context = None,                
                        gis=None):

    """
    Function is designed to generate training sample image chips from the input imagery data with 
    labeled vector data or classified images. The output of this service tool is the data store string 
    where the output image chips, labels and metadata files are going to be stored.

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    input_raster           Required. raster layer that needs to be exported for training
    ------------------     --------------------------------------------------------------------
    input_class_data       Labeled data, either a feature layer or image layer. 
                           Vector inputs should follow a training sample format as 
                           generated by the ArcGIS Pro Training Sample Manager. 
                           Raster inputs should follow a classified raster format as generated by the Classify Raster tool.
    ------------------     --------------------------------------------------------------------
    chip_format            Optional String. The raster format for the image chip outputs. 
                           - TIFF: TIFF format 
                           - PNG: PNG format
                           - JPEG: JPEG format 
                           - MRF: MRF (Meta Raster Format)

    ------------------     --------------------------------------------------------------------
    tile_size              Optional dictionary. The size of the image chips.
                           Example: {"x": 256, "y": 256}
    ------------------     --------------------------------------------------------------------
    stride_size            Optional dictionary.
                           The distance to move in the X and Y when creating the next image chip. 
                           When stride is equal to the tile size, there will be no overlap. 
                           When stride is equal to half of the tile size, there will be 50% overlap.
                           Example: {"x": 128, "y": 128}
    ------------------     --------------------------------------------------------------------
    metadata_format        Optional string. The format of the output metadata labels. There are 4 options for output metadata labels for the training data,
                           KITTI Rectangles, PASCAL VOCrectangles, Classified Tiles (a class map) and RCNN_Masks. If your input training sample data
                           is a feature class layer such as building layer or standard classification training sample file, 
                           use the KITTI or PASCAL VOC rectangle option. 
                           The output metadata is a .txt file or .xml file containing the training sample data contained 
                           in the minimum bounding rectangle. The name of the metadata file matches the input source image 
                           name. If your input training sample data is a class map, use the Classified Tiles as your output metadata format option. 
                           - KITTI_rectangles: The metadata follows the same format as the Karlsruhe Institute of Technology and Toyota 
                           Technological Institute (KITTI) Object Detection Evaluation dataset. The KITTI dataset is a vision benchmark suite. 
                           This is the default.The label files are plain text files. All values, both numerical or strings, are separated by 
                           spaces, and each row corresponds to one object. 
                           - PASCAL_VOC_rectangles: The metadata follows the same format as the Pattern Analysis, Statistical Modeling and 
                           Computational Learning, Visual Object Classes (PASCAL_VOC) dataset. The PASCAL VOC dataset is a standardized 
                           image data set for object class recognition.The label files are XML files and contain information about image name, 
                           class value, and bounding box(es). 
                           - Classified_Tiles: This option will output one classified image chip per input image chip. 
                           No other meta data for each image chip. Only the statistics output has more information on the 
                           classes such as class names, class values, and output statistics. 
                           - RCNN_Masks: This option will output image chips that have a mask on the areas where the sample exists. 
                           The model generates bounding boxes and segmentation masks for each instance of an object in the image. 
                           It's based on Feature Pyramid Network (FPN) and a ResNet101 backbone.
    ------------------     --------------------------------------------------------------------
    classvalue_field        Optional string. Specifies the field which contains the class values. If all field is specified, 
                            the system will look for a ‘value’ or ‘classvalue’ field. If this feature does 
                            not contain a class field, the system will presume all records belong the 1 class.

    ------------------     --------------------------------------------------------------------
    buffer_radius          Optional integer. Specifies a radius for point feature classes to specify training sample area.

    ------------------     --------------------------------------------------------------------
    output_location        This is the output location for training sample data. 
                           It can be the server data store path or a shared file system path. 
                           Example: 
                           Server datastore path - 
                            /fileshare/deeplearning/rooftoptrainingsamples 
                            /cloudstore/s3deeplearning/rooftoptrainingsamples 
                            
                            File share path – \\\\servername\\deeplearning\\rooftoptrainingsamples
    ------------------     --------------------------------------------------------------------
    context                Context contains additional settings that affect task execution. 
                           1. exportAllTiles - Choose if the image chips with overlapped labeled data will be exported. 
                              true - Export all the image chips, including those that do not overlap labeled data. This is the default. 
                              false - Export only the image chips that overlap the labelled data. 
                           2. startIndex - Allows you to set the start index for the sequence of image chips. 
                              This lets you append more image chips to an existing sequence. The default value is 0. 
                              Syntax: {"exportAllTiles" : true, "startIndex": 0 }

                           3. cellSize - cell size can be set using this key in context parameter
    ------------------     --------------------------------------------------------------------
    gis                    Optional GIS. The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The classified imagery layer item

    """

    task = "ExportTrainingDataforDeepLearning"

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.rasterAnalytics.url
    gptool = _arcgis.gis._GISResource(url, gis)

    params = {}

    if output_location:
        params["outputLocation"] = output_location
    else:
        raise RuntimeError("output_location cannot be None")

    if input_raster:
        params["inputRaster"] = _layer_input(input_raster)
    else:
        raise RuntimeError("input_raster cannot be None")

    if input_class_data:
        params["inputClassData"] = _layer_input(input_class_data)

    if chip_format is not None:
        chipFormatAllowedValues = ['TIFF', 'PNG', 'JPEG','MRF']
        if not chip_format in chipFormatAllowedValues:
            raise RuntimeError('chip_format can only be one of the following: '+ str(chipFormatAllowedValues))
        params["chipFormat"] = chip_format

    if tile_size:
        params["tileSize"] = tile_size

    if stride_size:
        params["strideSize"] = stride_size

    if metadata_format is not None:
        metadataFormatAllowedValues = ['KITTI_rectangles', 'PASCAL_VOC_rectangles', 'Classified_Tiles', 'RCNN_Masks']
        if not metadata_format in metadataFormatAllowedValues:
            raise RuntimeError('metadata_format can only be one of the following: '+ str(metadataFormatAllowedValues))

        params['metadataFormat'] = metadata_format

    if buffer_radius is not None:
        params["bufferRadius"]= buffer_radius
    
    if classvalue_field is not None:
        params["classValueField"]= classvalue_field

    if context is not None:
        params["context"] = context

    task_url, job_info, job_id = _analysis_job(gptool, task, params)

    job_info = _analysis_job_status(gptool, task_url, job_info)
    job_values = _analysis_job_results(gptool, task_url, job_info, job_id)
    item_properties = {
        "properties": {
            "jobUrl": task_url + '/jobs/' + job_info['jobId'],
            "jobType": "GPServer",
            "jobId": job_info['jobId'],
            "jobStatus": "completed"
        }
    }
    return job_values["outLocation"]



