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


def delete_rows(rows):
     """
     Geoprocessing tool that removes all records from a table, unless a selection is defined on the table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows                                  required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'rows': ['in_rows', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteRows', inputs, in_db, out_db)

          
def copy_rows(rows, config_keyword=None):
     """
     Geoprocessing tool that duplicates the contents of a table, table view, feature layer, or feature class to another table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'optional'], 'rows': ['in_rows', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'CopyRows', inputs, in_db, out_db)

          
def copy_features(features, config_keyword=None, spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None):
     """
     Geoprocessing tool to copy features to a new feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'spatial_grid_2': ['spatial_grid_2', 'optional'], 'config_keyword': ['config_keyword', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'features': ['in_features', 'required'], 'spatial_grid_3': ['spatial_grid_3', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'CopyFeatures', inputs, in_db, out_db)

          
def dissolve(features, dissolve_field=None, statistics_fields=None, multi_part='true', unsplit_lines='false'):
     """
     Geoprocessing tool used to aggregate features based on specified attributes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics_fields                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     unsplit_lines                         optional. Default value: false. Value choices: UNSPLIT_LINES,DISSOLVE_LINES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     multi_part                            optional. Default value: true. Value choices: MULTI_PART,SINGLE_PART
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'statistics_fields': ['statistics_fields', 'optional'], 'dissolve_field': ['dissolve_field', 'optional'], 'unsplit_lines': ['unsplit_lines', 'optional'], 'features': ['in_features', 'required'], 'multi_part': ['multi_part', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'Dissolve', inputs, in_db, out_db)

          
def make_feature_layer(features, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a feature layer from an input feature class or layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_info                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_info': ['field_info', 'optional'], 'workspace': ['workspace', 'optional'], 'features': ['in_features', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeFeatureLayer', inputs, in_db, out_db)

          
def save_to_layer_file(layer, is_relative_path=None, version='CURRENT'):
     """
     Geoprocessing tool that creates a layer file (.lyrx) that references geographic data stored on disk.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     is_relative_path                      optional. Default value: None. Value choices: RELATIVE,ABSOLUTE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               optional. Default value: CURRENT. Value choices: CURRENT,10.4,10.3,10.2,10.1,10,9.3,9.2,9.1,9.0,8.3
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'is_relative_path': ['is_relative_path', 'optional'], 'layer': ['in_layer', 'required'], 'version': ['version', 'optional']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'SaveToLayerFile', inputs, in_db, out_db)

          
def add_join(layer_or_view, field, jotable, jofield, jotype='true'):
     """
     Geoprocessing tool that  joins a layer to another layer or table (where layer is a feature layer, table view, or raster layer with raster attribute table) based on a common field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jotable                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     layer_or_view                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jotype                                optional. Default value: true. Value choices: KEEP_ALL,KEEP_COMMON
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'jotype': ['join_type', 'optional'], 'field': ['in_field', 'required'], 'jofield': ['join_field', 'required'], 'jotable': ['join_table', 'required'], 'layer_or_view': ['in_layer_or_view', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddJoin', inputs, in_db, out_db)

          
def remove_join(layer_or_view, joname=None):
     """
     Geoprocessing tool that removes a join from a feature layer or table view.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer_or_view                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joname                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'joname': ['join_name', 'optional'], 'layer_or_view': ['in_layer_or_view', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveJoin', inputs, in_db, out_db)

          
def copy(data, data_type=None):
     """
     Geoprocessing tool that duplicates all types of geodata as well as most other dataset types.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'data_type': ['data_type', 'optional'], 'data': ['in_data', 'required']}
     out_db = {'data': ['out_data', 'required', None, None]}
     return _execute_tool('management', 'Copy', inputs, in_db, out_db)

          
def delete(data, data_type=None):
     """
     Geoprocessing tool that permanently removes the specified item from disk.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'data_type': ['data_type', 'optional'], 'data': ['in_data', 'required']}
     out_db = {}
     return _execute_tool('management', 'Delete', inputs, in_db, out_db)

          
def rename(data, data_type=None):
     """
     Geoprocessing tool that changes the name of a dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'data_type': ['data_type', 'optional'], 'data': ['in_data', 'required']}
     out_db = {'data': ['out_data', 'required', None, None]}
     return _execute_tool('management', 'Rename', inputs, in_db, out_db)

          
def create_folder(out_folder_path, out_name):
     """
     Geoprocessing tool that creates a folder.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder_path                       required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_folder_path': ['out_folder_path', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateFolder', inputs, in_db, out_db)

          
def create_feature_dataset(out_dataset_path, out_name, spatial_reference=None):
     """
     Geoprocessing tool that creates a feature dataset in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_dataset_path                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_dataset_path': ['out_dataset_path', 'required'], 'out_name': ['out_name', 'required'], 'spatial_reference': ['spatial_reference', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFeatureDataset', inputs, in_db, out_db)

          
def pivot_table(table, fields, pivot_field, value_field):
     """
     Geoprocessing tool that uses a pivot and value field to streamline the input table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     value_field                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     pivot_field                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'value_field': ['value_field', 'required'], 'pivot_field': ['pivot_field', 'required'], 'table': ['in_table', 'required'], 'fields': ['fields', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'PivotTable', inputs, in_db, out_db)

          
def create_feature_class(out_path, out_name, geometry_type='POLYGON', template=None, has_m='DISABLED', has_z='DISABLED', spatial_reference=None, config_keyword=None, spatial_grid_1='1000', spatial_grid_2='0', spatial_grid_3='0'):
     """
     Geoprocessing tool that creates a feature class, either in an ArcSDE, file geodatabase, or personal geodatabase, or as a shapefile in a folder.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         optional. Default value: POLYGON. Value choices: POINT,MULTIPOINT,POLYGON,POLYLINE,MULTIPATCH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        optional. Default value: 1000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     has_z                                 optional. Default value: DISABLED. Value choices: DISABLED,SAME_AS_TEMPLATE,ENABLED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     has_m                                 optional. Default value: DISABLED. Value choices: DISABLED,SAME_AS_TEMPLATE,ENABLED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'spatial_grid_3': ['spatial_grid_3', 'optional'], 'out_path': ['out_path', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'has_z': ['has_z', 'optional'], 'out_name': ['out_name', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'has_m': ['has_m', 'optional'], 'geometry_type': ['geometry_type', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFeatureClass', inputs, in_db, out_db)

          
def create_table(out_path, out_name, template=None, config_keyword=None):
     """
     Geoprocessing tool that creates a geodatabase table, an INFO table, or dBASE table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'out_path': ['out_path', 'required'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateTable', inputs, in_db, out_db)

          
def make_table_view(table, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a table view from an input table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_info                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_info': ['field_info', 'optional'], 'workspace': ['workspace', 'optional'], 'table': ['in_table', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'view': ['out_view', 'required', None, None]}
     return _execute_tool('management', 'MakeTableView', inputs, in_db, out_db)

          
def add_spatial_index(features, spatial_grid_1='0', spatial_grid_2='0', spatial_grid_3='0'):
     """
     Geoprocessing tool that adds a spatial index to a feature class

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        optional. Default value: 0. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'spatial_grid_2': ['spatial_grid_2', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddSpatialIndex', inputs, in_db, out_db)

          
def remove_spatial_index(features):
     """
     Geoprocessing tool that deletes the spatial index from a shapefile, file geodatabase feature class, or enterprise geodatabase feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveSpatialIndex', inputs, in_db, out_db)

          
def create_domain(workspace, domaname, field_type, domadescription=None, domatype='CODED', split_policy='DEFAULT', merge_policy='DEFAULT'):
     """
     Geoprocessing tool that creates an attribute domain in the specified workspace.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_type                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domadescription                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_policy                          optional. Default value: DEFAULT. Value choices: DEFAULT,DUPLICATE,GEOMETRY_RATIO
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     merge_policy                          optional. Default value: DEFAULT. Value choices: DEFAULT,SUM_VALUES,AREA_WEIGHTED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domatype                              optional. Default value: CODED. Value choices: CODED,RANGE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'domadescription': ['domain_description', 'optional'], 'split_policy': ['split_policy', 'optional'], 'domatype': ['domain_type', 'optional'], 'merge_policy': ['merge_policy', 'optional'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required'], 'field_type': ['field_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDomain', inputs, in_db, out_db)

          
def delete_domain(workspace, domaname):
     """
     Geoprocessing tool to delete a domain from a workspace.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteDomain', inputs, in_db, out_db)

          
def add_coded_value_to_domain(workspace, domaname, code, code_description):
     """
     Geoprocessing tool that adds a value to a domain's coded value list.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code_description                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'domaname': ['domain_name', 'required'], 'code_description': ['code_description', 'required'], 'code': ['code', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddCodedValueToDomain', inputs, in_db, out_db)

          
def delete_coded_value_from_domain(workspace, domaname, code):
     """
     Geoprocessing tool that removes a value from a coded value domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'domaname': ['domain_name', 'required'], 'code': ['code', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteCodedValueFromDomain', inputs, in_db, out_db)

          
def set_value_for_range_domain(workspace, domaname, mvalue, max_value):
     """
     Geoprocessing tool that sets the minimun and maximum values for an existing Range domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mvalue                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     max_value                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mvalue': ['min_value', 'required'], 'domaname': ['domain_name', 'required'], 'max_value': ['max_value', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetValueForRangeDomain', inputs, in_db, out_db)

          
def assign_domain_to_field(table, field_name, domaname, subtype_code=None):
     """
     Geoprocessing tool that sets the domain for a particular field and, optionally, for a subtype.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_name                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_name': ['field_name', 'required'], 'subtype_code': ['subtype_code', 'optional'], 'domaname': ['domain_name', 'required'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'AssignDomainToField', inputs, in_db, out_db)

          
def remove_domain_from_field(table, field_name, subtype_code=None):
     """
     Geoprocessing tool that removes an attribute domain association from a feature class or table field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_name                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_name': ['field_name', 'required'], 'subtype_code': ['subtype_code', 'optional'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveDomainFromField', inputs, in_db, out_db)

          
def table_to_domain(table, code_field, description_field, workspace, domaname, domadescription=None, update_option='APPEND'):
     """
     Geoprocessing tool that creates or updates a coded value domain with values from a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     description_field                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_option                         optional. Default value: APPEND. Value choices: APPEND,REPLACE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domadescription                       optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_option': ['update_option', 'optional'], 'domadescription': ['domain_description', 'optional'], 'table': ['in_table', 'required'], 'workspace': ['in_workspace', 'required'], 'code_field': ['code_field', 'required'], 'description_field': ['description_field', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'TableToDomain', inputs, in_db, out_db)

          
def domain_to_table(workspace, domaname, code_field, description_field, configuration_keyword=None):
     """
     Geoprocessing tool that creates a table from an attribute domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     description_field                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     configuration_keyword                 optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'code_field': ['code_field', 'required'], 'domaname': ['domain_name', 'required'], 'configuration_keyword': ['configuration_keyword', 'optional'], 'description_field': ['description_field', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'DomainToTable', inputs, in_db, out_db)

          
def select_layer_by_attribute(layer_or_view, selection_type='NEW_SELECTION', where_clause=None):
     """
     Geoprocessing tool that adds, updates, or removes a selection on a layer or table view based on an attribute query.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer_or_view                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_type                        optional. Default value: NEW_SELECTION. Value choices: NEW_SELECTION,ADD_TO_SELECTION,REMOVE_FROM_SELECTION,SUBSET_SELECTION,SWITCH_SELECTION,CLEAR_SELECTION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'where_clause': ['where_clause', 'optional'], 'selection_type': ['selection_type', 'optional'], 'layer_or_view': ['in_layer_or_view', 'required']}
     out_db = {}
     return _execute_tool('management', 'SelectLayerByAttribute', inputs, in_db, out_db)

          
def select_layer_by_location(layer, overlap_type='INTERSECT', select_features=None, search_distance=None, selection_type='NEW_SELECTION', invert_spatial_relationship='false'):
     """
     Geoprocessing tool that selects features in a layer based on a spatial relationship to features in another layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     select_features                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_distance                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_type                        optional. Default value: NEW_SELECTION. Value choices: NEW_SELECTION,ADD_TO_SELECTION,REMOVE_FROM_SELECTION,SUBSET_SELECTION,SWITCH_SELECTION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overlap_type                          optional. Default value: INTERSECT. Value choices: INTERSECT,INTERSECT_3D,WITHIN_A_DISTANCE_GEODESIC,WITHIN_A_DISTANCE,WITHIN_A_DISTANCE_3D,CONTAINS,COMPLETELY_CONTAINS,CONTAINS_CLEMENTINI,WITHIN,COMPLETELY_WITHIN,WITHIN_CLEMENTINI,ARE_IDENTICAL_TO,BOUNDARY_TOUCHES,SHARE_A_LINE_SEGMENT_WITH,CROSSED_BY_THE_OUTLINE_OF,HAVE_THEIR_CENTER_IN
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     invert_spatial_relationship           optional. Default value: false. Value choices: INVERT,NOT_INVERT
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'select_features': ['select_features', 'optional'], 'search_distance': ['search_distance', 'optional'], 'layer': ['in_layer', 'required'], 'selection_type': ['selection_type', 'optional'], 'invert_spatial_relationship': ['invert_spatial_relationship', 'optional'], 'overlap_type': ['overlap_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SelectLayerByLocation', inputs, in_db, out_db)

          
def get_count(rows):
     """
     Geoprocessing tool that reports the number of rows of the input data.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows                                  required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'rows': ['in_rows', 'required']}
     out_db = {}
     return _execute_tool('management', 'GetCount', inputs, in_db, out_db)

          
def create_version(workspace, parent_version, version_name, access_permission='PRIVATE'):
     """
     Geoprocessing tool to create a new version in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     parent_version                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     version_name                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     access_permission                     optional. Default value: PRIVATE. Value choices: PRIVATE,PUBLIC,PROTECTED
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'access_permission': ['access_permission', 'optional'], 'parent_version': ['parent_version', 'required'], 'version_name': ['version_name', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateVersion', inputs, in_db, out_db)

          
def delete_version(workspace, version_name):
     """
     Geoprocessing tool to delete a specific version from a geodatabase

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_name                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'version_name': ['version_name', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteVersion', inputs, in_db, out_db)

          
def register_as_versioned(dataset, edit_to_base='false'):
     """
     Geoprocessing tool to register enterprise, workgroup, or desktop geodatabase data as versioned.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_to_base                          optional. Default value: false. Value choices: EDITS_TO_BASE,NO_EDITS_TO_BASE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'edit_to_base': ['edit_to_base', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RegisterAsVersioned', inputs, in_db, out_db)

          
def unregister_as_versioned(dataset, keep_edit='true', compress_default='false'):
     """
     Geoprocessing tool to unregister an enterprise, workgroup, or desktop geodatabase dataset as versioned.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     keep_edit                             optional. Default value: true. Value choices: KEEP_EDIT,NO_KEEP_EDIT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compress_default                      optional. Default value: false. Value choices: COMPRESS_DEFAULT,NO_COMPRESS_DEFAULT
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'keep_edit': ['keep_edit', 'optional'], 'compress_default': ['compress_default', 'optional']}
     out_db = {}
     return _execute_tool('management', 'UnregisterAsVersioned', inputs, in_db, out_db)

          
def alter_version(workspace, version, name=None, description=None, access='PRIVATE'):
     """
     Geoprocessing tool that alters the database version's properties of name, description, and access permissions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     access                                optional. Default value: PRIVATE. Value choices: PRIVATE,PUBLIC,PROTECTED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     name                                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     description                           optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'access': ['access', 'optional'], 'version': ['in_version', 'required'], 'name': ['name', 'optional'], 'description': ['description', 'optional'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'AlterVersion', inputs, in_db, out_db)

          
def table_to_relationship_class(origtable, destination_table, relationship_type, forward_label, backward_label, message_direction, cardinality, relationship_table, attribute_fields, origprimary_key, origforeign_key, destination_primary_key, destination_foreign_key):
     """
     Geoprocessing tool that creates an attributed relationship class from the Origin, Destination, and Relationship Tables.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     relationship_table                    required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cardinality                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     attribute_fields                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     message_direction                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     forward_label                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     backward_label                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_foreign_key               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_table                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     relationship_type                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origtable                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origprimary_key                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origforeign_key                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_primary_key               required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'relationship_table': ['relationship_table', 'required'], 'cardinality': ['cardinality', 'required'], 'attribute_fields': ['attribute_fields', 'required'], 'message_direction': ['message_direction', 'required'], 'forward_label': ['forward_label', 'required'], 'backward_label': ['backward_label', 'required'], 'destination_foreign_key': ['destination_foreign_key', 'required'], 'destination_table': ['destination_table', 'required'], 'relationship_type': ['relationship_type', 'required'], 'origtable': ['origin_table', 'required'], 'origprimary_key': ['origin_primary_key', 'required'], 'origforeign_key': ['origin_foreign_key', 'required'], 'destination_primary_key': ['destination_primary_key', 'required']}
     out_db = {'relationship_class': ['out_relationship_class', 'required', None, None]}
     return _execute_tool('management', 'TableToRelationshipClass', inputs, in_db, out_db)

          
def feature_to_point(features, point_location='false'):
     """
     Geoprocessing tool that creates a representative point for each input feature.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_location                        optional. Default value: false. Value choices: INSIDE,CENTROID
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'point_location': ['point_location', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToPoint', inputs, in_db, out_db)

          
def feature_vertices_to_points(features, point_location='ALL'):
     """
     Geoprocessing tool that creates points from input feature vertices.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_location                        optional. Default value: ALL. Value choices: ALL,MID,START,END,BOTH_ENDS,DANGLE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'point_location': ['point_location', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureVerticesToPoints', inputs, in_db, out_db)

          
def feature_to_line(features, cluster_tolerance=None, attributes='true'):
     """
     Geoprocessing tool that creates line features by converting polygon boundaries to lines, or splitting line or polygon features at their intersections.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attributes                            optional. Default value: true. Value choices: ATTRIBUTES,NO_ATTRIBUTES
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'attributes': ['attributes', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToLine', inputs, in_db, out_db)

          
def feature_to_polygon(features, cluster_tolerance=None, attributes='true', label_features=None):
     """
     Geoprocessing tool that creates polygons from areas enclosed by line or polygon features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attributes                            optional. Default value: true. Value choices: ATTRIBUTES,NO_ATTRIBUTES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     label_features                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'attributes': ['attributes', 'optional'], 'features': ['in_features', 'required'], 'label_features': ['label_features', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToPolygon', inputs, in_db, out_db)

          
def polygon_to_line(features, neighbor_option='true'):
     """
     Geoprocessing tool that creates a feature class containing lines converted from polygon boundaries with or without considering neighboring polygons.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     neighbor_option                       optional. Default value: true. Value choices: IDENTIFY_NEIGHBORS,IGNORE_NEIGHBORS
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'neighbor_option': ['neighbor_option', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'PolygonToLine', inputs, in_db, out_db)

          
def define_projection(dataset, coor_system):
     """
     Geoprocessing tool to record the coordinate system information for the specific input dataset or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     coor_system                           required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'coor_system': ['coor_system', 'required']}
     out_db = {}
     return _execute_tool('management', 'DefineProjection', inputs, in_db, out_db)

          
def eliminate(features, selection='true', ex_where_clause=None, ex_features=None):
     """
     Geoprocessing tool to merge selected polygons with neighboring polygons.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ex_features                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection                             optional. Default value: true. Value choices: LENGTH,AREA
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ex_where_clause                       optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'ex_features': ['ex_features', 'optional'], 'selection': ['selection', 'optional'], 'features': ['in_features', 'required'], 'ex_where_clause': ['ex_where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'Eliminate', inputs, in_db, out_db)

          
def repair_geometry(features, delete_null='true'):
     """
     Geoprocessing tool that inspects the features for geometry problems, fixes the problems that are found, and then  prints a list of the problems that were fixed.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_null                           optional. Default value: true. Value choices: DELETE_NULL,KEEP_NULL
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'delete_null': ['delete_null', 'optional'], 'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'RepairGeometry', inputs, in_db, out_db)

          
def create_topology(dataset, out_name, cluster_tolerance=None):
     """
     Geoprocessing tool to create a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'out_name': ['out_name', 'required'], 'cluster_tolerance': ['in_cluster_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateTopology', inputs, in_db, out_db)

          
def remove_feature_class_from_topology(topology, featureclass):
     """
     Geoprocessing tool to remove a feature class from participating in a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     topology                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     featureclass                          required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'topology': ['in_topology', 'required'], 'featureclass': ['in_featureclass', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveFeatureClassFromTopology', inputs, in_db, out_db)

          
def add_rule_to_topology(topology, rule_type, featureclass, subtype=None, featureclass2=None, subtype2=None):
     """
     Geoprocessing tool to add a rule to a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rule_type                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     topology                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     featureclass                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     featureclass2                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype                               optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype2                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype': ['subtype', 'optional'], 'featureclass2': ['in_featureclass2', 'optional'], 'topology': ['in_topology', 'required'], 'rule_type': ['rule_type', 'required'], 'subtype2': ['subtype2', 'optional'], 'featureclass': ['in_featureclass', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddRuleToTopology', inputs, in_db, out_db)

          
def validate_topology(topology, visible_extent='false'):
     """
     Geoprocessing tool that validates a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     topology                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     visible_extent                        optional. Default value: false. Value choices: Visible_Extent,Full_Extent
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'topology': ['in_topology', 'required'], 'visible_extent': ['visible_extent', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ValidateTopology', inputs, in_db, out_db)

          
def set_cluster_tolerance(topology, cluster_tolerance):
     """
     Geoprocessing tool to set  the cluster tolerance value of a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     topology                              required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetClusterTolerance', inputs, in_db, out_db)

          
def make_query_table(table, key_field_option, key_field=None, field=None, where_clause=None):
     """
     Geoprocessing tool that applies an SQL query to a database and the results are represented in either a layer or a table view.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     key_field_option                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     key_field                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'key_field': ['in_key_field', 'optional'], 'key_field_option': ['in_key_field_option', 'required'], 'field': ['in_field', 'optional'], 'table': ['in_table', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'MakeQueryTable', inputs, in_db, out_db)

          
def make_xy_event_layer(table, x_field, y_field, spatial_reference=None, z_field=None):
     """
     Geoprocessing tool that creates a new point feature layer based on x- and y-coordinates defined in a source table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_field                               optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'y_field': ['in_y_field', 'required'], 'z_field': ['in_z_field', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'x_field': ['in_x_field', 'required'], 'table': ['table', 'required']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeXYEventLayer', inputs, in_db, out_db)

          
def make_raster_layer(raster, where_clause=None, envelope=None, band_index=None):
     """
     Geoprocessing tool that makes a temporary raster layer from a raster dataset that will be available to select as a variable while working in the same application's session.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     envelope                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'where_clause': ['where_clause', 'optional'], 'band_index': ['band_index', 'optional'], 'envelope': ['envelope', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {'rasterlayer': ['out_rasterlayer', 'required', None, None]}
     return _execute_tool('management', 'MakeRasterLayer', inputs, in_db, out_db)

          
def flip(raster):
     """
     Geoprocessing tool that reorients the raster by turning it over, from top to bottom, along the horizontal axis through the center of the raster.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Flip', inputs, in_db, out_db)

          
def mirror(raster):
     """
     Geoprocessing tool that reorients the raster by flipping it, from left to right, along the vertical axis through the center of the raster

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Mirror', inputs, in_db, out_db)

          
def project_raster(raster, out_coor_system, resampling_type='NEAREST', cell_size=None, geographic_transform=None, registration_point=None, coor_system=None):
     """
     Geoprocessing tool that transforms the raster dataset from one projection to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_coor_system                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geographic_transform                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       optional. Default value: NEAREST. Value choices: NEAREST,BILINEAR,CUBIC,MAJORITY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     registration_point                    optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'optional'], 'coor_system': ['in_coor_system', 'optional'], 'registration_point': ['Registration_Point', 'optional'], 'out_coor_system': ['out_coor_system', 'required'], 'geographic_transform': ['geographic_transform', 'optional'], 'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'ProjectRaster', inputs, in_db, out_db)

          
def rescale(raster, x_scale, y_scale):
     """
     Geoprocessing tool that resizes a raster by the specified x and y scale factors.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_scale                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_scale                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'y_scale': ['y_scale', 'required'], 'x_scale': ['x_scale', 'required'], 'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Rescale', inputs, in_db, out_db)

          
def shift(raster, x_value, y_value, snap_raster=None):
     """
     Geoprocessing tool that moves (slides) the raster to a new geographic location, based on x and y shift values.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_value                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_value                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     snap_raster                           optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'y_value': ['y_value', 'required'], 'snap_raster': ['in_snap_raster', 'optional'], 'x_value': ['x_value', 'required'], 'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Shift', inputs, in_db, out_db)

          
def warp(raster, source_control_points, target_control_points, transformation_type='POLYORDER1', resampling_type='NEAREST'):
     """
     Geoprocessing tool that performs a transformation on the raster based on the source and target control points using a polynomial transformation.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_control_points                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     source_control_points                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       optional. Default value: NEAREST. Value choices: NEAREST,BILINEAR,CUBIC,MAJORITY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   optional. Default value: POLYORDER1. Value choices: POLYORDER0,POLYSIMILARITY,POLYORDER1,POLYORDER2,POLYORDER3,ADJUST,SPLINE,PROJECTIVE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'target_control_points': ['target_control_points', 'required'], 'transformation_type': ['transformation_type', 'optional'], 'resampling_type': ['resampling_type', 'optional'], 'source_control_points': ['source_control_points', 'required'], 'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Warp', inputs, in_db, out_db)

          
def append(inputs, target, schema_type='TEST', field_mapping=None, subtype=None):
     """
     Geoprocessing tool that appends multiple input datasets into an existing target dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     inputs                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mapping                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype                               optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     schema_type                           optional. Default value: TEST. Value choices: TEST,NO_TEST
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_mapping': ['field_mapping', 'optional'], 'inputs': ['inputs', 'required'], 'subtype': ['subtype', 'optional'], 'schema_type': ['schema_type', 'optional'], 'target': ['target', 'required']}
     out_db = {}
     return _execute_tool('management', 'Append', inputs, in_db, out_db)

          
def delete_features(features):
     """
     Geoprocessing tool used to remove features from a feature class or layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteFeatures', inputs, in_db, out_db)

          
def add_field(table, field_name, field_type, field_precision=None, field_scale=None, field_length=None, field_alias=None, field_is_nullable='true', field_is_required='false', field_domain=None):
     """
     Geoprocessing tool to add a new field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_name                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_type                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_length                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_domain                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_scale                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_precision                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_required                     optional. Default value: false. Value choices: REQUIRED,NON_REQUIRED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_alias                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_nullable                     optional. Default value: true. Value choices: NULLABLE,NON_NULLABLE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_name': ['field_name', 'required'], 'field_domain': ['field_domain', 'optional'], 'field_scale': ['field_scale', 'optional'], 'table': ['in_table', 'required'], 'field_precision': ['field_precision', 'optional'], 'field_is_required': ['field_is_required', 'optional'], 'field_type': ['field_type', 'required'], 'field_length': ['field_length', 'optional'], 'field_alias': ['field_alias', 'optional'], 'field_is_nullable': ['field_is_nullable', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddField', inputs, in_db, out_db)

          
def assign_default_to_field(table, field_name, default_value=None, subtype_code=None, clear_value='false'):
     """
     Geoprocessing tool used to create a default value for a specified field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_name                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_value                           optional. Default value: false. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_value                         optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_name': ['field_name', 'required'], 'subtype_code': ['subtype_code', 'optional'], 'clear_value': ['clear_value', 'optional'], 'table': ['in_table', 'required'], 'default_value': ['default_value', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AssignDefaultToField', inputs, in_db, out_db)

          
def calculate_field(table, field, expression, expression_type='VB', code_block=None):
     """
     Geoprocessing tool used to perform field calculations.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     expression                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     expression_type                       optional. Default value: VB. Value choices: VB,PYTHON,PYTHON_9.3
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code_block                            optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'expression': ['expression', 'required'], 'expression_type': ['expression_type', 'optional'], 'field': ['field', 'required'], 'code_block': ['code_block', 'optional'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'CalculateField', inputs, in_db, out_db)

          
def delete_field(table, drop_field):
     """
     Geoprocessing tool used to remove fields from a dataset

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     drop_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'drop_field': ['drop_field', 'required'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteField', inputs, in_db, out_db)

          
def multipart_to_singlepart(features):
     """
     Geoprocessing tool that creates singlepart features from multipart features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'MultipartToSinglepart', inputs, in_db, out_db)

          
def integrate(features, cluster_tolerance=None):
     """
     Geoprocessing tool that updates one or more  feature classes by inserting common coordinate vertices for features that fall within the given x,y tolerance and by adding vertices where feature segments intersect.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'Integrate', inputs, in_db, out_db)

          
def merge(inputs, field_mappings=None):
     """
     Geoprocessing tool that combines multiple input datasets of the same data type into a single, new output dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     inputs                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mappings                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'inputs': ['inputs', 'required'], 'field_mappings': ['field_mappings', 'optional']}
     out_db = {'output': ['output', 'required', None, None]}
     return _execute_tool('management', 'Merge', inputs, in_db, out_db)

          
def feature_compare(base_features, test_features, sort_field, compare_type='ALL', ignore_options=None, xy_tolerance=None, m_tolerance='0', z_tolerance='0', attribute_tolerances=None, omit_field=None, continue_compare='false'):
     """
     Geoprocessing tool that compares two feature classes or layers and returns the comparison results. Feature Compare can report differences with geometry, tabular values, spatial reference, and field definitions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     base_features                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_features                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_options                        optional. Default value: None. Value choices: IGNORE_M,IGNORE_Z,IGNORE_POINTID,IGNORE_EXTENSION_PROPERTIES,IGNORE_SUBTYPES,IGNORE_RELATIONSHIPCLASSES,IGNORE_REPRESENTATIONCLASSES,IGNORE_FIELDALIAS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      optional. Default value: false. Value choices: CONTINUE_COMPARE,NO_CONTINUE_COMPARE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          optional. Default value: ALL. Value choices: ALL,GEOMETRY_ONLY,ATTRIBUTES_ONLY,SCHEMA_ONLY,SPATIAL_REFERENCE_ONLY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     m_tolerance                           optional. Default value: 0. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'base_features': ['in_base_features', 'required'], 'omit_field': ['omit_field', 'optional'], 'compare_type': ['compare_type', 'optional'], 'ignore_options': ['ignore_options', 'optional'], 'test_features': ['in_test_features', 'required'], 'm_tolerance': ['m_tolerance', 'optional'], 'z_tolerance': ['z_tolerance', 'optional'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'attribute_tolerances': ['attribute_tolerances', 'optional'], 'sort_field': ['sort_field', 'required'], 'continue_compare': ['continue_compare', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'FeatureCompare', inputs, in_db, out_db)

          
def file_compare(base_file, test_file, file_type='ASCII', continue_compare='false'):
     """
     Geoprocessing tool which compares two files and returns the comparison results. File Compare can report differences between two ASCII files or two binary files.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     test_file                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     base_file                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file_type                             optional. Default value: ASCII. Value choices: ASCII,BINARY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      optional. Default value: false. Value choices: CONTINUE_COMPARE,NO_CONTINUE_COMPARE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'test_file': ['in_test_file', 'required'], 'file_type': ['file_type', 'optional'], 'base_file': ['in_base_file', 'required'], 'continue_compare': ['continue_compare', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'FileCompare', inputs, in_db, out_db)

          
def raster_compare(base_raster, test_raster, compare_type='RASTER_DATASET', ignore_option=None, continue_compare='false', parameter_tolerances=None, attribute_tolerances=None, omit_field=None):
     """
     Geoprocessing tool that compares the properties of two raster datasets or two mosaic datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     base_raster                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_raster                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          optional. Default value: RASTER_DATASET. Value choices: RASTER_DATASET,GDB_RASTER_DATASET,GDB_RASTER_CATALOG,MOSAIC_DATASET
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_option                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     parameter_tolerances                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      optional. Default value: false. Value choices: CONTINUE_COMPARE,NO_CONTINUE_COMPARE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'attribute_tolerances': ['attribute_tolerances', 'optional'], 'omit_field': ['omit_field', 'optional'], 'compare_type': ['compare_type', 'optional'], 'ignore_option': ['ignore_option', 'optional'], 'base_raster': ['in_base_raster', 'required'], 'test_raster': ['in_test_raster', 'required'], 'parameter_tolerances': ['parameter_tolerances', 'optional'], 'continue_compare': ['continue_compare', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'RasterCompare', inputs, in_db, out_db)

          
def table_compare(base_table, test_table, sort_field, compare_type='ALL', ignore_options=None, attribute_tolerances=None, omit_field=None, continue_compare='false'):
     """
     Geoprocessing tool compares two tables or table views and returns the comparison results.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     test_table                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     base_table                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          optional. Default value: ALL. Value choices: ALL,ATTRIBUTES_ONLY,SCHEMA_ONLY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_options                        optional. Default value: None. Value choices: IGNORE_EXTENSION_PROPERTIES,IGNORE_SUBTYPES,IGNORE_RELATIONSHIPCLASSES,IGNORE_FIELDALIAS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      optional. Default value: false. Value choices: CONTINUE_COMPARE,NO_CONTINUE_COMPARE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'attribute_tolerances': ['attribute_tolerances', 'optional'], 'omit_field': ['omit_field', 'optional'], 'test_table': ['in_test_table', 'required'], 'compare_type': ['compare_type', 'optional'], 'ignore_options': ['ignore_options', 'optional'], 'base_table': ['in_base_table', 'required'], 'sort_field': ['sort_field', 'required'], 'continue_compare': ['continue_compare', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'TableCompare', inputs, in_db, out_db)

          
def create_file_gdb(out_folder_path, out_name, out_version='CURRENT'):
     """
     Geoprocessing tool that creates a file geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder_path                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_version                           optional. Default value: CURRENT. Value choices: CURRENT,10.0,9.3,9.2
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_version': ['out_version', 'optional'], 'out_folder_path': ['out_folder_path', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateFileGDB', inputs, in_db, out_db)

          
def compress(workspace):
     """
     Geoprocessing tool to compress an enterprise geodatabase

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'Compress', inputs, in_db, out_db)

          
def add_subtype(table, subtype_code, subtype_description):
     """
     Geoprocessing tool that adds a new subtype to the subtypes in the input table

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_description                   required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     subtype_code                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype_description': ['subtype_description', 'required'], 'subtype_code': ['subtype_code', 'required'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddSubtype', inputs, in_db, out_db)

          
def remove_subtype(table, subtype_code):
     """
     Geoprocessing tool that removes a subtype from the input table using its code.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype_code': ['subtype_code', 'required'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveSubtype', inputs, in_db, out_db)

          
def set_default_subtype(table, subtype_code):
     """
     Geoprocessing tool that sets the default subtype value for the input table's subtype.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype_code': ['subtype_code', 'required'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetDefaultSubtype', inputs, in_db, out_db)

          
def set_subtype_field(table, field=None, clear_value='false'):
     """
     Geoprocessing tool that defines the field in the input table or feature class that stores the subtype codes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_value                           optional. Default value: false. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'clear_value': ['clear_value', 'optional'], 'field': ['field', 'optional'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetSubtypeField', inputs, in_db, out_db)

          
def add_colormap(raster, template_raster=None, input_clr_file=None):
     """
     Geoprocessing tool that adds a color map to a raster dataset, if it does not already exist or replaces a color map with the one specified.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_clr_file                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_raster                       optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_clr_file': ['input_CLR_file', 'optional'], 'template_raster': ['in_template_raster', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddColormap', inputs, in_db, out_db)

          
def build_raster_attribute_table(raster, overwrite='false'):
     """
     Geoprocessing tool that adds a raster attribute table to a raster dataset or updates an existing one.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overwrite                             optional. Default value: false. Value choices: Overwrite,NONE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'overwrite': ['overwrite', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'BuildRasterAttributeTable', inputs, in_db, out_db)

          
def delete_colormap(raster):
     """
     Geoprocessing tool that removes the color map associated with a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteColormap', inputs, in_db, out_db)

          
def delete_raster_attribute_table(raster):
     """
     Geoprocessing tool that removes the raster attribute table associated with a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteRasterAttributeTable', inputs, in_db, out_db)

          
def build_pyramids(raster_dataset, pyramid_level=None, skip_first='false', resample_technique='NEAREST', compression_type='DEFAULT', compression_quality='75', skip_existing='false'):
     """
     Geoprocessing tool that builds or deletes raster pyramids for a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_level                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resample_technique                    optional. Default value: NEAREST. Value choices: NEAREST,BILINEAR,CUBIC
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         optional. Default value: false. Value choices: SKIP_EXISTING,OVERWRITE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   optional. Default value: 75. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_first                            optional. Default value: false. Value choices: SKIP_FIRST,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_type                      optional. Default value: DEFAULT. Value choices: DEFAULT,JPEG,LZ77,NONE,JPEG_YCbCr
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'pyramid_level': ['pyramid_level', 'optional'], 'resample_technique': ['resample_technique', 'optional'], 'skip_existing': ['skip_existing', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'compression_quality': ['compression_quality', 'optional'], 'skip_first': ['SKIP_FIRST', 'optional'], 'compression_type': ['compression_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildPyramids', inputs, in_db, out_db)

          
def calculate_statistics(raster_dataset, x_skip_factor=None, y_skip_factor=None, ignore_values=None, skip_existing='false', area_of_interest='in_memory\{BC80ECFE-15B0-41C3-8FA1-A0A41602275C}'):
     """
     Geoprocessing tool that calculates statistics for a raster dataset or mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     x_skip_factor                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_values                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         optional. Default value: false. Value choices: SKIP_EXISTING,OVERWRITE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      optional. Default value: in_memory\{BC80ECFE-15B0-41C3-8FA1-A0A41602275C}. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_skip_factor                         optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'x_skip_factor': ['x_skip_factor', 'optional'], 'skip_existing': ['skip_existing', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'ignore_values': ['ignore_values', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'y_skip_factor': ['y_skip_factor', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateStatistics', inputs, in_db, out_db)

          
def get_raster_properties(raster, property_type='MINIMUM', band_index=None):
     """
     Geoprocessing tool that returns the properties of a raster dataset, mosaic dataset, or a raster product.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     property_type                         optional. Default value: MINIMUM. Value choices: MAXIMUM,MINIMUM,MEAN,STD,UNIQUEVALUECOUNT,TOP,LEFT,RIGHT,BOTTOM,CELLSIZEX,CELLSIZEY,VALUETYPE,COLUMNCOUNT,ROWCOUNT,BANDCOUNT,ALLNODATA,ANYNODATA,SENSORNAME,PRODUCTNAME,ACQUISITIONDATE,SOURCETYPE,CLOUDCOVER,SUNAZIMUTH,SUNELEVATION,SENSORAZIMUTH,SENSORELEVATION,OFFNADIR,WAVELENGTH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'property_type': ['property_type', 'optional'], 'band_index': ['band_index', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'GetRasterProperties', inputs, in_db, out_db)

          
def copy_raster(raster, config_keyword=None, background_value=None, nodata_value=None, onebit_to_eightbit='false', colormap_to_rgb='false', pixel_type=None, scale_pixel_value='false', rgb_to_colormap='false', format=None, transform='false'):
     """
     Geoprocessing tool that makes a copy of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transform                             optional. Default value: false. Value choices: Transform,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rgb_to_colormap                       optional. Default value: false. Value choices: RGBToColormap,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            optional. Default value: None. Value choices: 1_BIT,2_BIT,4_BIT,8_BIT_UNSIGNED,8_BIT_SIGNED,16_BIT_UNSIGNED,16_BIT_SIGNED,32_BIT_UNSIGNED,32_BIT_SIGNED,32_BIT_FLOAT,64_BIT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                optional. Default value: None. Value choices: TIFF,IMAGINE Image,BMP,GIF,PNG,JPEG,JPEG2000,Esri Grid,Esri BIL,Esri BSQ,Esri BIP,ENVI,CRF,MRF
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap_to_rgb                       optional. Default value: false. Value choices: ColormapToRGB,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scale_pixel_value                     optional. Default value: false. Value choices: ScalePixelValue,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    optional. Default value: false. Value choices: OneBitTo8Bit,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'transform': ['transform', 'optional'], 'rgb_to_colormap': ['RGB_to_Colormap', 'optional'], 'scale_pixel_value': ['scale_pixel_value', 'optional'], 'pixel_type': ['pixel_type', 'optional'], 'format': ['format', 'optional'], 'background_value': ['background_value', 'optional'], 'config_keyword': ['config_keyword', 'optional'], 'raster': ['in_raster', 'required'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'nodata_value': ['nodata_value', 'optional']}
     out_db = {'rasterdataset': ['out_rasterdataset', 'required', None, None]}
     return _execute_tool('management', 'CopyRaster', inputs, in_db, out_db)

          
def create_random_raster(out_path, out_name, distribution='UNIFORM 0.0 1.0', raster_extent=None, cellsize=None):
     """
     Geoprocessing tool that creates a random raster dataset based on a user-specified distribution and extent.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_extent                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          optional. Default value: UNIFORM 0.0 1.0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'raster_extent': ['raster_extent', 'optional'], 'distribution': ['distribution', 'optional'], 'cellsize': ['cellsize', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomRaster', inputs, in_db, out_db)

          
def create_raster_dataset(out_path, out_name, pixel_type, number_of_bands, cellsize=None, raster_spatial_reference=None, config_keyword=None, pyramids='PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP', tile_size='128 128', compression='LZ77', pyramid_origin=None):
     """
     Geoprocessing tool that creates a raster dataset as a file or in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_bands                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     pixel_type                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_spatial_reference              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramids                              optional. Default value: PYRAMIDS -1 NEAREST DEFAULT 75 NO_SKIP. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             optional. Default value: 128 128. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression                           optional. Default value: LZ77. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_origin                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster_spatial_reference': ['raster_spatial_reference', 'optional'], 'pyramids': ['pyramids', 'optional'], 'tile_size': ['tile_size', 'optional'], 'cellsize': ['cellsize', 'optional'], 'out_name': ['out_name', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'number_of_bands': ['number_of_bands', 'required'], 'compression': ['compression', 'optional'], 'pyramid_origin': ['pyramid_origin', 'optional'], 'out_path': ['out_path', 'required'], 'pixel_type': ['pixel_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateRasterDataset', inputs, in_db, out_db)

          
def mosaic(inputs, target, mosaic_type='LAST', colormap='FIRST', background_value=None, nodata_value=None, onebit_to_eightbit='false', mosaicking_tolerance='0', matching_method=None):
     """
     Geoprocessing tool that mosaics multiple input rasters into an existing raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     inputs                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     matching_method                       optional. Default value: NONE. Value choices: NONE,STATISTIC_MATCHING,HISTOGRAM_MATCHING,LINEARCORRELATION_MATCHING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap                              optional. Default value: FIRST. Value choices: REJECT,FIRST,LAST,MATCH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_type                           optional. Default value: LAST. Value choices: FIRST,LAST,BLEND,MEAN,MINIMUM,MAXIMUM,SUM
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicking_tolerance                  optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    optional. Default value: false. Value choices: OneBitTo8Bit,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'target': ['target', 'required'], 'matching_method': ['MatchingMethod', 'optional'], 'inputs': ['inputs', 'required'], 'colormap': ['colormap', 'optional'], 'background_value': ['background_value', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'mosaic_type': ['mosaic_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Mosaic', inputs, in_db, out_db)

          
def workspace_to_raster_dataset(workspace, raster_dataset, include_subdirectories='false', mosaic_type='LAST', colormap='FIRST', background_value=None, nodata_value=None, onebit_to_eightbit='false', mosaicking_tolerance='0', matching_method=None, colormap_to_rgb='false'):
     """
     Geoprocessing tool that mosaics all the raster datasets stored within the specified workspace into one raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     matching_method                       optional. Default value: NONE. Value choices: NONE,STATISTIC_MATCHING,HISTOGRAM_MATCHING,LINEARCORRELATION_MATCHING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    optional. Default value: false. Value choices: OneBitTo8Bit,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap                              optional. Default value: FIRST. Value choices: REJECT,FIRST,LAST,MATCH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_type                           optional. Default value: LAST. Value choices: FIRST,LAST,BLEND,MEAN,MINIMUM,MAXIMUM,SUM
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap_to_rgb                       optional. Default value: false. Value choices: ColormapToRGB,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicking_tolerance                  optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_subdirectories                optional. Default value: false. Value choices: INCLUDE_SUBDIRECTORIES,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'matching_method': ['MatchingMethod', 'optional'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'workspace': ['in_workspace', 'required'], 'raster_dataset': ['in_raster_dataset', 'required'], 'colormap': ['colormap', 'optional'], 'background_value': ['background_value', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional'], 'include_subdirectories': ['include_subdirectories', 'optional'], 'mosaic_type': ['mosaic_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'WorkspaceToRasterDataset', inputs, in_db, out_db)

          
def clip(raster, rectangle, template_dataset=None, nodata_value=None, clipping_geometry='false', maintaclipping_extent='false'):
     """
     Geoprocessing tool that creates a spatial subset of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rectangle                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintaclipping_extent                 optional. Default value: false. Value choices: MAINTAIN_EXTENT,NO_MAINTAIN_EXTENT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clipping_geometry                     optional. Default value: false. Value choices: ClippingGeometry,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'maintaclipping_extent': ['maintain_clipping_extent', 'optional'], 'rectangle': ['rectangle', 'required'], 'template_dataset': ['in_template_dataset', 'optional'], 'raster': ['in_raster', 'required'], 'clipping_geometry': ['clipping_geometry', 'optional'], 'nodata_value': ['nodata_value', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Clip', inputs, in_db, out_db)

          
def composite_bands(rasters):
     """
     Geoprocessing tool that creates a single raster dataset from multiple bands and can also create a subset of the bands.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rasters                               required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'rasters': ['in_rasters', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'CompositeBands', inputs, in_db, out_db)

          
def resample(raster, cell_size=None, resampling_type='NEAREST'):
     """
     Geoprocessing tool that alters the raster dataset by changing the cell size and resampling method.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       optional. Default value: NEAREST. Value choices: NEAREST,BILINEAR,CUBIC,MAJORITY
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'optional'], 'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Resample', inputs, in_db, out_db)

          
def export_raster_world_file(raster_dataset):
     """
     Geoprocessing tool that creates a world file based on the geographic information of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster_dataset': ['in_raster_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'ExportRasterWorldFile', inputs, in_db, out_db)

          
def get_cell_value(raster, location_point, band_index=None):
     """
     Geoprocessing tool that retrieves the pixel value at a specific x,y coordinate.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_point                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'location_point': ['location_point', 'required'], 'band_index': ['band_index', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'GetCellValue', inputs, in_db, out_db)

          
def make_wcs_layer(wcs_coverage, template=None, band_index=None):
     """
     Geoprocessing tool that creates a temporary raster layer from a WCS service.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     wcs_coverage                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'band_index': ['band_index', 'optional'], 'wcs_coverage': ['in_wcs_coverage', 'required'], 'template': ['template', 'optional']}
     out_db = {'wcs_layer': ['out_wcs_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeWCSLayer', inputs, in_db, out_db)

          
def apply_symbology_from_layer(layer, symbology_layer):
     """
     Geoprocessing tool that applies the symbology from a specified layer to the Input Layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     symbology_layer                       required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'layer': ['in_layer', 'required'], 'symbology_layer': ['in_symbology_layer', 'required']}
     out_db = {}
     return _execute_tool('management', 'ApplySymbologyFromLayer', inputs, in_db, out_db)

          
def mosaic_to_new_raster(input_rasters, output_location, raster_dataset_name_with_extension, number_of_bands, coordinate_system_for_the_raster=None, pixel_type='8_BIT_UNSIGNED', cellsize=None, mosaic_method='LAST', mosaic_colormap_mode='FIRST'):
     """
     Geoprocessing tool that mosaics multiple raster datasets into a new raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_location                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_bands                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster_dataset_name_with_extension    required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_rasters                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_colormap_mode                  optional. Default value: FIRST. Value choices: REJECT,FIRST,LAST,MATCH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system_for_the_raster      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_method                         optional. Default value: LAST. Value choices: FIRST,LAST,BLEND,MEAN,MINIMUM,MAXIMUM,SUM
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            optional. Default value: 8_BIT_UNSIGNED. Value choices: 1_BIT,2_BIT,4_BIT,8_BIT_UNSIGNED,8_BIT_SIGNED,16_BIT_UNSIGNED,16_BIT_SIGNED,32_BIT_UNSIGNED,32_BIT_SIGNED,32_BIT_FLOAT,64_BIT
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'output_location': ['output_location', 'required'], 'coordinate_system_for_the_raster': ['coordinate_system_for_the_raster', 'optional'], 'mosaic_method': ['mosaic_method', 'optional'], 'cellsize': ['cellsize', 'optional'], 'input_rasters': ['input_rasters', 'required'], 'number_of_bands': ['number_of_bands', 'required'], 'raster_dataset_name_with_extension': ['raster_dataset_name_with_extension', 'required'], 'mosaic_colormap_mode': ['mosaic_colormap_mode', 'optional'], 'pixel_type': ['pixel_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MosaicToNewRaster', inputs, in_db, out_db)

          
def dice(features, vertex_limit):
     """
     Geoprocessing tool that subdivides a feature into smaller features based on a specified vertex limit.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     vertex_limit                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'vertex_limit': ['vertex_limit', 'required'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'Dice', inputs, in_db, out_db)

          
def split_line_at_point(features, point_features, search_radius=None):
     """
     Geoprocessing tool to split line features based on intersection or proximity to point features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_features                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'point_features': ['point_features', 'required'], 'features': ['in_features', 'required'], 'search_radius': ['search_radius', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'SplitLineatPoint', inputs, in_db, out_db)

          
def unsplit_line(features, dissolve_field=None, statistics_fields=None):
     """
     Geoprocessing tool that aggregates line features based on specified attributes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics_fields                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'statistics_fields': ['statistics_fields', 'optional'], 'dissolve_field': ['dissolve_field', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'UnsplitLine', inputs, in_db, out_db)

          
def split_raster(raster, out_folder, out_base_name, split_method, format, resampling_type='NEAREST', num_rasters='1 1', tile_size='2048 2048', overlap='0', units='PIXELS', cell_size=None, origin=None, split_polygon_feature_class=None, clip_type=None, template_extent=None, nodata_value=None):
     """
     Geoprocessing tool that creates a tiled output from an input raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     format                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_base_name                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     split_method                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     origin                                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_polygon_feature_class           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     num_rasters                           optional. Default value: 1 1. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             optional. Default value: 2048 2048. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       optional. Default value: NEAREST. Value choices: NEAREST,BILINEAR,CUBIC
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_type                             optional. Default value: NONE. Value choices: NONE,EXTENT,FEATURE_CLASS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overlap                               optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_extent                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     units                                 optional. Default value: PIXELS. Value choices: PIXELS,METERS,FEET,DEGREES,KILOMETERS,MILES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'origin': ['origin', 'optional'], 'split_polygon_feature_class': ['split_polygon_feature_class', 'optional'], 'template_extent': ['template_extent', 'optional'], 'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required'], 'out_folder': ['out_folder', 'required'], 'cell_size': ['cell_size', 'optional'], 'num_rasters': ['num_rasters', 'optional'], 'tile_size': ['tile_size', 'optional'], 'split_method': ['split_method', 'required'], 'clip_type': ['clip_type', 'optional'], 'format': ['format', 'required'], 'overlap': ['overlap', 'optional'], 'out_base_name': ['out_base_name', 'required'], 'units': ['units', 'optional'], 'nodata_value': ['nodata_value', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SplitRaster', inputs, in_db, out_db)

          
def eliminate_polygon_part(features, condition='AREA', part_area='0 Unknown', part_area_percent='0', part_option='true'):
     """
     Geoprocessing tool that creates a new output feature class containing the features from input polygons with some parts or holes of a specified size deleted.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_option                           optional. Default value: true. Value choices: CONTAINED_ONLY,ANY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_area                             optional. Default value: 0 Unknown. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_area_percent                     optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     condition                             optional. Default value: AREA. Value choices: AREA,PERCENT,AREA_AND_PERCENT,AREA_OR_PERCENT
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'part_option': ['part_option', 'optional'], 'part_area': ['part_area', 'optional'], 'part_area_percent': ['part_area_percent', 'optional'], 'features': ['in_features', 'required'], 'condition': ['condition', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'EliminatePolygonPart', inputs, in_db, out_db)

          
def points_to_line(input_features, line_field=None, sort_field=None, close_line='false'):
     """
     Geoprocessing tool used to create line features from points.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_features                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     close_line                            optional. Default value: false. Value choices: CLOSE,NO_CLOSE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_field                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_field                            optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_features': ['Input_Features', 'required'], 'sort_field': ['Sort_Field', 'optional'], 'line_field': ['Line_Field', 'optional'], 'close_line': ['Close_Line', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'PointsToLine', inputs, in_db, out_db)

          
def change_version(features, version_type, version_name=None, date=None):
     """
     Geoprocessing tool used to change the enterprise geodatabase version you are connected to. Only works when working with feature layers or table views.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_type                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_name                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     date                                  optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'version_type': ['version_type', 'required'], 'version_name': ['version_name', 'optional'], 'date': ['date', 'optional'], 'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'ChangeVersion', inputs, in_db, out_db)

          
def register_with_geodatabase(dataset, object_id_field=None, shape_field=None, geometry_type=None, spatial_reference=None, extent=None):
     """
     Geoprocessing tool that registers feature classes, tables, views, and raster layers that were created outside of the geodatabase with the geodatabase in order for them to participate in geodatabase functionality.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         optional. Default value: None. Value choices: POINT,MULTIPOINT,POLYGON,POLYLINE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     object_id_field                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shape_field                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'geometry_type': ['in_geometry_type', 'optional'], 'spatial_reference': ['in_spatial_reference', 'optional'], 'object_id_field': ['in_object_id_field', 'optional'], 'extent': ['in_extent', 'optional'], 'shape_field': ['in_shape_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RegisterwithGeodatabase', inputs, in_db, out_db)

          
def delete_identical(dataset, fields, xy_tolerance=None, z_tolerance='0'):
     """
     Geoprocessing tool to delete records in a feature class or table which have identical values in a list of fields.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'z_tolerance': ['z_tolerance', 'optional'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'fields': ['fields', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteIdentical', inputs, in_db, out_db)

          
def find_identical(dataset, fields, xy_tolerance=None, z_tolerance='0', output_record_option='false'):
     """
     Geoprocessing tool that reports any records in a feature class or table that have identical values in a list of fields, and generates a table listing these identical records.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_record_option                  optional. Default value: false. Value choices: ONLY_DUPLICATES,ALL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'output_record_option': ['output_record_option', 'optional'], 'z_tolerance': ['z_tolerance', 'optional'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'fields': ['fields', 'required']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'FindIdentical', inputs, in_db, out_db)

          
def change_privileges(dataset, user, view=None, edit=None):
     """
     Geoprocessing tool to change  privileges on a dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     user                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit                                  optional. Default value: None. Value choices: AS_IS,GRANT,REVOKE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view                                  optional. Default value: None. Value choices: AS_IS,GRANT,REVOKE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'user': ['user', 'required'], 'edit': ['Edit', 'optional'], 'view': ['View', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ChangePrivileges', inputs, in_db, out_db)

          
def create_spatial_reference(spatial_reference=None, spatial_reference_template=None, xy_domain=None, z_domain=None, m_domain=None, template=None, expand_ratio='0'):
     """
     Geoprocessing tool to create a spatial reference for use in ModelBuilder and scripting.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     m_domain                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_domain                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     expand_ratio                          optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference_template            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_domain                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'m_domain': ['m_domain', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'z_domain': ['z_domain', 'optional'], 'expand_ratio': ['expand_ratio', 'optional'], 'spatial_reference_template': ['spatial_reference_template', 'optional'], 'xy_domain': ['xy_domain', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateSpatialReference', inputs, in_db, out_db)

          
def raster_to_dted(raster, out_folder, dted_level, resampling_type='BILINEAR'):
     """
     Geoprocessing tool that splits a raster dataset into files based on the DTED tiling structure.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dted_level                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       optional. Default value: BILINEAR. Value choices: BILINEAR,NEAREST,CUBIC
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_folder': ['out_folder', 'required'], 'dted_level': ['dted_level', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'RasterToDTED', inputs, in_db, out_db)

          
def bearing_distance_to_line(table, x_field, y_field, distance_field, distance_units, bearing_field, bearing_units, line_type='0', id_field=None, spatial_reference='{B286C06B-0879-11D2-AACA-00C04FA33C20};IsHighPrecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in an x-coordinate field, y-coordinate field, bearing field, and distance field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance_units                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     bearing_field                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     bearing_units                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     distance_field                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_type                             optional. Default value: 0. Value choices: GEODESIC,GREAT_CIRCLE,RHUMB_LINE,NORMAL_SECTION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: {B286C06B-0879-11D2-AACA-00C04FA33C20};IsHighPrecision. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'distance_units': ['distance_units', 'required'], 'line_type': ['line_type', 'optional'], 'bearing_field': ['bearing_field', 'required'], 'x_field': ['x_field', 'required'], 'table': ['in_table', 'required'], 'id_field': ['id_field', 'optional'], 'bearing_units': ['bearing_units', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'y_field': ['y_field', 'required'], 'distance_field': ['distance_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'BearingDistanceToLine', inputs, in_db, out_db)

          
def table_to_ellipse(table, x_field, y_field, major_field, minor_field, distance_units, azimuth_field=None, azimuth_units='9102', id_field=None, spatial_reference='{B286C06B-0879-11D2-AACA-00C04FA33C20};IsHighPrecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic ellipse features constructed based on the values in an x-coordinate field, y-coordinate field, major-axis field, minor-axis field, and azimuth field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance_units                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     major_field                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     minor_field                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: {B286C06B-0879-11D2-AACA-00C04FA33C20};IsHighPrecision. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     azimuth_field                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     azimuth_units                         optional. Default value: 9102. Value choices: DEGREES,MILS,RADS,GRADS
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'distance_units': ['distance_units', 'required'], 'azimuth_units': ['azimuth_units', 'optional'], 'azimuth_field': ['azimuth_field', 'optional'], 'major_field': ['major_field', 'required'], 'table': ['in_table', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'id_field': ['id_field', 'optional'], 'minor_field': ['minor_field', 'required'], 'y_field': ['y_field', 'required'], 'x_field': ['x_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'TableToEllipse', inputs, in_db, out_db)

          
def xy_to_line(table, startx_field, starty_field, endx_field, endy_field, line_type='0', id_field=None, spatial_reference='{B286C06B-0879-11D2-AACA-00C04FA33C20};IsHighPrecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in a start x-coordinate field, start y-coordinate field, end x-coordinate field, and end y-coordinate field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     starty_field                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     endy_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     endx_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     startx_field                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_type                             optional. Default value: 0. Value choices: GEODESIC,GREAT_CIRCLE,RHUMB_LINE,NORMAL_SECTION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: {B286C06B-0879-11D2-AACA-00C04FA33C20};IsHighPrecision. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'line_type': ['line_type', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'endx_field': ['endx_field', 'required'], 'table': ['in_table', 'required'], 'startx_field': ['startx_field', 'required'], 'starty_field': ['starty_field', 'required'], 'id_field': ['id_field', 'optional'], 'endy_field': ['endy_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'XYToLine', inputs, in_db, out_db)

          
def convert_coordinate_notation(table, x_field, y_field, input_coordinate_format, output_coordinate_format, exclude_invalid_records, id_field=None, spatial_reference=None, coor_system=None):
     """
     Geoprocessing tool that converts coordinate notations from one format to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     x_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     exclude_invalid_records               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_coordinate_format              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_coordinate_format               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'spatial_reference': ['spatial_reference', 'optional'], 'coor_system': ['in_coor_system', 'optional'], 'x_field': ['x_field', 'required'], 'table': ['in_table', 'required'], 'exclude_invalid_records': ['exclude_invalid_records', 'required'], 'id_field': ['id_field', 'optional'], 'output_coordinate_format': ['output_coordinate_format', 'required'], 'y_field': ['y_field', 'required'], 'input_coordinate_format': ['input_coordinate_format', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'ConvertCoordinateNotation', inputs, in_db, out_db)

          
def minimum_bounding_geometry(features, geometry_type='RECTANGLE_BY_AREA', group_option=None, group_field=None, mbg_fields_option='false'):
     """
     Geoprocessing tool that creates polygons which represent a specified minimum bounding geometry enclosing each input feature or a group of input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     group_field                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         optional. Default value: RECTANGLE_BY_AREA. Value choices: RECTANGLE_BY_AREA,RECTANGLE_BY_WIDTH,CONVEX_HULL,CIRCLE,ENVELOPE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     group_option                          optional. Default value: NONE. Value choices: NONE,ALL,LIST
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mbg_fields_option                     optional. Default value: false. Value choices: MBG_FIELDS,NO_MBG_FIELDS
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'group_field': ['group_field', 'optional'], 'geometry_type': ['geometry_type', 'optional'], 'group_option': ['group_option', 'optional'], 'features': ['in_features', 'required'], 'mbg_fields_option': ['mbg_fields_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'MinimumBoundingGeometry', inputs, in_db, out_db)

          
def add_rasters_to_mosaic_dataset(mosaic_dataset, raster_type, input_path, update_cellsize_ranges='true', update_boundary='true', update_overviews='false', maximum_pyramid_levels=None, maximum_cell_size='0', minimum_dimension='1500', spatial_reference=None, filter=None, sub_folder='true', duplicate_items_action='ALLOW_DUPLICATES', build_pyramids='false', calculate_statistics='false', build_thumbnails='false', operation_description=None, force_spatial_reference='false', estimate_statistics='false', aux_inputs=None):
     """
     Geoprocessing tool that ingests raster datasets from a file, folder, raster catalog, or image service to a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_type                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_path                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_overviews                      optional. Default value: false. Value choices: UPDATE_OVERVIEWS,NO_OVERVIEWS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sub_folder                            optional. Default value: true. Value choices: SUBFOLDERS,NO_SUBFOLDERS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     force_spatial_reference               optional. Default value: false. Value choices: FORCE_SPATIAL_REFERENCE,NO_FORCE_SPATIAL_REFERENCE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     calculate_statistics                  optional. Default value: false. Value choices: CALCULATE_STATISTICS,NO_STATISTICS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_dimension                     optional. Default value: 1500. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     filter                                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                optional. Default value: true. Value choices: UPDATE_CELL_SIZES,NO_CELL_SIZES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate_statistics                   optional. Default value: false. Value choices: ESTIMATE_STATISTICS,NO_STATISTICS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_pyramids                        optional. Default value: false. Value choices: BUILD_PYRAMIDS,NO_PYRAMIDS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_thumbnails                      optional. Default value: false. Value choices: BUILD_THUMBNAILS,NO_THUMBNAILS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     aux_inputs                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_pyramid_levels                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     duplicate_items_action                optional. Default value: ALLOW_DUPLICATES. Value choices: ALLOW_DUPLICATES,EXCLUDE_DUPLICATES,OVERWRITE_DUPLICATES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     operation_description                 optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_cell_size                     optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       optional. Default value: true. Value choices: UPDATE_BOUNDARY,NO_BOUNDARY
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_overviews': ['update_overviews', 'optional'], 'sub_folder': ['sub_folder', 'optional'], 'input_path': ['input_path', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'force_spatial_reference': ['force_spatial_reference', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional'], 'raster_type': ['raster_type', 'required'], 'minimum_dimension': ['minimum_dimension', 'optional'], 'filter': ['filter', 'optional'], 'maximum_cell_size': ['maximum_cell_size', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'aux_inputs': ['aux_inputs', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_pyramid_levels': ['maximum_pyramid_levels', 'optional'], 'duplicate_items_action': ['duplicate_items_action', 'optional'], 'operation_description': ['operation_description', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddRastersToMosaicDataset', inputs, in_db, out_db)

          
def build_boundary(mosaic_dataset, where_clause=None, append_to_existing='false', simplification_method=None):
     """
     Geoprocessing tool that updates the extent of the boundary of  a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     append_to_existing                    optional. Default value: false. Value choices: APPEND,OVERWRITE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     simplification_method                 optional. Default value: NONE. Value choices: NONE,CONVEX_HULL,ENVELOPE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'append_to_existing': ['append_to_existing', 'optional'], 'simplification_method': ['simplification_method', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildBoundary', inputs, in_db, out_db)

          
def build_footprints(mosaic_dataset, where_clause=None, reset_footprint='RADIOMETRY', mdata_value='1', max_data_value='254', approx_num_vertices='80', shrink_distance='0', maintaedges='false', skip_derived_images='true', update_boundary='true', request_size='2000', mregion_size='100', simplification_method=None, edge_tolerance=None, max_sliver_size='20', mthinness_ratio='0.05'):
     """
     Geoprocessing tool that computes the footprints for the rasters in a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_derived_images                   optional. Default value: true. Value choices: SKIP_DERIVED_IMAGES,NO_SKIP_DERIVED_IMAGES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     approx_num_vertices                   optional. Default value: 80. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_sliver_size                       optional. Default value: 20. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edge_tolerance                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mdata_value                           optional. Default value: 1. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     simplification_method                 optional. Default value: NONE. Value choices: NONE,CONVEX_HULL,ENVELOPE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_data_value                        optional. Default value: 254. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mthinness_ratio                       optional. Default value: 0.05. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mregion_size                          optional. Default value: 100. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintaedges                           optional. Default value: false. Value choices: MAINTAIN_EDGES,NO_MAINTAIN_EDGES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     reset_footprint                       optional. Default value: RADIOMETRY. Value choices: NONE,GEOMETRY,RADIOMETRY,COPY_TO_SIBLING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          optional. Default value: 2000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shrink_distance                       optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       optional. Default value: true. Value choices: UPDATE_BOUNDARY,NO_BOUNDARY
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_derived_images': ['skip_derived_images', 'optional'], 'approx_num_vertices': ['approx_num_vertices', 'optional'], 'max_sliver_size': ['max_sliver_size', 'optional'], 'edge_tolerance': ['edge_tolerance', 'optional'], 'mdata_value': ['min_data_value', 'optional'], 'simplification_method': ['simplification_method', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'max_data_value': ['max_data_value', 'optional'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'shrink_distance': ['shrink_distance', 'optional'], 'maintaedges': ['maintain_edges', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'reset_footprint': ['reset_footprint', 'optional'], 'where_clause': ['where_clause', 'optional'], 'request_size': ['request_size', 'optional'], 'update_boundary': ['update_boundary', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildFootprints', inputs, in_db, out_db)

          
def build_overviews(mosaic_dataset, where_clause=None, define_missing_tiles='true', generate_overviews='true', generate_missing_images='true', regenerate_stale_images='true'):
     """
     Geoprocessing tool that defines and generates overviews for a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_missing_images               optional. Default value: true. Value choices: GENERATE_MISSING_IMAGES,IGNORE_MISSING_IMAGES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     define_missing_tiles                  optional. Default value: true. Value choices: DEFINE_MISSING_TILES,NO_DEFINE_MISSING_TILES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     regenerate_stale_images               optional. Default value: true. Value choices: REGENERATE_STALE_IMAGES,IGNORE_STALE_IMAGES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_overviews                    optional. Default value: true. Value choices: GENERATE_OVERVIEWS,NO_GENERATE_OVERVIEWS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'define_missing_tiles': ['define_missing_tiles', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'generate_overviews': ['generate_overviews', 'optional'], 'regenerate_stale_images': ['regenerate_stale_images', 'optional'], 'generate_missing_images': ['generate_missing_images', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildOverviews', inputs, in_db, out_db)

          
def build_seamlines(mosaic_dataset, cell_size=None, sort_method='NORTH_WEST', sort_order='true', order_by_attribute=None, order_by_base_value=None, view_point=None, computation_method='RADIOMETRY', blend_width=None, blend_type='BOTH', request_size='1000', request_size_type='PIXELS', blend_width_units='PIXELS', area_of_interest='in_memory\{18B3C9C4-BE24-4D7F-B8A9-FAE3BD65574A}', where_clause=None, update_existing='false', mregion_size='100', mthinness_ratio='0.05', max_sliver_size='20'):
     """
     Geoprocessing tool that generates seamlines for your mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_sliver_size                       optional. Default value: 20. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_by_base_value                   optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_by_attribute                    optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_order                            optional. Default value: true. Value choices: ASCENDING,DESCENDING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      optional. Default value: in_memory\{18B3C9C4-BE24-4D7F-B8A9-FAE3BD65574A}. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mthinness_ratio                       optional. Default value: 0.05. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size_type                     optional. Default value: PIXELS. Value choices: PIXELS,PIXELSIZE_FACTOR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_existing                       optional. Default value: false. Value choices: UPDATE_EXISTING,IGNORE_EXISTING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mregion_size                          optional. Default value: 100. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_method                           optional. Default value: NORTH_WEST. Value choices: NORTH_WEST,CLOSEST_TO_VIEWPOINT,BY_ATTRIBUTE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width_units                     optional. Default value: PIXELS. Value choices: PIXELS,GROUND_UNITS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     computation_method                    optional. Default value: RADIOMETRY. Value choices: GEOMETRY,RADIOMETRY,COPY_FOOTPRINT,COPY_TO_SIBLING,EDGE_DETECTION,VORONOI,DISPARITY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          optional. Default value: 1000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_type                            optional. Default value: BOTH. Value choices: BOTH,INSIDE,OUTSIDE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'blend_width': ['blend_width', 'optional'], 'max_sliver_size': ['max_sliver_size', 'optional'], 'order_by_attribute': ['order_by_attribute', 'optional'], 'order_by_base_value': ['order_by_base_value', 'optional'], 'sort_order': ['sort_order', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'computation_method': ['computation_method', 'optional'], 'update_existing': ['update_existing', 'optional'], 'cell_size': ['cell_size', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'view_point': ['view_point', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'sort_method': ['sort_method', 'optional'], 'blend_width_units': ['blend_width_units', 'optional'], 'request_size_type': ['request_size_type', 'optional'], 'request_size': ['request_size', 'optional'], 'blend_type': ['blend_type', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildSeamlines', inputs, in_db, out_db)

          
def calculate_cell_size_ranges(mosaic_dataset, where_clause=None, do_compute_min='true', do_compute_max='true', max_range_factor='10', cell_size_tolerance_factor='0.8', update_missing_only='false'):
     """
     Geoprocessing tool that computes the minimum and maximum cell sizes for the rasters in a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_missing_only                   optional. Default value: false. Value choices: UPDATE_MISSING_ONLY,UPDATE_ALL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size_tolerance_factor            optional. Default value: 0.8. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     do_compute_max                        optional. Default value: true. Value choices: MAX_CELL_SIZES,NO_MAX_CELL_SIZES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_range_factor                      optional. Default value: 10. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     do_compute_min                        optional. Default value: true. Value choices: MIN_CELL_SIZES,NO_MIN_CELL_SIZES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_missing_only': ['update_missing_only', 'optional'], 'cell_size_tolerance_factor': ['cell_size_tolerance_factor', 'optional'], 'do_compute_max': ['do_compute_max', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'max_range_factor': ['max_range_factor', 'optional'], 'do_compute_min': ['do_compute_min', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateCellSizeRanges', inputs, in_db, out_db)

          
def color_balance_mosaic_dataset(mosaic_dataset, balancing_method='DODGING', color_surface_type='SINGLE_COLOR', target_raster=None, exclude_raster=None, stretch_type=None, gamma='1', block_field=None):
     """
     Geoprocessing tool that color balances a mosaic dataset so the tiles appear seamless.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     stretch_type                          optional. Default value: NONE. Value choices: NONE,STANDARD_DEVIATION,MINIMUM_MAXIMUM,ADAPTIVE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     block_field                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     color_surface_type                    optional. Default value: SINGLE_COLOR. Value choices: SINGLE_COLOR,COLOR_GRID,FIRST_ORDER,SECOND_ORDER,THIRD_ORDER
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_raster                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     balancing_method                      optional. Default value: DODGING. Value choices: DODGING,HISTOGRAM,STANDARD_DEVIATION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gamma                                 optional. Default value: 1. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     exclude_raster                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'exclude_raster': ['exclude_raster', 'optional'], 'block_field': ['block_field', 'optional'], 'color_surface_type': ['color_surface_type', 'optional'], 'target_raster': ['target_raster', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'balancing_method': ['balancing_method', 'optional'], 'gamma': ['gamma', 'optional'], 'stretch_type': ['stretch_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ColorBalanceMosaicDataset', inputs, in_db, out_db)

          
def compute_dirty_area(mosaic_dataset, timestamp, where_clause=None):
     """
     Geoprocessing tool that identifies an area within a mosaic dataset that has changed since a specified point in time.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     timestamp                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'timestamp': ['timestamp', 'required'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'ComputeDirtyArea', inputs, in_db, out_db)

          
def create_mosaic_dataset(workspace, mosaicdataset_name, coordinate_system, num_bands=None, pixel_type=None, product_definition=None, product_band_definitions=None):
     """
     Geoprocessing tool that makes an empty mosaic dataset in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicdataset_name                    required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     coordinate_system                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     product_band_definitions              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     num_bands                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     product_definition                    optional. Default value: NONE. Value choices: NONE,NATURAL_COLOR_RGB,NATURAL_COLOR_RGBI,FALSE_COLOR_IRG,VECTOR_FIELD_UV,VECTOR_FIELD_MAGNITUDE_DIRECTION,DEIMOS2_4BANDS,DMCII_3BANDS,DUBAISAT-2_4BANDS,FORMOSAT-2_4BANDS,GEOEYE-1_4BANDS,GF-1 PMS_4BANDS,GF-1 WFV_4BANDS,GF-2 PMS_4BANDS,GF-4 PMI_4BANDS,HJ 1A/1B CCD_4BANDS,IKONOS_4BANDS,JILIN-1_3BANDS,KOMPSAT-2_4BANDS,KOMPSAT-3_4BANDS,LANDSAT_6BANDS,LANDSAT_MSS_4BANDS,LANDSAT_8BANDS,PLEIADES-1_4BANDS,QUICKBIRD_4BANDS,RAPIDEYE_5BANDS,SENTINEL2_13BANDS,SPOT-5_4BANDS,SPOT-6_4BANDS,SPOT-7_4BANDS,TH-01_4BANDS,WORLDVIEW-2_8BANDS,WORLDVIEW-3_8BANDS,ZY1-02C PMS_3BANDS,ZY3-CRESDA_4BANDS,ZY3-SASMAC_4BANDS,CUSTOM
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            optional. Default value: None. Value choices: 1_BIT,2_BIT,4_BIT,8_BIT_UNSIGNED,8_BIT_SIGNED,16_BIT_UNSIGNED,16_BIT_SIGNED,32_BIT_UNSIGNED,32_BIT_SIGNED,32_BIT_FLOAT,64_BIT
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'product_band_definitions': ['product_band_definitions', 'optional'], 'product_definition': ['product_definition', 'optional'], 'workspace': ['in_workspace', 'required'], 'mosaicdataset_name': ['in_mosaicdataset_name', 'required'], 'num_bands': ['num_bands', 'optional'], 'coordinate_system': ['coordinate_system', 'required'], 'pixel_type': ['pixel_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateMosaicDataset', inputs, in_db, out_db)

          
def create_referenced_mosaic_dataset(dataset, coordinate_system=None, number_of_bands=None, pixel_type=None, where_clause=None, template_dataset=None, extent=None, select_using_features='true', lod_field=None, minps_field=None, maxps_field=None, pixel_size=None, build_boundary='true'):
     """
     Geoprocessing tool that creates a new mosaic dataset from a selection set of a raster catalog, or a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     select_using_features                 optional. Default value: true. Value choices: SELECT_USING_FEATURES,NO_SELECT_USING_FEATURES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lod_field                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_size                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minps_field                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maxps_field                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_bands                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_boundary                        optional. Default value: true. Value choices: BUILD_BOUNDARY,NO_BOUNDARY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            optional. Default value: None. Value choices: 1_BIT,2_BIT,4_BIT,8_BIT_UNSIGNED,8_BIT_SIGNED,16_BIT_UNSIGNED,16_BIT_SIGNED,32_BIT_UNSIGNED,32_BIT_SIGNED,32_BIT_FLOAT,64_BIT
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'lod_field': ['lod_field', 'optional'], 'coordinate_system': ['coordinate_system', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'select_using_features': ['select_using_features', 'optional'], 'extent': ['extent', 'optional'], 'dataset': ['in_dataset', 'required'], 'pixel_size': ['pixelSize', 'optional'], 'minps_field': ['minPS_field', 'optional'], 'maxps_field': ['maxPS_field', 'optional'], 'number_of_bands': ['number_of_bands', 'optional'], 'where_clause': ['where_clause', 'optional'], 'build_boundary': ['build_boundary', 'optional'], 'pixel_type': ['pixel_type', 'optional']}
     out_db = {'mosaic_dataset': ['out_mosaic_dataset', 'required', None, None]}
     return _execute_tool('management', 'CreateReferencedMosaicDataset', inputs, in_db, out_db)

          
def define_overviews(mosaic_dataset, overview_image_folder=None, template_dataset=None, extent=None, pixel_size=None, number_of_levels=None, tile_rows='5120', tile_cols='5120', overview_factor='3', force_overview_tiles='false', resampling_method='BILINEAR', compression_method='JPEG', compression_quality='80'):
     """
     Geoprocessing tool that defines the tiling schema and properties of the preprocessed raster datasets that will cover part or all of a mosaic dataset at varying resolutions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_method                     optional. Default value: BILINEAR. Value choices: NEAREST,BILINEAR,CUBIC
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overview_image_folder                 optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_cols                             optional. Default value: 5120. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overview_factor                       optional. Default value: 3. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   optional. Default value: 80. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_rows                             optional. Default value: 5120. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    optional. Default value: JPEG. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_size                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_levels                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     force_overview_tiles                  optional. Default value: false. Value choices: FORCE_OVERVIEW_TILES,NO_FORCE_OVERVIEW_TILES
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'resampling_method': ['resampling_method', 'optional'], 'overview_image_folder': ['overview_image_folder', 'optional'], 'tile_cols': ['tile_cols', 'optional'], 'overview_factor': ['overview_factor', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'extent': ['extent', 'optional'], 'tile_rows': ['tile_rows', 'optional'], 'compression_method': ['compression_method', 'optional'], 'pixel_size': ['pixel_size', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'number_of_levels': ['number_of_levels', 'optional'], 'force_overview_tiles': ['force_overview_tiles', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DefineOverviews', inputs, in_db, out_db)

          
def generate_exclude_area(raster, pixel_type, generate_method, max_red='255', max_green='255', max_blue='255', max_white='255', max_black='0', max_magenta='255', max_cyan='255', max_yellow='255', percentage_low='0', percentage_high='100'):
     """
     Geoprocessing tool that generates exclude areas to use within the Color Balance Mosaic Dataset tool.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_method                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     pixel_type                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_yellow                            optional. Default value: 255. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cyan                              optional. Default value: 255. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage_low                        optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_green                             optional. Default value: 255. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage_high                       optional. Default value: 100. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_blue                              optional. Default value: 255. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_red                               optional. Default value: 255. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_magenta                           optional. Default value: 255. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_black                             optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_white                             optional. Default value: 255. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'percentage_low': ['percentage_low', 'optional'], 'max_cyan': ['max_cyan', 'optional'], 'max_green': ['max_green', 'optional'], 'max_blue': ['max_blue', 'optional'], 'max_magenta': ['max_magenta', 'optional'], 'generate_method': ['generate_method', 'required'], 'raster': ['in_raster', 'required'], 'max_yellow': ['max_yellow', 'optional'], 'percentage_high': ['percentage_high', 'optional'], 'max_red': ['max_red', 'optional'], 'max_black': ['max_black', 'optional'], 'max_white': ['max_white', 'optional'], 'pixel_type': ['pixel_type', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'GenerateExcludeArea', inputs, in_db, out_db)

          
def import_mosaic_dataset_geometry(mosaic_dataset, target_featureclass_type, target_jofield, input_featureclass, input_jofield):
     """
     Geoprocessing tool that imports geometry to a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_jofield                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_featureclass                    required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_jofield                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_featureclass_type              required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'target_jofield': ['target_join_field', 'required'], 'input_featureclass': ['input_featureclass', 'required'], 'input_jofield': ['input_join_field', 'required'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'target_featureclass_type': ['target_featureclass_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportMosaicDatasetGeometry', inputs, in_db, out_db)

          
def remove_rasters_from_mosaic_dataset(mosaic_dataset, where_clause=None, update_boundary='true', mark_overviews_items='true', delete_overview_images='true', delete_item_cache='true', remove_items='true', update_cellsize_ranges='true'):
     """
     Geoprocessing tool that removes rasters from a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_item_cache                     optional. Default value: true. Value choices: DELETE_ITEM_CACHE,NO_DELETE_ITEM_CACHE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     remove_items                          optional. Default value: true. Value choices: REMOVE_MOSAICDATASET_ITEMS,NO_REMOVE_MOSAICDATASET_ITEMS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_overview_images                optional. Default value: true. Value choices: DELETE_OVERVIEW_IMAGES,NO_DELETE_OVERVIEW_IMAGES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                optional. Default value: true. Value choices: UPDATE_CELL_SIZES,NO_CELL_SIZES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mark_overviews_items                  optional. Default value: true. Value choices: MARK_OVERVIEW_ITEMS,NO_MARK_OVERVIEW_ITEMS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       optional. Default value: true. Value choices: UPDATE_BOUNDARY,NO_BOUNDARY
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'delete_item_cache': ['delete_item_cache', 'optional'], 'remove_items': ['remove_items', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'delete_overview_images': ['delete_overview_images', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'where_clause': ['where_clause', 'optional'], 'mark_overviews_items': ['mark_overviews_items', 'optional'], 'update_boundary': ['update_boundary', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RemoveRastersFromMosaicDataset', inputs, in_db, out_db)

          
def synchronize_mosaic_dataset(mosaic_dataset, where_clause=None, new_items='false', sync_only_stale='true', update_cellsize_ranges='true', update_boundary='true', update_overviews='false', build_pyramids='false', calculate_statistics='false', build_thumbnails='false', build_item_cache='false', rebuild_raster='true', update_fields='true', fields_to_update=None, existing_items='true', broken_items='false', skip_existing_items='true', refresh_aggregate_info='false', estimate_statistics='false'):
     """
     Geoprocessing tool that rebuilds the raster item and updates affected fields in the mosaic dataset using the raster type and options that were used when it was originally added.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_overviews                      optional. Default value: false. Value choices: UPDATE_OVERVIEWS,NO_OVERVIEWS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields_to_update                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_pyramids                        optional. Default value: false. Value choices: BUILD_PYRAMIDS,NO_PYRAMIDS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_item_cache                      optional. Default value: false. Value choices: BUILD_ITEM_CACHE,NO_ITEM_CACHE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rebuild_raster                        optional. Default value: true. Value choices: REBUILD_RASTER,NO_RASTER
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     calculate_statistics                  optional. Default value: false. Value choices: CALCULATE_STATISTICS,NO_STATISTICS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing_items                   optional. Default value: true. Value choices: SKIP_EXISTING_ITEMS,OVERWRITE_EXISTING_ITEMS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       optional. Default value: true. Value choices: UPDATE_BOUNDARY,NO_BOUNDARY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                optional. Default value: true. Value choices: UPDATE_CELL_SIZES,NO_CELL_SIZES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     broken_items                          optional. Default value: false. Value choices: REMOVE_BROKEN_ITEMS,IGNORE_BROKEN_ITEMS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate_statistics                   optional. Default value: false. Value choices: ESTIMATE_STATISTICS,NO_STATISTICS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     refresh_aggregate_info                optional. Default value: false. Value choices: REFRESH_INFO,NO_REFRESH_INFO
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_thumbnails                      optional. Default value: false. Value choices: BUILD_THUMBNAILS,NO_THUMBNAILS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     existing_items                        optional. Default value: true. Value choices: UPDATE_EXISTING_ITEMS,IGNORE_EXISTING_ITEMS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_items                             optional. Default value: false. Value choices: UPDATE_WITH_NEW_ITEMS,NO_NEW_ITEMS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_fields                         optional. Default value: true. Value choices: UPDATE_FIELDS,NO_FIELDS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sync_only_stale                       optional. Default value: true. Value choices: SYNC_STALE,SYNC_ALL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_overviews': ['update_overviews', 'optional'], 'fields_to_update': ['fields_to_update', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'build_item_cache': ['build_item_cache', 'optional'], 'rebuild_raster': ['rebuild_raster', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional'], 'update_fields': ['update_fields', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'broken_items': ['broken_items', 'optional'], 'new_items': ['new_items', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'refresh_aggregate_info': ['refresh_aggregate_info', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'existing_items': ['existing_items', 'optional'], 'where_clause': ['where_clause', 'optional'], 'skip_existing_items': ['skip_existing_items', 'optional'], 'sync_only_stale': ['sync_only_stale', 'optional'], 'update_boundary': ['update_boundary', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SynchronizeMosaicDataset', inputs, in_db, out_db)

          
def calculate_end_time(table, start_field, end_field, fields=None):
     """
     Geoprocessing tool that populates the values for a specified end time  field with values calculated using the specified start time field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     end_field                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     start_field                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'end_field': ['end_field', 'required'], 'start_field': ['start_field', 'required'], 'table': ['in_table', 'required'], 'fields': ['fields', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateEndTime', inputs, in_db, out_db)

          
def convert_time_field(table, input_time_field, input_time_format, output_time_field, output_time_type='DATE', output_time_format=None):
     """
     Geoprocessing tool to convert timestamps stored in a text or numeric field to a date field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_time_field                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_format                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_field                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_time_type                      optional. Default value: DATE. Value choices: DATE,TEXT,LONG,SHORT,DOUBLE,FLOAT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_time_format                    optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'output_time_type': ['output_time_type', 'optional'], 'table': ['in_table', 'required'], 'output_time_format': ['output_time_format', 'optional'], 'input_time_field': ['input_time_field', 'required'], 'input_time_format': ['input_time_format', 'required'], 'output_time_field': ['output_time_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeField', inputs, in_db, out_db)

          
def convert_time_zone(table, input_time_field, input_time_zone, output_time_field, output_time_zone, input_dst='true', output_dst='true'):
     """
     Geoprocessing tool to convert time values from one time zone to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_time_field                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_zone                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_zone                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_field                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_dst                            optional. Default value: true. Value choices: OUTPUT_ADJUSTED_FOR_DST,OUTPUT_NOT_ADJUSTED_FOR_DST
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_dst                             optional. Default value: true. Value choices: INPUT_ADJUSTED_FOR_DST,INPUT_NOT_ADJUSTED_FOR_DST
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_dst': ['input_dst', 'optional'], 'table': ['in_table', 'required'], 'output_dst': ['output_dst', 'optional'], 'input_time_field': ['input_time_field', 'required'], 'output_time_zone': ['output_time_zone', 'required'], 'input_time_zone': ['input_time_zone', 'required'], 'output_time_field': ['output_time_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeZone', inputs, in_db, out_db)

          
def transpose_fields(table, field, transposed_field_name, value_field_name, attribute_fields=None):
     """
     Geoprocessing tool to transpose data values stored in columns  of a table or feature class into rows.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transposed_field_name                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     value_field_name                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_fields                      optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'transposed_field_name': ['in_transposed_field_name', 'required'], 'value_field_name': ['in_value_field_name', 'required'], 'attribute_fields': ['attribute_fields', 'optional'], 'field': ['in_field', 'required'], 'table': ['in_table', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'TransposeFields', inputs, in_db, out_db)

          
def warp_from_file(raster, link_file, transformation_type='POLYORDER1', resampling_type='NEAREST'):
     """
     Geoprocessing tool that performs a transformation on the raster based on a link file, using a polynomial transformation.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     link_file                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       optional. Default value: NEAREST. Value choices: NEAREST,BILINEAR,CUBIC,MAJORITY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   optional. Default value: POLYORDER1. Value choices: POLYORDER0,POLYSIMILARITY,POLYORDER1,POLYORDER2,POLYORDER3,ADJUST,SPLINE,PROJECTIVE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'link_file': ['link_file', 'required'], 'transformation_type': ['transformation_type', 'optional'], 'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'WarpFromFile', inputs, in_db, out_db)

          
def import_xml_workspace_document(target_geodatabase, file, import_type='DATA', config_keyword=None):
     """
     Geoprocessing tool that imports the contents of an XML workspace document into an existing geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_geodatabase                    required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     import_type                           optional. Default value: DATA. Value choices: DATA,SCHEMA_ONLY
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'file': ['in_file', 'required'], 'target_geodatabase': ['target_geodatabase', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'import_type': ['import_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ImportXMLWorkspaceDocument', inputs, in_db, out_db)

          
def alter_mosaic_dataset_schema(mosaic_dataset, side_tables=None, raster_type_names=None, editor_tracking='false'):
     """
     Geoprocessing tool to define the editing operations nonowners have when editing a mosaic dataset in an enterprise geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     side_tables                           optional. Default value: None. Value choices: ANALYSIS,BOUNDARY,CACHE,COLOR_CORRECTION,DEFINITION,LEVELS,LOG,OVERVIEW,SEAMLINE,STEREO,VIEW
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     editor_tracking                       optional. Default value: false. Value choices: EDITOR_TRACKING,NO_EDITOR_TRACKING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_type_names                     optional. Default value: None. Value choices: ADS,CADRG/ECRG,CIB,DEIMOS-2,DMCii,DTED,DubaiSat-2,FORMOSAT-2,Frame Camera,GF-1 PMS,GF-1 WFV,GF-2 PMS,GF-4 PMI,GRIB,GeoEye-1,HDF,HJ 1A/1B CCD,HRE,IKONOS,Jilin-1,KOMPSAT-2,KOMPSAT-3,LAS,Landsat 1-5 MSS,Landsat 4-5 TM,Landsat 7 ETM+,Landsat 8,NCDRD,NITF,NetCDF,Pleiades-1,QuickBird,RADARSAT-2,RapidEye,Raster Process Definition,SPOT 5,SPOT 6,SPOT 7,Scanned Aerial Imagery,Sentinel-2,TH-01,UAV/UAS,WorldView-1,WorldView-2,WorldView-3,ZY1-02C HRC,ZY1-02C PMS,ZY3-CRESDA,ZY3-SASMAC
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'side_tables': ['side_tables', 'optional'], 'editor_tracking': ['editor_tracking', 'optional'], 'raster_type_names': ['raster_type_names', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'AlterMosaicDatasetSchema', inputs, in_db, out_db)

          
def analyze_mosaic_dataset(mosaic_dataset, where_clause=None, checker_keywords=None):
     """
     Geoprocessing tool that checks a mosaic dataset for errors, and possible improvements.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     checker_keywords                      optional. Default value: None. Value choices: FOOTPRINT,FUNCTION,RASTER,PATHS,SOURCE_VALIDITY,STALE,PYRAMIDS,STATISTICS,PERFORMANCE,INFORMATION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'checker_keywords': ['checker_keywords', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AnalyzeMosaicDataset', inputs, in_db, out_db)

          
def compact(workspace):
     """
     Geoprocessing tool for compacting a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'Compact', inputs, in_db, out_db)

          
def clear_workspace_cache(data=None):
     """
     Geoprocessing tool clears any enterprise geodatabase workspaces from the enterprise geodatabase workspace cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data                                  optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ClearWorkspaceCache', inputs, in_db, out_db)

          
def analyze_datasets(input_database, include_system, datasets=None, analyze_base='true', analyze_delta='true', analyze_archive='true'):
     """
     Geoprocessing tool to  update  database statistics of base tables, delta tables, and archive tables, along with the statistics on those tables' indexes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_system                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasets                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_delta                         optional. Default value: true. Value choices: ANALYZE_DELTA,NO_ANALYZE_DELTA
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_base                          optional. Default value: true. Value choices: ANALYZE_BASE,NO_ANALYZE_BASE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_archive                       optional. Default value: true. Value choices: ANALYZE_ARCHIVE,NO_ANALYZE_ARCHIVE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'include_system': ['include_system', 'required'], 'datasets': ['in_datasets', 'optional'], 'analyze_delta': ['analyze_delta', 'optional'], 'analyze_base': ['analyze_base', 'optional'], 'input_database': ['input_database', 'required'], 'analyze_archive': ['analyze_archive', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AnalyzeDatasets', inputs, in_db, out_db)

          
def rebuild_indexes(input_database, include_system, datasets=None, delta_only='true'):
     """
     Geoprocessing tool to update indexes of datasets stored in a database or geodatabase in DB2, Oracle, PostgreSQL, or SQL Server. In geodatabases, indexes  can also be rebuilt on  states and state_lineage geodatabase system tables and the delta tables of versioned datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_system                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasets                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delta_only                            optional. Default value: true. Value choices: ONLY_DELTAS,ALL
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'include_system': ['include_system', 'required'], 'input_database': ['input_database', 'required'], 'datasets': ['in_datasets', 'optional'], 'delta_only': ['delta_only', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RebuildIndexes', inputs, in_db, out_db)

          
def check_geometry(features):
     """
     Geoprocessing tool to generate a report of geometry problems in a feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'CheckGeometry', inputs, in_db, out_db)

          
def reconcile_versions(input_database, reconcile_mode, target_version=None, edit_versions=None, acquire_locks='true', abort_if_conflicts='false', conflict_definition='BY_OBJECT', conflict_resolution='FAVOR_TARGET_VERSION', with_post='false', with_delete='false'):
     """
     Geoprocessing tool that reconciles a version or multiple versions against a target version.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     reconcile_mode                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     abort_if_conflicts                    optional. Default value: false. Value choices: ABORT_CONFLICTS,NO_ABORT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     acquire_locks                         optional. Default value: true. Value choices: LOCK_ACQUIRED,NO_LOCK_ACQUIRED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     with_post                             optional. Default value: false. Value choices: POST,NO_POST
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     conflict_resolution                   optional. Default value: FAVOR_TARGET_VERSION. Value choices: FAVOR_TARGET_VERSION,FAVOR_EDIT_VERSION
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     conflict_definition                   optional. Default value: BY_OBJECT. Value choices: BY_OBJECT,BY_ATTRIBUTE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_versions                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     with_delete                           optional. Default value: false. Value choices: DELETE_VERSION,KEEP_VERSION
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'abort_if_conflicts': ['abort_if_conflicts', 'optional'], 'target_version': ['target_version', 'optional'], 'acquire_locks': ['acquire_locks', 'optional'], 'with_post': ['with_post', 'optional'], 'conflict_resolution': ['conflict_resolution', 'optional'], 'input_database': ['input_database', 'required'], 'conflict_definition': ['conflict_definition', 'optional'], 'edit_versions': ['edit_versions', 'optional'], 'with_delete': ['with_delete', 'optional'], 'reconcile_mode': ['reconcile_mode', 'required']}
     out_db = {'log': ['out_log', 'optional', None, None]}
     return _execute_tool('management', 'ReconcileVersions', inputs, in_db, out_db)

          
def add_attachments(dataset, jofield, match_table, match_jofield, match_path_field, working_folder=None):
     """
     Geoprocessing tool that adds file attachments to the records of a geodatabase feature class or table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_jofield                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_table                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_path_field                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     working_folder                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'match_jofield': ['in_match_join_field', 'required'], 'match_table': ['in_match_table', 'required'], 'working_folder': ['in_working_folder', 'optional'], 'jofield': ['in_join_field', 'required'], 'match_path_field': ['in_match_path_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddAttachments', inputs, in_db, out_db)

          
def disable_attachments(dataset):
     """
     Geoprocessing tool that disables attachments on a geodatabase feature class or table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'DisableAttachments', inputs, in_db, out_db)

          
def enable_attachments(dataset):
     """
     Geoprocessing tool that enables attachments on a geodatabase feature class or table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'EnableAttachments', inputs, in_db, out_db)

          
def remove_attachments(dataset, jofield, match_table, match_jofield, match_name_field=None):
     """
     Geoprocessing tool that removes attachments from geodatabase feature class or table records.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_jofield                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_table                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     match_name_field                      optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'match_jofield': ['in_match_join_field', 'required'], 'match_name_field': ['in_match_name_field', 'optional'], 'match_table': ['in_match_table', 'required'], 'jofield': ['in_join_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveAttachments', inputs, in_db, out_db)

          
def set_mosaic_dataset_properties(mosaic_dataset, rows_maximum_imagesize='4100', columns_maximum_imagesize='15000', allowed_compressions='None;LZ77;JPEG;LERC', default_compression_type=None, jpeg_quality='75', lerc_tolerance='0', resampling_type='BILINEAR', clip_to_footprints='false', footprints_may_contanodata='true', clip_to_boundary='true', color_correction='false', allowed_mensuration_capabilities=None, default_mensuration_capabilities='None', allowed_mosaic_methods='Center;NorthWest;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None', default_mosaic_method='Center', order_field=None, order_base=None, sorting_order='true', mosaic_operator='FIRST', blend_width='10', view_point_x='600', view_point_y='300', max_num_per_mosaic='20', cell_size_tolerance='0.8', cell_size=None, metadata_level='FULL', transmission_fields=None, use_time='false', start_time_field=None, end_time_field=None, time_format=None, geographic_transform=None, max_num_of_download_items='20', max_num_of_records_returned='1000', data_source_type='GENERIC', minimum_pixel_contribution='1', processing_templates=None, default_processing_template='None', time_interval=None, time_interval_units=None):
     """
     Geoprocessing tool that sets the default properties of a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width                           optional. Default value: 10. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_mensuration_capabilities      optional. Default value: None. Value choices: None,Basic,Base-Top Height,Base-Top Shadow Height,Top-Top Shadow Height,3D
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geographic_transform                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     start_time_field                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sorting_order                         optional. Default value: true. Value choices: ASCENDING,DESCENDING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size_tolerance                   optional. Default value: 0.8. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     end_time_field                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_source_type                      optional. Default value: GENERIC. Value choices: GENERIC,THEMATIC,PROCESSED,ELEVATION,SCIENTIFIC,VECTOR_UV,VECTOR_MAGDIR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_pixel_contribution            optional. Default value: 1. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       optional. Default value: BILINEAR. Value choices: NEAREST,BILINEAR,CUBIC,MAJORITY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_compressions                  optional. Default value: None;LZ77;JPEG;LERC. Value choices: None,JPEG,LZ77,LERC
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point_y                          optional. Default value: 300. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_interval_units                   optional. Default value: None. Value choices: None,Milliseconds,Seconds,Minutes,Hours,Days,Weeks,Months,Years,Decades,Centuries
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_to_boundary                      optional. Default value: true. Value choices: CLIP,NOT_CLIP
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jpeg_quality                          optional. Default value: 75. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     processing_templates                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_time                              optional. Default value: false. Value choices: ENABLED,DISABLED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_to_footprints                    optional. Default value: false. Value choices: CLIP,NOT_CLIP
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_compression_type              optional. Default value: NONE. Value choices: None,JPEG,LZ77,LERC
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_base                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     color_correction                      optional. Default value: false. Value choices: APPLY,NOT_APPLY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_of_download_items             optional. Default value: 20. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_mensuration_capabilities      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transmission_fields                   optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_mosaic_methods                optional. Default value: Center;NorthWest;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None. Value choices: None,Center,NorthWest,LockRaster,ByAttribute,Nadir,Viewpoint,Seamline
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_of_records_returned           optional. Default value: 1000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_format                           optional. Default value: None. Value choices: YYYY,YYYYMM,YYYY/MM,YYYY-MM,YYYYMMDD,YYYY/MM/DD,YYYY-MM-DD,YYYYMMDDhhmmss,YYYY/MM/DD hh:mm:ss,YYYY-MM-DD hh:mm:ss,YYYYMMDDhhmmss.s,YYYY/MM/DD hh:mm:ss.s,YYYY-MM-DD hh:mm:ss.s
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     metadata_level                        optional. Default value: FULL. Value choices: NONE,BASIC,FULL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows_maximum_imagesize                optional. Default value: 4100. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_per_mosaic                    optional. Default value: 20. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     footprints_may_contanodata            optional. Default value: true. Value choices: FOOTPRINTS_MAY_CONTAIN_NODATA,FOOTPRINTS_DO_NOT_CONTAIN_NODATA
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point_x                          optional. Default value: 600. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     columns_maximum_imagesize             optional. Default value: 15000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_operator                       optional. Default value: FIRST. Value choices: FIRST,LAST,MIN,MAX,MEAN,BLEND,SUM
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lerc_tolerance                        optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_field                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_processing_template           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_interval                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_mosaic_method                 optional. Default value: Center. Value choices: None,Center,NorthWest,LockRaster,ByAttribute,Nadir,Viewpoint,Seamline
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'blend_width': ['blend_width', 'optional'], 'default_mensuration_capabilities': ['default_mensuration_capabilities', 'optional'], 'geographic_transform': ['geographic_transform', 'optional'], 'max_num_per_mosaic': ['max_num_per_mosaic', 'optional'], 'sorting_order': ['sorting_order', 'optional'], 'cell_size_tolerance': ['cell_size_tolerance', 'optional'], 'start_time_field': ['start_time_field', 'optional'], 'data_source_type': ['data_source_type', 'optional'], 'minimum_pixel_contribution': ['minimum_pixel_contribution', 'optional'], 'resampling_type': ['resampling_type', 'optional'], 'allowed_compressions': ['allowed_compressions', 'optional'], 'view_point_y': ['view_point_y', 'optional'], 'cell_size': ['cell_size', 'optional'], 'time_format': ['time_format', 'optional'], 'clip_to_boundary': ['clip_to_boundary', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'processing_templates': ['processing_templates', 'optional'], 'use_time': ['use_time', 'optional'], 'clip_to_footprints': ['clip_to_footprints', 'optional'], 'default_compression_type': ['default_compression_type', 'optional'], 'order_base': ['order_base', 'optional'], 'color_correction': ['color_correction', 'optional'], 'time_interval_units': ['time_interval_units', 'optional'], 'max_num_of_download_items': ['max_num_of_download_items', 'optional'], 'allowed_mensuration_capabilities': ['allowed_mensuration_capabilities', 'optional'], 'transmission_fields': ['transmission_fields', 'optional'], 'allowed_mosaic_methods': ['allowed_mosaic_methods', 'optional'], 'max_num_of_records_returned': ['max_num_of_records_returned', 'optional'], 'end_time_field': ['end_time_field', 'optional'], 'metadata_level': ['metadata_level', 'optional'], 'rows_maximum_imagesize': ['rows_maximum_imagesize', 'optional'], 'jpeg_quality': ['JPEG_quality', 'optional'], 'footprints_may_contanodata': ['footprints_may_contain_nodata', 'optional'], 'order_field': ['order_field', 'optional'], 'columns_maximum_imagesize': ['columns_maximum_imagesize', 'optional'], 'mosaic_operator': ['mosaic_operator', 'optional'], 'lerc_tolerance': ['LERC_Tolerance', 'optional'], 'view_point_x': ['view_point_x', 'optional'], 'default_processing_template': ['default_processing_template', 'optional'], 'time_interval': ['time_interval', 'optional'], 'default_mosaic_method': ['default_mosaic_method', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetMosaicDatasetProperties', inputs, in_db, out_db)

          
def set_raster_properties(raster, data_type=None, statistics=None, stats_file=None, nodata=None, key_properties=None):
     """
     Geoprocessing tool that sets properties on a raster dataset or mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     stats_file                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             optional. Default value: None. Value choices: GENERIC,ELEVATION,THEMATIC,PROCESSED,SCIENTIFIC,VECTOR_UV,VECTOR_MAGDIR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata                                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     key_properties                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'nodata': ['nodata', 'optional'], 'data_type': ['data_type', 'optional'], 'statistics': ['statistics', 'optional'], 'stats_file': ['stats_file', 'optional'], 'key_properties': ['key_properties', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetRasterProperties', inputs, in_db, out_db)

          
def download_rasters(image_service, out_folder, where_clause=None, selection_feature=None, clipping='false', convert_rasters='false', format='TIFF', compression_method=None, compression_quality=None, maintain_folder='false'):
     """
     Geoprocessing tool that downloads source files of the selected rasters from an image service to a designated location.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     image_service                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clipping                              optional. Default value: false. Value choices: CLIPPING,NO_CLIPPING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintain_folder                       optional. Default value: false. Value choices: MAINTAIN_FOLDER,NO_MAINTAIN_FOLDER
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_feature                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                optional. Default value: TIFF. Value choices: TIFF,BIL,BSQ,BIP,BMP,ENVI,IMAGINE Image,JPEG,GIF,JP2,PNG
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     convert_rasters                       optional. Default value: false. Value choices: ALWAYS_CONVERT,CONVERT_AS_REQUIRED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    optional. Default value: NONE. Value choices: NONE,JPEG,LZW,PACKBITS,RLE,CCITT_GROUP3,CCITT_GROUP4,CCITT_1D
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_folder': ['out_folder', 'required'], 'clipping': ['clipping', 'optional'], 'image_service': ['in_image_service', 'required'], 'maintain_folder': ['MAINTAIN_FOLDER', 'optional'], 'selection_feature': ['selection_feature', 'optional'], 'format': ['format', 'optional'], 'convert_rasters': ['convert_rasters', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'compression_method': ['compression_method', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DownloadRasters', inputs, in_db, out_db)

          
def create_enterprise_geodatabase(database_platform, instance_name, authorization_file, database_name=None, account_authentication='false', database_admin='sa', database_admpassword=None, sde_schema='true', gdb_admname='sde', gdb_admpassword=None, tablespace_name=None):
     """
     Geoprocessing tool that creates a database, geodatabase, and geodatabase administrator user in a Microsoft SQL Server  or PostgreSQL DBMS and creates a geodatabase, tablespace, and geodatabase administrator user in an Oracle DBMS.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_platform                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     instance_name                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     authorization_file                    required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gdb_admname                           optional. Default value: sde. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sde_schema                            optional. Default value: true. Value choices: SDE_SCHEMA,DBO_SCHEMA
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_admpassword                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_name                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tablespace_name                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_admin                        optional. Default value: sa. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     account_authentication                optional. Default value: false. Value choices: OPERATING_SYSTEM_AUTH,DATABASE_AUTH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gdb_admpassword                       optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'authorization_file': ['authorization_file', 'required'], 'gdb_admname': ['gdb_admin_name', 'optional'], 'sde_schema': ['sde_schema', 'optional'], 'instance_name': ['instance_name', 'required'], 'database_name': ['database_name', 'optional'], 'tablespace_name': ['tablespace_name', 'optional'], 'database_admin': ['database_admin', 'optional'], 'account_authentication': ['account_authentication', 'optional'], 'database_platform': ['database_platform', 'required'], 'gdb_admpassword': ['gdb_admin_password', 'optional'], 'database_admpassword': ['database_admin_password', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateEnterpriseGeodatabase', inputs, in_db, out_db)

          
def enable_enterprise_geodatabase(input_database, authorization_file):
     """
     Geoprocessing tool that creates geodatabase system tables, stored procedures, functions, and types in an existing database.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     authorization_file                    required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required'], 'authorization_file': ['authorization_file', 'required']}
     out_db = {}
     return _execute_tool('management', 'EnableEnterpriseGeodatabase', inputs, in_db, out_db)

          
def feature_envelope_to_polygon(features, single_envelope='false'):
     """
     Geoprocessing tool that creates polygon features representing the envelopes of input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     single_envelope                       optional. Default value: false. Value choices: MULTIPART,SINGLEPART
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'single_envelope': ['single_envelope', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureEnvelopeToPolygon', inputs, in_db, out_db)

          
def create_database_connection(out_folder_path, out_name, database_platform, instance, account_authentication='true', username=None, password=None, save_user_pass='true', database=None, schema=None, version_type='TRANSACTIONAL', version=None, date=None):
     """
     Geoprocessing tool for creating connection files to databases or enterprise, workgroup, or desktop geodatabases.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     instance                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     database_platform                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder_path                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     schema                                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     username                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     save_user_pass                        optional. Default value: true. Value choices: SAVE_USERNAME,DO_NOT_SAVE_USERNAME
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     date                                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     account_authentication                optional. Default value: true. Value choices: DATABASE_AUTH,OPERATING_SYSTEM_AUTH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_type                          optional. Default value: TRANSACTIONAL. Value choices: TRANSACTIONAL,HISTORICAL,POINT_IN_TIME
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     password                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'database': ['database', 'optional'], 'version_type': ['version_type', 'optional'], 'account_authentication': ['account_authentication', 'optional'], 'database_platform': ['database_platform', 'required'], 'password': ['password', 'optional'], 'out_name': ['out_name', 'required'], 'date': ['date', 'optional'], 'username': ['username', 'optional'], 'instance': ['instance', 'required'], 'schema': ['schema', 'optional'], 'version': ['version', 'optional'], 'out_folder_path': ['out_folder_path', 'required'], 'save_user_pass': ['save_user_pass', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseConnection', inputs, in_db, out_db)

          
def delete_mosaic_dataset(mosaic_dataset, delete_overview_images='true', delete_item_cache='true'):
     """
     Geoprocessing tool that deletes a mosaic dataset, overviews, and item cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_overview_images                optional. Default value: true. Value choices: DELETE_OVERVIEW_IMAGES,NO_DELETE_OVERVIEW_IMAGES
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_item_cache                     optional. Default value: true. Value choices: DELETE_ITEM_CACHE,NO_DELETE_ITEM_CACHE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'delete_overview_images': ['delete_overview_images', 'optional'], 'delete_item_cache': ['delete_item_cache', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteMosaicDataset', inputs, in_db, out_db)

          
def generate_attachment_match_table(dataset, folder, key_field, file_filter=None, use_relative_paths='true'):
     """
     Geoprocessing tool that creates a Match Table to be used with the Add Attachments and Remove Attachment tools.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     key_field                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     folder                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file_filter                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_relative_paths                    optional. Default value: true. Value choices: RELATIVE,ABSOLUTE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'key_field': ['in_key_field', 'required'], 'folder': ['in_folder', 'required'], 'file_filter': ['in_file_filter', 'optional'], 'use_relative_paths': ['in_use_relative_paths', 'optional']}
     out_db = {'match_table': ['out_match_table', 'required', None, None]}
     return _execute_tool('management', 'GenerateAttachmentMatchTable', inputs, in_db, out_db)

          
def create_database_view(input_database, view_name, view_definition):
     """
     Geoprocessing tool for creating a view in a database or enterprise geodatabase based on an SQL expression.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_name                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     view_definition                       required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'view_name': ['view_name', 'required'], 'input_database': ['input_database', 'required'], 'view_definition': ['view_definition', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseView', inputs, in_db, out_db)

          
def sort_coded_value_domain(workspace, domaname, sort_by, sort_order):
     """
     Geoprocessing tool that sorts the code or description of a coded value domain in either ascending or descending order.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_order                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_by                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'sort_order': ['sort_order', 'required'], 'domaname': ['domain_name', 'required'], 'sort_by': ['sort_by', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'SortCodedValueDomain', inputs, in_db, out_db)

          
def disable_editor_tracking(dataset, creator='true', creation_date='true', last_editor='true', last_edit_date='true'):
     """
     Geoprocessing tool to disable editor tracking on a feature class, table, mosaic dataset, or raster catalog.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creation_date                         optional. Default value: true. Value choices: DISABLE_CREATION_DATE,NO_DISABLE_CREATION_DATE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_editor                           optional. Default value: true. Value choices: DISABLE_LAST_EDITOR,NO_DISABLE_LAST_EDITOR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_edit_date                        optional. Default value: true. Value choices: DISABLE_LAST_EDIT_DATE,NO_DISABLE_LAST_EDIT_DATE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creator                               optional. Default value: true. Value choices: DISABLE_CREATOR,NO_DISABLE_CREATOR
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'creation_date': ['creation_date', 'optional'], 'last_edit_date': ['last_edit_date', 'optional'], 'last_editor': ['last_editor', 'optional'], 'creator': ['creator', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DisableEditorTracking', inputs, in_db, out_db)

          
def enable_editor_tracking(dataset, creator_field=None, creation_date_field=None, last_editor_field=None, last_edit_date_field=None, add_fields=None, record_dates_in='UTC'):
     """
     Geoprocessing tool to enable  editor tracking for a feature class, table, mosaic dataset, or raster catalog.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creator_field                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_editor_field                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_edit_date_field                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     record_dates_in                       optional. Default value: UTC. Value choices: UTC,DATABASE_TIME
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     add_fields                            optional. Default value: None. Value choices: ADD_FIELDS,NO_ADD_FIELDS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creation_date_field                   optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'creator_field': ['creator_field', 'optional'], 'last_edit_date_field': ['last_edit_date_field', 'optional'], 'add_fields': ['add_fields', 'optional'], 'record_dates_in': ['record_dates_in', 'optional'], 'creation_date_field': ['creation_date_field', 'optional'], 'last_editor_field': ['last_editor_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'EnableEditorTracking', inputs, in_db, out_db)

          
def truncate_table(table):
     """
     Geoprocessing tool for truncating a table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'TruncateTable', inputs, in_db, out_db)

          
def upgrade_dataset(dataset):
     """
     Geoprocessing tool that will upgrade mosaic datasets, network datasets, and parcel fabrics to the current ArcGIS release.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'UpgradeDataset', inputs, in_db, out_db)

          
def export_mosaic_dataset_paths(mosaic_dataset, where_clause=None, export_mode='ALL', types_of_paths=None):
     """
     Geoprocessing tool that creates a table listing the paths to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     export_mode                           optional. Default value: ALL. Value choices: ALL,BROKEN
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     types_of_paths                        optional. Default value: None. Value choices: RASTER,ITEM_CACHE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'export_mode': ['export_mode', 'optional'], 'types_of_paths': ['types_of_paths', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'ExportMosaicDatasetPaths', inputs, in_db, out_db)

          
def repair_mosaic_dataset_paths(mosaic_dataset, paths_list, where_clause=None):
     """
     Geoprocessing tool that repairs broken file paths within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     paths_list                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'paths_list': ['paths_list', 'required'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RepairMosaicDatasetPaths', inputs, in_db, out_db)

          
def create_database_user(input_database, user_name, user_authentication_type='false', user_password=None, role=None, tablespace_name=None):
     """
     Geoprocessing tool to create a database user in an Oracle, PostgreSQL, or Microsoft SQL Server database.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     user_name                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     role                                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tablespace_name                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_password                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_authentication_type              optional. Default value: false. Value choices: OPERATING_SYSTEM_USER,DATABASE_USER
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'tablespace_name': ['tablespace_name', 'optional'], 'user_password': ['user_password', 'optional'], 'role': ['role', 'optional'], 'user_name': ['user_name', 'required'], 'input_database': ['input_database', 'required'], 'user_authentication_type': ['user_authentication_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseUser', inputs, in_db, out_db)

          
def join_field(data, field, jotable, jofield, fields=None):
     """
     Geoprocessing tool that permanently joins the contents of a table to another table based on a common attribute field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jotable                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     data                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fields': ['fields', 'optional'], 'field': ['in_field', 'required'], 'jofield': ['join_field', 'required'], 'jotable': ['join_table', 'required'], 'data': ['in_data', 'required']}
     out_db = {}
     return _execute_tool('management', 'JoinField', inputs, in_db, out_db)

          
def edit_raster_function(mosaic_dataset, edit_mosaic_dataset_item='false', edit_options='INSERT', function_chadefinition=None, location_function_name=None):
     """
     Geoprocessing tool that adds, replaces, or removes a raster function template in a mosaic dataset, items in a mosaic dataset, or a raster layer that contains a raster function.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_options                          optional. Default value: INSERT. Value choices: INSERT,REPLACE,REMOVE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_function_name                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     function_chadefinition                optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_mosaic_dataset_item              optional. Default value: false. Value choices: EDIT_MOSAIC_DATASET_ITEM,EDIT_MOSAIC_DATASET
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'edit_options': ['edit_options', 'optional'], 'location_function_name': ['location_function_name', 'optional'], 'function_chadefinition': ['function_chain_definition', 'optional'], 'edit_mosaic_dataset_item': ['edit_mosaic_dataset_item', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'EditRasterFunction', inputs, in_db, out_db)

          
def build_mosaic_dataset_item_cache(mosaic_dataset, where_clause=None, define_cache='true', generate_cache='true', item_cache_folder=None, compression_method='LOSSLESS', compression_quality='80', max_allowed_rows='200000', max_allowed_columns='200000', request_size_type='PIXEL_SIZE_FACTOR', request_size='1'):
     """
     Geoprocessing tool that inserts the Cached Raster function into the function chain for items within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          optional. Default value: 1. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_cache                        optional. Default value: true. Value choices: GENERATE_CACHE,NO_GENERATE_CACHE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    optional. Default value: LOSSLESS. Value choices: NONE,LOSSLESS,LOSSY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size_type                     optional. Default value: PIXEL_SIZE_FACTOR. Value choices: PIXEL_SIZE,PIXEL_SIZE_FACTOR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     item_cache_folder                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_allowed_columns                   optional. Default value: 200000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     define_cache                          optional. Default value: true. Value choices: DEFINE_CACHE,NO_DEFINE_CACHE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_allowed_rows                      optional. Default value: 200000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   optional. Default value: 80. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'request_size': ['request_size', 'optional'], 'generate_cache': ['generate_cache', 'optional'], 'compression_method': ['compression_method', 'optional'], 'request_size_type': ['request_size_type', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'item_cache_folder': ['item_cache_folder', 'optional'], 'max_allowed_columns': ['max_allowed_columns', 'optional'], 'define_cache': ['define_cache', 'optional'], 'max_allowed_rows': ['max_allowed_rows', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildMosaicDatasetItemCache', inputs, in_db, out_db)

          
def batch_build_pyramids(input_raster_datasets, pyramid_levels='-1', skip_first_level='false', pyramid_resampling_technique='NEAREST', pyramid_compression_type='DEFAULT', compression_quality='75', skip_existing=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_raster_datasets                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         optional. Default value: None. Value choices: OVERWRITE,SKIP_EXISTING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_resampling_technique          optional. Default value: NEAREST. Value choices: NEAREST,BILINEAR,CUBIC
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_first_level                      optional. Default value: false. Value choices: SKIP_FIRST,NONE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   optional. Default value: 75. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_levels                        optional. Default value: -1. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_compression_type              optional. Default value: DEFAULT. Value choices: DEFAULT,JPEG,LZ77,NONE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['Skip_Existing', 'optional'], 'pyramid_resampling_technique': ['Pyramid_resampling_technique', 'optional'], 'skip_first_level': ['Skip_first_level', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required'], 'compression_quality': ['Compression_quality', 'optional'], 'pyramid_levels': ['Pyramid_levels', 'optional'], 'pyramid_compression_type': ['Pyramid_compression_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchBuildPyramids', inputs, in_db, out_db)

          
def batch_calculate_statistics(input_raster_datasets, number_of_columns_to_skip='1', number_of_rows_to_skip='1', ignore_values=None, skip_existing=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_raster_datasets                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_values                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         optional. Default value: None. Value choices: OVERWRITE,SKIP_EXISTING
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_rows_to_skip                optional. Default value: 1. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_columns_to_skip             optional. Default value: 1. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'ignore_values': ['Ignore_values', 'optional'], 'skip_existing': ['Skip_Existing', 'optional'], 'number_of_rows_to_skip': ['Number_of_rows_to_skip', 'optional'], 'number_of_columns_to_skip': ['Number_of_columns_to_skip', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required']}
     out_db = {}
     return _execute_tool('management', 'BatchCalculateStatistics', inputs, in_db, out_db)

          
def sort(dataset, sort_field, spatial_sort_method='UR'):
     """
     Geoprocessing tool that reorders records in a feature class or table based on field values.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_sort_method                   optional. Default value: UR. Value choices: UL,UR,LL,LR,PEANO
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'spatial_sort_method': ['spatial_sort_method', 'optional'], 'sort_field': ['sort_field', 'required']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'Sort', inputs, in_db, out_db)

          
def match_photos_to_rows_by_time(input_folder, input_table, time_field, add_photos_as_attachments='false', time_tolerance='0', clock_offset='0'):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_field                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_table                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_folder                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clock_offset                          optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_tolerance                        optional. Default value: 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     add_photos_as_attachments             optional. Default value: false. Value choices: ADD_ATTACHMENTS,NO_ATTACHMENTS
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'time_tolerance': ['Time_Tolerance', 'optional'], 'input_folder': ['Input_Folder', 'required'], 'clock_offset': ['Clock_Offset', 'optional'], 'time_field': ['Time_Field', 'required'], 'input_table': ['Input_Table', 'required'], 'add_photos_as_attachments': ['Add_Photos_As_Attachments', 'optional']}
     out_db = {'unmatched_photos_table': ['Unmatched_Photos_Table', 'optional', None, None], 'output_table': ['Output_Table', 'required', None, None]}
     return _execute_tool('management', 'MatchPhotosToRowsByTime', inputs, in_db, out_db)

          
def register_raster(raster, register_mode, reference_raster=None, input_link_file=None, transformation_type='POLYORDER1', maximum_rms_value=None):
     """
     Geoprocessing tool that registers an image to a reference image.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     register_mode                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     reference_raster                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_link_file                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_rms_value                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   optional. Default value: POLYORDER1. Value choices: POLYORDER0,POLYSIMILARITY,POLYORDER1,POLYORDER2,POLYORDER3,PROJECTIVE,SPLINE,ADJUST
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'reference_raster': ['reference_raster', 'optional'], 'register_mode': ['register_mode', 'required'], 'maximum_rms_value': ['maximum_rms_value', 'optional'], 'transformation_type': ['transformation_type', 'optional'], 'input_link_file': ['input_link_file', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {'output_cpt_link_file': ['output_cpt_link_file', 'optional', None, None]}
     return _execute_tool('management', 'RegisterRaster', inputs, in_db, out_db)

          
def create_role(input_database, role, grant_revoke='GRANT', user_name=None):
     """
     Geoprocessing tool to create a database role in an Oracle, PostgreSQL, or Microsoft SQL Server database and add users to or remove them from the role.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     role                                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_name                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     grant_revoke                          optional. Default value: GRANT. Value choices: GRANT,REVOKE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'role': ['role', 'required'], 'user_name': ['user_name', 'optional'], 'input_database': ['input_database', 'required'], 'grant_revoke': ['grant_revoke', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRole', inputs, in_db, out_db)

          
def export_tile_cache(cache_source, target_cache_folder, target_cache_name, export_cache_type='TILE_CACHE', storage_format_type='COMPACT', scales=None, area_of_interest='in_memory\{5C2A1BE5-7672-4AB1-8E1E-8C853CB4DE67}'):
     """
     Geoprocessing tool that exports tiles from an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_source                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_cache_name                     required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_cache_folder                   required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      optional. Default value: in_memory\{5C2A1BE5-7672-4AB1-8E1E-8C853CB4DE67}. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     storage_format_type                   optional. Default value: COMPACT. Value choices: COMPACT,EXPLODED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     export_cache_type                     optional. Default value: TILE_CACHE. Value choices: TILE_CACHE,TILE_PACKAGE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cache_source': ['in_cache_source', 'required'], 'target_cache_name': ['in_target_cache_name', 'required'], 'storage_format_type': ['storage_format_type', 'optional'], 'target_cache_folder': ['in_target_cache_folder', 'required'], 'area_of_interest': ['area_of_interest', 'optional'], 'export_cache_type': ['export_cache_type', 'optional'], 'scales': ['scales', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ExportTileCache', inputs, in_db, out_db)

          
def generate_tile_cache_tiling_scheme(dataset, tiling_scheme_generation_method, number_of_scales, predefined_tiling_scheme=None, scales=None, scales_type='false', tile_origin='0 0', dpi='96', tile_size='256 x 256', tile_format='MIXED', tile_compression_quality='75', storage_format='COMPACT', lerc_error=None):
     """
     Geoprocessing tool that generates an XML tiling scheme file used to create tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_scales                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     tiling_scheme_generation_method       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_origin                           optional. Default value: 0 0. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     predefined_tiling_scheme              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             optional. Default value: 256 x 256. Value choices: 128 x 128,256 x 256,512 x 512,1024 x 1024
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales_type                           optional. Default value: false. Value choices: CELL_SIZE,SCALE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_compression_quality              optional. Default value: 75. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     storage_format                        optional. Default value: COMPACT. Value choices: COMPACT,EXPLODED
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lerc_error                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dpi                                   optional. Default value: 96. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_format                           optional. Default value: MIXED. Value choices: PNG,PNG8,PNG24,PNG32,JPEG,MIXED,LERC
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'scales': ['scales', 'optional'], 'tile_origin': ['tile_origin', 'optional'], 'tiling_scheme_generation_method': ['tiling_scheme_generation_method', 'required'], 'lerc_error': ['lerc_error', 'optional'], 'tile_format': ['tile_format', 'optional'], 'dataset': ['in_dataset', 'required'], 'predefined_tiling_scheme': ['predefined_tiling_scheme', 'optional'], 'number_of_scales': ['number_of_scales', 'required'], 'scales_type': ['scales_type', 'optional'], 'tile_compression_quality': ['tile_compression_quality', 'optional'], 'tile_size': ['tile_size', 'optional'], 'dpi': ['dpi', 'optional'], 'storage_format': ['storage_format', 'optional']}
     out_db = {'tiling_scheme': ['out_tiling_scheme', 'required', None, None]}
     return _execute_tool('management', 'GenerateTileCacheTilingScheme', inputs, in_db, out_db)

          
def import_tile_cache(cache_target, cache_source, scales=None, area_of_interest='in_memory\{D6AB050F-D3FD-409C-B375-61816774DB6C}', overwrite='false'):
     """
     Geoprocessing tool that imports tiles from an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_target                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cache_source                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overwrite                             optional. Default value: false. Value choices: OVERWRITE,MERGE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      optional. Default value: in_memory\{D6AB050F-D3FD-409C-B375-61816774DB6C}. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cache_target': ['in_cache_target', 'required'], 'scales': ['scales', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'overwrite': ['overwrite', 'optional'], 'cache_source': ['in_cache_source', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportTileCache', inputs, in_db, out_db)

          
def manage_tile_cache(cache_location, manage_mode, cache_name=None, datasource=None, tiling_scheme='ARCGISONLINE_SCHEME', import_tiling_scheme=None, scales=None, area_of_interest='in_memory\{1084126B-ABAA-4CB2-B931-966A25BAD608}', max_cell_size=None, mcached_scale=None, max_cached_scale=None):
     """
     Geoprocessing tool that creates a tile cache or updates tiles in an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     manage_mode                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cache_location                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cached_scale                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tiling_scheme                         optional. Default value: ARCGISONLINE_SCHEME. Value choices: ARCGISONLINE_SCHEME,ARCGISONLINE+_SCHEME,ARCGISONLINE_ELEVATION_SCHEME,ARCGISONLINE_ELEVATION+_SCHEME,IMPORT_SCHEME
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mcached_scale                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cell_size                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_name                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     import_tiling_scheme                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      optional. Default value: in_memory\{1084126B-ABAA-4CB2-B931-966A25BAD608}. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasource                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'manage_mode': ['manage_mode', 'required'], 'max_cached_scale': ['max_cached_scale', 'optional'], 'tiling_scheme': ['tiling_scheme', 'optional'], 'mcached_scale': ['min_cached_scale', 'optional'], 'max_cell_size': ['max_cell_size', 'optional'], 'cache_name': ['in_cache_name', 'optional'], 'import_tiling_scheme': ['import_tiling_scheme', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'datasource': ['in_datasource', 'optional'], 'cache_location': ['in_cache_location', 'required'], 'scales': ['scales', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ManageTileCache', inputs, in_db, out_db)

          
def disable_archiving(dataset, preserve_history='true'):
     """
     Geoprocessing tool that disables archiving on a geodatabase feature class, table, or feature dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     preserve_history                      optional. Default value: true. Value choices: PRESERVE,DELETE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'preserve_history': ['preserve_history', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DisableArchiving', inputs, in_db, out_db)

          
def enable_archiving(dataset):
     """
     Geoprocessing tool that enables archiving on a table, feature class, or feature dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'EnableArchiving', inputs, in_db, out_db)

          
def merge_mosaic_dataset_items(mosaic_dataset, where_clause=None, block_field=None, max_rows_per_merged_items='1000'):
     """
     Geoprocessing tool that merges together two or more mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     block_field                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_rows_per_merged_items             optional. Default value: 1000. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'max_rows_per_merged_items': ['max_rows_per_merged_items', 'optional'], 'block_field': ['block_field', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MergeMosaicDatasetItems', inputs, in_db, out_db)

          
def split_mosaic_dataset_items(mosaic_dataset, where_clause=None):
     """
     Geoprocessing tool that splits mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SplitMosaicDatasetItems', inputs, in_db, out_db)

          
def compute_pansharpen_weights(raster, panchromatic_image, band_indexes=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     panchromatic_image                    required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_indexes                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'band_indexes': ['band_indexes', 'optional'], 'panchromatic_image': ['in_panchromatic_image', 'required'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'ComputePansharpenWeights', inputs, in_db, out_db)

          
def project(dataset, out_coor_system, transform_method=None, coor_system=None, preserve_shape='false', max_deviation=None, vertical='false'):
     """
     Geoprocessing tool that projects spatial data from one coordinate system to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_coor_system                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_deviation                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     preserve_shape                        optional. Default value: false. Value choices: PRESERVE_SHAPE,NO_PRESERVE_SHAPE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transform_method                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     vertical                              optional. Default value: false. Value choices: VERTICAL,NO_VERTICAL
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'coor_system': ['in_coor_system', 'optional'], 'vertical': ['vertical', 'optional'], 'out_coor_system': ['out_coor_system', 'required'], 'max_deviation': ['max_deviation', 'optional'], 'preserve_shape': ['preserve_shape', 'optional'], 'transform_method': ['transform_method', 'optional']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'Project', inputs, in_db, out_db)

          
def batch_project(input_feature_class_or_dataset, output_workspace, output_coordinate_system=None, template_dataset=None, transformation=None):
     """
     Geoprocessing tool to change the coordinate system of a set of input feature classes or feature datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_workspace                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_feature_class_or_dataset        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_coordinate_system              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'template_dataset': ['Template_dataset', 'optional'], 'transformation': ['Transformation', 'optional'], 'output_workspace': ['Output_Workspace', 'required'], 'output_coordinate_system': ['Output_Coordinate_System', 'optional'], 'input_feature_class_or_dataset': ['Input_Feature_Class_or_Dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'BatchProject', inputs, in_db, out_db)

          
def add_geometry_attributes(input_features, geometry_properties, length_unit=None, area_unit=None, coordinate_system=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_features                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     geometry_properties                   required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     length_unit                           optional. Default value: None. Value choices: FEET_US,METERS,KILOMETERS,MILES_US,NAUTICAL_MILES,YARDS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_unit                             optional. Default value: None. Value choices: ACRES,HECTARES,SQUARE_MILES_US,SQUARE_KILOMETERS,SQUARE_METERS,SQUARE_FEET_US,SQUARE_YARDS,SQUARE_NAUTICAL_MILES
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_features': ['Input_Features', 'required'], 'coordinate_system': ['Coordinate_System', 'optional'], 'length_unit': ['Length_Unit', 'optional'], 'geometry_properties': ['Geometry_Properties', 'required'], 'area_unit': ['Area_Unit', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddGeometryAttributes', inputs, in_db, out_db)

          
def migrate_relationship_class(relationship_class):
     """
     Geoprocessing tool that migrates an ObjectID-based relationship class to a GlobalID-based relationship class

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     relationship_class                    required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'relationship_class': ['in_relationship_class', 'required']}
     out_db = {}
     return _execute_tool('management', 'MigrateRelationshipClass', inputs, in_db, out_db)

          
def export_mosaic_dataset_geometry(mosaic_dataset, where_clause=None, geometry_type='FOOTPRINT'):
     """
     Geoprocessing tool that exports feature classes for the footprint, boundary, or seamline of a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         optional. Default value: FOOTPRINT. Value choices: FOOTPRINT,BOUNDARY,SEAMLINE,LEVEL
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'geometry_type': ['geometry_type', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'ExportMosaicDatasetGeometry', inputs, in_db, out_db)

          
def export_mosaic_dataset_items(mosaic_dataset, out_folder, out_base_name=None, where_clause=None, format='TIFF', nodata_value=None, clip_type=None, template_dataset=None, cell_size=None):
     """
     Geoprocessing tool that creates a copy of your processed images within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_base_name                         optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_type                             optional. Default value: NONE. Value choices: NONE,EXTENT,FEATURE_CLASS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                optional. Default value: TIFF. Value choices: TIFF,BMP,ENVI,Esri BIL,Esri BIP,Esri BSQ,GIF,GRID,IMAGINE IMAGE,JP2,JPEG,PNG
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_folder': ['out_folder', 'required'], 'cell_size': ['cell_size', 'optional'], 'template_dataset': ['template_dataset', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'clip_type': ['clip_type', 'optional'], 'format': ['format', 'optional'], 'out_base_name': ['out_base_name', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ExportMosaicDatasetItems', inputs, in_db, out_db)

          
def remove_field_conflict_filter(table, fields):
     """
     Geoprocessing tool for removing a field conflict filter to a geodatabase table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['table', 'required'], 'fields': ['fields', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveFieldConflictFilter', inputs, in_db, out_db)

          
def export_geodatabase_configuration_keywords(input_database):
     """
     Geoprocessing tool that exports the configuration keywords, parameters, and values from the specified enterprise geodatabase to an editable file.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required']}
     out_db = {'file': ['out_file', 'required', None, None]}
     return _execute_tool('management', 'ExportGeodatabaseConfigurationKeywords', inputs, in_db, out_db)

          
def import_geodatabase_configuration_keywords(input_database, file):
     """
     Geoprocessing tool that allows you to define data storage parameters for an enterprise geodatabase by importing a file containing storage keywords and parameters.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     file                                  required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required'], 'file': ['in_file', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportGeodatabaseConfigurationKeywords', inputs, in_db, out_db)

          
def alter_field(table, field, new_field_name=None, new_field_alias=None, field_type='LONG', field_length=None, field_is_nullable='true', clear_field_alias='false'):
     """
     Geoprocessing tool  to alter the field properties of geodatabase tables and feature classes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_length                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_field_alias                     optional. Default value: false. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_field_alias                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_field_name                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_type                            optional. Default value: LONG. Value choices: TEXT,FLOAT,DOUBLE,SHORT,LONG,DATE,BLOB,RASTER,GUID
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_nullable                     optional. Default value: true. Value choices: NULLABLE,NON_NULLABLE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_length': ['field_length', 'optional'], 'clear_field_alias': ['clear_field_alias', 'optional'], 'new_field_alias': ['new_field_alias', 'optional'], 'table': ['in_table', 'required'], 'field': ['field', 'required'], 'new_field_name': ['new_field_name', 'optional'], 'field_type': ['field_type', 'optional'], 'field_is_nullable': ['field_is_nullable', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterField', inputs, in_db, out_db)

          
def geodetic_densify(features, geodetic_type, distance='50 Kilometers'):
     """
     Geoprocessing tool that replaces segments with densified approximation of geodetic curves.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geodetic_type                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance                              optional. Default value: 50 Kilometers. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'distance': ['distance', 'optional'], 'geodetic_type': ['geodetic_type', 'required'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'GeodeticDensify', inputs, in_db, out_db)

          
def configure_geodatabase_log_file_tables(input_database, log_file_type, log_file_pool_size=None, use_tempdb='false'):
     """
     Geoprocessing tool that allows you to alter the type of log file tables used by an enterprise geodatabase to maintain lists of records cached by ArcGIS.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     log_file_type                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     log_file_pool_size                    optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_tempdb                            optional. Default value: false. Value choices: USE_TEMBDB,NOT_USE_TEMBDB
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'log_file_pool_size': ['log_file_pool_size', 'optional'], 'use_tempdb': ['use_tempdb', 'optional'], 'input_database': ['input_database', 'required'], 'log_file_type': ['log_file_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConfigureGeodatabaseLogFileTables', inputs, in_db, out_db)

          
def delete_schema_geodatabase(input_database):
     """
     Geoprocessing tool that deletes a user-schema geodatabase from a geodatabase in Oracle.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteSchemaGeodatabase', inputs, in_db, out_db)

          
def diagnose_version_tables(input_database, target_version=None, input_tables=None):
     """
     Geoprocessing tool to identify inconsistencies in the delta (A and D) tables of a versioned geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_tables                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_tables': ['input_tables', 'optional'], 'input_database': ['input_database', 'required'], 'target_version': ['target_version', 'optional']}
     out_db = {'log': ['out_log', 'required', None, None]}
     return _execute_tool('management', 'DiagnoseVersionTables', inputs, in_db, out_db)

          
def repair_version_tables(input_database, target_version=None, input_tables=None):
     """
     Geoprocessing tool to repair inconsistencies in the delta (A and D) tables of a versioned geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_tables                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_tables': ['input_tables', 'optional'], 'input_database': ['input_database', 'required'], 'target_version': ['target_version', 'optional']}
     out_db = {'log': ['out_log', 'required', None, None]}
     return _execute_tool('management', 'RepairVersionTables', inputs, in_db, out_db)

          
def analyze_tools_for_pro(input):
     """
     Geoprocessing tool that analyzes Python scripts and custom geoprocessing tools for functionality that is not supported in ArcGIS Pro.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input                                 required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input': ['input', 'required']}
     out_db = {'report': ['report', 'optional', None, None]}
     return _execute_tool('management', 'AnalyzeToolsForPro', inputs, in_db, out_db)

          
def export_topology_errors(topology, out_path, out_basename):
     """
     Geoprocessing tool to export errors and exceptions from a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_path                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     topology                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_basename                          required.
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_path': ['out_path', 'required'], 'topology': ['in_topology', 'required'], 'out_basename': ['out_basename', 'required']}
     out_db = {}
     return _execute_tool('management', 'ExportTopologyErrors', inputs, in_db, out_db)

          
def generate_raster_from_raster_function(raster_function, raster_function_arguments=None, raster_properties=None, format=None):
     """
     Geoprocessing tool that uses raster functions to process raster datasets and write an output.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_function                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                optional. Default value: None. Value choices: TIFF,IMAGINE Image,Esri Grid,CRF,MRF
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_function_arguments             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_properties                     optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'format': ['format', 'optional'], 'raster_function': ['raster_function', 'required'], 'raster_function_arguments': ['raster_function_arguments', 'optional'], 'raster_properties': ['raster_properties', 'optional']}
     out_db = {'raster_dataset': ['out_raster_dataset', 'required', None, None]}
     return _execute_tool('management', 'GenerateRasterFromRasterFunction', inputs, in_db, out_db)

          
def generate_tessellation(extent, shape_type='HEXAGON', size=None, spatial_reference=None):
     """
     Geoprocessing tool that generates a feature class of a  tessellated grid of regular polygons to cover a given extent. The shapes can either be triangles, squares, or hexagons.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shape_type                            optional. Default value: HEXAGON. Value choices: SQUARE,TRIANGLE,HEXAGON
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     size                                  optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'shape_type': ['Shape_Type', 'optional'], 'spatial_reference': ['Spatial_Reference', 'optional'], 'extent': ['Extent', 'required'], 'size': ['Size', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'GenerateTessellation', inputs, in_db, out_db)

          
def create_fishnet(origcoord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, corner_coord=None, labels='true', template=None, geometry_type='POLYLINE'):
     """
     Geoprocessing tool that creates a fishnet of rectangular cells.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_axis_coord                          required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_height                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_width                            required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origcoord                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_columns                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_rows                           required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         optional. Default value: POLYLINE. Value choices: POLYLINE,POLYGON
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     labels                                optional. Default value: true. Value choices: LABELS,NO_LABELS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     corner_coord                          optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'y_axis_coord': ['y_axis_coord', 'required'], 'cell_height': ['cell_height', 'required'], 'cell_width': ['cell_width', 'required'], 'labels': ['labels', 'optional'], 'origcoord': ['origin_coord', 'required'], 'geometry_type': ['geometry_type', 'optional'], 'number_columns': ['number_columns', 'required'], 'number_rows': ['number_rows', 'required'], 'corner_coord': ['corner_coord', 'optional'], 'template': ['template', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'CreateFishnet', inputs, in_db, out_db)

          
def create_random_points(out_path, out_name, constraining_feature_class=None, constraining_extent=None, number_of_points_or_field='100', minimum_allowed_distance='0 Unknown', create_multipoint_output='false', multipoint_size='10'):
     """
     Geoprocessing tool that creates a specified number of random points in an extent window, inside polygon features, on point features, or along line features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_points_or_field             optional. Default value: 100. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     constraining_extent                   optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     constraining_feature_class            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_allowed_distance              optional. Default value: 0 Unknown. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     create_multipoint_output              optional. Default value: false. Value choices: MULTIPOINT,POINT
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     multipoint_size                       optional. Default value: 10. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_path': ['out_path', 'required'], 'constraining_extent': ['constraining_extent', 'optional'], 'constraining_feature_class': ['constraining_feature_class', 'optional'], 'out_name': ['out_name', 'required'], 'minimum_allowed_distance': ['minimum_allowed_distance', 'optional'], 'create_multipoint_output': ['create_multipoint_output', 'optional'], 'number_of_points_or_field': ['number_of_points_or_field', 'optional'], 'multipoint_size': ['multipoint_size', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomPoints', inputs, in_db, out_db)

          
def generate_points_along_lines(input_features, point_placement, distance=None, percentage=None, include_end_points=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_features                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     point_placement                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_end_points                    optional. Default value: None. Value choices: END_POINTS,NO_END_POINTS
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance                              optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_features': ['Input_Features', 'required'], 'include_end_points': ['Include_End_Points', 'optional'], 'distance': ['Distance', 'optional'], 'point_placement': ['Point_Placement', 'required'], 'percentage': ['Percentage', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'GeneratePointsAlongLines', inputs, in_db, out_db)

          
def append_control_points(master_control_points, input_control_points, z_field=None, tag_field=None, dem=None, xy_accuracy=None, z_accuracy=None):
     """
     Geoprocessing tool that combines tie points and control points.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_control_points                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     master_control_points                 required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dem                                   optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_accuracy                            optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_field                               optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tag_field                             optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_accuracy                           optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dem': ['in_dem', 'optional'], 'z_accuracy': ['in_z_accuracy', 'optional'], 'z_field': ['in_z_field', 'optional'], 'xy_accuracy': ['in_xy_accuracy', 'optional'], 'input_control_points': ['in_input_control_points', 'required'], 'tag_field': ['in_tag_field', 'optional'], 'master_control_points': ['in_master_control_points', 'required']}
     out_db = {}
     return _execute_tool('management', 'AppendControlPoints', inputs, in_db, out_db)

          
def apply_block_adjustment(mosaic_dataset, adjustment_operation, input_solution_table=None, pan_to_ms_scaling_factor=None, dem=None, zoffset=None, control_point_table=None, adjust_footprints='false'):
     """
     Geoprocessing tool that applies the geographic adjustments to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     adjustment_operation                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_solution_table                  optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_point_table                   optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pan_to_ms_scaling_factor              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     zoffset                               optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dem                                   optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     adjust_footprints                     optional. Default value: false. Value choices: ADJUST_FOOTPRINTS,NO_ADJUST_FOOTPRINTS
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_solution_table': ['input_solution_table', 'optional'], 'control_point_table': ['control_point_table', 'optional'], 'pan_to_ms_scaling_factor': ['pan_to_ms_scaling_factor', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'dem': ['DEM', 'optional'], 'zoffset': ['zoffset', 'optional'], 'adjust_footprints': ['adjust_footprints', 'optional'], 'adjustment_operation': ['adjustment_operation', 'required']}
     out_db = {}
     return _execute_tool('management', 'ApplyBlockAdjustment', inputs, in_db, out_db)

          
def compute_block_adjustment(mosaic_dataset, control_points, transformation_type, maximum_residual_value='5', adjustment_options=None, location_accuracy='MEDIUM'):
     """
     Geoprocessing tool that computes the adjustments to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_points                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     transformation_type                   required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_residual_value                optional. Default value: 5. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     adjustment_options                    optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     optional. Default value: MEDIUM. Value choices: LOW,MEDIUM,HIGH
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'adjustment_options': ['adjustment_options', 'optional'], 'location_accuracy': ['location_accuracy', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'transformation_type': ['transformation_type', 'required'], 'maximum_residual_value': ['maximum_residual_value', 'optional'], 'control_points': ['in_control_points', 'required']}
     out_db = {'solution_point_table': ['out_solution_point_table', 'optional', None, None], 'quality_table': ['out_quality_table', 'optional', None, None], 'solution_table': ['out_solution_table', 'required', None, None]}
     return _execute_tool('management', 'ComputeBlockAdjustment', inputs, in_db, out_db)

          
def compute_camera_model(mosaic_dataset, gps_accuracy='HIGH', estimate='true', refine='true', apply_adjustment='true', maximum_residual='5', initial_tiepoint_resolution='8', maximum_overlap=None, minimum_coverage='0.2', remove='false', control_points=None, options=None):
     """
     Geoprocessing tool that automatically constructs and refines a camera model for aerial images and, in particular, UAV and UAS images, where the exterior and interior camera models are coarse or undefined.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_coverage                      optional. Default value: 0.2. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     refine                                optional. Default value: true. Value choices: REFINE,NO_REFINE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     options                               optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gps_accuracy                          optional. Default value: HIGH. Value choices: HIGH,MEDIUM,LOW,VERY_LOW
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     initial_tiepoint_resolution           optional. Default value: 8. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_residual                      optional. Default value: 5. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate                              optional. Default value: true. Value choices: ESTIMATE,NO_ESTIMATE
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_overlap                       optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     apply_adjustment                      optional. Default value: true. Value choices: APPLY,NO_APPLY
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_points                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     remove                                optional. Default value: false. Value choices: REMOVE,NO_REMOVE
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'refine': ['refine', 'optional'], 'gps_accuracy': ['gps_accuracy', 'optional'], 'minimum_coverage': ['minimum_coverage', 'optional'], 'maximum_overlap': ['maximum_overlap', 'optional'], 'maximum_residual': ['maximum_residual', 'optional'], 'options': ['options', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'initial_tiepoint_resolution': ['initial_tiepoint_resolution', 'optional'], 'estimate': ['estimate', 'optional'], 'control_points': ['in_control_points', 'optional'], 'apply_adjustment': ['apply_adjustment', 'optional'], 'remove': ['remove', 'optional']}
     out_db = {'solution_point_table': ['out_solution_point_table', 'optional', None, None], 'control_points': ['out_control_points', 'optional', None, None], 'solution_table': ['out_solution_table', 'optional', None, None], 'dsm': ['out_dsm', 'optional', None, None], 'flight_path': ['out_flight_path', 'optional', None, None]}
     return _execute_tool('management', 'ComputeCameraModel', inputs, in_db, out_db)

          
def compute_control_points(mosaic_dataset, reference_images, similarity='HIGH', density='MEDIUM', distribution='RANDOM', area_of_interest=None, location_accuracy='MEDIUM'):
     """
     Geoprocessing tool that computes control points for your mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     reference_images                      required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     similarity                            optional. Default value: HIGH. Value choices: LOW,MEDIUM,HIGH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          optional. Default value: RANDOM. Value choices: RANDOM,REGULAR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     optional. Default value: MEDIUM. Value choices: LOW,MEDIUM,HIGH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     density                               optional. Default value: MEDIUM. Value choices: LOW,MEDIUM,HIGH
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'location_accuracy': ['location_accuracy', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'density': ['density', 'optional'], 'reference_images': ['in_reference_images', 'required'], 'area_of_interest': ['area_of_interest', 'optional'], 'similarity': ['similarity', 'optional'], 'distribution': ['distribution', 'optional']}
     out_db = {'image_feature_points': ['out_image_feature_points', 'optional', None, None], 'control_points': ['out_control_points', 'required', None, None]}
     return _execute_tool('management', 'ComputeControlPoints', inputs, in_db, out_db)

          
def compute_tie_points(mosaic_dataset, similarity='MEDIUM', mask_dataset=None, density='MEDIUM', distribution='RANDOM', location_accuracy='MEDIUM'):
     """
     Geoprocessing tool that computes the tie points for the  items within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     similarity                            optional. Default value: MEDIUM. Value choices: LOW,MEDIUM,HIGH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     density                               optional. Default value: MEDIUM. Value choices: LOW,MEDIUM,HIGH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          optional. Default value: RANDOM. Value choices: RANDOM,REGULAR
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     optional. Default value: MEDIUM. Value choices: LOW,MEDIUM,HIGH
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mask_dataset                          optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mask_dataset': ['in_mask_dataset', 'optional'], 'location_accuracy': ['location_accuracy', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'density': ['density', 'optional'], 'similarity': ['similarity', 'optional'], 'distribution': ['distribution', 'optional']}
     out_db = {'control_points': ['out_control_points', 'required', None, None], 'image_features': ['out_image_features', 'optional', None, None]}
     return _execute_tool('management', 'ComputeTiePoints', inputs, in_db, out_db)

          
def build_stereo_model(mosaic_dataset, minimum_angle='10', maximum_angle='70', minimum_overlap='0.5', maximum_diff_op=None, maximum_diff_gsd='2'):
     """
     Geoprocessing tool that generates a stereo model on imagery in a  mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_overlap                       optional. Default value: 0.5. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_angle                         optional. Default value: 70. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_gsd                      optional. Default value: 2. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_angle                         optional. Default value: 10. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_op                       optional. Default value: None. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'minimum_overlap': ['minimum_overlap', 'optional'], 'maximum_angle': ['maximum_angle', 'optional'], 'maximum_diff_gsd': ['maximum_diff_GSD', 'optional'], 'minimum_angle': ['minimum_angle', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildStereoModel', inputs, in_db, out_db)

          
def generate_point_cloud(mosaic_dataset, matching_method, object_size='50', ground_spacing=None, minimum_pairs='2', minimum_area='0.6', minimum_adjustment_quality='0.2', maximum_diff_gsd='2', maximum_diff_op='8'):
     """
     Geoprocessing tool that generates a 3D point cloud from stereo images.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     matching_method                       required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     object_size                           optional. Default value: 50. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ground_spacing                        optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_op                       optional. Default value: 8. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_gsd                      optional. Default value: 2. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_adjustment_quality            optional. Default value: 0.2. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_pairs                         optional. Default value: 2. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_area                          optional. Default value: 0.6. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'object_size': ['object_size', 'optional'], 'matching_method': ['matching_method', 'required'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'ground_spacing': ['ground_spacing', 'optional'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'maximum_diff_gsd': ['maximum_diff_gsd', 'optional'], 'minimum_adjustment_quality': ['minimum_adjustment_quality', 'optional'], 'minimum_pairs': ['minimum_pairs', 'optional'], 'minimum_area': ['minimum_area', 'optional']}
     out_db = {'folder': ['out_folder', 'required', None, None], 'base_name': ['out_base_name', 'required', None, None]}
     return _execute_tool('management', 'GeneratePointCloud', inputs, in_db, out_db)

          
def interpolate_from_point_cloud(container, cell_size, interpolation_method, smooth_method, surface_type='DTM', fill_dem=None):
     """
     Geoprocessing tool that interpolates a digital surface model (DSM) or digital elevation model (DEM) from a point cloud.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     smooth_method                         required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     interpolation_method                  required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     container                             required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fill_dem                              optional. Default value: None. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     surface_type                          optional. Default value: DTM. Value choices: DTM,DSM
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'required'], 'smooth_method': ['smooth_method', 'required'], 'interpolation_method': ['interpolation_method', 'required'], 'fill_dem': ['fill_dem', 'optional'], 'container': ['in_container', 'required'], 'surface_type': ['surface_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'InterpolateFromPointCloud', inputs, in_db, out_db)

          
def compute_mosaic_candidates(mosaic_dataset, maximum_overlap='0.6', maximum_area_loss='0.05'):
     """
     Geoprocessing tool that finds the image candidates in a mosaic dataset that best represents the mosaic area, and will be used to generate an orthomosaic.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        required.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_area_loss                     optional. Default value: 0.05. Value choices: 
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_overlap                       optional. Default value: 0.6. Value choices: 
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'maximum_area_loss': ['maximum_area_loss', 'optional'], 'maximum_overlap': ['maximum_overlap', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'ComputeMosaicCandidates', inputs, in_db, out_db)

          