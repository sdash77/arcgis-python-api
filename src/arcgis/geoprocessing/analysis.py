import os
import sys
import uuid
import random
import string
import arcpy
from collections import namedtuple
from arcgis.features import SpatialDataFrame
import pandas as pd

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
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     buffer_distance_or_field              Required GPComposite. Distance [value or field]
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_end_type                         Optional GPString. End Type. Default value: round. Value choices: round, flat
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                Optional GPString. Method. Default value: planar. Value choices: geodesic, planar
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_option                       Optional GPString. Dissolve Type. Default value: none. Value choices: none, all, list
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_side                             Optional GPString. Side Type. Default value: full. Value choices: full, left, right, outside_only
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        Optional GPMultiValue. Dissolve Field(s). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'line_end_type': ['line_end_type', 'optional'], 'features': ['in_features', 'required'], 'dissolve_option': ['dissolve_option', 'optional'], 'buffer_distance_or_field': ['buffer_distance_or_field', 'required'], 'method': ['method', 'optional'], 'line_side': ['line_side', 'optional'], 'dissolve_field': ['dissolve_field', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Buffer', inputs, in_db, out_db)

          
def clip(features, clip_features, cluster_tolerance=None):
     """
     Geoprocessing tool that extracts input features that overlay the clip features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_features                         Required GPFeatureLayer. Clip Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'clip_features': ['clip_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Clip', inputs, in_db, out_db)

          
def erase(features, erase_features, cluster_tolerance=None):
     """
     Geoprocessing tool creates a feature class by overlaying the Input Features with the polygons of the Erase Features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     erase_features                        Required GPFeatureLayer. Erase Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'erase_features': ['erase_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Erase', inputs, in_db, out_db)

          
def identity(features, identity_features, joattributes='all', cluster_tolerance=None, relationship='false'):
     """
     Geoprocessing tool computes a geometric intersection of the input features and identity features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     identity_features                     Required GPFeatureLayer. Identity Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     relationship                          Optional GPBoolean. Keep relationships. Default value: false. Value choices: keep_relationships, no_relationships
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          Optional GPString. JoinAttributes. Default value: all. Value choices: no_fid, only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'relationship': ['relationship', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'identity_features': ['identity_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Identity', inputs, in_db, out_db)

          
def intersect(features, joattributes='all', cluster_tolerance='-1 unknown', output_type='input'):
     """
     Geoprocessing tool that computes a geometric intersection of the input features. Features or portions of features which overlap in all layers and/or feature classes will be written to the output feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPValueTable. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_type                           Optional GPString. Output Type. Default value: input. Value choices: input, line, point
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: -1 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          Optional GPString. JoinAttributes. Default value: all. Value choices: no_fid, only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'output_type': ['output_type', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Intersect', inputs, in_db, out_db)

          
def update(features, update_features, keep_borders='true', cluster_tolerance=None):
     """
     Geoprocessing tool that computes a geometric intersection of the Input Features and Update Features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_features                       Required GPFeatureLayer. Update Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     keep_borders                          Optional GPBoolean. Borders. Default value: true. Value choices: borders, no_borders
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_features': ['update_features', 'required'], 'features': ['in_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'keep_borders': ['keep_borders', 'optional']}
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

     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     split_features                        Required GPFeatureLayer. Split Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_workspace                         Required GPComposite. Target Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'split_field': ['split_field', 'required'], 'features': ['in_features', 'required'], 'split_features': ['split_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'out_workspace': ['out_workspace', 'required']}
     out_db = {}
     return _execute_tool('analysis', 'Split', inputs, in_db, out_db)

          
def near(features, near_features, search_radius=None, location='false', angle='false', method='planar'):
     """
     Geoprocessing tool that calculates distance and additional proximity information between features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     near_features                         Required GPMultiValue. Near Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional GPLinearUnit. Search Radius. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                Optional GPString. Method. Default value: planar. Value choices: planar, geodesic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location                              Optional GPBoolean. Location. Default value: false. Value choices: location, no_location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     angle                                 Optional GPBoolean. Angle. Default value: false. Value choices: angle, no_angle
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'search_radius': ['search_radius', 'optional'], 'near_features': ['near_features', 'required'], 'features': ['in_features', 'required'], 'location': ['location', 'optional'], 'method': ['method', 'optional'], 'angle': ['angle', 'optional']}
     out_db = {}
     return _execute_tool('analysis', 'Near', inputs, in_db, out_db)

          
def point_distance(features, near_features, search_radius=None):
     """
     Geoprocessing tool that determines the distances from input point features to all points in the near features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     near_features                         Required GPFeatureLayer. Near Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional GPLinearUnit. Search Radius. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'search_radius': ['search_radius', 'optional'], 'near_features': ['near_features', 'required'], 'features': ['in_features', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'PointDistance', inputs, in_db, out_db)

          
def select(features, where_clause=None):
     """
     Geoprocessing tool that uses a select expression to extract features from one feature class and output them to a new feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Expression. Default value: none
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
     table                                 Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Expression. Default value: none
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
     frequency_fields                      Required GPMultiValue. Frequency Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     summary_fields                        Optional GPMultiValue. Summary Field(s). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'frequency_fields': ['frequency_fields', 'required'], 'summary_fields': ['summary_fields', 'optional'], 'table': ['in_table', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'Frequency', inputs, in_db, out_db)

          
def create_thiessen_polygons(features, fields_to_copy='only_fid'):
     """
     Geoprocessing tool to create Thiessen polygons from point features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields_to_copy                        Optional GPString. Output Fields. Default value: only_fid. Value choices: only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fields_to_copy': ['fields_to_copy', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'CreateThiessenPolygons', inputs, in_db, out_db)

          
def spatial_join(target_features, jofeatures, jooperation='join_one_to_one', jotype='true', field_mapping=None, match_option='intersect', search_radius=None, distance_field_name=None):
     """
     Geoprocessing tool used to join the attributes of two feature classes based on the spatial relationships between the features in the two feature classes and to write the join an output.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jofeatures                            Required GPFeatureLayer. Join Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_features                       Required GPFeatureLayer. Target Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jooperation                           Optional GPString. Join Operation. Default value: join_one_to_one. Value choices: join_one_to_one, join_one_to_many
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jotype                                Optional GPBoolean. Keep All Target Features. Default value: true. Value choices: keep_all, keep_common
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mapping                         Optional GPFieldMapping. Field Map of Join Features. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance_field_name                   Optional GPString. Distance Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     match_option                          Optional GPString. Match Option. Default value: intersect. Value choices: intersect, intersect_3d, within_a_distance_geodesic, within_a_distance, within_a_distance_3d, contains, completely_contains, contains_clementini, within, completely_within, within_clementini, are_identical_to, boundary_touches, share_a_line_segment_with, crossed_by_the_outline_of, have_their_center_in, closest_geodesic, closest
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional GPLinearUnit. Search Radius. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'jooperation': ['join_operation', 'optional'], 'jotype': ['join_type', 'optional'], 'field_mapping': ['field_mapping', 'optional'], 'distance_field_name': ['distance_field_name', 'optional'], 'search_radius': ['search_radius', 'optional'], 'jofeatures': ['join_features', 'required'], 'target_features': ['target_features', 'required'], 'match_option': ['match_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'SpatialJoin', inputs, in_db, out_db)

          
def multiple_ring_buffer(input_features, distances, buffer_unit='default', field_name='distance', dissolve_option='all', outside_polygons_only='false'):
     """
     Geoprocessing tool that creates multiple buffers at specified distances around the input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distances                             Required GPMultiValue. Distances
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_features                        Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_option                       Optional GPString. Dissolve Option. Default value: all. Value choices: all, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     buffer_unit                           Optional GPString. Buffer Unit. Default value: default. Value choices: default, centimeters, decimaldegrees, feet, inches, kilometers, meters, miles, millimeters, nauticalmiles, points, yards, decimeters
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_name                            Optional GPString. Field Name. Default value: distance
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     outside_polygons_only                 Optional GPBoolean. Outside Polygons Only. Default value: false. Value choices: outside_only, full
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'outside_polygons_only': ['Outside_Polygons_Only', 'optional'], 'distances': ['Distances', 'required'], 'dissolve_option': ['Dissolve_Option', 'optional'], 'input_features': ['Input_Features', 'required'], 'buffer_unit': ['Buffer_Unit', 'optional'], 'field_name': ['Field_Name', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'MultipleRingBuffer', inputs, in_db, out_db)

          
def generate_near_table(features, near_features, search_radius=None, location='false', angle='false', closest='true', closest_count='0', method='planar'):
     """
     Geoprocessing tool to calculate distance and other proximity information between features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     near_features                         Required GPMultiValue. Near Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional GPLinearUnit. Search Radius. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     closest_count                         Optional GPLong. Maximum number of closest matches. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     closest                               Optional GPBoolean. Find only closest feature. Default value: true. Value choices: closest, all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                Optional GPString. Method. Default value: planar. Value choices: planar, geodesic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     angle                                 Optional GPBoolean. Angle. Default value: false. Value choices: angle, no_angle
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location                              Optional GPBoolean. Location. Default value: false. Value choices: location, no_location
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'search_radius': ['search_radius', 'optional'], 'near_features': ['near_features', 'required'], 'features': ['in_features', 'required'], 'location': ['location', 'optional'], 'method': ['method', 'optional'], 'closest': ['closest', 'optional'], 'closest_count': ['closest_count', 'optional'], 'angle': ['angle', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'GenerateNearTable', inputs, in_db, out_db)

          
def union(features, joattributes='all', cluster_tolerance=None, gaps='true'):
     """
     Geoprocessing tool computes a geometric union of the input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPValueTable. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gaps                                  Optional GPBoolean. Gaps Allowed. Default value: true. Value choices: gaps, no_gaps
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          Optional GPString. JoinAttributes. Default value: all. Value choices: no_fid, only_fid, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'gaps': ['gaps', 'optional'], 'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Union', inputs, in_db, out_db)

          
def tabulate_intersection(zone_features, zone_fields, class_features, class_fields=None, sum_fields=None, xy_tolerance='-1 unknown', out_units='unknown'):
     """
     Geoprocessing tool that cross-tabulates the intersection between two feature classes to determine how much of one feature class' features are inside the other's.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     zone_fields                           Required GPMultiValue. Zone Fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     class_features                        Required GPFeatureLayer. Input Class Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     zone_features                         Required GPFeatureLayer. Input Zone Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional GPLinearUnit. XY Tolerance. Default value: -1 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_units                             Optional GPString. Output Units. Default value: unknown. Value choices: unknown, inches, feet, yards, miles, nautical_miles, millimeters, centimeters, decimeters, meters, kilometers, decimal_degrees, points, ares, acres, hectares, square_inches, square_feet, square_yards, square_miles, square_millimeters, square_centimeters, square_decimeters, square_meters, square_kilometers
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     class_fields                          Optional GPMultiValue. Class Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sum_fields                            Optional GPMultiValue. Sum Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'zone_fields': ['zone_fields', 'required'], 'class_fields': ['class_fields', 'optional'], 'out_units': ['out_units', 'optional'], 'class_features': ['in_class_features', 'required'], 'zone_features': ['in_zone_features', 'required'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'sum_fields': ['sum_fields', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'TabulateIntersection', inputs, in_db, out_db)

          
def polygon_neighbors(features, fields=None, area_overlap='false', both_sides='true', cluster_tolerance='-1 unknown', out_linear_units='unknown', out_area_units='unknown'):
     """
     Geoprocessing tool that creates a table with statistics based on polygon contiguity (overlaps, coincident edges, or nodes).

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_area_units                        Optional GPString. Output Area Units. Default value: unknown. Value choices: unknown, square_inches, square_feet, square_yards, acres, square_miles, square_millimeters, square_decimeters, square_centimeters, square_meters, square_kilometers, ares, hectares
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: -1 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_overlap                          Optional GPBoolean. Include area overlaps. Default value: false. Value choices: area_overlap, no_area_overlap
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     both_sides                            Optional GPBoolean. Include both sides of neighbor relationship. Default value: true. Value choices: both_sides, no_both_sides
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Optional GPMultiValue. Report By Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_linear_units                      Optional GPString. Output Linear Units. Default value: unknown. Value choices: unknown, inches, points, feet, yards, miles, nautical_miles, millimeters, centimeters, meters, kilometers, decimeters, decimal_degrees
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'out_area_units': ['out_area_units', 'optional'], 'area_overlap': ['area_overlap', 'optional'], 'both_sides': ['both_sides', 'optional'], 'fields': ['in_fields', 'optional'], 'out_linear_units': ['out_linear_units', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'PolygonNeighbors', inputs, in_db, out_db)

          
def split_by_attributes(input_table, target_workspace, split_fields):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_fields                          Required GPMultiValue. Split Fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_table                           Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_workspace                      Required DEWorkspace. Target Workspace
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'split_fields': ['Split_Fields', 'required'], 'input_table': ['Input_Table', 'required'], 'target_workspace': ['Target_Workspace', 'required']}
     out_db = {}
     return _execute_tool('analysis', 'SplitByAttributes', inputs, in_db, out_db)

          
def graphic_buffer(features, buffer_distance_or_field, line_caps='square', line_joins='miter', miter_limit='10', max_deviation='0 unknown'):
     """
     Geoprocessing tool that creates buffer polygons around input features to a specified distance and provides control over the generation of the buffer features ends (caps) and corners (joins).

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     buffer_distance_or_field              Required GPComposite. Distance [value or field]
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_caps                             Optional GPString. Caps Type. Default value: square. Value choices: square, butt, round
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     miter_limit                           Optional GPDouble. Miter Limit. Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_deviation                         Optional GPLinearUnit. Maximum Offset Deviation. Default value: 0 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_joins                            Optional GPString. Join Type. Default value: miter. Value choices: miter, bevel, round
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'line_caps': ['line_caps', 'optional'], 'miter_limit': ['miter_limit', 'optional'], 'features': ['in_features', 'required'], 'buffer_distance_or_field': ['buffer_distance_or_field', 'required'], 'max_deviation': ['max_deviation', 'optional'], 'line_joins': ['line_joins', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'GraphicBuffer', inputs, in_db, out_db)

          