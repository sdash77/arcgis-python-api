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


def buffer(features, buffer_distance_or_field, line_side='FULL', line_end_type='ROUND', dissolve_option=None, dissolve_field=None, method='PLANAR'):
     """
     Geoprocessing tool that creates buffer polygons around input features to a specified distance.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     buffer_distance_or_field              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                optional. Default value: PLANAR. Value choices: GEODESIC,PLANAR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_end_type                         optional. Default value: ROUND. Value choices: ROUND,FLAT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_option                       optional. Default value: NONE. Value choices: NONE,ALL,LIST
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_side                             optional. Default value: FULL. Value choices: FULL,LEFT,RIGHT,OUTSIDE_ONLY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'buffer_distance_or_field': ['buffer_distance_or_field', 'required'], 'line_side': ['line_side', 'optional'], 'dissolve_option': ['dissolve_option', 'optional'], 'line_end_type': ['line_end_type', 'optional'], 'features': ['in_features', 'required'], 'dissolve_field': ['dissolve_field', 'optional'], 'method': ['method', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Buffer', inputs, in_db, out_db)

          
def clip(features, clip_features, cluster_tolerance=None):
     """
     Geoprocessing tool that extracts input features that overlay the clip features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     clip_features                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'clip_features': ['clip_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Clip', inputs, in_db, out_db)

          
def erase(features, erase_features, cluster_tolerance=None):
     """
     Geoprocessing tool creates a feature class by overlaying the Input Features with the polygons of the Erase Features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     erase_features                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'erase_features': ['erase_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Erase', inputs, in_db, out_db)

          
def identity(features, identity_features, joattributes='ALL', cluster_tolerance=None, relationship='false'):
     """
     Geoprocessing tool computes a geometric intersection of the input features and identity features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     identity_features                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     relationship                          optional. Default value: false. Value choices: KEEP_RELATIONSHIPS,NO_RELATIONSHIPS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          optional. Default value: ALL. Value choices: NO_FID,ONLY_FID,ALL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'identity_features': ['identity_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'relationship': ['relationship', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Identity', inputs, in_db, out_db)

          
def intersect(features, joattributes='ALL', cluster_tolerance='-1 Unknown', output_type='INPUT'):
     """
     Geoprocessing tool that computes a geometric intersection of the input features. Features or portions of features which overlap in all layers and/or feature classes will be written to the output feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          optional. Default value: ALL. Value choices: NO_FID,ONLY_FID,ALL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_type                           optional. Default value: INPUT. Value choices: INPUT,LINE,POINT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: -1 Unknown. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'output_type': ['output_type', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Intersect', inputs, in_db, out_db)

          
def update(features, update_features, keep_borders='true', cluster_tolerance=None):
     """
     Geoprocessing tool that computes a geometric intersection of the Input Features and Update Features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     update_features                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     keep_borders                          optional. Default value: true. Value choices: BORDERS,NO_BORDERS
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'update_features': ['update_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'keep_borders': ['keep_borders', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Update', inputs, in_db, out_db)

          
def split(features, split_features, split_field, out_workspace, cluster_tolerance=None):
     """
     Geoprocessing tool that uses overlaying split features to cut features into multiple smaller sections.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_workspace                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     split_field                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     split_features                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'out_workspace': ['out_workspace', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'split_field': ['split_field', 'required'], 'split_features': ['split_features', 'required']}
     out_db = {}
     return _execute_tool('analysis', 'Split', inputs, in_db, out_db)

          
def near(features, near_features, search_radius=None, location='false', angle='false', method='PLANAR'):
     """
     Geoprocessing tool that calculates distance and additional proximity information between features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     near_features                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     angle                                 optional. Default value: false. Value choices: ANGLE,NO_ANGLE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location                              optional. Default value: false. Value choices: LOCATION,NO_LOCATION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     method                                optional. Default value: PLANAR. Value choices: PLANAR,GEODESIC
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'search_radius': ['search_radius', 'optional'], 'near_features': ['near_features', 'required'], 'method': ['method', 'optional'], 'angle': ['angle', 'optional'], 'features': ['in_features', 'required'], 'location': ['location', 'optional']}
     out_db = {}
     return _execute_tool('analysis', 'Near', inputs, in_db, out_db)

          
def select(features, where_clause=None):
     """
     Geoprocessing tool that uses a select expression to extract features from one feature class and output them to a new feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Select', inputs, in_db, out_db)

          
def frequency(table, frequency_fields, summary_fields=None):
     """
     Geoprocessing tool to read a table and create a new table containing the unique occurrences of field values and the frequency of their occurrence.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     frequency_fields                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     summary_fields                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'summary_fields': ['summary_fields', 'optional'], 'frequency_fields': ['frequency_fields', 'required'], 'table': ['in_table', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('analysis', 'Frequency', inputs, in_db, out_db)

          
def union(features, joattributes='ALL', cluster_tolerance=None, gaps='true'):
     """
     Geoprocessing tool computes a geometric union of the input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joattributes                          optional. Default value: ALL. Value choices: NO_FID,ONLY_FID,ALL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gaps                                  optional. Default value: true. Value choices: GAPS,NO_GAPS
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'joattributes': ['join_attributes', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'gaps': ['gaps', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('analysis', 'Union', inputs, in_db, out_db)

          