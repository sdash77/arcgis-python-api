import os
import sys
import uuid
import random
import string
import arcpy
from collections import namedtuple
from arcgis.features import SpatialDataFrame
import pandas as pd

def _set_env_values():
     import arcgis
     from arcpy import env
     from arcgis.env import scratchgdb, workspace, overwrite_output
     if overwrite_output is None:
          arcgis.env.overwrite_output = env.overwriteOutput
     else:
          env.overwriteOutput = overwrite_output
     if workspace:
          env.workspace = workspace
     arcgis.env.scratchgdb = env.scratchGDB

def _execute_tool(module, tool, inputs, in_db, out_db):
     _set_env_values()
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
                                              out_name=random.choice(string.ascii_letters) + uuid.uuid4().hex[:5])
               inputs[k] = fc
          elif isinstance(inputs[k], pd.DataFrame):
               t = random.choice(string.ascii_letters) + uuid.uuid4().hex[:5] + '.csv'
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
     if len(res) == 1:
          return res[0]
     return tp(*res)


def buffer(features, buffer_distance_or_field, line_side='full', line_end_type='round', dissolve_option=None, dissolve_field=None, method='planar'):
     """
     Geoprocessing tool that creates buffer polygons around input features to a specified distance.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     buffer_distance_or_field              Required Linear unit or Field. Distance [value or field]
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_end_type                         Optional String. End Type. Default value: round. Value choices: round, flat
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                Optional String. Method. Default value: planar. Value choices: geodesic, planar
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        Optional Multiple Value. Dissolve Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_side                             Optional String. Side Type. Default value: full. Value choices: full, left, right, outside_only
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_option                       Optional String. Dissolve Type. Default value: none. Value choices: none, all, list
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'buffer_distance_or_field': ['buffer_distance_or_field', 'required'], 'line_end_type': ['line_end_type', 'optional'], 'dissolve_field': ['dissolve_field', 'optional'], 'line_side': ['line_side', 'optional'], 'method': ['method', 'optional'], 'features': ['in_features', 'required'], 'dissolve_option': ['dissolve_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Buffer', inputs, in_db, out_db)


def clip(features, clip_features, cluster_tolerance=None):
     """
     Geoprocessing tool that extracts input features that overlay the clip features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     clip_features                         Required Feature Layer. Clip Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'clip_features': ['clip_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Clip', inputs, in_db, out_db)


def erase(features, erase_features, cluster_tolerance=None):
     """
     Geoprocessing tool creates a feature class by overlaying the Input Features with the polygons of the Erase Features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     erase_features                        Required Feature Layer. Erase Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'erase_features': ['erase_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Erase', inputs, in_db, out_db)


def identity(features, identity_features, joattributes='all', cluster_tolerance=None, relationship='false'):
     """
     Geoprocessing tool computes a geometric intersection of the input features and identity features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     identity_features                     Required Feature Layer. Identity Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     relationship                          Optional Boolean. Keep relationships. Default value: false. Value choices: keep_relationships, no_relationships
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          Optional String. JoinAttributes. Default value: all. Value choices: no_fid, only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'relationship': ['relationship', 'optional'], 'identity_features': ['identity_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Identity', inputs, in_db, out_db)


def intersect(features, joattributes='all', cluster_tolerance='-1 unknown', output_type='input'):
     """
     Geoprocessing tool that computes a geometric intersection of the input features. Features or portions of features which overlap in all layers and/or feature classes will be written to the output feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Value Table. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: -1 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_type                           Optional String. Output Type. Default value: input. Value choices: input, line, point
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          Optional String. JoinAttributes. Default value: all. Value choices: no_fid, only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'output_type': ['output_type', 'optional'], 'joattributes': ['join_attributes', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Intersect', inputs, in_db, out_db)


def update(features, update_features, keep_borders='true', cluster_tolerance=None):
     """
     Geoprocessing tool that computes a geometric intersection of the Input Features and Update Features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_features                       Required Feature Layer. Update Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     keep_borders                          Optional Boolean. Borders. Default value: true. Value choices: borders, no_borders
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_features': ['update_features', 'required'], 'keep_borders': ['keep_borders', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Update', inputs, in_db, out_db)


def split(features, split_features, split_field, out_workspace, cluster_tolerance=None):
     """
     Geoprocessing tool that uses overlaying split features to cut features into multiple smaller sections.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_field                           Required Field. Split Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     split_features                        Required Feature Layer. Split Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_workspace                         Required Workspace or Feature Dataset. Target Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'split_field': ['split_field', 'required'], 'split_features': ['split_features', 'required'], 'features': ['in_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'out_workspace': ['out_workspace', 'required']}
     out_db = {}
     return _execute_tool('analysis', 'Split', inputs, in_db, out_db)


def near(features, near_features, search_radius=None, location='false', angle='false', method='planar'):
     """
     Geoprocessing tool that calculates distance and additional proximity information between features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     near_features                         Required Multiple Value. Near Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                Optional String. Method. Default value: planar. Value choices: planar, geodesic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location                              Optional Boolean. Location. Default value: false. Value choices: location, no_location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     angle                                 Optional Boolean. Angle. Default value: false. Value choices: angle, no_angle
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional Linear unit. Search Radius. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'near_features': ['near_features', 'required'], 'search_radius': ['search_radius', 'optional'], 'method': ['method', 'optional'], 'location': ['location', 'optional'], 'features': ['in_features', 'required'], 'angle': ['angle', 'optional']}
     out_db = {}
     return _execute_tool('analysis', 'Near', inputs, in_db, out_db)


def point_distance(features, near_features, search_radius=None):
     """
     Geoprocessing tool that determines the distances from input point features to all points in the near features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     near_features                         Required Feature Layer. Near Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional Linear unit. Search Radius. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'near_features': ['near_features', 'required'], 'features': ['in_features', 'required'], 'search_radius': ['search_radius', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'PointDistance', inputs, in_db, out_db)


def select(features, where_clause=None):
     """
     Geoprocessing tool that uses a select expression to extract features from one feature class and output them to a new feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Expression. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Select', inputs, in_db, out_db)


def table_select(table, where_clause=None):
     """
     Geoprocessing tool that selects table records matching a Structured Query Language (SQL) expression and writes them to an output table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View or Raster Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Expression. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'TableSelect', inputs, in_db, out_db)


def frequency(table, frequency_fields, summary_fields=None):
     """
     Geoprocessing tool to read a table and create a new table containing the unique occurrences of field values and the frequency of their occurrence.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View or Raster Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     frequency_fields                      Required Multiple Value. Frequency Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     summary_fields                        Optional Multiple Value. Summary Field(s). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'summary_fields': ['summary_fields', 'optional'], 'frequency_fields': ['frequency_fields', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'Frequency', inputs, in_db, out_db)


def create_thiessen_polygons(features, fields_to_copy='only_fid'):
     """
     Geoprocessing tool to create Thiessen polygons from point features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields_to_copy                        Optional String. Output Fields. Default value: only_fid. Value choices: only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fields_to_copy': ['fields_to_copy', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'CreateThiessenPolygons', inputs, in_db, out_db)


def spatial_join(target_features, join_features, join_operation='join_one_to_one', join_type='true', field_mapping=None, match_option='intersect', search_radius=None, distance_field_name=None):
     """
     Geoprocessing tool used to join the attributes of two feature classes based on the spatial relationships between the features in the two feature classes and to write the join an output.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     join_features                            Required Feature Layer. Join Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_features                       Required Feature Layer. Target Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     join_type                                Optional Boolean. Keep All Target Features. Default value: true. Value choices: keep_all, keep_common
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mapping                         Optional Field Mappings. Field Map of Join Features. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     match_option                          Optional String. Match Option. Default value: intersect. Value choices: intersect, intersect_3d, within_a_distance_geodesic, within_a_distance, within_a_distance_3d, contains, completely_contains, contains_clementini, within, completely_within, within_clementini, are_identical_to, boundary_touches, share_a_line_segment_with, crossed_by_the_outline_of, have_their_center_in, closest_geodesic, closest
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance_field_name                   Optional String. Distance Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional Linear unit. Search Radius. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     join_operation                           Optional String. Join Operation. Default value: join_one_to_one. Value choices: join_one_to_one, join_one_to_many
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'join_type': ['join_type', 'optional'],
              'join_features': ['join_features', 'required'],
              'field_mapping': ['field_mapping', 'optional'],
              'match_option': ['match_option', 'optional'],
              'target_features': ['target_features', 'required'],
              'search_radius': ['search_radius', 'optional'],
              'distance_field_name': ['distance_field_name', 'optional'],
              'join_operation': ['join_operation', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'SpatialJoin', inputs, in_db, out_db)


def multiple_ring_buffer(input_features, distances, buffer_unit='default', field_name='distance', dissolve_option='all', outside_polygons_only='false'):
     """
     Geoprocessing tool that creates multiple buffers at specified distances around the input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distances                             Required Multiple Value. Distances
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_features                        Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     buffer_unit                           Optional String. Buffer Unit. Default value: default. Value choices: default, centimeters, decimaldegrees, feet, inches, kilometers, meters, miles, millimeters, nauticalmiles, points, yards, decimeters
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     outside_polygons_only                 Optional Boolean. Outside Polygons Only. Default value: false. Value choices: outside_only, full
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_name                            Optional String. Field Name. Default value: distance
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_option                       Optional String. Dissolve Option. Default value: all. Value choices: all, none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'buffer_unit': ['Buffer_Unit', 'optional'], 'input_features': ['Input_Features', 'required'], 'field_name': ['Field_Name', 'optional'], 'outside_polygons_only': ['Outside_Polygons_Only', 'optional'], 'distances': ['Distances', 'required'], 'dissolve_option': ['Dissolve_Option', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'MultipleRingBuffer', inputs, in_db, out_db)


def generate_near_table(features, near_features, search_radius=None, location='false', angle='false', closest='true', closest_count='0', method='planar'):
     """
     Geoprocessing tool to calculate distance and other proximity information between features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     near_features                         Required Multiple Value. Near Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     closest                               Optional Boolean. Find only closest feature. Default value: true. Value choices: closest, all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location                              Optional Boolean. Location. Default value: false. Value choices: location, no_location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional Linear unit. Search Radius. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                Optional String. Method. Default value: planar. Value choices: planar, geodesic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     closest_count                         Optional Long. Maximum number of closest matches. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     angle                                 Optional Boolean. Angle. Default value: false. Value choices: angle, no_angle
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'closest': ['closest', 'optional'], 'near_features': ['near_features', 'required'], 'search_radius': ['search_radius', 'optional'], 'method': ['method', 'optional'], 'location': ['location', 'optional'], 'closest_count': ['closest_count', 'optional'], 'features': ['in_features', 'required'], 'angle': ['angle', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'GenerateNearTable', inputs, in_db, out_db)


def union(features, joattributes='all', cluster_tolerance=None, gaps='true'):
     """
     Geoprocessing tool computes a geometric union of the input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Value Table. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gaps                                  Optional Boolean. Gaps Allowed. Default value: true. Value choices: gaps, no_gaps
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          Optional String. JoinAttributes. Default value: all. Value choices: no_fid, only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'gaps': ['gaps', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Union', inputs, in_db, out_db)


def tabulate_intersection(zone_features, zone_fields, class_features, class_fields=None, sum_fields=None, xy_tolerance='-1 unknown', out_units='unknown'):
     """
     Geoprocessing tool that cross-tabulates the intersection between two feature classes to determine how much of one feature class' features are inside the other's.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     class_features                        Required Feature Layer. Input Class Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     zone_fields                           Required Multiple Value. Zone Fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     zone_features                         Required Feature Layer. Input Zone Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional Linear unit. XY Tolerance. Default value: -1 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sum_fields                            Optional Multiple Value. Sum Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_units                             Optional String. Output Units. Default value: unknown. Value choices: unknown, inches, feet, yards, miles, nautical_miles, millimeters, centimeters, decimeters, meters, kilometers, decimal_degrees, points, ares, acres, hectares, square_inches, square_feet, square_yards, square_miles, square_millimeters, square_centimeters, square_decimeters, square_meters, square_kilometers
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     class_fields                          Optional Multiple Value. Class Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'xy_tolerance': ['xy_tolerance', 'optional'], 'class_features': ['in_class_features', 'required'], 'zone_fields': ['zone_fields', 'required'], 'class_fields': ['class_fields', 'optional'], 'zone_features': ['in_zone_features', 'required'], 'out_units': ['out_units', 'optional'], 'sum_fields': ['sum_fields', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'TabulateIntersection', inputs, in_db, out_db)


def polygon_neighbors(features, fields=None, area_overlap='false', both_sides='true', cluster_tolerance='-1 unknown', out_linear_units='unknown', out_area_units='unknown'):
     """
     Geoprocessing tool that creates a table with statistics based on polygon contiguity (overlaps, coincident edges, or nodes).

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_area_units                        Optional String. Output Area Units. Default value: unknown. Value choices: unknown, square_inches, square_feet, square_yards, acres, square_miles, square_millimeters, square_decimeters, square_centimeters, square_meters, square_kilometers, ares, hectares
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     both_sides                            Optional Boolean. Include both sides of neighbor relationship. Default value: true. Value choices: both_sides, no_both_sides
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Optional Multiple Value. Report By Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_overlap                          Optional Boolean. Include area overlaps. Default value: false. Value choices: area_overlap, no_area_overlap
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_linear_units                      Optional String. Output Linear Units. Default value: unknown. Value choices: unknown, inches, points, feet, yards, miles, nautical_miles, millimeters, centimeters, meters, kilometers, decimeters, decimal_degrees
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: -1 unknown
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_area_units': ['out_area_units', 'optional'], 'both_sides': ['both_sides', 'optional'], 'fields': ['in_fields', 'optional'], 'area_overlap': ['area_overlap', 'optional'], 'out_linear_units': ['out_linear_units', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'PolygonNeighbors', inputs, in_db, out_db)


def split_by_attributes(input_table, target_workspace, split_fields):
     """


     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_fields                          Required Multiple Value. Split Fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_workspace                      Required Workspace. Target Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_table                           Required Table View. Input Table
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'split_fields': ['Split_Fields', 'required'], 'target_workspace': ['Target_Workspace', 'required'], 'input_table': ['Input_Table', 'required']}
     out_db = {}
     return _execute_tool('analysis', 'SplitByAttributes', inputs, in_db, out_db)


def graphic_buffer(features, buffer_distance_or_field, line_caps='square', line_joins='miter', miter_limit='10', max_deviation='0 unknown'):
     """
     Geoprocessing tool that creates buffer polygons around input features to a specified distance and provides control over the generation of the buffer features ends (caps) and corners (joins).

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     buffer_distance_or_field              Required Linear unit or Field. Distance [value or field]
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_caps                             Optional String. Caps Type. Default value: square. Value choices: square, butt, round
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_deviation                         Optional Linear unit. Maximum Offset Deviation. Default value: 0 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_joins                            Optional String. Join Type. Default value: miter. Value choices: miter, bevel, round
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     miter_limit                           Optional Double. Miter Limit. Default value: 10
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'buffer_distance_or_field': ['buffer_distance_or_field', 'required'], 'max_deviation': ['max_deviation', 'optional'], 'line_joins': ['line_joins', 'optional'], 'line_caps': ['line_caps', 'optional'], 'features': ['in_features', 'required'], 'miter_limit': ['miter_limit', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'GraphicBuffer', inputs, in_db, out_db)

