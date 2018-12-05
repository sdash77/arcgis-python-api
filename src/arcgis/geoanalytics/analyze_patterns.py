"""
These tools help you identify, quantify, and visualize spatial patterns in your data.

calculate_density takes known quantities of some phenomenon and spreads these quantities across the map.
find_hot_spots identifies statistically significant clustering in the spatial pattern of your data.
"""
import json as _json
from datetime import datetime as _datetime
import logging as _logging
import arcgis as _arcgis
from arcgis.features import FeatureSet as _FeatureSet
from arcgis.geoprocessing._support import _execute_gp_tool
from arcgis.geoprocessing import DataFile
from ._util import _id_generator, _feature_input, _set_context, _create_output_service

_log=_logging.getLogger(__name__)

_use_async=True

def forest_based_regression(input_layer,
                            prediction_type,
                            features_to_predict,

                            output_name=None,
                            gis=None):
    """
    Creates models and generates predictions using an adaptation of Leo Breiman's random forest
    algorithm, which is a supervised machine learning method. Predictions can be performed for both
    categorical variables (classification) and continuous variables (regression). Explanatory
    variables can take the form of fields in the attribute table of the training features. In
    addition to validation of model performance based on the training data, predictions can be made
    to another feature dataset.

    The following are examples:

        + Given data on occurrence of seagrass, as well as a number of environmental explanatory variables represented as both attributes which has been enriched using a multi-variable grid to calculate distances to factories upstream and major ports, future seagrass occurrence can be predicted based on future projections for those same environmental explanatory variables.
        + Suppose you have crop yield data at hundreds of farms across the country along with other attributes at each of those farms (number of employees, acreage, and so on). Using these pieces of data, you can provide a set of features representing farms where you don't have crop yield (but you do have all of the other variables), and make a prediction about crop yield.
        + Housing values can be predicted based on the prices of houses that have been sold in the current year. The sale price of homes sold along with information about the number of bedrooms, distance to schools, proximity to major highways, average income, and crime counts can be used to predict sale prices of similar homes.


    **Forest Based Classification and Regression is available at ArcGIS Enterprise 10.7.**

    ==========================   ===============================================================
    **Argument**                 **Description**
    --------------------------   ---------------------------------------------------------------
    input_layer                  required FeatureSet, The table, point, line or polygon features
                                 containing potential incidents.
    --------------------------   ---------------------------------------------------------------
    prediction_type              Specifies the operation mode of the tool. The tool can be run to train a model to only assess performance, or train a model and predict features. Prediction types are as follows:
                                    + Train - This is the default. A model will be trained, but no predictions will be generated. Use this option to assess the accuracy of your model before generating predictions. This option will output model diagnostics in the messages window and a chart of variable importance.
                                    + TrainAndPredict - Predictions or classifications will be generated for features. Explanatory variables must be provided for both the training features and the features to be predicted. The output of this option will be a feature service, model diagnostics, and an optional table of variable importance.
    --------------------------   ---------------------------------------------------------------
    features_to_predict          Optional dict. The variable from the `input_layer` parameter
                                 containing the values to be used to train the model, and a
                                 boolean denoting if it's categorical. This field contains known
                                 (training) values of the variable that will be used to predict
                                 at unknown locations.
    --------------------------   ---------------------------------------------------------------
    variable_predict
    --------------------------   ---------------------------------------------------------------
    explanatory_variable_match
    --------------------------   ---------------------------------------------------------------
    return_importance_table
    --------------------------   ---------------------------------------------------------------
    number_of_trees
    --------------------------   ---------------------------------------------------------------
    min_leaf_size
    --------------------------   ---------------------------------------------------------------
    max_tree_depth
    --------------------------   ---------------------------------------------------------------
    sample_size
    --------------------------   ---------------------------------------------------------------
    random_vars
    --------------------------   ---------------------------------------------------------------
    percentage_for_validation
    --------------------------   ---------------------------------------------------------------
    output_trained_name
    --------------------------   ---------------------------------------------------------------
    output_name                  optional string, The task will create a feature service of the
                                 results. You define the name of the service.
    --------------------------   ---------------------------------------------------------------
    gis                          optional GIS, the GIS on which this tool runs. If not
                                 specified, the active GIS is used.
    ==========================   ===============================================================

    :returns:
       Output feature layer item


    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Forest Based Regression_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Forest Based Classification And Regression')

    _set_context(params)

    param_db={
        "input_layer": (_FeatureSet, "inFeatures"),
        "prediction_type" : (str, "predictionType"),
        "features_to_predict" : (_FeatureSet, "featuresToPredict"),
        "variable_predict" : (_FeatureSet, "featuresToPredict"),
        "explanatory_variables" : (list, "explanatoryVariables"),
        "explanatory_variable_match" : (list, "explanatoryVariableMatching"),
        "return_importance_table" : (bool, "returnVariableOfImportanceTable"),
        "number_of_trees" : (int, "numberOfTrees"),
        "min_leaf_size" : (int, "minimumLeafSize"),
        "sample_size" : (int, "sampleSize"),
        "random_vars" : (str, "randomVariables"),
        "percentage_for_validation" : (int, "percentageForValidation"),
        "outputTrainedName" : (str, "output_name"),
        "context": (str, "context"),
        "outputTrainedName": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "outputTrainedName", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        _execute_gp_tool(gis, "ForestBasedClassificationAndRegression", params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

    return


def _generalized_linear_regression(input_layer,
                                features_to_predict,
                                dependent_variable,
                                explanatory_variables,
                                regression_family="Continuous",
                                generate_coef_table=False,
                                variable_matching=None,
                                output_name=None,
                                gis=None):
    """
    TODO: need the docstring
    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Find Point Clusters_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Find Point Clusters')

    _set_context(params)

    param_db={
        "input_layer": (_FeatureSet, "inputLayer"),
        "output_name": (str, "outputName"),
        "features_to_predict" : (_FeatureSet, "featuresToPredict"),
        "dependent_variable" : (str, "dependentVariable"),
        "explanatory_variables" : (str, "explanatoryVariables"),
        "regression_family" : (str, "regressionFamily"),
        "generate_coef_table" : (bool, "generateCoefficientTable"),
        "variable_matching" : (str, "explanatoryVariableMatching"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        _execute_gp_tool(gis, "FindPointClusters", params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

    return

def find_point_clusters(
    input_layer,
    method,
    min_feature_clusters,
    search_distance=None,
    distance_unit=None,
    output_name=None,
    gis=None):
    """
    This tool extracts clusters from your input point features and identifies any surrounding noise.

    For example, a nongovernmental organization is studying a particular pest-borne disease. It has
    a point dataset representing households in a study area, some of which are infested, and some of
    which are not. By using the Find Point Clusters tool, an analyst can determine clusters of
    infested households to help pinpoint an area to begin treatment and extermination of pests.

    ==========================   ===============================================================
    **Argument**                 **Description**
    --------------------------   ---------------------------------------------------------------
    input_layer                  required FeatureSet, The table, point, line or polygon features
                                 containing potential incidents.
    --------------------------   ---------------------------------------------------------------
    method                       required String. The algorithm used for cluster analysis. This
                                 parameter must be specified as DBSCAN or HDBSCAN.
    --------------------------   ---------------------------------------------------------------
    min_feature_clusters         optional Integer. Minimum number of clusters to find in a dataset.
    --------------------------   ---------------------------------------------------------------
    search_distance              optional Float.  The distance to search between points to form
                                 a cluster.  This is required for DBSCAN.
    --------------------------   ---------------------------------------------------------------
    distance_unit                optional String. The `search_distance` units.
    --------------------------   ---------------------------------------------------------------
    output_name                  optional string, The task will create a feature service of the
                                 results. You define the name of the service.
    --------------------------   ---------------------------------------------------------------
    gis                          optional GIS, the GIS on which this tool runs. If not
                                 specified, the active GIS is used.
    ==========================   ===============================================================

    :returns:
       Output feature layer item

    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Find Point Clusters_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Find Point Clusters')

    _set_context(params)

    param_db={
        "input_layer": (_FeatureSet, "inputLayer"),
        "method" : (str, "clusterMethod"),
        "min_feature_clusters": (int, "minFeaturesCluster"),
        "distance_unit": (str, "searchDistanceUnit"),
        "search_distance" : (float, "searchDistance"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        _execute_gp_tool(gis, "FindPointClusters", params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

    return

def calculate_density(
    input_layer,
    fields=None,
    weight="""Uniform""",
    bin_type="""Square""",
    bin_size=None,
    bin_size_unit=None,
    time_step_interval=None,
    time_step_interval_unit=None,
    time_step_repeat_interval=None,
    time_step_repeat_interval_unit=None,
    time_step_reference=None,
    radius=None,
    radius_unit=None,
    area_units="""SquareKilometers""",
    output_name=None,
    gis=None):
    """




Parameters:

   input_layer: Input Points (Feature layer). Required parameter.

   fields: Population Field (str). Optional parameter.

   weight: Weight (str). Required parameter.
      Choice list:['Uniform', 'Kernel']

   bin_type: Output Bin Type (str). Required parameter.
      Choice list:['Square', 'Hexagon']

   bin_size: Output Bin Size (float). Required parameter.

   bin_size_unit: Output Bin Size Unit (str). Required parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   time_step_interval: Time Step Interval (int). Optional parameter.

   time_step_interval_unit: Time Step Interval Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   time_step_repeat_interval: Time Step Repeat Interval (int). Optional parameter.

   time_step_repeat_interval_unit: Time Step Repeat Interval Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   time_step_reference: Time Step Reference (_datetime). Optional parameter.

   radius: Radius (float). Required parameter.

   radius_unit: Radius Unit (str). Required parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   area_units: Area Unit Scale Factor (str). Optional parameter.
      Choice list:['SquareMeters', 'SquareKilometers', 'Hectares', 'SquareFeet', 'SquareYards', 'SquareMiles', 'Acres']

   output_name: Output Features Name (str). Required parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.


Returns:
   output - Output Features as a feature layer collection item


    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Calculate Density Analysis_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Calculate Density')

    params['output_name']=_json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db={
        "input_layer": (_FeatureSet, "inputLayer"),
        "fields": (str, "fields"),
        "weight": (str, "weight"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_repeat_interval": (int, "timeStepRepeatInterval"),
        "time_step_repeat_interval_unit": (str, "timeStepRepeatIntervalUnit"),
        "time_step_reference": (_datetime, "timeStepReference"),
        "radius": (float, "radius"),
        "radius_unit": (str, "radiusUnit"),
        "area_units": (str, "areaUnits"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        _execute_gp_tool(gis, "CalculateDensity", params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise


calculate_density.__annotations__={
    'fields': str,
    'weight': str,
    'bin_type': str,
    'bin_size': float,
    'bin_size_unit': str,
    'time_step_interval': int,
    'time_step_interval_unit': str,
    'time_step_repeat_interval': int,
    'time_step_repeat_interval_unit': str,
    'time_step_reference': _datetime,
    'radius': float,
    'radius_unit': str,
    'area_units': str,
    'output_name': str}


def find_hot_spots(
    point_layer,
    bin_size=5,
    bin_size_unit="Miles",
    neighborhood_distance=5,
    neighborhood_distance_unit="Miles",
    time_step_interval=None,
    time_step_interval_unit=None,
    time_step_alignment=None,
    time_step_reference=None,
    output_name=None,
    gis=None):
    """

    Parameters:

       point_layer: Input Points (FeatureSet). Required parameter.

       bin_size: Bin Size (float). Optional parameter.

       bin_size_unit: Bin Size Unit (str). Optional parameter.
          Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

       neighborhood_distance: Neighborhood Distance (float). Optional parameter.

       neighborhood_distance_unit: Neighborhood Distance Unit (str). Optional parameter.
          Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

       time_step_interval: Time Step Interval (int). Optional parameter.

       time_step_interval_unit: Time Step Interval Unit (str). Optional parameter.
          Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

       time_step_alignment: Time Step Alignment (str). Optional parameter.
          Choice list:['EndTime', 'StartTime', 'ReferenceTime']

       time_step_reference: Time Step Reference (_datetime). Optional parameter.

       output_name: Output Features Name (str). Optional parameter.

       gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.


    Returns:
       output - Output Features as a feature layer collection item


    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Hotspot Analysis_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Find Hotspots')

    params['output_name']=_json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db={
        "point_layer": (_FeatureSet, "pointLayer"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "neighborhood_distance": (float, "neighborhoodDistance"),
        "neighborhood_distance_unit": (str, "neighborhoodDistanceUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_alignment": (str, "timeStepAlignment"),
        "time_step_reference": (_datetime, "timeStepReference"),
        #"cell_size" : (int, "cellSize"),
        #"cell_size_units": (str, "cellSizeUnits"),
        #"shape_type" : (str, "shapeType"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        _execute_gp_tool(gis, "FindHotSpots", params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

find_hot_spots.__annotations__={
    'bin_size': float,
    'bin_size_unit': str,
    'neighborhood_distance': float,
    'neighborhood_distance_unit': str,
    'time_step_interval': int,
    'time_step_interval_unit': str,
    'time_step_alignment': str,
    'time_step_reference': _datetime,
    'output_name': str}


def create_space_time_cube(point_layer: _FeatureSet,
                           bin_size: float,
                           bin_size_unit: str,
                           time_step_interval: int,
                           time_step_interval_unit: str,
                           time_step_alignment: str=None,
                           time_step_reference: _datetime=None,
                           summary_fields: str=None,
                           output_name: str=None,
                           context: str=None,
                           gis=None) -> DataFile:
    """
    Summarizes a set of points into a netCDF data structure by aggregating them into space-time bins. Within each bin,
    the points are counted and specified attributes are aggregated. For all bin locations, the trend for counts and
    summary field values are evaluated.

    Parameters:

       point_layer: Input Features (FeatureSet). Required parameter.

       bin_size: Distance Interval (float). Required parameter.

       bin_size_unit: Distance Interval Unit (str). Required parameter.
          Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

       time_step_interval: Time Step Interval (int). Required parameter.

       time_step_interval_unit: Time Step Interval Unit (str). Required parameter.
          Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

       time_step_alignment: Time Step Alignment (str). Optional parameter.
          Choice list:['EndTime', 'StartTime', 'ReferenceTime']

       time_step_reference: Time Step Reference (datetime). Optional parameter.

       summary_fields: Summary Fields (str). Optional parameter.

       output_name: Output Name (str). Required parameter.

       context: Context (str). Optional parameter.

        gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.


    Returns:
       output_cube - Output Space Time Cube as a DataFile

    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if value is not None:
            params[key]=value

    _set_context(params)

    param_db={
        "point_layer": (_FeatureSet, "pointLayer"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_alignment": (str, "timeStepAlignment"),
        "time_step_reference": (_datetime, "timeStepReference"),
        "summary_fields": (str, "summaryFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output_cube": (DataFile, "Output Space Time Cube"),
    }
    return_values=[
        {"name": "output_cube", "display_name": "Output Space Time Cube", "type": DataFile},
    ]

    return _execute_gp_tool(gis, "CreateSpaceTimeCube", params, param_db, return_values, _use_async, url, True)

