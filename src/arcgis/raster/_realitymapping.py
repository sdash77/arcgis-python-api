"""
The realitymapping python API allows automating realitymapping tasks in the server environment.

For more information about realitymapping workflows in ArcGIS, please visit the help documentation at
`Realitymapping in ArcGIS <https://pro.arcgis.com/en/pro-app/latest/help/data/imagery/reality-mapping-in-arcgis-pro.htm>`_

"""

from __future__ import annotations
from typing import Any, Optional, Union
import arcgis
import json
from arcgis.gis import GIS, Item
import collections
from ._util import _flatten_adjust_settings, _nestify_context, _validate_settings, _update_settings, get_request, post_request
import string as _string
import random as _random

from arcgis.geoprocessing._support import (
    _analysis_job,
    _analysis_job_results,
    _analysis_job_status,
    _layer_input,
)
from arcgis.features.layer import FeatureLayer
import requests


###################################################################################################
###
### INTERNAL FUNCTIONS
###
###################################################################################################


def _execute_task(gis, taskname, params):
    gptool_url = gis.properties.helperServices.realityMapping.url
    gptool = arcgis.gis._GISResource(gptool_url, gis)
    task = taskname

    task_url, job_info, job_id = _analysis_job(gptool, task, params)
    # print ('task url is ', task_url)

    job_info = _analysis_job_status(gptool, task_url, job_info)
    job_values = _analysis_job_results(gptool, task_url, job_info, job_id)

    item_properties = {
        "properties": {
            "jobUrl": task_url + "/jobs/" + job_info["jobId"],
            "jobType": "GPServer",
            "jobId": job_info["jobId"],
            "jobStatus": "completed",
        }
    }
    return job_values


def _id_generator(size=6, chars=_string.ascii_uppercase + _string.digits):
    return "".join(_random.choice(chars) for _ in range(size))


###################################################################################################
###################################################################################################
def _create_project(
    name: str,
    sensor_type: str = "Drone",
    scenario_type: str = "Drone",
    *,
    gis: Optional[GIS] = None,
    future: Optional[bool] = False,
    **kwargs,
):
    """
    Creates a new realitymapping project item on your enterprise.
    This project item can be specified as input to the realitymapping functions as value to the
    image_collection parameter.

    The realitymapping project item can be opened in Reality Maker web app.
    The RMProject includes all project inputs, ancillary data such as image footprints and block adjustment reports,
    intermediate products such as image collections, quick block adjustment results, final products,
    and status at each stage of processing.

    The create_project method also creates a new folder and adds the realitymapping project item to it.
    All the realitymapping products such as the image collection, orthomosaic products etc will be added in the
    same folder. The folder name will be same the project name with the prefix "_realitymapping_"

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    name                   Required string. The name of the project item to be created.
    ------------------     --------------------------------------------------------------------
    definition             Optional dictionary.  The project definition dictionary.
                        the definition contais the template informatios such as adjustSettings,
                        processingStates, rasterType, information about the flights.
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The realitymapping project item

    """

    gis = arcgis.env.active_gis if gis is None else gis

    if sensor_type and sensor_type.lower() not in [
        "drone",
        "satellite",
        "aerialdigital",
        "aerialscanned",
    ]:
        raise RuntimeError(
            "Invalid sensor type. Supported values are 'Drone', 'Satellite', 'AerialDigital', 'AerialScanned'"
        )
    if scenario_type and scenario_type.lower() not in [
        "drone",
        "aerial_nadir",
        "aerial_oblique",
    ]:
        raise RuntimeError(
            "Invalid scenario type. Supported values are 'Drone', 'Aerial_Nadir', 'Aerial_Oblique'"
        )
    if (
        sensor_type
        and sensor_type.lower() == "aerialdigital"
        and scenario_type.lower()
        not in [
            "aerial_nadir",
            "aerial_oblique",
        ]
    ):
        raise RuntimeError(
            "Invalid scenario type for Aerial Digital sensor. Supported values are 'Aerial_Nadir', 'Aerial_Oblique'"
        )
    if sensor_type and sensor_type.lower() == "satellite":
        scenario_type = ""

    gis = arcgis.env.active_gis if gis is None else gis
    from ._util import _initialize_project
    project_settings = _initialize_project(sensor_type, scenario_type, is_rm=True)
    project_definition = {"name": name, "processing_settings": project_settings}
    result = gis._tools.realitymapping.create_project(project_definition, future=future, **kwargs)
    item = Item(gis=gis, itemid=result["reality_project"]["itemId"])
    return item


###################################################################################################
###
### PUBLIC API
###
###################################################################################################
def is_supported(gis=None):
    """
    Returns True if the GIS supports realitymapping. If a gis isn't specified,
    checks if :meth:`~arcgis.env.active_gis` supports realitymapping
    """
    gis = arcgis.env.active_gis if gis is None else gis
    if "realityMapping" in gis.properties.helperServices:
        return True
    else:
        return False


###################################################################################################
## Compute Sensor model
###################################################################################################
def compute_sensor_model(
    mission,
    mode: str = "Quick",
    location_accuracy: str = "High",
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    compute_sensor_model computes the bundle block adjustment for the image collection
    and applies the frame xform to the images. It will also generate the control point
    table, solution table, solution points table and flight path table.
    These tables will not be published as Portal items.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    mode                   Optional string.  the mode to be used for bundle block adjustment
                           Only the following modes are supported:

                           - 'Quick' : Computes tie points and adjustment at 8x of the source imagery resolution

                           - 'Full'  : adjust the images in Quick mode then at 1x of the source imagery resolution

                           - 'Refine' : adjust the image at 1x of the source imagery resolution

                           By default, 'Quick' mode is applied to compute the sensor model.
    ------------------     --------------------------------------------------------------------
    location_accuracy      Optional string. this option allows users to specify the GPS location accuracy level of the
                           source image. It determines how far the underline tool will search for neighboring
                           matching images, then calculate tie points and compute adjustments.

                           Possible values for location_accuracy are:

                           - 'VeryHigh'    : Imagery was collected with a high-accuracy, differential GPS, such as RTK or PPK. This option will hold image locations fixed during block adjustment

                           - 'High'    : GPS accuracy is 0 to 10 meters, and the tool uses a maximum of 4 by 3 images

                           - 'Medium'  : GPS accuracy of 10 to 20 meters, and the tool uses a maximum of 4 by 6 images

                           - 'Low'     : GPS accuracy of 20 to 50 meters, and the tool uses a maximum of 4 by 12 images

                           - 'VeryLow' : GPS accuracy is more than 50 meters, and the tool uses a maximum of 4 by 20 images

                           The default location_accuracy is 'High'
    ------------------     --------------------------------------------------------------------
    context                Optional dictionary. The context parameter is used to configure additional client settings
                           for block adjustment. The supported configurable parameters are for compute mosaic dataset
                           candidates after the adjustment.

                           Example:

                               {
                               "computeCandidate": False,
                               "maxoverlap": 0.6,
                               "maxloss": 0.05,
                               }
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The imagery layer url

    """

    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")
    
    image_collection = mission.image_collection
    settings = {}

    try:
        project = mission._project
        project_adj_settings = project.settings
        if (
            isinstance(project_adj_settings, dict)
            and ("template" in project_adj_settings.keys())
            and "adjustSettings" in project_adj_settings["template"].keys()
        ):
            project_adj_settings = project_adj_settings["template"][
                "adjustSettings"
            ]
        keys_to_pop = ["parallelProcessingFactor"]

        if isinstance(context, dict):
            adjust_options = context.pop("adjustOptions", [])
            adjust_options = _flatten_adjust_settings(adjust_options)
            # context is flattened
            context.update(adjust_options)
            # update adj dict with all the params from context
            project_adj_settings.update(context)
            # pop the keys that are not relevant to the adj settings
            for key in keys_to_pop:
                project_adj_settings.pop(key, None)
            # update context with default values from project_adj_settings if they are not present in context
            context.update(project_adj_settings)
            _nestify_context(context)

            if (
                project_adj_settings["locationAccuracy"].lower()
                != location_accuracy.lower()
            ):
                project_adj_settings.update({"locationAccuracy": location_accuracy})
        elif context is None:
            context = dict(project_adj_settings)
            _nestify_context(context)
        # update the settings to update flight json
        settings = project_adj_settings
    except:
        adj_dict = {}
        if isinstance(context, dict):
            context_new = {k.lower(): v for k, v in context.items()}
            adj_keys = [
                "computeCandidate",
                "maxOverlap",
                "maxLoss",
                "maxResidual",
                "initPointResolution",
                "k",
                "p",
                "principalPoint",
                "focalLength",
            ]
            adj_dict = {
                k: context_new[k.lower()]
                for k in adj_keys
                if k.lower() in context_new
            }
            adj_dict.update({"locationAccuracy": location_accuracy})
            settings = adj_dict

    settings.update({"mode": mode})

    return gis._tools.realitymapping.compute_sensor_model(
        image_collection=image_collection,
        mode=mode,
        location_accuracy=location_accuracy,
        context=context,
        future=future,
        **kwargs,
    )


###################################################################################################
## Alter processing states
###################################################################################################
def alter_processing_states(
    mission,
    new_states: dict[str, Any],
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    Alter the processing states of the image collection.
    The states are stored as key property "Orthomapping".
    The content of the state is a dictionary including
    several properties which can be set based on the process
    done on the image collection.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    new_states             Required dictionary. The state to set on the image_collection

                           This a dictionary of states that should be set on the image collection
                           The new states that can be set on the image collection are:
                           blockadjustment, dem, gcp, seamlines, colorcorrection, adjust_index, imagetype

                           Example:

                               | {"blockadjustment": "raw",
                               |  "dem": "Dense_Natual_Neighbor",
                               |  "seamlines":"VORONOI",
                               |  "colorcorrection":"SingleColor",
                               |  "imagetype": "UAV/UAS",
                               |  "adjust_index": 0}
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The result will be the newly set states dictionary

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.alter_processing_states(
        image_collection=image_collection,
        new_states=new_states,
        future=future,
        **kwargs,
    )


###################################################################################################
## Get processing states
###################################################################################################
def get_processing_states(
    mission, *, gis: Optional[GIS] = None, future: bool = False, **kwargs
):
    """
    Retrieve the processing states of the image collection

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The result will be the newly set states dictionary

    """

    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.get_processing_states(
        image_collection=image_collection, future=future, **kwargs
    )


###################################################################################################
## Match control points
###################################################################################################
def match_control_points(
    mission,
    control_points: list[dict[str, Any]],
    similarity: str = "High",
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    The match_control_points is a function that takes a collection of ground control points
    as input (control points to be specified as a list of dictionary objects), and each of the 
    ground control points needs at least one matching tie point in the control point sets. 
    The function will compute the remaining matching tie points for all control point sets.
    
    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    control_points         Required, a list of control point sets objects.

                           The schema of control points follows the schema 
                           of the mosaic dataset control point table. 

                           The control point object should contain the point geometry, pointID, type, status and the
                           imagePoints. (the imagePoints attribute inside the control points object lists the imageIDs)

                           -- pointID (int) - The ID of the point within the control point table.

                           -- type (int)    - The type of the control point as determined by its numeric value

                                                 1: Tie Point 
                                                 2: Ground Control Point.
                                                 3: Check Point

                           -- status (int)  - The status of the point. A value of 0 indicates that the point will not be used in computation. A non-zero value indicates otherwise.

                           -- imageID (int) - Image identification using the ObjectID from the mosaic dataset footprint table.

                           Example:

                               | [{
                               | "status": 1,
                               | "type": 2,
                               | "x": -117.0926538,
                               | "y": 34.00704253,
                               | "z": 634.2175,
                               | "spatialReference": {
                               |     "wkid": 4326
                               | }, // default WGS84
                               | "imagePointSpatialReference": {}, // default ICS
                               | "pointId": 1,
                               | "xyAccuracy": "0.008602325",
                               | "zAccuracy": "0.015",
                               | "imagePoints": [{
                               |     "imageID": 1,
                               |     "x": 2986.5435987557084,
                               |     "y": -2042.5193648409431,
                               |     "u": 3057.4580682832734,
                               |     "v": -1909.1506872159698
                               | },
                               | {
                               |     "imageID": 2,
                               |     "x": 1838.2814361401108,
                               |     "y": -2594.5280063817972,
                               |     "u": 3059.4079724863363,
                               |     "v": -2961.292545463305
                               | },
                               | {
                               |     "imageID": 12,
                               |     "x": 5332.855578204663,
                               |     "y": -2533.2805429751907,
                               |     "u": 614.2338676573158,
                               |     "v": -165.10836768947297
                               | },
                               | {
                               |     "imageID": 13,
                               |     "x": 4932.0895715254455,
                               |     "y": -1833.8401744114287,
                               |     "u": 616.9396928182223,
                               |     "v": -1243.1445126959693
                               | }]
                               | },
                               | …
                               | …
                               | ] 
    ------------------     --------------------------------------------------------------------
    similarity             Optional string. Choose the tolerance level for your control point matching. 

                           - Low- The similarity tolerance for finding control points will be low. \
                           This option will produce the most control points, \
                           but some may have a higher level of error. 

                           - Medium - The similarity tolerance for finding control points will be medium.
                           
                           - High - The similarity tolerance for finding control points will be high. \
                           This option will produce the least number of control points, \
                           but each matching pair will have a lower level of error. This is the default. 
    ------------------     --------------------------------------------------------------------
    context                Optional dictionary.Additional settings such as the input control points 
                           spatial reference can be specified here. 

                           For Example:

                                {"groundControlPointsSpatialReference": {"wkid": 3459}, "imagePointSpatialReference": {"wkid": 3459}}

                           Note: The ground control points spatial reference and image point spatial reference 
                           spatial reference set in the context parameter is to decide the returned point set's 
                           ground control points spatial reference and image point spatial reference. 
                           If these two parameters are not set here, the tool will use the spatial reference 
                           defined in the input point set. And if no spatial reference is defined in the point set,
                           then the default ground control points coordinates are in lon/lat and image points 
                           coordinates are in image coordinate system. 
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        A list of dictionary objects

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.match_control_points(
        image_collection=image_collection,
        control_points=control_points,
        similarity=similarity,
        context=context,
        future=future,
        **kwargs,
    )


###################################################################################################
## Compute Control Points
###################################################################################################
def compute_control_points(
    mission,
    reference_image=None,
    image_location_accuracy: str = "High",
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This service tool is used for computing matching control points between images
    within an image collection and/or matching control points between the image 
    collection images and the reference image.
    `Compute Control Points <https://pro.arcgis.com/en/pro-app/tool-reference/data-management/compute-control-points.htm>`_
    
    ====================================    ====================================================================
    **Parameter**                            **Description**
    ------------------------------------    --------------------------------------------------------------------
    mission                                 Required, the input mission. The mission must be a 
                                            :class:`~arcgis.raster.realitymapping.RMMission` object.

                                            The mission must exist.
    ------------------------------------    --------------------------------------------------------------------
    reference_image                         This is the reference image service that can be used to generate ground control 
                                            points set with the image service. 
                                            It can be a portal Item or an image service URL or a URI
    ------------------------------------    --------------------------------------------------------------------
    image_location_accuracy                 Optional string. This option allows you to specify the GPS location accuracy 
                                            level of the source image. It determines how far the tool will search for 
                                            neighboring matching images for calculating tie points and block adjustments. 
                                            
                                            The following are the available options:
                                            Low, Medium, High

                                            - Low- GPS accuracy of 20 to 50 meters, and the tool uses a maximum of 4 by 12 images. 

                                            - Medium- GPS accuracy of 10 to 20 meters, and the tool uses a maximum of 4 by 6 images. 

                                            - High- GPS accuracy of 0 to 10 meters, and the tool uses a maximum of 4 by 3 images.

                                            If the image collection is created from satellite data, it will be automatically switched 
                                            to use RPC adjustment mode. In this case, the mode need not be explicitly set by the user.

                                            Default is High
    ------------------------------------    --------------------------------------------------------------------
    context                                 Optional dictionary. Context contains additional environment settings that affect 
                                            output control points generation. 
                                            
                                            Possible keys and their possible values are: 

                                            pointSimilarity- Sets LOW, MEDIUM, or HIGH tolerance for computing control points with varying levels of potential error.
                                                             
                                            - LOW tolerance will produce the most control point, but may have a higher \
                                              level of error.

                                            - HIGH tolerance will produce the least number of control point, \
                                              but each matching pair will have a lower level of error.

                                            - MEDIUM tolerance will set the similarity tolerance to medium.

                                            pointDensity- Sets the number of tie points (LOW, MEDIUM, or HIGH), to be created. 
                                                          
                                            - LOW point density will create the fewest number of tie points. \

                                            - MEDIUM point density will create a moderate number of tie points. \

                                            - HIGH point density will create the highest number of tie points. \

                                            pointDistribution- Randomly generates points that are better for overlapping areas with irregular shapes.
                                                               
                                            - RANDOM- will generate points that are better for overlapping areas \
                                              with irregular shapes.

                                            - REGULAR- will generate points based on a \
                                              fixed pattern and uses the point density to determine how frequently to create points.

                                            Example:

                                                {
                                                "pointSimilarity":"MEDIUM",
                                                "pointDensity": "MEDIUM",
                                                "pointDistribution": "RANDOM"
                                                }
    ------------------------------------    --------------------------------------------------------------------
    gis                                     Optional :class:`~arcgis.gis.GIS` . the GIS on which this tool runs. If not specified, the active GIS is used.
    ====================================    ====================================================================

    :return:
        The imagery layer url

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.compute_control_points(
        image_collection=image_collection,
        reference_image=reference_image,
        image_location_accuracy=image_location_accuracy,
        context=context,
        future=future,
        **kwargs,
    )


###################################################################################################
## Edit control points
###################################################################################################
def edit_control_points(
    mission,
    control_points: list[dict[str, Any]],
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This service can be used to append additional ground control point sets to
    the image collection's control points. It is recommended that a ground control point (GCP) set
    should contain one ground control point and multiple tie points.
    The service tool can also be used to edit tie point sets.
    The input control points dictionary will always replace the points in the tie points
    table if the point IDs already exist.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    control_points         Required, a list of control point sets objects.

                           The schema of control points follows the schema
                           of the mosaic dataset control point table.

                           The control point object should contain the point geometry, pointID, type, status and the
                           imagePoints. (the imagePoints attribute inside the control points object lists the imageIDs)

                           -- pointID (int) - The ID of the point within the control point table.

                           -- type (int)    - The type of the control point as determined by its numeric value

                                                 1: Tie Point
                                                 2: Ground Control Point.
                                                 3: Check Point

                           -- status (int)  - The status of the point. A value of 0 indicates that the point will not be used in computation. A non-zero value indicates otherwise.

                           -- imageID (int) - Image identification using the ObjectID from the mosaic dataset footprint table.

                           Example:

                               | [{
                               | "status": 1,
                               | "type": 2,
                               | "x": -117.0926538,
                               | "y": 34.00704253,
                               | "z": 634.2175,
                               | "spatialReference": {
                               |     "wkid": 4326
                               | }, // default WGS84
                               | "imagePointSpatialReference": {}, // default ICS
                               | "pointId": 1,
                               | "xyAccuracy": "0.008602325",
                               | "zAccuracy": "0.015",
                               | "imagePoints": [{
                               |     "imageID": 1,
                               |     "x": 2986.5435987557084,
                               |     "y": -2042.5193648409431,
                               |     "u": 3057.4580682832734,
                               |     "v": -1909.1506872159698
                               | },
                               | {
                               |     "imageID": 2,
                               |     "x": 1838.2814361401108,
                               |     "y": -2594.5280063817972,
                               |     "u": 3059.4079724863363,
                               |     "v": -2961.292545463305
                               | },
                               | {
                               |     "imageID": 12,
                               |     "x": 5332.855578204663,
                               |     "y": -2533.2805429751907,
                               |     "u": 614.2338676573158,
                               |     "v": -165.10836768947297
                               | },
                               | {
                               |     "imageID": 13,
                               |     "x": 4932.0895715254455,
                               |     "y": -1833.8401744114287,
                               |     "u": 616.9396928182223,
                               |     "v": -1243.1445126959693
                               | }]
                               | },
                               | …
                               | …
                               | ]


    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The Imagery layer url

    """

    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.edit_control_points(
        image_collection=image_collection,
        input_control_points=control_points,
        future=future,
        **kwargs,
    )


###################################################################################################
## Generate orthomosaic
###################################################################################################
def generate_orthomosaic(
    mission,
    out_ortho,
    regen_seamlines: bool = True,
    recompute_color_correction: bool = True,
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    Function can be used for generating single ortho-rectified mosaicked image from image collection after
    the block adjustment.

    ===================================    ====================================================================
    **Parameter**                           **Description**
    -----------------------------------    --------------------------------------------------------------------
    mission                                Required, the input mission. The mission must be a 
                                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                                           The mission must exist.
    -----------------------------------    --------------------------------------------------------------------
    out_ortho                               Required. This is the ortho-mosaicked image converted from the image
                                            collection after the block adjustment.
                                            It can be a url, uri, portal item, or string representing the name of output dem
                                            (either existing or to be created.)
                                            Like Raster Analysis services, the service can be an existing multi-tenant service URL.
    -----------------------------------    --------------------------------------------------------------------
    regen_seamlines                        Optional, boolean.
                                           Choose whether to apply seamlines before the orthomosaic image generation or not.
                                           The seamlines will always be regenerated if this parameter is set to True.
                                           The user can set the seamline options through the context parameter.
                                           If the seamline generation options are not set, the default will be used.

                                           Default value is True
    -----------------------------------    --------------------------------------------------------------------
    recompute_color_correction              Optional, boolean.
                                            Choose whether to apply color correction settings to the output ortho-image or not.
                                            Color correction will always be recomputed if this option is set to True.
                                            The user can configure the compute color correction settings through the context parameter.
                                            If there is no color collection setting, the default will be used.

                                            Default value is True
    -----------------------------------    --------------------------------------------------------------------
    context                                Optional dictionary. Context contains additional environment settings that affect output
                                           image. The supported environment settings for this tool are:

                                           1. Output Spatial Reference (outSR)-the output features will
                                              be projected into the output spatial reference.

                                           2. Extent (extent) - extent that would clip or expand the output image

                                           3. Cell Size (cellSize) - The output raster will have the resolution specified by cell size.

                                           4. Compute Seamlines (seamlinesMethod) - Default.

                                           5. Clipping Geometry (clippingGeometry) - Clips the orthomosaic image to an area of
                                              interest defined by the geometry.

                                           6. Orthomosaic As Overview (orthoMosaicAsOvr) - Adds the orthomosaic as an overview of the image collection.

                                           7. Compute Color Correction (colorcorrectionMethod) — Default.

                                           Example:

                                               | {
                                               |   "outSR": {"wkid": 3516},
                                               |   "extent": {"xmin": 470614.263139,
                                               |             "ymin": 8872849.409968,
                                               |             "xmax": 532307.351827,
                                               |             "ymax": 8920205.372412,
                                               |             "spatialReference": {"wkid": 32628}},
                                               |   "clippingGeometry": {},
                                               |   "orthoMosaicAsOvr": False,
                                               |   "seamlinesMethod": "VORONOI",
                                               |   "minRegionSize": 100,
                                               |   "pixelSize": "",
                                               |   "blendType": "Both",
                                               |   "blendWidth": None,
                                               |   "blendUnit": "Pixels",
                                               |   "requestSize": 1000,
                                               |   "minThinnessRatio": 0.05,
                                               |   "maxSliverSize": 20
                                               |   "colorCorrectionMethod": "DODGING",
                                               |   "dodgingSurface": "Single_Color",
                                               |   "referenceImg": {"url": "``https://...``"},
                                               |   "skipRows": 10,
                                               |   "skipCols": 10,
                                               |   "reCalculateSats": "OVERWRITE"
                                               |  }
    -----------------------------------    --------------------------------------------------------------------
    gis                                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ===================================    ====================================================================

    :return:
        The Orthomosaicked Imagery layer item

    """
    gis = arcgis.env.active_gis if gis is None else gis

    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    if mission.workspace:
        if context:
            context["workspace"] = mission.workspace
        else:
            context = {"workspace": mission.workspace}

    if kwargs is not None:
        if "folder" in kwargs:
            folder = kwargs["folder"]
        else:
            for f in gis.users.me.folders:
                if f._fid == image_collection.ownerFolder:
                    folder = f.properties
                    break
        kwargs.update({"folder": folder})

    color_balance_keys = [
        "targetRaster",
        "skipX",
        "skipY",
        "overwriteStats",
        "dodgingSurface",
        "colorCorrectionMethod",
    ]
    color_balance_dict = {}
    color_balance_dict.update(
        {
            "colorBalance": {
                "skipX": 0,
                "skipY": 0,
                "overwriteStats": "SKIP_EXISTING",
                "colorCorrectionMethod": "DODGING",
                "dodgingSurface": "SINGLE_COLOR",
                "targetImage": "",
            }
        }
    )

    ortho_dict = {}
    if isinstance(context, dict):
        context_new = {k.lower(): v for k, v in context.items()}
        color_balance_dict["colorBalance"].update(
            {
                k: context_new[k.lower()]
                for k in color_balance_keys
                if k.lower() in context_new
            }
        )
        if "colorCorrectionMethod" in color_balance_dict["colorBalance"]:
            color_balance_dict["colorBalance"]["method"] = color_balance_dict[
                "colorBalance"
            ].pop("colorCorrectionMethod")
        if "dodgingSurface" in color_balance_dict["colorBalance"]:
            color_balance_dict["colorBalance"]["surfaceType"] = color_balance_dict[
                "colorBalance"
            ].pop("dodgingSurface")

        seamline_keys = [
            "computeCandidate",
            "maxOverlap",
            "maxLoss",
            "pixelSize",
            "blendType",
            "blendUnit",
            "requestSizeType",
            "requestSize",
            "minThinnessRatio",
            "maxSliverSize",
            "seamlinesMethod",
        ]
        seamline_dict = {}
        seamline_dict.update(
            {
                "seamline": {
                    "seamlinesMethod": "DISPARITY",
                    "minRegionSize": 100,
                    "pixelSize": "",
                    "blendType": "Both",
                    "blendWidth": None,
                    "blendUnit": "Pixels",
                    "requestSizeType": "Pixels",
                    "requestSize": 1000,
                    "minThinnessRatio": 0.05,
                    "maxSliverSize": 20,
                }
            }
        )

        seamline_dict["seamline"].update(
            {
                k: context_new[k.lower()]
                for k in seamline_keys
                if k.lower() in context_new
            }
        )
        if "seamlinesMethod" in seamline_dict["seamline"]:
            seamline_dict["seamline"]["method"] = seamline_dict["seamline"].pop(
                "seamlinesMethod"
            )

        ortho_mosaic_as_ovr = context.get("orthoMosaicAsOvr", False)
        ortho_dict = {"ortho": {"orthoMosaicAsOvr": ortho_mosaic_as_ovr}}

        if regen_seamlines:
            ortho_dict.update(seamline_dict)
        if recompute_color_correction:
            ortho_dict.update(color_balance_dict)

    return gis._tools.realitymapping.generate_orthomosaic(
        image_collection=image_collection,
        output_ortho_image=out_ortho,
        regen_seamlines=regen_seamlines,
        recompute_color_correction=recompute_color_correction,
        context=context,
        future=future,
        **kwargs,
    )


###################################################################################################
## Generate report
###################################################################################################
def generate_report(
    mission,
    report_format: str = "PDF",
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This function is used to generate realitymapping report with image collection
    that has been block adjusted. The report would contain information about
    the quality of the adjusted images, the distribution of the control points, etc.
    The output of this service tool is a downloadable html page.

    ===================    ====================================================================
    **Parameter**           **Description**
    -------------------    --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    -------------------    --------------------------------------------------------------------
    report_format          Type of the format to be generated. Possible PDF, HTML. Default - PDF
    -------------------    --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ===================    ====================================================================

    :return:
        The URL of a single html webpage that is a formatted realitymapping report

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.generate_report(
        image_collection=image_collection,
        report_format=report_format,
        future=future,
        **kwargs,
    )


###################################################################################################
## query camera info
###################################################################################################
def query_camera_info(
    camera_query: Optional[str] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This service tool is used to query specific or the entire digital camera
    database. The digital camera database contains the specs
    of digital camera sensors that were used to capture drone images.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    camera_query           Required String. This is a SQL query statement that can
                           be used to filter a portion of the digital camera
                           database.
                           Digital camera database can be queried using the fields Make, Model,
                           Focallength, Columns, Rows, PixelSize.

                           Example:

                            "Make='Rollei' and Model='RCP-8325'"
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================


    :return:
        Data Frame representing the camera database

    """
    gis = arcgis.env.active_gis if gis is None else gis

    return gis._tools.realitymapping.query_camera_info(
        camera_query=camera_query, future=future, **kwargs
    )


###################################################################################################
## query control points
###################################################################################################
def query_control_points(
    mission,
    query: str,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    Query for control points in an image collection. It allows users to query
    among certain control point sets that has ground control points inside.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    query                  Required string. a SQL statement used for querying the point;

                           Example:

                            "pointID > 100"
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================


    :return:
        A dictionary object

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.query_control_points(
        image_collection=image_collection,
        where=query,
        future=future,
        **kwargs,
    )


###################################################################################################
## Reset image collection
###################################################################################################
def reset_image_collection(
    mission, *, gis: Optional[GIS] = None, future: bool = False, **kwargs
):
    """
    Reset the image collection. It is used to reset the image collection to its
    original state. The image collection could be adjusted during the orthomapping
    workflow and if the user is not satisfied with the result, they will be able
    to clear any existing adjustment settings and revert the images back to
    un-adjusted state

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input mission. The mission must be a 
                           :class:`~arcgis.raster.realitymapping.RMMission` object.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        A boolean indicating whether the reset was successful or not

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    return gis._tools.realitymapping.reset_image_collection(
        image_collection=image_collection,
        future=future,
        **kwargs,
    )


def compute_spatial_reference_factory_code(latitude: float, longitude: float):
    """
    Computes spatial reference factory code. This value may be used as out_sr value in create image collection function

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    latitude               latitude value in decimal degrees that will be used to compute UTM zone
    ------------------     --------------------------------------------------------------------
    longitude              longitude value in decimal degrees that will be used to compute UTM zone
    ==================     ====================================================================

    :return:
        factory_code : spatial reference factory code
    """
    from math import isnan, fabs, floor

    zone = 0
    if (
        isnan(longitude)
        or isnan(latitude)
        or fabs(longitude) > 180.0
        or fabs(latitude) > 90.0
    ):
        raise RuntimeError("Incorrect latitude or longitude value")

    zone = floor((longitude + 180) / 6) + 1
    if latitude >= 56.0 and latitude < 64.0 and longitude >= 3.0 and longitude < 12.0:
        zone = 32

    if latitude >= 72.0 and latitude < 84.0:
        if longitude >= 0.0 and longitude < 9.0:
            zone = 31
        elif longitude >= 9.0 and longitude < 21.0:
            zone = 33
        elif longitude >= 21.0 and longitude < 33.0:
            zone = 35
        elif longitude >= 33.0 and longitude < 42.0:
            zone = 37

    if latitude >= 0:
        srid = 32601
    else:
        srid = 32701

    factory_code = srid + zone - 1

    return factory_code


###################################################################################################
## Query exif info
###################################################################################################
def query_exif_info(
    input_images, *, gis: Optional[GIS] = None, future: bool = False, **kwargs
):
    """
    The `query_exif_info` reads the Exif header metadata from single or
    multiple images in shared data store. The Exif metadata is usually stored
    in drone image files. Some common Exif metadata information are GPS
    locations, camera model, focal length, and more.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    input_images           Required String/list of Strings.  The input images could be a single image path, list of image paths,
                           or a folder path, or a list of folder paths. The image file paths can also be server data store path.

                           Eg:

                           - "\\servername\drone\imagefolder\image_file.jpg"
                           - "/cloudStores/S3DataStore/yvwd13"
                           - "/fileShares/drones/SampleEXIF/YUN_0040.jpg"
                           - ["/fileShares/drones/SampleEXIF/DJI_0002.JPG", "/fileShares/drones/SampleEXIF/YUN_0040.jpg"]
                           - ["/cloudStores/S3DataStore/yvwd13", "/cloudStores/S3DataStore/BogotaFarm"]
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        A dictionary object

    """
    gis = arcgis.env.active_gis if gis is None else gis

    return gis._tools.realitymapping.query_exif_info(
        input_images=input_images, future=future, **kwargs
    )


###################################################################################################
## Reconstruct surface
###################################################################################################
def reconstruct_surface(
    mission,
    scenario: Optional[str] = "DRONE",
    forward_overlap: Optional[int] = None,
    sideward_overlap: Optional[int] = None,
    quality: Optional[str] = "ULTRA",
    area_of_interest: Optional[Union[str, FeatureLayer]] = "AUTO",
    waterbody_features: Optional[FeatureLayer] = None,
    correction_feature: Optional[FeatureLayer] = None,
    reconstruct_options: Optional[str] = None,
    output_dsm_name: Optional[str] = None,
    output_true_ortho_name: Optional[str] = None,
    output_dsm_mesh_name: Optional[str] = None,
    output_point_cloud_name: Optional[str] = None,
    output_mesh_name: Optional[str] = None,
    output_dtm_name: Optional[str] = None,
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    The `reconstruct_surface` generates a digital surface model (DSM), true
    orthos, 2.5D meshes, 3D meshes, and point clouds from adjusted imagery.

    =========================================================================   ===========================================================================
    **Parameter**                                                                **Description**
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    mission                                                                     Required, the input mission. The mission must be a 
                                                                                :class:`~arcgis.raster.realitymapping.RMMission` object.

                                                                                The mission must exist.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    scenario                                                                    Optional String. Specifies the type of imagery that will be used to generate the output products.

                                                                                - DRONE: The input imagery will be defined as having been acquired with drones or terrestrial cameras.
                                                                                - AERIAL_NADIR: The input imagery will be defined as having been acquired with large, photogrammetric camera systems.
                                                                                - AERIAL_OBLIQUE: The input imagery will be defined as having been acquired with oblique camera systems.
                                                                                - SATELLITE: The input imagery will be defined as having been acquired with a satellite.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    forward_overlap                                                             Optional Integer. The forward (in-strip) overlap percentage that will be used between the images.
                                                                                The default is 60.
                                                                                This parameter is enabled when the scenario parameter is set to AERIAL_NADIR.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    sideward_overlap                                                            Optional Integer. The sideward (cross-strip) overlap percentage that will be used between the images.
                                                                                The default is 30.
                                                                                This parameter is enabled when the scenario parameter is set to AERIAL_NADIR.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    quality                                                                     Optional String. Specifies the quality of the final product.

                                                                                - ULTRA - Input images will be used at their original (full) resolution.
                                                                                - HIGH - Input images will be downsampled two times.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    area_of_interest                                                            Optional :class:`~arcgis.features.FeatureLayer` or String. The area of interest that will
                                                                                be used to select images for processing. The area of interest can be computed automatically
                                                                                or defined using an input feature.
                                                                                If the value contains 3D geometries, the z-component will be ignored. If the value includes
                                                                                overlapping features, the union of these features will be computed.

                                                                                - NONE - All images will be used in processing.
                                                                                - AUTO - The processing extent will be calculated automatically. This is the default.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    waterbody_features                                                          Optional :class:`~arcgis.features.FeatureLayer`. A polygon that will define the extent of large water bodies.
                                                                                For the best results, use a 3D feature.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    correction_features                                                         Optional :class:`~arcgis.features.FeatureLayer`. A polygon that will define the extent of all surfaces that are not water bodies.
                                                                                The value must be a 3D feature.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    reconstruction_options                                                      Optional dict or shared data path (this path must be accessible by the server).
                                                                                This specifies the values for the tool parameters. If this parameter is specified, the properties of
                                                                                the file or dictionary will set the default values for the remaining optional parameters.
                                                                                The list of keywords and an example of this JSON can be found here:
                                                                                `Reconstruct Surface tool <https://pro.arcgis.com/en/pro-app/latest/tool-reference/reality-mapping/reconstruct-surface.htm>`_
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_dsm_name                                                             Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_true_ortho_name                                                      Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_dsm_mesh_name                                                        Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_point_cloud_name                                                     Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_mesh_name                                                            Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_dtm_name                                                             Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    context                                                                     Context contains additional settings that affect task execution.

                                                                                context parameter overwrites values set through arcgis.env parameter

                                                                                This function has the following settings:

                                                                                - Extent (extent): A bounding box that defines the analysis area.

                                                                                    Example:

                                                                                        | {"extent": {"xmin": -122.68,
                                                                                        | "ymin": 45.53,
                                                                                        | "xmax": -122.45,
                                                                                        | "ymax": 45.6,
                                                                                        | "spatialReference": {"wkid": 4326}}}

                                                                                - Cell Size (cellSize): The output raster will have the resolution
                                                                                specified by cell size.

                                                                                    Example:

                                                                                        {'cellSize': 11} or {'cellSize': {'url': <image_service_url>}}  or {'cellSize': 'MaxOfIn'}

                                                                                - Parallel Processing Factor (parallelProcessingFactor): controls
                                                                                Raster Processing (CPU) service instances.

                                                                                    Example:

                                                                                    Syntax example with a specified number of processing instances:

                                                                                        {"parallelProcessingFactor": "2"}

                                                                                    Syntax example with a specified percentage of total
                                                                                    processing instances:

                                                                                        {"parallelProcessingFactor": "60%"}

                                                                                - Output DSM product settings: controls
                                                                                the environment variables for creating the DSM product.

                                                                                    Example:

                                                                                    Syntax example with a specified number of processing instances:

                                                                                        {key: {"outputType": "Tiled", "compression": "JPEG 75", "resamplingMethod": "NEAREST", "cellSize": 10, "noData": 0}}

                                                                                - Output True Ortho product settings: controls
                                                                                the environment variables for creating the DSM product.

                                                                                    Example:

                                                                                    Syntax example with a specified number of processing instances:

                                                                                        {"true_ortho": {"outputType": "Mosaic", "compression": "JPEG 75", "resamplingMethod": "NEAREST", "cellSize": 10, "noData": 0}}
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    gis                                                                         Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    future                                                                      Optional boolean. If True, the result will be a GPJob object and results will be returned asynchronously.
    =========================================================================   ===========================================================================

    :return: Named Tuple

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    if not isinstance(mission, RMMission):
        raise TypeError("The mission parameter must be a RMMission object.")

    image_collection = mission.image_collection

    if mission.workspace:
        if context:
            context["workspace"] = mission.workspace
        else:
            context = {"workspace": mission.workspace}

    if kwargs is not None:
        if "folder" in kwargs:
            folder = kwargs["folder"]
        else:
            for f in gis.users.me.folders:
                if f._fid == image_collection.ownerFolder:
                    folder = f.properties
                    break
        kwargs.update({"folder": folder})

    return gis._tools.realitymapping.reconstruct_surface(
        image_collection=image_collection,
        scenario=scenario,
        forward_overlap=forward_overlap,
        sideward_overlap=sideward_overlap,
        quality=quality,
        area_of_interest=area_of_interest,
        waterbody_features=waterbody_features,
        correction_feature=correction_feature,
        reconstruct_options=reconstruct_options,
        output_dsm_name=output_dsm_name,
        output_true_ortho_name=output_true_ortho_name,
        output_dsm_mesh_name=output_dsm_mesh_name,
        output_point_cloud_name=output_point_cloud_name,
        output_mesh_name=output_mesh_name,
        output_dtm_name=output_dtm_name,
        context=context,
        future=future,
        **kwargs,
    )


class RMProject:
    """

    RMProject represents an Realitymapping Project Item in the portal.

    Usage: ``arcgis.raster.RMProject(project, gis=gis)``

    ====================================     ====================================================================
    **Parameter**                             **Description**
    ------------------------------------     --------------------------------------------------------------------
    project                                  Required string or Realitymapping Project Item

                                             Example:

                                                | project = "RM_project"
                                                | om_item = gis.content.get("85a54236c6364a88a7c7c2b1a31fd901")
                                                | project = rm_item
    ------------------------------------     --------------------------------------------------------------------
    definition                               Optional dictionary. Custom project definition.
    ------------------------------------     --------------------------------------------------------------------
    gis                                      Optional  :class:`~arcgis.gis.GIS` . Represents the GIS object of the Realitymapping
                                             Project item.
    ====================================     ====================================================================

    .. code-block:: python

        # Example Usage

        project = RMProject('rm_proj', gis=gis)

        # Example Usage

        rm_item = gis.content.get("85a54236c6364a88a7c7c2b1a31fd901")
        project = RMProject(rm_item, gis=gis)

    """

    _spatial_reference = None

    def __init__(
        self,
        project=None,
        definition=None,
        sensor_type="Drone",
        scenario_type="Drone",
        *,
        gis: Optional[GIS] = None,
        **kwargs,
    ):
        if not isinstance(project, Item):
            try:
                project = _create_project(
                    name=project,
                    sensor_type=sensor_type,
                    scenario_type=scenario_type,
                    gis=gis,
                )
            except:
                raise RuntimeError("Creation of realitymapping project failed.")

        if project.type == "Reality Mapping Project":
            self._project_item = project
        else:
            raise RuntimeError(
                "Invalid project. Project is not of type Reality Mapping Project."
            )
        try:
            self._project_name = self._project_item.title
        except:
            self._project_name = self._project_item.name

        self._mission_list = []
        gis = arcgis.env.active_gis if gis is None else gis
        self._gis = gis

        content = self._gis.content
        fm = content.folders
        try:
            for folder in fm.list():
                if folder.properties["id"] == self._project_item.ownerFolder:
                    self._folder = folder
                    break
        except:
            self._folder = None
        
        self._reality_url = self._gis._url[:self._gis._url.find(".com")+4] + ":6443/arcgis/reality/api"

    def _get_project_json(self):
        url = f"{self._reality_url}/projects/{self._project_item.itemid}"
        headers = {"Authorization": f"Bearer {self._gis.session.auth.token}"}
        resp = get_request(url, headers=headers)
        if resp is None:
            raise RuntimeError("Failed to retrieve project JSON.")
        return resp
    
    @property
    def _project_json(self):
        return self._get_project_json()
    
    @property
    def missions(self):
        """
        The ``missions`` property returns all the missions associated with the project

        :return: A list of missions of the realitymapping project
        """
        from ._realitymapping_mission import RMMission

        url = f"{self._reality_url}/projects/{self._project_item.itemid}/missions"
        headers = {"Authorization": f"Bearer {self._gis.session.auth.token}"}
        res_list = get_request(url, headers=headers)
        if res_list is None:
            raise RuntimeError("Failed to retrieve missions for the project.")
        self._mission_list = []
        for mission in res_list:
            name = mission["name"]
            mid = mission["id"]
            self._mission_list.append(RMMission(mission_name=name, mission_id=mid, project=self))

        return self._mission_list

    @property
    def mission_count(self):
        """
        The ``count`` property returns the number of missions associated with the project

        :return: An integer representing the number of missions
        """
        if not self._mission_list:
            len(self.missions)
        return len(self._mission_list)

    @property
    def spatial_reference(self):
        if self._spatial_reference is None:
            try:
                if self._project_json:
                    if "outputSpatialReference" in self._project_json:
                        self._spatial_reference = self._project_json["outputSpatialReference"]
                else:
                    self._project_json = self._get_project_json()
                    self._spatial_reference = self._project_json.get("outputSpatialReference", None)
            except:
                self._spatial_reference = None

        return self._spatial_reference

    @property
    def item(self):
        """
        The ``item`` property returns the portal item associated with the Project.

        :return: A portal item
        """
        return self._project_item
    
    @property
    def groups(self):
        """
        The ``groups`` property returns the groups associated with the Project.

        :return: A list of groups
        """
        return self._project_item.sharing.groups.list()

    def delete(self):
        """
        The ``delete`` method deletes the project item from the portal and all the associated products.

        :return: A boolean indicating whether the deletion was successful or not
        """
        return self._gis._tools.realitymapping.delete_project(self, future=False)

    @property
    def settings(self):
        return self._project_json.get("processingSettings", {})

    @settings.setter
    def settings(self, new_settings):
        """
        The ``settings`` method updates the properties of the project item.
        """
        if new_settings is None:
            raise ValueError("new_settings cannot be None")
        
        current_settings = self.settings
        is_valid = _validate_settings(current_settings, new_settings)
        
        if not is_valid:
            raise ValueError("Invalid settings provided.")
        
        # update the current settings with the new settings
        _update_settings(current_settings, new_settings)
        payload = {"processingSettings": current_settings}
        
        url = f"{self._reality_url}/projects/{self._project_item.itemid}/update"
        headers = {"Authorization": f"Bearer {self._gis.session.auth.token}"}
        resp = post_request(url, payload=payload, headers=headers)
        if resp is None:
            raise RuntimeError("Failed to update project settings.")
        
    def create_mission(
        self,
        image_list,
        mission_name=None,
        raster_type_name=None,
        raster_type_params=None,
        out_sr=None,
        context=None,
        *,
        gis=None,
        future=False,
        **kwargs,
    ):
        gis = arcgis.env.active_gis if gis is None else gis
        project_item = {"itemId": self._project_item.itemid}

        random_name = _id_generator()
        if mission_name is None:
            mission_name = "mission_" + random_name
        if image_collection is None:
            from datetime import datetime
            image_collection = f"{mission_name}_image_collection_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        if raster_type_name is None:
            raster_type_name = "UAV/UAS"

        _ra = gis._tools.rasteranalysis
        input_rasters, image_collection, raster_type, context, _ = (
            _ra._sanitize_inputs(
                image_collection=image_collection,
                input_rasters=image_list,
                raster_type_name=raster_type_name,
                raster_type_params=raster_type_params,
                out_sr=out_sr,
                context=context,
                folder=self._folder,
                **kwargs,
            )
        )

        mission_def = {"name": mission_name}
        if context is None:
            context = {"workspace": image_collection}
        else:
            if "workspace" not in context:
                context["workspace"] = image_collection

        mission = gis._tools.realitymapping.create_mission(
            project_item=project_item,
            mission_definition=mission_def,
            input_rasters=input_rasters,
            image_collection=image_collection,
            raster_type=raster_type,
            context=context,
            future=future,
            **kwargs,
        )

        from ._realitymapping_mission import RMMission
        return RMMission(mission_name=mission_name, mission_id=mission["mission"]["itemId"], project=self)

    def get_mission(self, name):
        """
        Returns a RMMission object with the name specified using the name parameter.

        ==================                   ====================================================================
        **Parameter**                         **Description**
        ------------------                   --------------------------------------------------------------------
        name                                 Required string. The name of the RMMission.
        ==================                   ====================================================================

        :return: The imagery layer url


        """

        res_list = self.missions
        missions_list = []
        for mission in res_list:
            mission_name = mission._mission_name
            if name == mission_name:
                missions_list.append(mission)

        if len(missions_list) == 1:
            return missions_list[0]
        return missions_list

    def merge_missions(
        self,
        missions,
        output_mission_name,
        output_collection_name=None,
        mission_settings=None,
        *,
        gis=None,
        future=False,
        **kwargs,
    ):
        gis = arcgis.env.active_gis if gis is None else gis
        output_collection_name = output_collection_name if output_collection_name else output_mission_name + "_collection"
        if kwargs.get("folder", None) is None:
            kwargs["folder"] = self._folder
        context = {"workspace": output_mission_name}
        
        mission = gis._tools.realitymapping.merge_missions(
            missions=missions,
            output_mission_name=output_mission_name,
            output_collection_name=output_collection_name,
            context=context,
            mission_settings=mission_settings,
            future=future,
            **kwargs,
        )

        from ._realitymapping_mission import RMMission
        return RMMission(mission_name=output_mission_name, mission_id=mission["mission"]["itemId"], project=self)

    def __repr__(self):
        return "<%s - %s>" % (type(self).__name__, self._project_name)
