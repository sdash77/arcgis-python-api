import os
import sys
import uuid
import random
import string
import arcpy
from collections import namedtuple
from arcgis.features import SpatialDataFrame
import pandas as pd

#from arcgis.geoprocessing._gp._base import _process_kwargs, _process_results

def _execute_tool(module, tool, inputs, in_db, out_db):
     module = getattr(arcpy,module)
     func = getattr(module, tool)
     args = {}
     #Pre-1). Ensure all SDF are feature class, all DataFrames are Tables

     #1). check that required parameters are there.
     #2). Assemble all input
     rkeys = []
     for k,v in in_db.items():
          if isinstance(inputs[k], SpatialDataFrame):
               fc = inputs[k].to_featureclass(out_location=arcpy.env.scratchGDB,
                                              out_name=random.choice(string.ascii_letters) +                                              uuid.uuid4().hex[:5])
               inputs[k] = fc
          elif isinstance(inputs[k], pd.DataFrame):
               t = random.choice(string.ascii_letters) +                                      uuid.uuid4().hex[:5] + '.csv'
               tbl = os.path.join(arcpy.env.scratchFolder, t)
               v.to_csv(t)
               inputs[k] = t
          if v[1] == 'required' and k in inputs:
               args[v[0]] = inputs[k]
          elif v[1] == 'required' and not (k in inputs):
               raise ValueError("Missing required parameter: %s" % k)
          elif v[1] == 'optional' and k in inputs:
               args[v[0]] = inputs[k]
     for k,v in out_db.items():
          if v[1] == 'required' and v[0].find('feature_class') > -1:
               fc = os.path.join(arcpy.env.scratchGDB,
                                 random.choice(string.ascii_letters) + uuid.uuid4().hex[:5])
               args[v[0]] = fc

     #3). pass to tool
     results = func(**args)
     #4). Handle outputs (out_db) and convert feature
     #    classes to sdf, tables to pd.DataFrames
     tp = namedtuple("Results", list(out_db.keys()))
     res = []
     for i in range(results.outputCount):
          v = results.getOutput(i)
          dt = arcpy.Describe(v).dataType
          if dt.lower() == 'featureclass':
               sdf = SpatialDataFrame.from_featureclass(v)
               res.append(sdf)
          elif dt.lower() == 'table':
               def _rows_as_dicts(cursor, colnames):
                    for row in cursor:
                         yield dict(zip(colnames, row))
               data = []
               with arcpy.da.SearchCursor(v, '*') as sc:
                    fields = sc.fields
                    data = [row for row in _rows_as_dicts(sc, fields)]
               sdf = pd.DataFrame.from_dict(data)
               res.append(sdf)
          else:
               res.append(v)
     return tp(*res)


def buffer(features, buffer_distance_or_field, line_side=None, line_end_type=None, dissolve_option=None, dissolve_field=None, method=None):
     """
     Geoprocessing tool that creates buffer polygons around input features to a specified distance.
     """
     inputs = locals()
     in_db = {'buffer_distance_or_field': ['buffer_distance_or_field', 'required'], 'method': ['method', 'optional'], 'line_end_type': ['line_end_type', 'optional'], 'features': ['in_features', 'required'], 'dissolve_option': ['dissolve_option', 'optional'], 'line_side': ['line_side', 'optional'], 'dissolve_field': ['dissolve_field', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Buffer', inputs, in_db, out_db)

          
def clip(features, clip_features, cluster_tolerance=None):
     """
     Geoprocessing tool that extracts input features that overlay the clip features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'clip_features': ['clip_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Clip', inputs, in_db, out_db)

          
def erase(features, erase_features, cluster_tolerance=None):
     """
     Geoprocessing tool creates a feature class by overlaying the Input Features with the polygons of the Erase Features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'erase_features': ['erase_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Erase', inputs, in_db, out_db)

          
def identity(features, identity_features, joattributes=None, cluster_tolerance=None, relationship=None):
     """
     Geoprocessing tool computes a geometric intersection of the input features and identity features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'identity_features': ['identity_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'relationship': ['relationship', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Identity', inputs, in_db, out_db)

          
def intersect(features, joattributes=None, cluster_tolerance=None, output_type=None):
     """
     Geoprocessing tool that computes a geometric intersection of the input features. Features or portions of features which overlap in all layers and/or feature classes will be written to the output feature class.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'output_type': ['output_type', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Intersect', inputs, in_db, out_db)

          
def symmetrical_difference(features, update_features, joattributes=None, cluster_tolerance=None):
     """
     Geoprocessing tool that computes a geometric intersection of the input and update features, returning those input features and update features that do not overlap
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'update_features': ['update_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'SymmetricalDifference', inputs, in_db, out_db)

          
def update(features, update_features, keep_borders=None, cluster_tolerance=None):
     """
     Geoprocessing tool that computes a geometric intersection of the Input Features and Update Features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'keep_borders': ['keep_borders', 'optional'], 'update_features': ['update_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Update', inputs, in_db, out_db)

          
def split(features, split_features, split_field, out_workspace, cluster_tolerance=None):
     """
     Geoprocessing tool that uses overlaying split features to cut features into multiple smaller sections.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'out_workspace': ['out_workspace', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'split_features': ['split_features', 'required'], 'split_field': ['split_field', 'required']}
     out_db = {}
     return _execute_tool('analysis', 'Split', inputs, in_db, out_db)

          
def near(features, near_features, search_radius=None, location=None, angle=None, method=None):
     """
     Geoprocessing tool that calculates distance and additional proximity information between features.
     """
     inputs = locals()
     in_db = {'angle': ['angle', 'optional'], 'near_features': ['near_features', 'required'], 'method': ['method', 'optional'], 'features': ['in_features', 'required'], 'location': ['location', 'optional'], 'search_radius': ['search_radius', 'optional']}
     out_db = {}
     return _execute_tool('analysis', 'Near', inputs, in_db, out_db)

          
def point_distance(features, near_features, search_radius=None):
     """
     Geoprocessing tool that determines the distances from input point features to all points in the near features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'near_features': ['near_features', 'required'], 'search_radius': ['search_radius', 'optional']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('analysis', 'PointDistance', inputs, in_db, out_db)

          
def select(features, where_clause=None):
     """
     Geoprocessing tool that uses a select expression to extract features from one feature class and output them to a new feature class.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Select', inputs, in_db, out_db)

          
def table_select(table, where_clause=None):
     """
     Geoprocessing tool that selects table records matching a Structured Query Language (SQL) expression and writes them to an output table.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('analysis', 'TableSelect', inputs, in_db, out_db)

          
def frequency(table, frequency_fields, summary_fields=None):
     """
     Geoprocessing tool to read a table and create a new table containing the unique occurrences of field values and the frequency of their occurrence.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'summary_fields': ['summary_fields', 'optional'], 'frequency_fields': ['frequency_fields', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('analysis', 'Frequency', inputs, in_db, out_db)

          
def summary_statistics(table, statistics_fields, case_field=None):
     """
     Geoprocessing tool that calculates summary statistics for field(s) in a table.
     """
     inputs = locals()
     in_db = {'case_field': ['case_field', 'optional'], 'table': ['in_table', 'required'], 'statistics_fields': ['statistics_fields', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('analysis', 'SummaryStatistics', inputs, in_db, out_db)

          
def create_thiessen_polygons(features, fields_to_copy=None):
     """
     Geoprocessing tool to create Thiessen polygons from point features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'fields_to_copy': ['fields_to_copy', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'CreateThiessenPolygons', inputs, in_db, out_db)

          
def spatial_join(target_features, jofeatures, jooperation=None, jotype=None, field_mapping=None, match_option=None, search_radius=None, distance_field_name=None):
     """
     Geoprocessing tool used to join the attributes of two feature classes based on the spatial relationships between the features in the two feature classes and to write the join an output.
     """
     inputs = locals()
     in_db = {'jooperation': ['join_operation', 'optional'], 'match_option': ['match_option', 'optional'], 'field_mapping': ['field_mapping', 'optional'], 'jofeatures': ['join_features', 'required'], 'target_features': ['target_features', 'required'], 'distance_field_name': ['distance_field_name', 'optional'], 'search_radius': ['search_radius', 'optional'], 'jotype': ['join_type', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'SpatialJoin', inputs, in_db, out_db)

          
def multiple_ring_buffer(input_features, distances, buffer_unit=None, field_name=None, dissolve_option=None, outside_polygons_only=None):
     """
     Geoprocessing tool that creates multiple buffers at specified distances around the input features.
     """
     inputs = locals()
     in_db = {'field_name': ['Field_Name', 'optional'], 'distances': ['Distances', 'required'], 'input_features': ['Input_Features', 'required'], 'dissolve_option': ['Dissolve_Option', 'optional'], 'outside_polygons_only': ['Outside_Polygons_Only', 'optional'], 'buffer_unit': ['Buffer_Unit', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_class', 'required']}
     return _execute_tool('analysis', 'MultipleRingBuffer', inputs, in_db, out_db)

          
def generate_near_table(features, near_features, search_radius=None, location=None, angle=None, closest=None, closest_count=None, method=None):
     """
     Geoprocessing tool to calculate distance and other proximity information between features.
     """
     inputs = locals()
     in_db = {'angle': ['angle', 'optional'], 'near_features': ['near_features', 'required'], 'closest': ['closest', 'optional'], 'method': ['method', 'optional'], 'features': ['in_features', 'required'], 'location': ['location', 'optional'], 'search_radius': ['search_radius', 'optional'], 'closest_count': ['closest_count', 'optional']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('analysis', 'GenerateNearTable', inputs, in_db, out_db)

          
def union(features, joattributes=None, cluster_tolerance=None, gaps=None):
     """
     Geoprocessing tool computes a geometric union of the input features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'gaps': ['gaps', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'Union', inputs, in_db, out_db)

          
def tabulate_intersection(zone_features, zone_fields, class_features, class_fields=None, sum_fields=None, xy_tolerance=None, out_units=None):
     """
     Geoprocessing tool that cross-tabulates the intersection between two feature classes to determine how much of one feature class' features are inside the other's.
     """
     inputs = locals()
     in_db = {'zone_features': ['in_zone_features', 'required'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'sum_fields': ['sum_fields', 'optional'], 'out_units': ['out_units', 'optional'], 'zone_fields': ['zone_fields', 'required'], 'class_features': ['in_class_features', 'required'], 'class_fields': ['class_fields', 'optional']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('analysis', 'TabulateIntersection', inputs, in_db, out_db)

          
def polygon_neighbors(features, fields=None, area_overlap=None, both_sides=None, cluster_tolerance=None, out_linear_units=None, out_area_units=None):
     """
     Geoprocessing tool that creates a table with statistics based on polygon contiguity (overlaps, coincident edges, or nodes).
     """
     inputs = locals()
     in_db = {'area_overlap': ['area_overlap', 'optional'], 'out_area_units': ['out_area_units', 'optional'], 'out_linear_units': ['out_linear_units', 'optional'], 'features': ['in_features', 'required'], 'both_sides': ['both_sides', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'fields': ['in_fields', 'optional']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('analysis', 'PolygonNeighbors', inputs, in_db, out_db)

          
def split_by_attributes(input_table, target_workspace, split_fields):
     """
     
     """
     inputs = locals()
     in_db = {'split_fields': ['Split_Fields', 'required'], 'target_workspace': ['Target_Workspace', 'required'], 'input_table': ['Input_Table', 'required']}
     out_db = {}
     return _execute_tool('analysis', 'SplitByAttributes', inputs, in_db, out_db)

          
def graphic_buffer(features, buffer_distance_or_field, line_caps=None, line_joins=None, miter_limit=None, max_deviation=None):
     """
     Geoprocessing tool that creates buffer polygons around input features to a specified distance and provides control over the generation of the buffer features ends (caps) and corners (joins).
     """
     inputs = locals()
     in_db = {'buffer_distance_or_field': ['buffer_distance_or_field', 'required'], 'miter_limit': ['miter_limit', 'optional'], 'features': ['in_features', 'required'], 'line_joins': ['line_joins', 'optional'], 'max_deviation': ['max_deviation', 'optional'], 'line_caps': ['line_caps', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('analysis', 'GraphicBuffer', inputs, in_db, out_db)

          