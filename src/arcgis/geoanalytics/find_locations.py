"""
These tools are used to identify areas that meet a number of different criteria you specify.

find_similar_locations finds locations most similar to one or more reference locations based on criteria you specify.
"""
import json as _json

import logging as _logging
import arcgis as _arcgis
from arcgis.features import FeatureSet as _FeatureSet
from arcgis.geoprocessing._support import _execute_gp_tool
from ._util import _id_generator, _feature_input, _set_context, _create_output_service

_log = _logging.getLogger(__name__)

# url = "https://dev003153.esri.com/gax/rest/services/System/GeoAnalyticsTools/GPServer"

_use_async = True

def detect_track_incidents(input_layer,
                           track_fields,
                           start_condition_expression,
                           end_condition_expression,
                           output_mode="AllFeatures",
                           output_name=None,
                           gis=None):
    """
    The Detect Incidents task works with a time-enabled layer of points,
    lines, areas, or tables that represents an instant in time. Using
    sequentially ordered features, called tracks, this tool determines
    which features are incidents of interest. Incidents are determined by
    conditions that you specify. First, the tool determines which features
    belong to a track using one or more fields. Using the time at each
    feature, the tracks are ordered sequentially and the incident condition
    is applied. Features that meet the starting incident condition are
    marked as an incident. You can optionally apply an ending incident
    condition; when the end condition is true, the feature is no longer
    an incident. The results will be returned with the original features
    with new columns representing the incident name and indicate which
    feature meets the incident condition. You can return all original
    features, only the features that are incidents, or all of the features
    within tracks where at least one incident occurred.

    For example, suppose you have GPS measurements of hurricanes every 10
    minutes. Each GPS measurement records the hurricane's name, location,
    time of recording, and wind speed. Using these fields, you could create
    an incident where any measurement with a wind speed greater than 208
    km/h is an incident titled Catastrophic. By not setting an end
    condition, the incident would end if the feature no longer meets the
    start condition (wind speed slows down to less than 208).

    Using another example, suppose you were monitoring concentrations of a
    chemical in your local water supply using a field called
    contanimateLevel. You know that the recommended levels are less than
    0.01 mg/L, and dangerous levels are above 0.03 mg/L. To detect
    incidents, where a value above 0.03mg/L is an incident, and remains an
    incident until contamination levels are back to normal, you create an
    incident using a start condition of contanimateLevel > 0.03 and an end
    condition of contanimateLevel < 0.01. This will mark any sequence where
    values exceed 0.03mg/L until they return to a value less than 0.01.

    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    input_layer       required FeatureSet, The table, point, line or polygon features
                      containing potential incidents.
    ----------------  ---------------------------------------------------------------
    track_fields      required string, The fields used to identify distinct tracks.
                      There can be multiple track_fields.
    ----------------  ---------------------------------------------------------------
    start_condition_expression   The condition used to identify incidents. If there
                                 is no endConditionExpression specified, any feature
                                 that meets this condition is an incident. If there
                                 is an end condition, any feature that meets the
                                 start_condition_expression and does not meet the
                                 end_condition_expression is an incident.
                                 The expressions are Arcade expressions.
    ----------------  ---------------------------------------------------------------
    end_condition_expression   The condition used to identify incidents. If there is
                               no endConditionExpression specified, any feature that
                               meets this condition is an incident. If there is an
                               end condition, any feature that meets the
                               start_condition_expression and does not meet the
                               end_condition_expression is an incident. This is an
                               Arcade expression.
    ----------------  ---------------------------------------------------------------
    output_mode       optional string, default value is AllFeatures.  Determines
                      which features are returned. Two modes are available:

                       - AllFeatures - All of the input features are returned.
                       - Incidents - Only features that were found to be incidents
                                     are returned.
    ----------------  ---------------------------------------------------------------
    output_name       optional string, The task will create a feature service of the
                      results. You define the name of the service.
    ----------------  ---------------------------------------------------------------
    gis               optional GIS, the GIS on which this tool runs. If not
                      specified, the active GIS is used.
    ================  ===============================================================

    :returns:
       Service
    """
    kwargs = locals()
    tool_name = "DetectIncidents"
    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url
    params = {
        "f" : "json"
    }
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Detect_Incidents_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Detect Track Incidents')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "track_fields": (str, "trackFields"),
        "start_condition_expression": (str, "startConditionExpression"),
        "end_condition_expression": (str, "endConditionExpression"),
        "output_mode": (str, "outputMode"),
        "output_name": (str, "outputName"),
        "output": (_FeatureSet, "output"),
        "context": (str, "context")
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]
    try:
        _execute_gp_tool(gis, tool_name, params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

    return

def find_similar_locations(
    input_layer,
    search_layer,
    analysis_fields,
    most_or_least_similar = """MostSimilar""",
    match_method = """AttributeValues""",
    number_of_results = 10,
    append_fields = None,
    output_name = None,
    gis = None):
    """

    Based on criteria you specify, find similar locations by measuring the similarity of locations in your candidate search layer to one or more reference locations.

    For example

    * Find the ten most similar stores by examining the number of employees and the annual sales.

    * Find the 100 most similar cities by examining the relationship between population, annual growth, and tax revenue.


   Parameters:

   input_layer: Input Layer (feature layer). Required parameter.

   search_layer: Search Layer (feature layer). Required parameter.

   analysis_fields: Analysis Fields (str). Required parameter.

   most_or_least_similar: Most Or Least Similar (str). Required parameter.
      Choice list:['MostSimilar', 'LeastSimilar', 'Both']

   match_method: Match Method (str). Required parameter.
      Choice list:['AttributeValues', 'AttributeProfiles']

   number_of_results: Number Of Results (int). Required parameter.

   append_fields: Fields To Append To Output (str). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.


Returns:
   output - Output feature layer Item


    """
    kwargs = locals()

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url

    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Similar Locations_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Find Similar Locations')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "search_layer": (_FeatureSet, "searchLayer"),
        "analysis_fields": (str, "analysisFields"),
        "most_or_least_similar": (str, "mostOrLeastSimilar"),
        "match_method": (str, "matchMethod"),
        "number_of_results": (int, "numberOfResults"),
        "append_fields": (str, "appendFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]
    try:
        _execute_gp_tool(gis, "FindSimilarLocations", params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

find_similar_locations.__annotations__ = {
    'most_or_least_similar': str,
    'match_method': str,
    'number_of_results': int,
    'append_fields': str,
    'output_name': str}

