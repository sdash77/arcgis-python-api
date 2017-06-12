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

