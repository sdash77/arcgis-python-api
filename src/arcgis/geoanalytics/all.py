import logging as _logging
import arcgis
from datetime import datetime
from arcgis.features import FeatureSet
from arcgis.mapping import MapImageLayer
from arcgis.geoprocessing import DataFile, LinearUnit, RasterData
from arcgis.geoprocessing._support import _execute_gp_tool

_log = _logging.getLogger(__name__)

_url = "https://dev003153.esri.com/gax/rest/services/System/GeoAnalyticsTools/GPServer"
_use_async = True


def aggregate_points(point_layer: FeatureSet,
                     bin_type: str = None,
                     bin_size: float = None,
                     bin_size_unit: str = None,
                     polygon_layer: FeatureSet = {},
                     time_step_interval: int = None,
                     time_step_interval_unit: str = None,
                     time_step_repeat_interval: int = None,
                     time_step_repeat_interval_unit: str = None,
                     time_step_reference: datetime = None,
                     summary_fields: str = None,
                     output_name: str = None,
                     context: str = None,
                     gis=None) -> FeatureSet:
    """




Parameters:

   point_layer: Input Points (FeatureSet). Required parameter.

   bin_type: Output Bin Type (str). Optional parameter.
      Choice list:['Square', 'Hexagon']

   bin_size: Bin Size (float). Optional parameter.

   bin_size_unit: Bin Size Unit (str). Optional parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   polygon_layer: Input Polygons (FeatureSet). Optional parameter.

   time_step_interval: Time Step Interval (int). Optional parameter.

   time_step_interval_unit: Time Step Interval Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   time_step_repeat_interval: Time Step Repeat Interval (int). Optional parameter.

   time_step_repeat_interval_unit: Time Step Repeat Interval Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   time_step_reference: Time Step Reference (datetime). Optional parameter.

   summary_fields: Summary Statistics (str). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

       gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "point_layer": (FeatureSet, "pointLayer"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "polygon_layer": (FeatureSet, "polygonLayer"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_repeat_interval": (int, "timeStepRepeatInterval"),
        "time_step_repeat_interval_unit": (str, "timeStepRepeatIntervalUnit"),
        "time_step_reference": (datetime, "timeStepReference"),
        "summary_fields": (str, "summaryFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "AggregatePoints", kwargs, param_db, return_values, _use_async, _url)


def describe_dataset(input_layer: FeatureSet = {},
                     context: str = None,
                     gis=None) -> str:
    """




Parameters:

   input_layer: Input Dataset (FeatureSet). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output JSON as a str


    """
    kwargs = locals()

    param_db = {
        "input_layer": (FeatureSet, "inputLayer"),
        "context": (str, "context"),
        "output": (str, "Output JSON"),
    }
    return_values = [
        {"name": "output", "display_name": "Output JSON", "type": str},
    ]

    return _execute_gp_tool(gis, "DescribeDataset", kwargs, param_db, return_values, _use_async, _url)


def join_features(target_layer: FeatureSet,
                  join_layer: FeatureSet,
                  join_operation: str = """JoinOneToOne""",
                  join_fields: str = None,
                  summary_fields: str = None,
                  spatial_relationship: str = None,
                  spatial_near_distance: float = None,
                  spatial_near_distance_unit: str = None,
                  temporal_relationship: str = None,
                  temporal_near_distance: int = None,
                  temporal_near_distance_unit: str = None,
                  attribute_relationship: str = None,
                  join_condition: str = None,
                  output_name: str = None,
                  context: str = None,
                  gis=None) -> FeatureSet:
    """




Parameters:

   target_layer: Target Features (FeatureSet). Required parameter.

   join_layer: Join Features (FeatureSet). Required parameter.

   join_operation: Join Operation (str). Required parameter.
      Choice list:['JoinOneToOne', 'JoinOneToMany']

   join_fields: Join Fields (str). Optional parameter.

   summary_fields: Summary Statistics (str). Optional parameter.

   spatial_relationship: Spatial Relationship (str). Optional parameter.
      Choice list:['Equals', 'Intersects', 'Contains', 'Within', 'Crosses', 'Touches', 'Overlaps', 'Near']

   spatial_near_distance: Near Spatial Distance (float). Optional parameter.

   spatial_near_distance_unit: Near Spatial Distance Unit (str). Optional parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   temporal_relationship: Temporal Relationship (str). Optional parameter.
      Choice list:['Equals', 'Intersects', 'During', 'Contains', 'Finishes', 'FinishedBy', 'Meets', 'MetBy', 'Overlaps', 'OverlappedBy', 'Starts', 'StartedBy', 'Near']

   temporal_near_distance: Near Temporal Distance (int). Optional parameter.

   temporal_near_distance_unit: Near Temporal Distance Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   attribute_relationship: Attribute Relationships (str). Optional parameter.

   join_condition: Join Condition (str). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "target_layer": (FeatureSet, "targetLayer"),
        "join_layer": (FeatureSet, "joinLayer"),
        "join_operation": (str, "joinOperation"),
        "join_fields": (str, "joinFields"),
        "summary_fields": (str, "summaryFields"),
        "spatial_relationship": (str, "spatialRelationship"),
        "spatial_near_distance": (float, "spatialNearDistance"),
        "spatial_near_distance_unit": (str, "spatialNearDistanceUnit"),
        "temporal_relationship": (str, "temporalRelationship"),
        "temporal_near_distance": (int, "temporalNearDistance"),
        "temporal_near_distance_unit": (str, "temporalNearDistanceUnit"),
        "attribute_relationship": (str, "attributeRelationship"),
        "join_condition": (str, "joinCondition"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "JoinFeatures", kwargs, param_db, return_values, _use_async, _url)


def create_buffers(input_layer: FeatureSet = {},
                   distance: float = None,
                   distance_unit: str = None,
                   field: str = None,
                   method: str = """Planar""",
                   dissolve_option: str = """None""",
                   dissolve_fields: str = None,
                   summary_fields: str = None,
                   multipart: bool = False,
                   output_name: str = None,
                   context: str = None,
                   gis=None) -> FeatureSet:
    """




Parameters:

   input_layer: Input Features (FeatureSet). Required parameter.

   distance: Buffer Distance (float). Optional parameter.

   distance_unit: Buffer Distance Unit (str). Optional parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   field: Buffer Distance Field (str). Optional parameter.

   method: Method (str). Required parameter.
      Choice list:['Geodesic', 'Planar']

   dissolve_option: Dissolve Option (str). Optional parameter.
      Choice list:['All', 'List', 'None']

   dissolve_fields: Dissolve Fields (str). Optional parameter.

   summary_fields: Summary Statistics (str). Optional parameter.

   multipart: Allow Multipart Geometries (bool). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "input_layer": (FeatureSet, "inputLayer"),
        "distance": (float, "distance"),
        "distance_unit": (str, "distanceUnit"),
        "field": (str, "field"),
        "method": (str, "method"),
        "dissolve_option": (str, "dissolveOption"),
        "dissolve_fields": (str, "dissolveFields"),
        "summary_fields": (str, "summaryFields"),
        "multipart": (bool, "multipart"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "CreateBuffers", kwargs, param_db, return_values, _use_async, _url)


def calculate_density(input_layer: FeatureSet = {},
                      fields: str = None,
                      weight: str = """Uniform""",
                      bin_type: str = """Square""",
                      bin_size: float = None,
                      bin_size_unit: str = None,
                      time_step_interval: int = None,
                      time_step_interval_unit: str = None,
                      time_step_repeat_interval: int = None,
                      time_step_repeat_interval_unit: str = None,
                      time_step_reference: datetime = None,
                      radius: float = None,
                      radius_unit: str = None,
                      area_units: str = """SquareKilometers""",
                      output_name: str = None,
                      context: str = None,
                      gis=None) -> FeatureSet:
    """




Parameters:

   input_layer: Input Points (FeatureSet). Required parameter.

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

   time_step_reference: Time Step Reference (datetime). Optional parameter.

   radius: Radius (float). Required parameter.

   radius_unit: Radius Unit (str). Required parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   area_units: Area Unit Scale Factor (str). Optional parameter.
      Choice list:['SquareMeters', 'SquareKilometers', 'Hectares', 'SquareFeet', 'SquareYards', 'SquareMiles', 'Acres']

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "input_layer": (FeatureSet, "inputLayer"),
        "fields": (str, "fields"),
        "weight": (str, "weight"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_repeat_interval": (int, "timeStepRepeatInterval"),
        "time_step_repeat_interval_unit": (str, "timeStepRepeatIntervalUnit"),
        "time_step_reference": (datetime, "timeStepReference"),
        "radius": (float, "radius"),
        "radius_unit": (str, "radiusUnit"),
        "area_units": (str, "areaUnits"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "CalculateDensity", kwargs, param_db, return_values, _use_async, _url)


def reconstruct_tracks(input_layer: FeatureSet = {},
                       track_fields: str = None,
                       method: str = """Planar""",
                       buffer_field: str = None,
                       summary_fields: str = None,
                       time_split: int = None,
                       time_split_unit: str = None,
                       output_name: str = None,
                       context: str = None,
                       gis=None) -> FeatureSet:
    """




Parameters:

   input_layer: Input Features (FeatureSet). Required parameter.

   track_fields: Track Fields (str). Required parameter.

   method: Method (str). Required parameter.
      Choice list:['Geodesic', 'Planar']

   buffer_field: Buffer Distance Field (str). Optional parameter.

   summary_fields: Summary Statistics (str). Optional parameter.

   time_split: Duration Split Threshold (int). Optional parameter.

   time_split_unit: Duration Split Threshold Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "input_layer": (FeatureSet, "inputLayer"),
        "track_fields": (str, "trackFields"),
        "method": (str, "method"),
        "buffer_field": (str, "bufferField"),
        "summary_fields": (str, "summaryFields"),
        "time_split": (int, "timeSplit"),
        "time_split_unit": (str, "timeSplitUnit"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "ReconstructTracks", kwargs, param_db, return_values, _use_async, _url)


def create_space_time_cube(point_layer: FeatureSet = {},
                           bin_size: float = None,
                           bin_size_unit: str = None,
                           time_step_interval: int = None,
                           time_step_interval_unit: str = None,
                           time_step_alignment: str = None,
                           time_step_reference: datetime = None,
                           summary_fields: str = None,
                           output_name: str = None,
                           context: str = None,
                           gis=None) -> DataFile:
    """




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
    kwargs = locals()

    param_db = {
        "point_layer": (FeatureSet, "pointLayer"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_alignment": (str, "timeStepAlignment"),
        "time_step_reference": (datetime, "timeStepReference"),
        "summary_fields": (str, "summaryFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output_cube": (DataFile, "Output Space Time Cube"),
    }
    return_values = [
        {"name": "output_cube", "display_name": "Output Space Time Cube", "type": DataFile},
    ]

    return _execute_gp_tool(gis, "CreateSpaceTimeCube", kwargs, param_db, return_values, _use_async, _url)


def copy_to_data_store(input_layer: FeatureSet = {},
                       output_name: str = None,
                       context: str = None,
                       gis=None) -> FeatureSet:
    """




Parameters:

   input_layer: Input Layer (FeatureSet). Required parameter.

   output_name: Output Layer Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Layer as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "input_layer": (FeatureSet, "inputLayer"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Layer"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Layer", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "CopyToDataStore", kwargs, param_db, return_values, _use_async, _url)


def summarize_attributes(input_layer: FeatureSet = {},
                         fields: str = None,
                         summary_fields: str = None,
                         output_name: str = None,
                         context: str = None,
                         gis=None) -> FeatureSet:
    """




Parameters:

   input_layer: Input Features (FeatureSet). Required parameter.

   fields: Summary Fields (str). Required parameter.

   summary_fields: Summary Statistics (str). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "input_layer": (FeatureSet, "inputLayer"),
        "fields": (str, "fields"),
        "summary_fields": (str, "summaryFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "SummarizeAttributes", kwargs, param_db, return_values, _use_async, _url)


def summarize_within(summary_polygons: FeatureSet = {},
                     bin_type: str = None,
                     bin_size: float = None,
                     bin_size_unit: str = None,
                     summarized_layer: FeatureSet = {},
                     standard_summary_fields: str = None,
                     weighted_summary_fields: str = None,
                     sum_shape: bool = True,
                     shape_units: str = None,
                     output_name: str = None,
                     context: str = None,
                     gis=None) -> FeatureSet:
    """




Parameters:

   summary_polygons: Summary Polygons Layer (FeatureSet). Optional parameter.

   bin_type: Output Bin Type (str). Optional parameter.
      Choice list:['Square', 'Hexagon']

   bin_size: Output Bin Size (float). Optional parameter.

   bin_size_unit: Output Bin Size Unit (str). Optional parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   summarized_layer: Layer To Summarize (FeatureSet). Required parameter.

   standard_summary_fields: Unweighted Summary Statistics (str). Optional parameter.

   weighted_summary_fields: Proportional Summary Statistics (str). Optional parameter.

   sum_shape: Summarize Shape (bool). Optional parameter.

   shape_units: Shape Measure Output Unit (str). Optional parameter.
      Choice list:['Meters', 'Kilometers', 'Feet', 'Yards', 'Miles', 'SquareMeters', 'SquareKilometers', 'Hectares', 'SquareFeet', 'SquareYards', 'SquareMiles', 'Acres']

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "summary_polygons": (FeatureSet, "summaryPolygons"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "summarized_layer": (FeatureSet, "summarizedLayer"),
        "standard_summary_fields": (str, "standardSummaryFields"),
        "weighted_summary_fields": (str, "weightedSummaryFields"),
        "sum_shape": (bool, "sumShape"),
        "shape_units": (str, "shapeUnits"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "SummarizeWithin", kwargs, param_db, return_values, _use_async, _url)


def find_similar_locations(input_layer: FeatureSet = {},
                           search_layer: FeatureSet = {},
                           analysis_fields: str = None,
                           most_or_least_similar: str = """MostSimilar""",
                           match_method: str = """AttributeValues""",
                           number_of_results: int = 10,
                           append_fields: str = None,
                           output_name: str = None,
                           context: str = None,
                           gis=None) -> FeatureSet:
    """




Parameters:

   input_layer: Input Layer (FeatureSet). Required parameter.

   search_layer: Search Layer (FeatureSet). Required parameter.

   analysis_fields: Analysis Fields (str). Required parameter.

   most_or_least_similar: Most Or Least Similar (str). Required parameter.
      Choice list:['MostSimilar', 'LeastSimilar', 'Both']

   match_method: Match Method (str). Required parameter.
      Choice list:['AttributeValues', 'AttributeProfiles']

   number_of_results: Number Of Results (int). Required parameter.

   append_fields: Fields To Append To Output (str). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "input_layer": (FeatureSet, "inputLayer"),
        "search_layer": (FeatureSet, "searchLayer"),
        "analysis_fields": (str, "analysisFields"),
        "most_or_least_similar": (str, "mostOrLeastSimilar"),
        "match_method": (str, "matchMethod"),
        "number_of_results": (int, "numberOfResults"),
        "append_fields": (str, "appendFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "FindSimilarLocations", kwargs, param_db, return_values, _use_async, _url)


def find_hot_spots(point_layer: FeatureSet = {},
                   bin_size: float = None,
                   bin_size_unit: str = None,
                   neighborhood_distance: float = None,
                   neighborhood_distance_unit: str = None,
                   time_step_interval: int = None,
                   time_step_interval_unit: str = None,
                   time_step_alignment: str = None,
                   time_step_reference: datetime = None,
                   output_name: str = None,
                   context: str = None,
                   gis=None) -> FeatureSet:
    """




Parameters:

   point_layer: Input Points (FeatureSet). Required parameter.

   bin_size: Bin Size (float). Required parameter.

   bin_size_unit: Bin Size Unit (str). Required parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   neighborhood_distance: Neighborhood Distance (float). Required parameter.

   neighborhood_distance_unit: Neighborhood Distance Unit (str). Required parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   time_step_interval: Time Step Interval (int). Optional parameter.

   time_step_interval_unit: Time Step Interval Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   time_step_alignment: Time Step Alignment (str). Optional parameter.
      Choice list:['EndTime', 'StartTime', 'ReferenceTime']

   time_step_reference: Time Step Reference (datetime). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   context: Context (str). Optional parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used. 


Returns:
   output - Output Features as a FeatureSet


    """
    kwargs = locals()

    param_db = {
        "point_layer": (FeatureSet, "pointLayer"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "neighborhood_distance": (float, "neighborhoodDistance"),
        "neighborhood_distance_unit": (str, "neighborhoodDistanceUnit"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_alignment": (str, "timeStepAlignment"),
        "time_step_reference": (datetime, "timeStepReference"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": FeatureSet},
    ]

    return _execute_gp_tool(gis, "FindHotSpots", kwargs, param_db, return_values, _use_async, _url)


