import os
import sys
import uuid
import random
import string
import arcpy
from collections import namedtuple
from arcgis.features import SpatialDataFrame, FeatureLayer
from arcgis.geometry import SpatialReference
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
     import arcgis
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
               fc = inputs[k].to_featureclass(out_location=arcgis.env.scratchgdb,
                                              out_name=random.choice(string.ascii_letters) + uuid.uuid4().hex[:5])
               inputs[k] = fc
          elif isinstance(inputs[k], pd.DataFrame):
               t = random.choice(string.ascii_letters) + uuid.uuid4().hex[:5] + '.csv'
               tbl = os.path.join(arcgis.env.scratchfolder, t)
               v.to_csv(t)
               inputs[k] = t
          elif isinstance(inputs[k], FeatureLayer):
               inputs[k] = inputs[k].query().df.to_featureclass(out_location=arcgis.env.scratchgdb,
                                                                out_name=random.choice(string.ascii_letters) + uuid.uuid4().hex[:5])
          elif isinstance(inputs[k], SpatialReference):
               inputs[k] = inputs[k].as_arcpy
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
     rows                                  Required Table View. Input Rows
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
     rows                                  Required Table View or Raster Layer. Input Rows
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional String. Configuration Keyword. Default value: none
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
     features                              Required Feature Layer or Raster Catalog Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional String. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        Optional Double. Output Spatial Grid 2. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        Optional Double. Output Spatial Grid 3. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        Optional Double. Output Spatial Grid 1. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'features': ['in_features', 'required'], 'spatial_grid_1': ['spatial_grid_1', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'CopyFeatures', inputs, in_db, out_db)


def dissolve(features, dissolve_field=None, statistics_fields=None, multi_part='true', unsplit_lines='false'):
     """
     Geoprocessing tool used to aggregate features based on specified attributes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     unsplit_lines                         Optional Boolean. Unsplit lines. Default value: false. Value choices: unsplit_lines, dissolve_lines
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics_fields                     Optional Value Table. Statistics Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        Optional Multiple Value. Dissolve_Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     multi_part                            Optional Boolean. Create multipart features. Default value: true. Value choices: multi_part, single_part
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'statistics_fields': ['statistics_fields', 'optional'], 'unsplit_lines': ['unsplit_lines', 'optional'], 'features': ['in_features', 'required'], 'dissolve_field': ['dissolve_field', 'optional'], 'multi_part': ['multi_part', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'Dissolve', inputs, in_db, out_db)


def make_feature_layer(features, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a feature layer from an input feature class or layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Optional Workspace or Feature Dataset. Workspace or Feature Dataset. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_info                            Optional Field Info. Field Info. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Expression. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'workspace': ['workspace', 'optional'], 'field_info': ['field_info', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeFeatureLayer', inputs, in_db, out_db)


def save_to_layer_file(layer, is_relative_path=None, version='current'):
     """
     Geoprocessing tool that creates a layer file (.lyrx) that references geographic data stored on disk.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer                                 Required Layer. Input Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     is_relative_path                      Optional Boolean. Store Relative Path. Default value: none. Value choices: relative, absolute
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               Optional String. Layer Version. Default value: current. Value choices: current, 10.4, 10.3, 10.2, 10.1, 10, 9.3, 9.2, 9.1, 9.0, 8.3
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'is_relative_path': ['is_relative_path', 'optional'], 'version': ['version', 'optional'], 'layer': ['in_layer', 'required']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'SaveToLayerFile', inputs, in_db, out_db)


def add_join(layer_or_view, field, jotable, jofield, jotype='true'):
     """
     Geoprocessing tool that  joins a layer to another layer or table (where layer is a feature layer, table view, or raster layer with raster attribute table) based on a common field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer_or_view                         Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Layer Name or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jotable                               Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Join Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               Required Field. Output Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jotype                                Optional Boolean. Keep All Target Features. Default value: true. Value choices: keep_all, keep_common
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'layer_or_view': ['in_layer_or_view', 'required'], 'jotable': ['join_table', 'required'], 'jotype': ['join_type', 'optional'], 'field': ['in_field', 'required'], 'jofield': ['join_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddJoin', inputs, in_db, out_db)


def remove_join(layer_or_view, joname=None):
     """
     Geoprocessing tool that removes a join from a feature layer or table view.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer_or_view                         Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Layer Name or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joname                                Optional String. Join. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'layer_or_view': ['in_layer_or_view', 'required'], 'joname': ['join_name', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RemoveJoin', inputs, in_db, out_db)


def copy(data, data_type=None):
     """
     Geoprocessing tool that duplicates all types of geodata as well as most other dataset types.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data                                  Required Data Element. Input Data
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional String. Data type. Default value: none
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
     data                                  Required Data Element or Layer or Table View or Graph. Input Data Element
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional String. Data type. Default value: none
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
     data                                  Required Data Element. Input Data Element
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional String. Data type. Default value: none
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
     out_name                              Required String. Folder Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder_path                       Required Folder. Folder Location
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
     out_dataset_path                      Required Workspace. Output Geodatabase
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required String. Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Coordinate System. Default value: none
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
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     value_field                           Required Field. Value Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                Required Multiple Value. Input Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     pivot_field                           Required Field. Pivot Field
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'value_field': ['value_field', 'required'], 'fields': ['fields', 'required'], 'pivot_field': ['pivot_field', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'PivotTable', inputs, in_db, out_db)


def create_feature_class(out_path, out_name, geometry_type='polygon', template=None, has_m='disabled', has_z='disabled', spatial_reference=None, config_keyword=None, spatial_grid_1='1000', spatial_grid_2='0', spatial_grid_3='0'):
     """
     Geoprocessing tool that creates a feature class, either in an ArcSDE, file geodatabase, or personal geodatabase, or as a shapefile in a folder.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              Required String. Feature Class Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              Required Workspace or Feature Dataset. Feature Class Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     has_m                                 Optional String. Has M. Default value: disabled. Value choices: disabled, same_as_template, enabled
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        Optional Double. Output Spatial Grid 2. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     has_z                                 Optional String. Has Z. Default value: disabled. Value choices: disabled, same_as_template, enabled
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional String. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        Optional Double. Output Spatial Grid 3. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional String. Geometry Type. Default value: polygon. Value choices: point, multipoint, polygon, polyline, multipatch
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional Multiple Value. Template Feature Class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        Optional Double. Output Spatial Grid 1. Default value: 1000
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'has_m': ['has_m', 'optional'], 'out_name': ['out_name', 'required'], 'geometry_type': ['geometry_type', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'has_z': ['has_z', 'optional'], 'config_keyword': ['config_keyword', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional'], 'out_path': ['out_path', 'required'], 'template': ['template', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'spatial_grid_2': ['spatial_grid_2', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFeatureClass', inputs, in_db, out_db)


def create_table(out_path, out_name, template=None, config_keyword=None):
     """
     Geoprocessing tool that creates a geodatabase table, an INFO table, or dBASE table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              Required String. Table Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              Required Workspace. Table Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional String. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional Multiple Value. Template Table Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'optional'], 'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateTable', inputs, in_db, out_db)


def make_table_view(table, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a table view from an input table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View or Raster Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Optional Workspace. Output Workspace. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_info                            Optional Field Info. Field Info. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Expression. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'workspace': ['workspace', 'optional'], 'field_info': ['field_info', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'view': ['out_view', 'required', None, None]}
     return _execute_tool('management', 'MakeTableView', inputs, in_db, out_db)


def add_spatial_index(features, spatial_grid_1='0', spatial_grid_2='0', spatial_grid_3='0'):
     """
     Geoprocessing tool that adds a spatial index to a feature class

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer or Raster Catalog Layer or Mosaic Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        Optional Double. Spatial Grid 2. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        Optional Double. Spatial Grid 3. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        Optional Double. Spatial Grid 1. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'spatial_grid_3': ['spatial_grid_3', 'optional'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'features': ['in_features', 'required'], 'spatial_grid_1': ['spatial_grid_1', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddSpatialIndex', inputs, in_db, out_db)


def remove_spatial_index(features):
     """
     Geoprocessing tool that deletes the spatial index from a shapefile, file geodatabase feature class, or enterprise geodatabase feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer or Raster Catalog Layer or Mosaic Layer. Input Features
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveSpatialIndex', inputs, in_db, out_db)


def create_domain(workspace, domaname, field_type, domadescription=None, domatype='coded', split_policy='default', merge_policy='default'):
     """
     Geoprocessing tool that creates an attribute domain in the specified workspace.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_type                            Required String. Field Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domadescription                       Optional String. Domain Description. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     merge_policy                          Optional String. Merge Policy. Default value: default. Value choices: default, sum_values, area_weighted
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domatype                              Optional String. Domain Type. Default value: coded. Value choices: coded, range
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_policy                          Optional String. Split Policy. Default value: default. Value choices: default, duplicate, geometry_ratio
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'merge_policy': ['merge_policy', 'optional'], 'field_type': ['field_type', 'required'], 'workspace': ['in_workspace', 'required'], 'domadescription': ['domain_description', 'optional'], 'domatype': ['domain_type', 'optional'], 'split_policy': ['split_policy', 'optional'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDomain', inputs, in_db, out_db)


def delete_domain(workspace, domaname):
     """
     Geoprocessing tool to delete a domain from a workspace.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteDomain', inputs, in_db, out_db)


def add_coded_value_to_domain(workspace, domaname, code, code_description):
     """
     Geoprocessing tool that adds a value to a domain's coded value list.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code                                  Required String. Code Value
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code_description                      Required String. Code Description
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'code': ['code', 'required'], 'workspace': ['in_workspace', 'required'], 'code_description': ['code_description', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddCodedValueToDomain', inputs, in_db, out_db)


def delete_coded_value_from_domain(workspace, domaname, code):
     """
     Geoprocessing tool that removes a value from a coded value domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code                                  Required Multiple Value. Code Value
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'code': ['code', 'required'], 'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteCodedValueFromDomain', inputs, in_db, out_db)


def set_value_for_range_domain(workspace, domaname, mvalue, max_value):
     """
     Geoprocessing tool that sets the minimun and maximum values for an existing Range domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_value                             Required String. Maximum Value
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mvalue                                Required String. Minimum Value
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'max_value': ['max_value', 'required'], 'mvalue': ['min_value', 'required'], 'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetValueForRangeDomain', inputs, in_db, out_db)


def assign_domain_to_field(table, field_name, domaname, subtype_code=None):
     """
     Geoprocessing tool that sets the domain for a particular field and, optionally, for a subtype.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          Optional Multiple Value. Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'domaname': ['domain_name', 'required'], 'field_name': ['field_name', 'required'], 'subtype_code': ['subtype_code', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AssignDomainToField', inputs, in_db, out_db)


def remove_domain_from_field(table, field_name, subtype_code=None):
     """
     Geoprocessing tool that removes an attribute domain association from a feature class or table field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          Optional Multiple Value. Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'subtype_code': ['subtype_code', 'optional'], 'field_name': ['field_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveDomainFromField', inputs, in_db, out_db)


def table_to_domain(table, code_field, description_field, workspace, domaname, domadescription=None, update_option='append'):
     """
     Geoprocessing tool that creates or updates a coded value domain with values from a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code_field                            Required Field. Code Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     description_field                     Required Field. Description Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domadescription                       Optional String. Domain Description. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_option                         Optional String. Update Option. Default value: append. Value choices: append, replace
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'domadescription': ['domain_description', 'optional'], 'update_option': ['update_option', 'optional'], 'workspace': ['in_workspace', 'required'], 'description_field': ['description_field', 'required'], 'table': ['in_table', 'required'], 'domaname': ['domain_name', 'required'], 'code_field': ['code_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'TableToDomain', inputs, in_db, out_db)


def domain_to_table(workspace, domaname, code_field, description_field, configuration_keyword=None):
     """
     Geoprocessing tool that creates a table from an attribute domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code_field                            Required String. Code Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     description_field                     Required String. Field Description
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     configuration_keyword                 Optional String. Configuration Keyword. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'configuration_keyword': ['configuration_keyword', 'optional'], 'code_field': ['code_field', 'required'], 'workspace': ['in_workspace', 'required'], 'description_field': ['description_field', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'DomainToTable', inputs, in_db, out_db)


def select_layer_by_attribute(layer_or_view, selection_type='new_selection', where_clause=None):
     """
     Geoprocessing tool that adds, updates, or removes a selection on a layer or table view based on an attribute query.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer_or_view                         Required Table View or Raster Layer or Mosaic Layer. Layer Name or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_type                        Optional String. Selection type. Default value: new_selection. Value choices: new_selection, add_to_selection, remove_from_selection, subset_selection, switch_selection, clear_selection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Expression. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'layer_or_view': ['in_layer_or_view', 'required'], 'selection_type': ['selection_type', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SelectLayerByAttribute', inputs, in_db, out_db)


def select_layer_by_location(layer, overlap_type='intersect', select_features=None, search_distance=None, selection_type='new_selection', invert_spatial_relationship='false'):
     """
     Geoprocessing tool that selects features in a layer based on a spatial relationship to features in another layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer                                 Required Feature Layer or Raster Catalog Layer or Mosaic Layer. Input Feature Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     invert_spatial_relationship           Optional Boolean. Invert Spatial Relationship. Default value: false. Value choices: invert, not_invert
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     select_features                       Optional Feature Layer. Selecting Features. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_type                        Optional String. Selection type. Default value: new_selection. Value choices: new_selection, add_to_selection, remove_from_selection, subset_selection, switch_selection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_distance                       Optional Linear unit. Search Distance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overlap_type                          Optional String. Relationship. Default value: intersect. Value choices: intersect, intersect_3d, within_a_distance_geodesic, within_a_distance, within_a_distance_3d, contains, completely_contains, contains_clementini, within, completely_within, within_clementini, are_identical_to, boundary_touches, share_a_line_segment_with, crossed_by_the_outline_of, have_their_center_in
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'select_features': ['select_features', 'optional'], 'layer': ['in_layer', 'required'], 'invert_spatial_relationship': ['invert_spatial_relationship', 'optional'], 'selection_type': ['selection_type', 'optional'], 'search_distance': ['search_distance', 'optional'], 'overlap_type': ['overlap_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SelectLayerByLocation', inputs, in_db, out_db)


def get_count(rows):
     """
     Geoprocessing tool that reports the number of rows of the input data.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows                                  Required Table View or Raster Layer. Input Rows
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'rows': ['in_rows', 'required']}
     out_db = {}
     return int(_execute_tool('management', 'GetCount', inputs, in_db, out_db))


def create_version(workspace, parent_version, version_name, access_permission='private'):
     """
     Geoprocessing tool to create a new version in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     parent_version                        Required String. Parent Version
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     version_name                          Required String. Version Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     access_permission                     Optional String. Access Permission. Default value: private. Value choices: private, public, protected
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'parent_version': ['parent_version', 'required'], 'version_name': ['version_name', 'required'], 'workspace': ['in_workspace', 'required'], 'access_permission': ['access_permission', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateVersion', inputs, in_db, out_db)


def delete_version(workspace, version_name):
     """
     Geoprocessing tool to delete a specific version from a geodatabase

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_name                          Required String. Version Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Database Connection
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
     dataset                               Required Table View or Feature Dataset. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_to_base                          Optional Boolean. Register the selected objects with the option to move edits to base. Default value: false. Value choices: edits_to_base, no_edits_to_base
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
     dataset                               Required Table View or Feature Dataset. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     keep_edit                             Optional Boolean. Do not run if there are edits in the delta tables. Default value: true. Value choices: keep_edit, no_keep_edit
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compress_default                      Optional Boolean. Compress all edits in the Default version into the base table. Default value: false. Value choices: compress_default, no_compress_default
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'compress_default': ['compress_default', 'optional'], 'keep_edit': ['keep_edit', 'optional']}
     out_db = {}
     return _execute_tool('management', 'UnregisterAsVersioned', inputs, in_db, out_db)


def alter_version(workspace, version, name=None, description=None, access='private'):
     """
     Geoprocessing tool that alters the database version's properties of name, description, and access permissions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               Required String. Input Version
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     access                                Optional String. Access Permission. Default value: private. Value choices: private, public, protected
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     name                                  Optional String. Version Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     description                           Optional String. Version Description. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'access': ['access', 'optional'], 'name': ['name', 'optional'], 'version': ['in_version', 'required'], 'description': ['description', 'optional'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'AlterVersion', inputs, in_db, out_db)


def table_to_relationship_class(origtable, destination_table, relationship_type, forward_label, backward_label, message_direction, cardinality, relationship_table, attribute_fields, origprimary_key, origforeign_key, destination_primary_key, destination_foreign_key):
     """
     Geoprocessing tool that creates an attributed relationship class from the Origin, Destination, and Relationship Tables.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_fields                      Required Multiple Value. Attribute Fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origprimary_key                       Required String. Origin Primary Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     relationship_type                     Required String. Relationship Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_foreign_key               Required String. Destination Foreign Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origtable                             Required Table View. Origin Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_table                     Required Table View. Destination Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     relationship_table                    Required Table View. Relationship Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     forward_label                         Required String. Forward Path Label
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     message_direction                     Required String. Message Direction
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origforeign_key                       Required String. Origin Foreign Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cardinality                           Required String. Cardinality
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_primary_key               Required String. Destination Primary Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     backward_label                        Required String. Backward Path Label
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'attribute_fields': ['attribute_fields', 'required'], 'origprimary_key': ['origin_primary_key', 'required'], 'relationship_type': ['relationship_type', 'required'], 'destination_foreign_key': ['destination_foreign_key', 'required'], 'origtable': ['origin_table', 'required'], 'destination_table': ['destination_table', 'required'], 'relationship_table': ['relationship_table', 'required'], 'forward_label': ['forward_label', 'required'], 'message_direction': ['message_direction', 'required'], 'origforeign_key': ['origin_foreign_key', 'required'], 'cardinality': ['cardinality', 'required'], 'destination_primary_key': ['destination_primary_key', 'required'], 'backward_label': ['backward_label', 'required']}
     out_db = {'relationship_class': ['out_relationship_class', 'required', None, None]}
     return _execute_tool('management', 'TableToRelationshipClass', inputs, in_db, out_db)


def feature_to_point(features, point_location='false'):
     """
     Geoprocessing tool that creates a representative point for each input feature.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_location                        Optional Boolean. Inside. Default value: false. Value choices: inside, centroid
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'point_location': ['point_location', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToPoint', inputs, in_db, out_db)


def feature_vertices_to_points(features, point_location='all'):
     """
     Geoprocessing tool that creates points from input feature vertices.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_location                        Optional String. Point Type. Default value: all. Value choices: all, mid, start, end, both_ends, dangle
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
     features                              Required Multiple Value. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attributes                            Optional Boolean. Preserve attributes. Default value: true. Value choices: attributes, no_attributes
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'attributes': ['attributes', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToLine', inputs, in_db, out_db)


def feature_to_polygon(features, cluster_tolerance=None, attributes='true', label_features=None):
     """
     Geoprocessing tool that creates polygons from areas enclosed by line or polygon features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Multiple Value. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     label_features                        Optional Feature Layer. Label Features. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attributes                            Optional Boolean. Preserve attributes. Default value: true. Value choices: attributes, no_attributes
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'label_features': ['label_features', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'attributes': ['attributes', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToPolygon', inputs, in_db, out_db)


def polygon_to_line(features, neighbor_option='true'):
     """
     Geoprocessing tool that creates a feature class containing lines converted from polygon boundaries with or without considering neighboring polygons.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     neighbor_option                       Optional Boolean. Identify and store polygon neighboring information. Default value: true. Value choices: identify_neighbors, ignore_neighbors
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'neighbor_option': ['neighbor_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'PolygonToLine', inputs, in_db, out_db)


def define_projection(dataset, coor_system):
     """
     Geoprocessing tool to record the coordinate system information for the specific input dataset or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Feature Layer or Geodataset. Input Dataset or Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     coor_system                           Required Coordinate System. Coordinate System
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
     features                              Required Feature Layer. Input Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ex_where_clause                       Optional SQL Expression. Exclusion Expression. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ex_features                           Optional Feature Layer. Exclusion Layer. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection                             Optional Boolean. Eliminating polygon by border. Default value: true. Value choices: length, area
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'ex_where_clause': ['ex_where_clause', 'optional'], 'features': ['in_features', 'required'], 'ex_features': ['ex_features', 'optional'], 'selection': ['selection', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'Eliminate', inputs, in_db, out_db)


def repair_geometry(features, delete_null='true'):
     """
     Geoprocessing tool that inspects the features for geometry problems, fixes the problems that are found, and then  prints a list of the problems that were fixed.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_null                           Optional Boolean. Delete Features with Null Geometry. Default value: true. Value choices: delete_null, keep_null
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
     dataset                               Required Feature Dataset. Input Feature Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required String. Output Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Double. Cluster Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'cluster_tolerance': ['in_cluster_tolerance', 'optional'], 'out_name': ['out_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateTopology', inputs, in_db, out_db)


def remove_feature_class_from_topology(topology, featureclass):
     """
     Geoprocessing tool to remove a feature class from participating in a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     topology                              Required Topology. Input Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     featureclass                          Required String. Feature Class to Remove
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
     topology                              Required Topology Layer. Input Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     featureclass                          Required Feature Layer. Input Feature class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     rule_type                             Required String. Rule Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype                               Optional String. Input Subtype. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     featureclass2                         Optional Feature Layer. Input Feature class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype2                              Optional String. Input Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'topology': ['in_topology', 'required'], 'subtype': ['subtype', 'optional'], 'featureclass2': ['in_featureclass2', 'optional'], 'subtype2': ['subtype2', 'optional'], 'featureclass': ['in_featureclass', 'required'], 'rule_type': ['rule_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddRuleToTopology', inputs, in_db, out_db)


def validate_topology(topology, visible_extent='false'):
     """
     Geoprocessing tool that validates a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     topology                              Required Topology Layer. Input Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     visible_extent                        Optional Boolean. Visible Extent. Default value: false. Value choices: visible_extent, full_extent
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
     topology                              Required Topology Layer. Input Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cluster_tolerance                     Required Double. Cluster Tolerance
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'topology': ['in_topology', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetClusterTolerance', inputs, in_db, out_db)


def make_query_table(table, key_field_option, key_field=None, field=None, where_clause=None):
     """
     Geoprocessing tool that applies an SQL query to a database and the results are represented in either a layer or a table view.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Multiple Value. Input Tables
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     key_field_option                      Required String. Key Field Options
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 Optional Value Table. Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     key_field                             Optional Multiple Value. Key Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Expression. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'field': ['in_field', 'optional'], 'where_clause': ['where_clause', 'optional'], 'key_field': ['in_key_field', 'optional'], 'key_field_option': ['in_key_field_option', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'MakeQueryTable', inputs, in_db, out_db)


def make_xy_event_layer(table, x_field, y_field, spatial_reference=None, z_field=None):
     """
     Geoprocessing tool that creates a new point feature layer based on x- and y-coordinates defined in a source table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. XY Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               Required Field. X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               Required Field. Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_field                               Optional Field. Z Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Spatial Reference. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['table', 'required'], 'z_field': ['in_z_field', 'optional'], 'x_field': ['in_x_field', 'required'], 'y_field': ['in_y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeXYEventLayer', inputs, in_db, out_db)


def make_raster_layer(raster, where_clause=None, envelope=None, band_index=None):
     """
     Geoprocessing tool that makes a temporary raster layer from a raster dataset that will be available to select as a variable while working in the same application's session.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Composite Geodataset. Input raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     envelope                              Optional Extent. Envelope. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional Value Table. Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Where clause. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'envelope': ['envelope', 'optional'], 'raster': ['in_raster', 'required'], 'band_index': ['band_index', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'rasterlayer': ['out_rasterlayer', 'required', None, None]}
     return _execute_tool('management', 'MakeRasterLayer', inputs, in_db, out_db)


def flip(raster):
     """
     Geoprocessing tool that reorients the raster by turning it over, from top to bottom, along the horizontal axis through the center of the raster.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Raster Layer or Mosaic Layer. Input Raster
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
     raster                                Required Raster Layer or Mosaic Layer. Input Raster
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Mirror', inputs, in_db, out_db)


def project_raster(raster, out_coor_system, resampling_type='nearest', cell_size=None, geographic_transform=None, registration_point=None, coor_system=None):
     """
     Geoprocessing tool that transforms the raster dataset from one projection to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Raster Layer or Mosaic Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_coor_system                       Required Coordinate System. Output Coordinate System
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional String. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geographic_transform                  Optional Multiple Value. Geographic Transformation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     registration_point                    Optional Point. Registration Point. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           Optional Coordinate System. Input Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional Cell Size XY. Output Cell Size. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required'], 'coor_system': ['in_coor_system', 'optional'], 'out_coor_system': ['out_coor_system', 'required'], 'cell_size': ['cell_size', 'optional'], 'registration_point': ['Registration_Point', 'optional'], 'geographic_transform': ['geographic_transform', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'ProjectRaster', inputs, in_db, out_db)


def rescale(raster, x_scale, y_scale):
     """
     Geoprocessing tool that resizes a raster by the specified x and y scale factors.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     x_scale                               Required Double. X Scale Factor
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                Required Raster Layer or Mosaic Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_scale                               Required Double. Y Scale Factor
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'x_scale': ['x_scale', 'required'], 'raster': ['in_raster', 'required'], 'y_scale': ['y_scale', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Rescale', inputs, in_db, out_db)


def shift(raster, x_value, y_value, snap_raster=None):
     """
     Geoprocessing tool that moves (slides) the raster to a new geographic location, based on x and y shift values.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Raster Layer or Mosaic Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_value                               Required Double. Shift X Coordinates by
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_value                               Required Double. Shift Y Coordinates by
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     snap_raster                           Optional Raster Layer. Input Snap Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'snap_raster': ['in_snap_raster', 'optional'], 'raster': ['in_raster', 'required'], 'x_value': ['x_value', 'required'], 'y_value': ['y_value', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Shift', inputs, in_db, out_db)


def warp(raster, source_control_points, target_control_points, transformation_type='polyorder1', resampling_type='nearest'):
     """
     Geoprocessing tool that performs a transformation on the raster based on the source and target control points using a polynomial transformation.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     source_control_points                 Required Multiple Value. Source Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                Required Raster Layer or Mosaic Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_control_points                 Required Multiple Value. Target Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional String. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   Optional String. Transformation Type. Default value: polyorder1. Value choices: polyorder0, polysimilarity, polyorder1, polyorder2, polyorder3, adjust, spline, projective
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'resampling_type': ['resampling_type', 'optional'], 'source_control_points': ['source_control_points', 'required'], 'raster': ['in_raster', 'required'], 'target_control_points': ['target_control_points', 'required'], 'transformation_type': ['transformation_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Warp', inputs, in_db, out_db)


def append(inputs, target, schema_type='test', field_mapping=None, subtype=None):
     """
     Geoprocessing tool that appends multiple input datasets into an existing target dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     inputs                                Required Multiple Value. Input Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target                                Required Table View or Raster Layer. Target Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype                               Optional String. Subtype. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mapping                         Optional Field Mappings. Field Map. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     schema_type                           Optional String. Schema Type. Default value: test. Value choices: test, no_test
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype': ['subtype', 'optional'], 'field_mapping': ['field_mapping', 'optional'], 'inputs': ['inputs', 'required'], 'target': ['target', 'required'], 'schema_type': ['schema_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Append', inputs, in_db, out_db)


def delete_features(features):
     """
     Geoprocessing tool used to remove features from a feature class or layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
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
     table                                 Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_type                            Required String. Field Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required String. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_nullable                     Optional Boolean. Field IsNullable. Default value: true. Value choices: nullable, non_nullable
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_alias                           Optional String. Field Alias. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_precision                       Optional Long. Field Precision. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_scale                           Optional Long. Field Scale. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_domain                          Optional String. Field Domain. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_required                     Optional Boolean. Field IsRequired. Default value: false. Value choices: required, non_required
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_length                          Optional Long. Field Length. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_length': ['field_length', 'optional'], 'field_is_nullable': ['field_is_nullable', 'optional'], 'field_type': ['field_type', 'required'], 'field_alias': ['field_alias', 'optional'], 'field_name': ['field_name', 'required'], 'table': ['in_table', 'required'], 'field_scale': ['field_scale', 'optional'], 'field_domain': ['field_domain', 'optional'], 'field_is_required': ['field_is_required', 'optional'], 'field_precision': ['field_precision', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddField', inputs, in_db, out_db)


def assign_default_to_field(table, field_name, default_value=None, subtype_code=None, clear_value='false'):
     """
     Geoprocessing tool used to create a default value for a specified field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_value                         Optional String. Default Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_value                           Optional Boolean. Clear Value. Default value: false
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          Optional Multiple Value. Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'default_value': ['default_value', 'optional'], 'clear_value': ['clear_value', 'optional'], 'subtype_code': ['subtype_code', 'optional'], 'field_name': ['field_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'AssignDefaultToField', inputs, in_db, out_db)


def calculate_field(table, field, expression, expression_type='vb', code_block=None):
     """
     Geoprocessing tool used to perform field calculations.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     expression                            Required SQL Expression. Expression
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code_block                            Optional String. Code Block. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     expression_type                       Optional String. Expression Type. Default value: vb. Value choices: vb, python, python_9.3
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'expression': ['expression', 'required'], 'field': ['field', 'required'], 'code_block': ['code_block', 'optional'], 'expression_type': ['expression_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateField', inputs, in_db, out_db)


def delete_field(table, drop_field):
     """
     Geoprocessing tool used to remove fields from a dataset

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     drop_field                            Required Multiple Value. Drop Field
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'drop_field': ['drop_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteField', inputs, in_db, out_db)


def multipart_to_singlepart(features):
     """
     Geoprocessing tool that creates singlepart features from multipart features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
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
     features                              Required Value Table. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional Linear unit. XY Tolerance. Default value: none
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
     inputs                                Required Multiple Value. Input Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mappings                        Optional Field Mappings. Field Map. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'inputs': ['inputs', 'required'], 'field_mappings': ['field_mappings', 'optional']}
     out_db = {'output': ['output', 'required', None, None]}
     return _execute_tool('management', 'Merge', inputs, in_db, out_db)


def feature_compare(base_features, test_features, sort_field, compare_type='all', ignore_options=None, xy_tolerance=None, m_tolerance='0', z_tolerance='0', attribute_tolerances=None, omit_field=None, continue_compare='false'):
     """
     Geoprocessing tool that compares two feature classes or layers and returns the comparison results. Feature Compare can report differences with geometry, tabular values, spatial reference, and field definitions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     base_features                         Required Feature Layer. Input Base Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_features                         Required Feature Layer. Input Test Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_field                            Required Value Table. Sort Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional Linear unit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_options                        Optional Multiple Value. Ignore Options. Default value: none. Value choices: ignore_m, ignore_z, ignore_pointid, ignore_extension_properties, ignore_subtypes, ignore_relationshipclasses, ignore_representationclasses, ignore_fieldalias
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          Optional String. Compare Type. Default value: all. Value choices: all, geometry_only, attributes_only, schema_only, spatial_reference_only
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            Optional Multiple Value. Omit Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     m_tolerance                           Optional Double. M Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  Optional Value Table. Attribute Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           Optional Double. Z Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional Boolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'xy_tolerance': ['xy_tolerance', 'optional'], 'omit_field': ['omit_field', 'optional'], 'sort_field': ['sort_field', 'required'], 'compare_type': ['compare_type', 'optional'], 'continue_compare': ['continue_compare', 'optional'], 'base_features': ['in_base_features', 'required'], 'test_features': ['in_test_features', 'required'], 'm_tolerance': ['m_tolerance', 'optional'], 'ignore_options': ['ignore_options', 'optional'], 'z_tolerance': ['z_tolerance', 'optional'], 'attribute_tolerances': ['attribute_tolerances', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'FeatureCompare', inputs, in_db, out_db)


def file_compare(base_file, test_file, file_type='ascii', continue_compare='false'):
     """
     Geoprocessing tool which compares two files and returns the comparison results. File Compare can report differences between two ASCII files or two binary files.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     test_file                             Required File. Input Test File
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     base_file                             Required File. Input Base File
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file_type                             Optional String. File Type. Default value: ascii. Value choices: ascii, binary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional Boolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'test_file': ['in_test_file', 'required'], 'base_file': ['in_base_file', 'required'], 'file_type': ['file_type', 'optional'], 'continue_compare': ['continue_compare', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'FileCompare', inputs, in_db, out_db)


def raster_compare(base_raster, test_raster, compare_type='raster_dataset', ignore_option=None, continue_compare='false', parameter_tolerances=None, attribute_tolerances=None, omit_field=None):
     """
     Geoprocessing tool that compares the properties of two raster datasets or two mosaic datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     base_raster                           Required Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Base Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_raster                           Required Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Test Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            Optional Multiple Value. Omit Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_option                         Optional Multiple Value. Ignore Options. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          Optional String. Compare Type. Default value: raster_dataset. Value choices: raster_dataset, gdb_raster_dataset, gdb_raster_catalog, mosaic_dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     parameter_tolerances                  Optional Value Table. Parameter Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  Optional Value Table. Attribute Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional Boolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'omit_field': ['omit_field', 'optional'], 'ignore_option': ['ignore_option', 'optional'], 'compare_type': ['compare_type', 'optional'], 'parameter_tolerances': ['parameter_tolerances', 'optional'], 'base_raster': ['in_base_raster', 'required'], 'test_raster': ['in_test_raster', 'required'], 'attribute_tolerances': ['attribute_tolerances', 'optional'], 'continue_compare': ['continue_compare', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'RasterCompare', inputs, in_db, out_db)


def table_compare(base_table, test_table, sort_field, compare_type='all', ignore_options=None, attribute_tolerances=None, omit_field=None, continue_compare='false'):
     """
     Geoprocessing tool compares two tables or table views and returns the comparison results.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     base_table                            Required Table View or Raster Layer. Input Base Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_field                            Required Value Table. Sort Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_table                            Required Table View or Raster Layer. Input Test Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            Optional Multiple Value. Omit Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_options                        Optional Multiple Value. Ignore Options. Default value: none. Value choices: ignore_extension_properties, ignore_subtypes, ignore_relationshipclasses, ignore_fieldalias
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional Boolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          Optional String. Compare Type. Default value: all. Value choices: all, attributes_only, schema_only
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  Optional Value Table. Attribute Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'ignore_options': ['ignore_options', 'optional'], 'compare_type': ['compare_type', 'optional'], 'test_table': ['in_test_table', 'required'], 'omit_field': ['omit_field', 'optional'], 'base_table': ['in_base_table', 'required'], 'continue_compare': ['continue_compare', 'optional'], 'sort_field': ['sort_field', 'required'], 'attribute_tolerances': ['attribute_tolerances', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'TableCompare', inputs, in_db, out_db)


def create_file_gdb(folder_path, name, version='current'):
     """
     Geoprocessing tool that creates a file geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     name                                  Required String. File GDB Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     folder_path                           Required Folder. File GDB Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               Optional String. File GDB Version. Default value: current. Value choices: current, 10.0, 9.3, 9.2
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'name': ['out_name', 'required'], 'folder_path': ['out_folder_path', 'required'], 'version': ['out_version', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFileGDB', inputs, in_db, out_db)


def compress(workspace):
     """
     Geoprocessing tool to compress an enterprise geodatabase

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Required Workspace. Input Database Connection
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
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     subtype_description                   Required String. Subtype Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     subtype_code                          Required Long. Subtype Code
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'subtype_description': ['subtype_description', 'required'], 'subtype_code': ['subtype_code', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddSubtype', inputs, in_db, out_db)


def remove_subtype(table, subtype_code):
     """
     Geoprocessing tool that removes a subtype from the input table using its code.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     subtype_code                          Required Multiple Value. Subtype Code
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'subtype_code': ['subtype_code', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveSubtype', inputs, in_db, out_db)


def set_default_subtype(table, subtype_code):
     """
     Geoprocessing tool that sets the default subtype value for the input table's subtype.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     subtype_code                          Required Long. Subtype Code
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'subtype_code': ['subtype_code', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetDefaultSubtype', inputs, in_db, out_db)


def set_subtype_field(table, field=None, clear_value='false'):
     """
     Geoprocessing tool that defines the field in the input table or feature class that stores the subtype codes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 Optional Field. Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_value                           Optional Boolean. Clear Value. Default value: false
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'field': ['field', 'optional'], 'clear_value': ['clear_value', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetSubtypeField', inputs, in_db, out_db)


def add_colormap(raster, template_raster=None, input_clr_file=None):
     """
     Geoprocessing tool that adds a color map to a raster dataset, if it does not already exist or replaces a color map with the one specified.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_clr_file                        Optional File. Input .clr or .act File. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_raster                       Optional Raster Layer. Input Template Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_clr_file': ['input_CLR_file', 'optional'], 'raster': ['in_raster', 'required'], 'template_raster': ['in_template_raster', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddColormap', inputs, in_db, out_db)


def build_raster_attribute_table(raster, overwrite='false'):
     """
     Geoprocessing tool that adds a raster attribute table to a raster dataset or updates an existing one.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overwrite                             Optional Boolean. Overwrite. Default value: false. Value choices: overwrite, none
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
     raster                                Required Raster Layer. Input Raster
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
     raster                                Required Raster Layer. Input Raster
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteRasterAttributeTable', inputs, in_db, out_db)


def build_pyramids(raster_dataset, pyramid_level=None, skip_first='false', resample_technique='nearest', compression_type='default', compression_quality='75', skip_existing='false'):
     """
     Geoprocessing tool that builds or deletes raster pyramids for a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        Required Raster Dataset or Raster Layer. Input Raster Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_level                         Optional Long. Pyramid levels. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_type                      Optional String. Pyramid compression type. Default value: default. Value choices: default, jpeg, lz77, none, jpeg_ycbcr
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional Boolean. Skip Existing. Default value: false. Value choices: skip_existing, overwrite
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_first                            Optional Boolean. Skip first level. Default value: false. Value choices: skip_first, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resample_technique                    Optional String. Pyramid resampling technique. Default value: nearest. Value choices: nearest, bilinear, cubic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional Long. Compression quality (1-100). Default value: 75
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'pyramid_level': ['pyramid_level', 'optional'], 'compression_type': ['compression_type', 'optional'], 'skip_existing': ['skip_existing', 'optional'], 'skip_first': ['SKIP_FIRST', 'optional'], 'resample_technique': ['resample_technique', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'BuildPyramids', inputs, in_db, out_db)


def calculate_statistics(raster_dataset, x_skip_factor=None, y_skip_factor=None, ignore_values=None, skip_existing='false', area_of_interest='in_memory\{bc80ecfe-15b0-41c3-8fa1-a0a41602275c}'):
     """
     Geoprocessing tool that calculates statistics for a raster dataset or mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        Required Mosaic Dataset or Mosaic Layer or Raster Dataset. Input Raster Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional Boolean. Skip Existing. Default value: false. Value choices: skip_existing, overwrite
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional Feature Set. Area of Interest. Default value: in_memory\{bc80ecfe-15b0-41c3-8fa1-a0a41602275c}
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_skip_factor                         Optional Long. Number of Rows to Skip. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_values                         Optional Multiple Value. Ignore Values. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     x_skip_factor                         Optional Long. Number of Columns to Skip. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['skip_existing', 'optional'], 'ignore_values': ['ignore_values', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'x_skip_factor': ['x_skip_factor', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'y_skip_factor': ['y_skip_factor', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateStatistics', inputs, in_db, out_db)


def get_raster_properties(raster, property_type='minimum', band_index=None):
     """
     Geoprocessing tool that returns the properties of a raster dataset, mosaic dataset, or a raster product.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Composite Geodataset. Input raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     property_type                         Optional String. Property type. Default value: minimum. Value choices: maximum, minimum, mean, std, uniquevaluecount, top, left, right, bottom, cellsizex, cellsizey, valuetype, columncount, rowcount, bandcount, allnodata, anynodata, sensorname, productname, acquisitiondate, sourcetype, cloudcover, sunazimuth, sunelevation, sensorazimuth, sensorelevation, offnadir, wavelength
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional String. Band Name. Default value: none
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
     raster                                Required Raster Dataset or Mosaic Dataset or Mosaic Layer or Raster Layer or File. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional String. Pixel Type. Default value: none. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional String. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    Optional Boolean. Convert 1 bit data to 8 bit. Default value: false. Value choices: onebitto8bit, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transform                             Optional Boolean. Apply Transformation. Default value: false. Value choices: transform, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scale_pixel_value                     Optional Boolean. Scale Pixel Value. Default value: false. Value choices: scalepixelvalue, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rgb_to_colormap                       Optional Boolean. RGB To Colormap. Default value: false. Value choices: rgbtocolormap, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional String. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      Optional Double. Ignore Background Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap_to_rgb                       Optional Boolean. Colormap to RGB. Default value: false. Value choices: colormaptorgb, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional String. Format. Default value: none. Value choices: tiff, imagine image, bmp, gif, png, jpeg, jpeg2000, esri grid, esri bil, esri bsq, esri bip, envi, crf, mrf
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'pixel_type': ['pixel_type', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'raster': ['in_raster', 'required'], 'scale_pixel_value': ['scale_pixel_value', 'optional'], 'rgb_to_colormap': ['RGB_to_Colormap', 'optional'], 'config_keyword': ['config_keyword', 'optional'], 'transform': ['transform', 'optional'], 'background_value': ['background_value', 'optional'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional'], 'format': ['format', 'optional']}
     out_db = {'rasterdataset': ['out_rasterdataset', 'required', None, None]}
     return _execute_tool('management', 'CopyRaster', inputs, in_db, out_db)


def create_random_raster(out_path, out_name, distribution='uniform 0.0 1.0', raster_extent=None, cellsize=None):
     """
     Geoprocessing tool that creates a random raster dataset based on a user-specified distribution and extent.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              Required String. Raster Dataset Name with Extension
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              Required Workspace or Raster Catalog. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_extent                         Optional Extent. Output extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          Optional String. Distribution. Default value: uniform 0.0 1.0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              Optional Double. Cellsize. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster_extent': ['raster_extent', 'optional'], 'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'distribution': ['distribution', 'optional'], 'cellsize': ['cellsize', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomRaster', inputs, in_db, out_db)


def create_raster_dataset(out_path, out_name, pixel_type, number_of_bands, cellsize=None, raster_spatial_reference=None, config_keyword=None, pyramids='pyramids -1 nearest default 75 no_skip', tile_size='128 128', compression='lz77', pyramid_origin=None):
     """
     Geoprocessing tool that creates a raster dataset as a file or in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Required String. Pixel Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_bands                       Required Long. Number of Bands
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required String. Raster Dataset Name with Extension
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              Required Workspace or Raster Catalog. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional String. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression                           Optional Compression. Compression. Default value: lz77
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_origin                        Optional Point. Pyramid Reference Point. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramids                              Optional Pyramid. Create pyramids. Default value: pyramids -1 nearest default 75 no_skip
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              Optional Double. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             Optional Tile Size. Tile size. Default value: 128 128
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_spatial_reference              Optional Coordinate System. Spatial Reference for Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'pixel_type': ['pixel_type', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'out_name': ['out_name', 'required'], 'number_of_bands': ['number_of_bands', 'required'], 'compression': ['compression', 'optional'], 'pyramid_origin': ['pyramid_origin', 'optional'], 'out_path': ['out_path', 'required'], 'pyramids': ['pyramids', 'optional'], 'cellsize': ['cellsize', 'optional'], 'tile_size': ['tile_size', 'optional'], 'raster_spatial_reference': ['raster_spatial_reference', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRasterDataset', inputs, in_db, out_db)


def mosaic(inputs, target, mosaic_type='last', colormap='first', background_value=None, nodata_value=None, onebit_to_eightbit='false', mosaicking_tolerance='0', matching_method=None):
     """
     Geoprocessing tool that mosaics multiple input rasters into an existing raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     inputs                                Required Multiple Value. Input Rasters
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target                                Required Raster Dataset. Target Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap                              Optional String. Mosaic Colormap Mode. Default value: first. Value choices: reject, first, last, match
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     matching_method                       Optional String. Color Matching Method. Default value: none. Value choices: none, statistic_matching, histogram_matching, linearcorrelation_matching
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    Optional Boolean. Convert 1 bit data to 8 bit. Default value: false. Value choices: onebitto8bit, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_type                           Optional String. Mosaic Operator. Default value: last. Value choices: first, last, blend, mean, minimum, maximum, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional Double. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      Optional Double. Ignore Background Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicking_tolerance                  Optional Double. Mosaicking Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'colormap': ['colormap', 'optional'], 'matching_method': ['MatchingMethod', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'target': ['target', 'required'], 'mosaic_type': ['mosaic_type', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'background_value': ['background_value', 'optional'], 'inputs': ['inputs', 'required'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Mosaic', inputs, in_db, out_db)


def workspace_to_raster_dataset(workspace, raster_dataset, include_subdirectories='false', mosaic_type='last', colormap='first', background_value=None, nodata_value=None, onebit_to_eightbit='false', mosaicking_tolerance='0', matching_method=None, colormap_to_rgb='false'):
     """
     Geoprocessing tool that mosaics all the raster datasets stored within the specified workspace into one raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster_dataset                        Required Raster Dataset. Target Raster Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap                              Optional String. Mosaic Colormap Mode. Default value: first. Value choices: reject, first, last, match
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     matching_method                       Optional String. Color Matching Method. Default value: none. Value choices: none, statistic_matching, histogram_matching, linearcorrelation_matching
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_subdirectories                Optional Boolean. Include Sub-directories. Default value: false. Value choices: include_subdirectories, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_type                           Optional String. Mosaic Operator. Default value: last. Value choices: first, last, blend, mean, minimum, maximum, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional Double. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      Optional Double. Ignore Background Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap_to_rgb                       Optional Boolean. Colormap to RGB. Default value: false. Value choices: colormaptorgb, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    Optional Boolean. Convert 1 bit data to 8 bit. Default value: false. Value choices: onebitto8bit, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicking_tolerance                  Optional Double. Mosaicking Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'colormap': ['colormap', 'optional'], 'matching_method': ['MatchingMethod', 'optional'], 'include_subdirectories': ['include_subdirectories', 'optional'], 'workspace': ['in_workspace', 'required'], 'mosaic_type': ['mosaic_type', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'background_value': ['background_value', 'optional'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'WorkspaceToRasterDataset', inputs, in_db, out_db)


def clip(raster, rectangle, template_dataset=None, nodata_value=None, clipping_geometry='false', maintaclipping_extent='false'):
     """
     Geoprocessing tool that creates a spatial subset of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rectangle                             Required Envelope. Rectangle
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                Required Mosaic Dataset or Mosaic Layer or Raster Dataset or Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional String. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintaclipping_extent                 Optional Boolean. Maintain Clipping Extent. Default value: false. Value choices: maintain_extent, no_maintain_extent
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional Raster Layer or Feature Layer. Output Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clipping_geometry                     Optional Boolean. Use Input Features for Clipping Geometry. Default value: false. Value choices: clippinggeometry, none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'maintaclipping_extent': ['maintain_clipping_extent', 'optional'], 'raster': ['in_raster', 'required'], 'nodata_value': ['nodata_value', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'rectangle': ['rectangle', 'required'], 'clipping_geometry': ['clipping_geometry', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Clip', inputs, in_db, out_db)


def composite_bands(rasters):
     """
     Geoprocessing tool that creates a single raster dataset from multiple bands and can also create a subset of the bands.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rasters                               Required Multiple Value. Input Rasters
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'rasters': ['in_rasters', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'CompositeBands', inputs, in_db, out_db)


def resample(raster, cell_size=None, resampling_type='nearest'):
     """
     Geoprocessing tool that alters the raster dataset by changing the cell size and resampling method.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Mosaic Dataset or Mosaic Layer or Raster Dataset or Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional String. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional Cell Size XY. Output Cell Size. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required'], 'cell_size': ['cell_size', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Resample', inputs, in_db, out_db)


def export_raster_world_file(raster_dataset):
     """
     Geoprocessing tool that creates a world file based on the geographic information of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        Required Raster Dataset. Input Raster Dataset
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
     raster                                Required Mosaic Dataset or Mosaic Layer or Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     location_point                        Required Point. Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional Value Table. Bands. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'band_index': ['band_index', 'optional'], 'raster': ['in_raster', 'required'], 'location_point': ['location_point', 'required']}
     out_db = {}
     return _execute_tool('management', 'GetCellValue', inputs, in_db, out_db)


def make_wcs_layer(wcs_coverage, template=None, band_index=None):
     """
     Geoprocessing tool that creates a temporary raster layer from a WCS service.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     wcs_coverage                          Required WCS Coverage or String. Input WCS Coverage
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional Value Table. Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional Extent. Template Extent. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'wcs_coverage': ['in_wcs_coverage', 'required'], 'band_index': ['band_index', 'optional'], 'template': ['template', 'optional']}
     out_db = {'wcs_layer': ['out_wcs_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeWCSLayer', inputs, in_db, out_db)


def apply_symbology_from_layer(layer, symbology_layer):
     """
     Geoprocessing tool that applies the symbology from a specified layer to the Input Layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     symbology_layer                       Required Layer. Symbology Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     layer                                 Required Layer. Input Layer
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'symbology_layer': ['in_symbology_layer', 'required'], 'layer': ['in_layer', 'required']}
     out_db = {}
     return _execute_tool('management', 'ApplySymbologyFromLayer', inputs, in_db, out_db)


def mosaic_to_new_raster(input_rasters, output_location, raster_dataset_name_with_extension, number_of_bands, coordinate_system_for_the_raster=None, pixel_type='8_bit_unsigned', cellsize=None, mosaic_method='last', mosaic_colormap_mode='first'):
     """
     Geoprocessing tool that mosaics multiple raster datasets into a new raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_bands                       Required Long. Number of Bands
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_location                       Required Workspace or Raster Catalog. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_rasters                         Required Multiple Value. Input Rasters
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster_dataset_name_with_extension    Required String. Raster Dataset Name with Extension
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional String. Pixel Type. Default value: 8_bit_unsigned. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_colormap_mode                  Optional String. Mosaic Colormap Mode. Default value: first. Value choices: reject, first, last, match
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_method                         Optional String. Mosaic Operator. Default value: last. Value choices: first, last, blend, mean, minimum, maximum, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              Optional Double. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system_for_the_raster      Optional Coordinate System. Spatial Reference for Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'pixel_type': ['pixel_type', 'optional'], 'mosaic_colormap_mode': ['mosaic_colormap_mode', 'optional'], 'mosaic_method': ['mosaic_method', 'optional'], 'coordinate_system_for_the_raster': ['coordinate_system_for_the_raster', 'optional'], 'raster_dataset_name_with_extension': ['raster_dataset_name_with_extension', 'required'], 'number_of_bands': ['number_of_bands', 'required'], 'output_location': ['output_location', 'required'], 'input_rasters': ['input_rasters', 'required'], 'cellsize': ['cellsize', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MosaicToNewRaster', inputs, in_db, out_db)


def dice(features, vertex_limit):
     """
     Geoprocessing tool that subdivides a feature into smaller features based on a specified vertex limit.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     vertex_limit                          Required Long. Vertex Limit
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
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
     point_features                        Required Feature Layer. Point Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional Linear unit. Search Radius. Default value: none
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
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics_fields                     Optional Value Table. Statistics Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        Optional Multiple Value. Dissolve_Field(s). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'statistics_fields': ['statistics_fields', 'optional'], 'features': ['in_features', 'required'], 'dissolve_field': ['dissolve_field', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'UnsplitLine', inputs, in_db, out_db)


def split_raster(raster, out_folder, out_base_name, split_method, format, resampling_type='nearest', num_rasters='1 1', tile_size='2048 2048', overlap='0', units='pixels', cell_size=None, origin=None, split_polygon_feature_class=None, clip_type=None, template_extent=None, nodata_value=None):
     """
     Geoprocessing tool that creates a tiled output from an input raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_method                          Required String. Split Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder                            Required Folder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                Required Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     format                                Required String. Output Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_base_name                         Required String.
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional String. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_extent                       Optional Extent. Template Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     num_rasters                           Optional Point. Number of Output Rasters. Default value: 1 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_polygon_feature_class           Optional Feature Layer. Split Polygon Feature Class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     units                                 Optional String. Units for Output Raster Size and Overlap. Default value: pixels. Value choices: pixels, meters, feet, degrees, kilometers, miles
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional Point. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional String. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_type                             Optional String. Clip Type. Default value: none. Value choices: none, extent, feature_class
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overlap                               Optional Double. Overlap. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     origin                                Optional Point. Lower left origin. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             Optional Point. Size of Output Rasters. Default value: 2048 2048
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'split_method': ['split_method', 'required'], 'num_rasters': ['num_rasters', 'optional'], 'split_polygon_feature_class': ['split_polygon_feature_class', 'optional'], 'units': ['units', 'optional'], 'overlap': ['overlap', 'optional'], 'format': ['format', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'template_extent': ['template_extent', 'optional'], 'out_folder': ['out_folder', 'required'], 'raster': ['in_raster', 'required'], 'cell_size': ['cell_size', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'clip_type': ['clip_type', 'optional'], 'origin': ['origin', 'optional'], 'tile_size': ['tile_size', 'optional'], 'out_base_name': ['out_base_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'SplitRaster', inputs, in_db, out_db)


def eliminate_polygon_part(features, condition='area', part_area='0 unknown', part_area_percent='0', part_option='true'):
     """
     Geoprocessing tool that creates a new output feature class containing the features from input polygons with some parts or holes of a specified size deleted.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_option                           Optional Boolean. Eliminate contained parts only. Default value: true. Value choices: contained_only, any
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_area                             Optional Areal unit. Area. Default value: 0 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_area_percent                     Optional Double. Percentage. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     condition                             Optional String. Condition. Default value: area. Value choices: area, percent, area_and_percent, area_or_percent
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'part_area': ['part_area', 'optional'], 'features': ['in_features', 'required'], 'part_area_percent': ['part_area_percent', 'optional'], 'condition': ['condition', 'optional'], 'part_option': ['part_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'EliminatePolygonPart', inputs, in_db, out_db)


def points_to_line(input_features, line_field=None, sort_field=None, close_line='false'):
     """
     Geoprocessing tool used to create line features from points.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_features                        Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_field                            Optional Field. Line Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_field                            Optional Field. Sort Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     close_line                            Optional Boolean. Close Line. Default value: false. Value choices: close, no_close
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'line_field': ['Line_Field', 'optional'], 'input_features': ['Input_Features', 'required'], 'sort_field': ['Sort_Field', 'optional'], 'close_line': ['Close_Line', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'PointsToLine', inputs, in_db, out_db)


def change_version(features, version_type, version_name=None, date=None):
     """
     Geoprocessing tool used to change the enterprise geodatabase version you are connected to. Only works when working with feature layers or table views.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer or Table View. Input Feature Layer or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     version_type                          Required String. Version Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     date                                  Optional Date. Date and Time. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_name                          Optional String. Version Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'date': ['date', 'optional'], 'version_name': ['version_name', 'optional'], 'features': ['in_features', 'required'], 'version_type': ['version_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'ChangeVersion', inputs, in_db, out_db)


def register_with_geodatabase(dataset, object_id_field=None, shape_field=None, geometry_type=None, spatial_reference=None, extent=None):
     """
     Geoprocessing tool that registers feature classes, tables, views, and raster layers that were created outside of the geodatabase with the geodatabase in order for them to participate in geodatabase functionality.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Table View or Raster Layer. Input Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     object_id_field                       Optional Field. Object ID Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Optional Envelope. Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional String. Geometry Type. Default value: none. Value choices: point, multipoint, polygon, polyline
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shape_field                           Optional Field. Shape Field. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'object_id_field': ['in_object_id_field', 'optional'], 'dataset': ['in_dataset', 'required'], 'spatial_reference': ['in_spatial_reference', 'optional'], 'shape_field': ['in_shape_field', 'optional'], 'extent': ['in_extent', 'optional'], 'geometry_type': ['in_geometry_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RegisterwithGeodatabase', inputs, in_db, out_db)


def delete_identical(dataset, fields, xy_tolerance=None, z_tolerance='0'):
     """
     Geoprocessing tool to delete records in a feature class or table which have identical values in a list of fields.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Table View. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                Required Multiple Value. Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional Linear unit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           Optional Double. Z Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'xy_tolerance': ['xy_tolerance', 'optional'], 'dataset': ['in_dataset', 'required'], 'fields': ['fields', 'required'], 'z_tolerance': ['z_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DeleteIdentical', inputs, in_db, out_db)


def find_identical(dataset, fields, xy_tolerance=None, z_tolerance='0', output_record_option='false'):
     """
     Geoprocessing tool that reports any records in a feature class or table that have identical values in a list of fields, and generates a table listing these identical records.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Table View. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                Required Multiple Value. Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional Linear unit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_record_option                  Optional Boolean. Output only duplicated records. Default value: false. Value choices: only_duplicates, all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           Optional Double. Z Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'xy_tolerance': ['xy_tolerance', 'optional'], 'dataset': ['in_dataset', 'required'], 'fields': ['fields', 'required'], 'z_tolerance': ['z_tolerance', 'optional'], 'output_record_option': ['output_record_option', 'optional']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'FindIdentical', inputs, in_db, out_db)


def change_privileges(dataset, user, view=None, edit=None):
     """
     Geoprocessing tool to change  privileges on a dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Multiple Value. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     user                                  Required String. User
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit                                  Optional String. Edit (Update/Insert/Delete). Default value: none. Value choices: as_is, grant, revoke
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view                                  Optional String. View (Select). Default value: none. Value choices: as_is, grant, revoke
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'view': ['View', 'optional'], 'edit': ['Edit', 'optional'], 'user': ['user', 'required']}
     out_db = {}
     return _execute_tool('management', 'ChangePrivileges', inputs, in_db, out_db)


def create_spatial_reference(spatial_reference=None, spatial_reference_template=None, xy_domain=None, z_domain=None, m_domain=None, template=None, expand_ratio='0'):
     """
     Geoprocessing tool to create a spatial reference for use in ModelBuilder and scripting.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_domain                              Optional String. Z Domain (min max). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     expand_ratio                          Optional Double. Grow XYDomain By Percentage. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Spatial Reference. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional Multiple Value. Template XYDomains. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference_template            Optional Feature Layer or Raster Dataset or Raster Catalog Layer. Spatial Reference Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     m_domain                              Optional String. M Domain (min max). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_domain                             Optional Envelope. XY Domain. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'z_domain': ['z_domain', 'optional'], 'expand_ratio': ['expand_ratio', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'template': ['template', 'optional'], 'spatial_reference_template': ['spatial_reference_template', 'optional'], 'm_domain': ['m_domain', 'optional'], 'xy_domain': ['xy_domain', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateSpatialReference', inputs, in_db, out_db)


def raster_to_dted(raster, out_folder, dted_level, resampling_type='bilinear'):
     """
     Geoprocessing tool that splits a raster dataset into files based on the DTED tiling structure.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder                            Required Folder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                Required Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dted_level                            Required String. DTED Level
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional String. Resampling Technique. Default value: bilinear. Value choices: bilinear, nearest, cubic
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'resampling_type': ['resampling_type', 'optional'], 'out_folder': ['out_folder', 'required'], 'raster': ['in_raster', 'required'], 'dted_level': ['dted_level', 'required']}
     out_db = {}
     return _execute_tool('management', 'RasterToDTED', inputs, in_db, out_db)


def bearing_distance_to_line(table, x_field, y_field, distance_field, distance_units, bearing_field, bearing_units, line_type='0', id_field=None, spatial_reference='{b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in an x-coordinate field, y-coordinate field, bearing field, and distance field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_field                               Required Field. Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     distance_units                        Required String. Distance Units
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     bearing_field                         Required Field. Bearing Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               Required Field. X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     bearing_units                         Required String. Bearing Units
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     distance_field                        Required Field. Distance Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_type                             Optional String. Line Type. Default value: 0. Value choices: geodesic, great_circle, rhumb_line, normal_section
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Spatial Reference. Default value: {b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'line_type': ['line_type', 'optional'], 'y_field': ['y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'distance_units': ['distance_units', 'required'], 'table': ['in_table', 'required'], 'bearing_field': ['bearing_field', 'required'], 'x_field': ['x_field', 'required'], 'bearing_units': ['bearing_units', 'required'], 'distance_field': ['distance_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'BearingDistanceToLine', inputs, in_db, out_db)


def table_to_ellipse(table, x_field, y_field, major_field, minor_field, distance_units, azimuth_field=None, azimuth_units='9102', id_field=None, spatial_reference='{b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic ellipse features constructed based on the values in an x-coordinate field, y-coordinate field, major-axis field, minor-axis field, and azimuth field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minor_field                           Required Field. Minor Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               Required Field. Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     distance_units                        Required String. Distance Units
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               Required Field. X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     major_field                           Required Field. Major Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     azimuth_units                         Optional String. Azimuth Units. Default value: 9102. Value choices: degrees, mils, rads, grads
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Spatial Reference. Default value: {b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     azimuth_field                         Optional Field. Azimuth Field. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'minor_field': ['minor_field', 'required'], 'id_field': ['id_field', 'optional'], 'y_field': ['y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'distance_units': ['distance_units', 'required'], 'table': ['in_table', 'required'], 'x_field': ['x_field', 'required'], 'azimuth_field': ['azimuth_field', 'optional'], 'azimuth_units': ['azimuth_units', 'optional'], 'major_field': ['major_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'TableToEllipse', inputs, in_db, out_db)


def xy_to_line(table, startx_field, starty_field, endx_field, endy_field, line_type='0', id_field=None, spatial_reference='{b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in a start x-coordinate field, start y-coordinate field, end x-coordinate field, and end y-coordinate field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     startx_field                          Required Field. Start X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     starty_field                          Required Field. Start Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     endy_field                            Required Field. End Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     endx_field                            Required Field. End X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_type                             Optional String. Line Type. Default value: 0. Value choices: geodesic, great_circle, rhumb_line, normal_section
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Spatial Reference. Default value: {b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'startx_field': ['startx_field', 'required'], 'line_type': ['line_type', 'optional'], 'starty_field': ['starty_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'table': ['in_table', 'required'], 'endy_field': ['endy_field', 'required'], 'id_field': ['id_field', 'optional'], 'endx_field': ['endx_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'XYToLine', inputs, in_db, out_db)


def convert_coordinate_notation(table, x_field, y_field, input_coordinate_format, output_coordinate_format, exclude_invalid_records, id_field=None, spatial_reference=None, coor_system=None):
     """
     Geoprocessing tool that converts coordinate notations from one format to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_coordinate_format               Required String. Input Coordinate Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_coordinate_format              Required String. Output Coordinate Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               Required Field. Y Field (Latitude)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               Required Field. X Field (Longitude)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     exclude_invalid_records               Required Boolean. Exclude records with invalid notation
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           Optional Coordinate System. Input Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Output Coordinate System. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'input_coordinate_format': ['input_coordinate_format', 'required'], 'output_coordinate_format': ['output_coordinate_format', 'required'], 'y_field': ['y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'table': ['in_table', 'required'], 'x_field': ['x_field', 'required'], 'exclude_invalid_records': ['exclude_invalid_records', 'required'], 'coor_system': ['in_coor_system', 'optional']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'ConvertCoordinateNotation', inputs, in_db, out_db)


def minimum_bounding_geometry(features, geometry_type='rectangle_by_area', group_option=None, group_field=None, mbg_fields_option='false'):
     """
     Geoprocessing tool that creates polygons which represent a specified minimum bounding geometry enclosing each input feature or a group of input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     group_field                           Optional Multiple Value. Group Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     group_option                          Optional String. Group Option. Default value: none. Value choices: none, all, list
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional String. Geometry Type. Default value: rectangle_by_area. Value choices: rectangle_by_area, rectangle_by_width, convex_hull, circle, envelope
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mbg_fields_option                     Optional Boolean. Add geometry characteristics as attributes to output. Default value: false. Value choices: mbg_fields, no_mbg_fields
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'group_field': ['group_field', 'optional'], 'group_option': ['group_option', 'optional'], 'geometry_type': ['geometry_type', 'optional'], 'features': ['in_features', 'required'], 'mbg_fields_option': ['mbg_fields_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'MinimumBoundingGeometry', inputs, in_db, out_db)


def add_rasters_to_mosaic_dataset(mosaic_dataset, raster_type, input_path, update_cellsize_ranges='true', update_boundary='true', update_overviews='false', maximum_pyramid_levels=None, maximum_cell_size='0', minimum_dimension='1500', spatial_reference=None, filter=None, sub_folder='true', duplicate_items_action='allow_duplicates', build_pyramids='false', calculate_statistics='false', build_thumbnails='false', operation_description=None, force_spatial_reference='false', estimate_statistics='false', aux_inputs=None):
     """
     Geoprocessing tool that ingests raster datasets from a file, folder, raster catalog, or image service to a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_path                            Required Multiple Value. Input Data
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster_type                           Required Raster Type. Raster Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     operation_description                 Optional String. Operation Description. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_pyramid_levels                Optional Long. Maximum Pyramid Levels Used. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional Boolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     calculate_statistics                  Optional Boolean. Calculate Statistics. Default value: false. Value choices: calculate_statistics, no_statistics
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_pyramids                        Optional Boolean. Build Raster Pyramids. Default value: false. Value choices: build_pyramids, no_pyramids
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     force_spatial_reference               Optional Boolean. Force this Coordinate System for Input Data. Default value: false. Value choices: force_spatial_reference, no_force_spatial_reference
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                Optional Boolean. Update Cell Size Ranges. Default value: true. Value choices: update_cell_sizes, no_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sub_folder                            Optional Boolean. Include Sub Folders. Default value: true. Value choices: subfolders, no_subfolders
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_dimension                     Optional Long. Minimum Pyramid Rows or Columns. Default value: 1500
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate_statistics                   Optional Boolean. Estimate Mosaic Dataset Statistics. Default value: false. Value choices: estimate_statistics, no_statistics
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Coordinate System for Input Data. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_thumbnails                      Optional Boolean. Build Thumbnails. Default value: false. Value choices: build_thumbnails, no_thumbnails
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_cell_size                     Optional Double. Maximum Pyramid Cell Size. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     duplicate_items_action                Optional String. Add New Datasets Only. Default value: allow_duplicates. Value choices: allow_duplicates, exclude_duplicates, overwrite_duplicates
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_overviews                      Optional Boolean. Update Overviews. Default value: false. Value choices: update_overviews, no_overviews
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     aux_inputs                            Optional Value Table. Auxiliary Inputs. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     filter                                Optional String. Input Data Filter. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'operation_description': ['operation_description', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'input_path': ['input_path', 'required'], 'maximum_pyramid_levels': ['maximum_pyramid_levels', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional'], 'duplicate_items_action': ['duplicate_items_action', 'optional'], 'force_spatial_reference': ['force_spatial_reference', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'minimum_dimension': ['minimum_dimension', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'maximum_cell_size': ['maximum_cell_size', 'optional'], 'raster_type': ['raster_type', 'required'], 'sub_folder': ['sub_folder', 'optional'], 'update_overviews': ['update_overviews', 'optional'], 'aux_inputs': ['aux_inputs', 'optional'], 'filter': ['filter', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddRastersToMosaicDataset', inputs, in_db, out_db)


def build_boundary(mosaic_dataset, where_clause=None, append_to_existing='false', simplification_method=None):
     """
     Geoprocessing tool that updates the extent of the boundary of  a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     append_to_existing                    Optional Boolean. Append To Existing Boundary. Default value: false. Value choices: append, overwrite
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     simplification_method                 Optional String. Simplification Method. Default value: none. Value choices: none, convex_hull, envelope
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'append_to_existing': ['append_to_existing', 'optional'], 'simplification_method': ['simplification_method', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildBoundary', inputs, in_db, out_db)


def build_footprints(mosaic_dataset, where_clause=None, reset_footprint='radiometry', mdata_value='1', max_data_value='254', approx_num_vertices='80', shrink_distance='0', maintaedges='false', skip_derived_images='true', update_boundary='true', request_size='2000', mregion_size='100', simplification_method=None, edge_tolerance=None, max_sliver_size='20', mthinness_ratio='0.05'):
     """
     Geoprocessing tool that computes the footprints for the rasters in a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     simplification_method                 Optional String. Simplification Method. Default value: none. Value choices: none, convex_hull, envelope
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mregion_size                          Optional Long. Minimum Region Size. Default value: 100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mdata_value                           Optional Double. Minimum Data Value. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shrink_distance                       Optional Double. Shrink distance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edge_tolerance                        Optional Double. Edge tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional Boolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     reset_footprint                       Optional String or Boolean. Computation Method. Default value: radiometry. Value choices: none, geometry, radiometry, copy_to_sibling
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_derived_images                   Optional Boolean. Skip overviews. Default value: true. Value choices: skip_derived_images, no_skip_derived_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintaedges                           Optional Boolean. Maintain sheet edges. Default value: false. Value choices: maintain_edges, no_maintain_edges
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_sliver_size                       Optional Long. Maximum Sliver Size. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          Optional Long. Request Size. Default value: 2000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     approx_num_vertices                   Optional Long. Approximate number of vertices. Default value: 80
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mthinness_ratio                       Optional Double. Minimum Thinness Ratio. Default value: 0.05
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_data_value                        Optional Double. Maximum Data Value. Default value: 254
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'simplification_method': ['simplification_method', 'optional'], 'reset_footprint': ['reset_footprint', 'optional'], 'mdata_value': ['min_data_value', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'shrink_distance': ['shrink_distance', 'optional'], 'edge_tolerance': ['edge_tolerance', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'skip_derived_images': ['skip_derived_images', 'optional'], 'maintaedges': ['maintain_edges', 'optional'], 'max_sliver_size': ['max_sliver_size', 'optional'], 'request_size': ['request_size', 'optional'], 'approx_num_vertices': ['approx_num_vertices', 'optional'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'max_data_value': ['max_data_value', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildFootprints', inputs, in_db, out_db)


def build_overviews(mosaic_dataset, where_clause=None, define_missing_tiles='true', generate_overviews='true', generate_missing_images='true', regenerate_stale_images='true'):
     """
     Geoprocessing tool that defines and generates overviews for a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     define_missing_tiles                  Optional Boolean. Define Missing Overview Tiles. Default value: true. Value choices: define_missing_tiles, no_define_missing_tiles
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     regenerate_stale_images               Optional Boolean. Regenerate Stale Overview Images Only. Default value: true. Value choices: regenerate_stale_images, ignore_stale_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_overviews                    Optional Boolean. Generate Overviews. Default value: true. Value choices: generate_overviews, no_generate_overviews
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_missing_images               Optional Boolean. Generate Missing Overview Images Only. Default value: true. Value choices: generate_missing_images, ignore_missing_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'define_missing_tiles': ['define_missing_tiles', 'optional'], 'generate_missing_images': ['generate_missing_images', 'optional'], 'regenerate_stale_images': ['regenerate_stale_images', 'optional'], 'generate_overviews': ['generate_overviews', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildOverviews', inputs, in_db, out_db)


def build_seamlines(mosaic_dataset, cell_size=None, sort_method='north_west', sort_order='true', order_by_attribute=None, order_by_base_value=None, view_point=None, computation_method='radiometry', blend_width=None, blend_type='both', request_size='1000', request_size_type='pixels', blend_width_units='pixels', area_of_interest='in_memory\{18b3c9c4-be24-4d7f-b8a9-fae3bd65574a}', where_clause=None, update_existing='false', mregion_size='100', mthinness_ratio='0.05', max_sliver_size='20'):
     """
     Geoprocessing tool that generates seamlines for your mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_type                            Optional String. Blend Type. Default value: both. Value choices: both, inside, outside
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mregion_size                          Optional Long. Minimum Region Size. Default value: 100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point                            Optional Point. View Point. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mthinness_ratio                       Optional Double. Minimum Thinness Ratio. Default value: 0.05
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional Feature Set. Area of Interest. Default value: in_memory\{18b3c9c4-be24-4d7f-b8a9-fae3bd65574a}
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_existing                       Optional Boolean. Update Existing Seamlines. Default value: false. Value choices: update_existing, ignore_existing
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size_type                     Optional String. Request Size Type. Default value: pixels. Value choices: pixels, pixelsize_factor
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_order                            Optional Boolean. Sort Ascending. Default value: true. Value choices: ascending, descending
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_method                           Optional String. Sort Method. Default value: north_west. Value choices: north_west, closest_to_viewpoint, by_attribute
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_by_base_value                   Optional Variant. Sort Base Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     computation_method                    Optional String. Computation Method. Default value: radiometry. Value choices: geometry, radiometry, copy_footprint, copy_to_sibling, edge_detection, voronoi, disparity
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_sliver_size                       Optional Long. Maximum Sliver Size. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          Optional Long. Request Size. Default value: 1000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width                           Optional Double. Blend Width. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional Multiple Value. Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_by_attribute                    Optional Field. Sort Attribute. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width_units                     Optional String. Blend Width Units. Default value: pixels. Value choices: pixels, ground_units
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'blend_type': ['blend_type', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'view_point': ['view_point', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'update_existing': ['update_existing', 'optional'], 'sort_method': ['sort_method', 'optional'], 'sort_order': ['sort_order', 'optional'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'order_by_base_value': ['order_by_base_value', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'computation_method': ['computation_method', 'optional'], 'request_size_type': ['request_size_type', 'optional'], 'request_size': ['request_size', 'optional'], 'blend_width': ['blend_width', 'optional'], 'cell_size': ['cell_size', 'optional'], 'where_clause': ['where_clause', 'optional'], 'order_by_attribute': ['order_by_attribute', 'optional'], 'max_sliver_size': ['max_sliver_size', 'optional'], 'blend_width_units': ['blend_width_units', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildSeamlines', inputs, in_db, out_db)


def calculate_cell_size_ranges(mosaic_dataset, where_clause=None, do_compute_min='true', do_compute_max='true', max_range_factor='10', cell_size_tolerance_factor='0.8', update_missing_only='false'):
     """
     Geoprocessing tool that computes the minimum and maximum cell sizes for the rasters in a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     do_compute_max                        Optional Boolean. Compute Maximum Cell Sizes. Default value: true. Value choices: max_cell_sizes, no_max_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_missing_only                   Optional Boolean. Update Missing Values Only. Default value: false. Value choices: update_missing_only, update_all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size_tolerance_factor            Optional Double. Cell Size Tolerance Factor. Default value: 0.8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_range_factor                      Optional Double. Maximum Cell Size Range Factor. Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     do_compute_min                        Optional Boolean. Compute Minimum Cell Sizes. Default value: true. Value choices: min_cell_sizes, no_min_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'do_compute_max': ['do_compute_max', 'optional'], 'update_missing_only': ['update_missing_only', 'optional'], 'cell_size_tolerance_factor': ['cell_size_tolerance_factor', 'optional'], 'max_range_factor': ['max_range_factor', 'optional'], 'do_compute_min': ['do_compute_min', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateCellSizeRanges', inputs, in_db, out_db)


def color_balance_mosaic_dataset(mosaic_dataset, balancing_method='dodging', color_surface_type='single_color', target_raster=None, exclude_raster=None, stretch_type=None, gamma='1', block_field=None):
     """
     Geoprocessing tool that color balances a mosaic dataset so the tiles appear seamless.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     color_surface_type                    Optional String. Color Surface Type. Default value: single_color. Value choices: single_color, color_grid, first_order, second_order, third_order
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     stretch_type                          Optional String. Stretch Type. Default value: none. Value choices: none, standard_deviation, minimum_maximum, adaptive
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_raster                         Optional Raster Layer or Internet Tiled Layer or Map Server Layer. Target Raster. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gamma                                 Optional Double. Gamma. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     balancing_method                      Optional String. Balance Method. Default value: dodging. Value choices: dodging, histogram, standard_deviation
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     block_field                           Optional String. Block Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     exclude_raster                        Optional Raster Layer. Exclude Area Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'color_surface_type': ['color_surface_type', 'optional'], 'target_raster': ['target_raster', 'optional'], 'gamma': ['gamma', 'optional'], 'stretch_type': ['stretch_type', 'optional'], 'balancing_method': ['balancing_method', 'optional'], 'block_field': ['block_field', 'optional'], 'exclude_raster': ['exclude_raster', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ColorBalanceMosaicDataset', inputs, in_db, out_db)


def compute_dirty_area(mosaic_dataset, timestamp, where_clause=None):
     """
     Geoprocessing tool that identifies an area within a mosaic dataset that has changed since a specified point in time.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     timestamp                             Required String. Start Date and Time
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'timestamp': ['timestamp', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'ComputeDirtyArea', inputs, in_db, out_db)


def create_mosaic_dataset(workspace, mosaicdataset_name, coordinate_system, num_bands=None, pixel_type=None, product_definition=None, product_band_definitions=None):
     """
     Geoprocessing tool that makes an empty mosaic dataset in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicdataset_name                    Required String. Mosaic Dataset Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     coordinate_system                     Required Spatial Reference. Coordinate System
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional String. Pixel Type. Default value: none. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     num_bands                             Optional Long. Number of Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     product_definition                    Optional String. Product Definition. Default value: none. Value choices: none, natural_color_rgb, natural_color_rgbi, false_color_irg, vector_field_uv, vector_field_magnitude_direction, deimos2_4bands, dmcii_3bands, dubaisat-2_4bands, formosat-2_4bands, geoeye-1_4bands, gf-1 pms_4bands, gf-1 wfv_4bands, gf-2 pms_4bands, gf-4 pmi_4bands, hj 1a/1b ccd_4bands, ikonos_4bands, jilin-1_3bands, kompsat-2_4bands, kompsat-3_4bands, landsat_6bands, landsat_mss_4bands, landsat_8bands, pleiades-1_4bands, quickbird_4bands, rapideye_5bands, sentinel2_13bands, spot-5_4bands, spot-6_4bands, spot-7_4bands, th-01_4bands, worldview-2_8bands, worldview-3_8bands, zy1-02c pms_3bands, zy3-cresda_4bands, zy3-sasmac_4bands, custom
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     product_band_definitions              Optional Value Table. Product Band Definitions. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'pixel_type': ['pixel_type', 'optional'], 'num_bands': ['num_bands', 'optional'], 'product_definition': ['product_definition', 'optional'], 'workspace': ['in_workspace', 'required'], 'product_band_definitions': ['product_band_definitions', 'optional'], 'mosaicdataset_name': ['in_mosaicdataset_name', 'required'], 'coordinate_system': ['coordinate_system', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateMosaicDataset', inputs, in_db, out_db)


def create_referenced_mosaic_dataset(dataset, coordinate_system=None, number_of_bands=None, pixel_type=None, where_clause=None, template_dataset=None, extent=None, select_using_features='true', lod_field=None, minps_field=None, maxps_field=None, pixel_size=None, build_boundary='true'):
     """
     Geoprocessing tool that creates a new mosaic dataset from a selection set of a raster catalog, or a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Raster Catalog Layer or Mosaic Dataset or Mosaic Layer. Input Raster Catalog or Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minps_field                           Optional Field. Minimum Cell Size Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maxps_field                           Optional Field. Maximum Cell Size Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_bands                       Optional Long. Number of Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional Raster Layer or Feature Layer. Extent from Dataset. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lod_field                             Optional Field. Scale Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system                     Optional Spatial Reference. Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     select_using_features                 Optional Boolean. Using Input Geometry for Selection. Default value: true. Value choices: select_using_features, no_select_using_features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional String. Pixel Type. Default value: none. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_size                            Optional Double. Maximum Visible Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_boundary                        Optional Boolean. Build Boundary. Default value: true. Value choices: build_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Optional Envelope. Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'minps_field': ['minPS_field', 'optional'], 'maxps_field': ['maxPS_field', 'optional'], 'number_of_bands': ['number_of_bands', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'lod_field': ['lod_field', 'optional'], 'coordinate_system': ['coordinate_system', 'optional'], 'select_using_features': ['select_using_features', 'optional'], 'pixel_type': ['pixel_type', 'optional'], 'pixel_size': ['pixelSize', 'optional'], 'build_boundary': ['build_boundary', 'optional'], 'extent': ['extent', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'mosaic_dataset': ['out_mosaic_dataset', 'required', None, None]}
     return _execute_tool('management', 'CreateReferencedMosaicDataset', inputs, in_db, out_db)


def define_overviews(mosaic_dataset, overview_image_folder=None, template_dataset=None, extent=None, pixel_size=None, number_of_levels=None, tile_rows='5120', tile_cols='5120', overview_factor='3', force_overview_tiles='false', resampling_method='bilinear', compression_method='jpeg', compression_quality='80'):
     """
     Geoprocessing tool that defines the tiling schema and properties of the preprocessed raster datasets that will cover part or all of a mosaic dataset at varying resolutions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     force_overview_tiles                  Optional Boolean. Force Overview Tiles. Default value: false. Value choices: force_overview_tiles, no_force_overview_tiles
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overview_factor                       Optional Long. Overview Sampling Factor. Default value: 3
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_cols                             Optional Long. Number Of Columns. Default value: 5120
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overview_image_folder                 Optional Workspace. Output Location. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    Optional String. Compression Method. Default value: jpeg
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional Long. Compression Quality. Default value: 80
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_size                            Optional Double. Pixel Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_method                     Optional String. Resampling Method. Default value: bilinear. Value choices: nearest, bilinear, cubic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_levels                      Optional Long. Number Of Levels. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Optional Envelope. Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_rows                             Optional Long. Number Of Rows. Default value: 5120
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional Raster Layer or Feature Layer. Extent from Dataset. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'force_overview_tiles': ['force_overview_tiles', 'optional'], 'overview_factor': ['overview_factor', 'optional'], 'tile_cols': ['tile_cols', 'optional'], 'overview_image_folder': ['overview_image_folder', 'optional'], 'compression_method': ['compression_method', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'pixel_size': ['pixel_size', 'optional'], 'resampling_method': ['resampling_method', 'optional'], 'number_of_levels': ['number_of_levels', 'optional'], 'extent': ['extent', 'optional'], 'tile_rows': ['tile_rows', 'optional'], 'template_dataset': ['in_template_dataset', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DefineOverviews', inputs, in_db, out_db)


def generate_exclude_area(raster, pixel_type, generate_method, max_red='255', max_green='255', max_blue='255', max_white='255', max_black='0', max_magenta='255', max_cyan='255', max_yellow='255', percentage_low='0', percentage_high='100'):
     """
     Geoprocessing tool that generates exclude areas to use within the Color Balance Mosaic Dataset tool.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Required String. Pixel Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                Required Mosaic Dataset or Composite Layer or Raster Dataset or Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     generate_method                       Required String. Generate Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_blue                              Optional Double. Maximum Blue. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_magenta                           Optional Double. Maximum Magenta. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage_high                       Optional Double. High Percentage. Default value: 100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cyan                              Optional Double. Maximum Cyan. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage_low                        Optional Double. Low Percentage. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_red                               Optional Double. Maximum Red. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_yellow                            Optional Double. Maximum Yellow. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_black                             Optional Double. Maximum Black. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_white                             Optional Double. Maximum White. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_green                             Optional Double. Maximum Green. Default value: 255
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'max_yellow': ['max_yellow', 'optional'], 'max_blue': ['max_blue', 'optional'], 'percentage_low': ['percentage_low', 'optional'], 'percentage_high': ['percentage_high', 'optional'], 'generate_method': ['generate_method', 'required'], 'max_white': ['max_white', 'optional'], 'max_magenta': ['max_magenta', 'optional'], 'pixel_type': ['pixel_type', 'required'], 'max_cyan': ['max_cyan', 'optional'], 'raster': ['in_raster', 'required'], 'max_red': ['max_red', 'optional'], 'max_black': ['max_black', 'optional'], 'max_green': ['max_green', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'GenerateExcludeArea', inputs, in_db, out_db)


def import_mosaic_dataset_geometry(mosaic_dataset, target_featureclass_type, target_jofield, input_featureclass, input_jofield):
     """
     Geoprocessing tool that imports geometry to a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_featureclass_type              Required String. Target Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_jofield                         Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_featureclass                    Required Feature Layer or Raster Catalog Layer. Input Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_jofield                        Required Field. Target Join Field
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'target_featureclass_type': ['target_featureclass_type', 'required'], 'input_jofield': ['input_join_field', 'required'], 'input_featureclass': ['input_featureclass', 'required'], 'target_jofield': ['target_join_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportMosaicDatasetGeometry', inputs, in_db, out_db)


def remove_rasters_from_mosaic_dataset(mosaic_dataset, where_clause=None, update_boundary='true', mark_overviews_items='true', delete_overview_images='true', delete_item_cache='true', remove_items='true', update_cellsize_ranges='true'):
     """
     Geoprocessing tool that removes rasters from a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mark_overviews_items                  Optional Boolean. Mark Affected Overviews. Default value: true. Value choices: mark_overview_items, no_mark_overview_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional Boolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     remove_items                          Optional Boolean. Remove Mosaic Dataset Items. Default value: true. Value choices: remove_mosaicdataset_items, no_remove_mosaicdataset_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_item_cache                     Optional Boolean. Delete Item Cache. Default value: true. Value choices: delete_item_cache, no_delete_item_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                Optional Boolean. Update Cell Size Ranges. Default value: true. Value choices: update_cell_sizes, no_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_overview_images                Optional Boolean. Delete Overview Images. Default value: true. Value choices: delete_overview_images, no_delete_overview_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'mark_overviews_items': ['mark_overviews_items', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'remove_items': ['remove_items', 'optional'], 'delete_item_cache': ['delete_item_cache', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'delete_overview_images': ['delete_overview_images', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RemoveRastersFromMosaicDataset', inputs, in_db, out_db)


def synchronize_mosaic_dataset(mosaic_dataset, where_clause=None, new_items='false', sync_only_stale='true', update_cellsize_ranges='true', update_boundary='true', update_overviews='false', build_pyramids='false', calculate_statistics='false', build_thumbnails='false', build_item_cache='false', rebuild_raster='true', update_fields='true', fields_to_update=None, existing_items='true', broken_items='false', skip_existing_items='true', refresh_aggregate_info='false', estimate_statistics='false'):
     """
     Geoprocessing tool that rebuilds the raster item and updates affected fields in the mosaic dataset using the raster type and options that were used when it was originally added.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rebuild_raster                        Optional Boolean. Rebuild Raster From Data Source. Default value: true. Value choices: rebuild_raster, no_raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields_to_update                      Optional Multiple Value. Fields To Update. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_fields                         Optional Boolean. Update Fields. Default value: true. Value choices: update_fields, no_fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional Boolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_thumbnails                      Optional Boolean. Build Thumbnails. Default value: false. Value choices: build_thumbnails, no_thumbnails
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     calculate_statistics                  Optional Boolean. Calculate Statistics. Default value: false. Value choices: calculate_statistics, no_statistics
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     broken_items                          Optional Boolean. Remove Items With Broken Data Source. Default value: false. Value choices: remove_broken_items, ignore_broken_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_item_cache                      Optional Boolean. Build Item Cache. Default value: false. Value choices: build_item_cache, no_item_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sync_only_stale                       Optional Boolean. Synchronize Stale Items Only. Default value: true. Value choices: sync_stale, sync_all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing_items                   Optional Boolean. Skip Existing Items. Default value: true. Value choices: skip_existing_items, overwrite_existing_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate_statistics                   Optional Boolean. Estimate Mosaic Dataset Statistics. Default value: false. Value choices: estimate_statistics, no_statistics
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_items                             Optional Boolean. Update With New Items. Default value: false. Value choices: update_with_new_items, no_new_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_pyramids                        Optional Boolean. Build Raster Pyramids. Default value: false. Value choices: build_pyramids, no_pyramids
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     existing_items                        Optional Boolean. Update Existing Items. Default value: true. Value choices: update_existing_items, ignore_existing_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     refresh_aggregate_info                Optional Boolean. Refresh Aggregate Information. Default value: false. Value choices: refresh_info, no_refresh_info
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                Optional Boolean. Update Cell Size Ranges. Default value: true. Value choices: update_cell_sizes, no_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_overviews                      Optional Boolean. Update Overviews. Default value: false. Value choices: update_overviews, no_overviews
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'rebuild_raster': ['rebuild_raster', 'optional'], 'fields_to_update': ['fields_to_update', 'optional'], 'update_fields': ['update_fields', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional'], 'broken_items': ['broken_items', 'optional'], 'build_item_cache': ['build_item_cache', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'sync_only_stale': ['sync_only_stale', 'optional'], 'skip_existing_items': ['skip_existing_items', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'new_items': ['new_items', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'existing_items': ['existing_items', 'optional'], 'refresh_aggregate_info': ['refresh_aggregate_info', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'update_overviews': ['update_overviews', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SynchronizeMosaicDataset', inputs, in_db, out_db)


def calculate_end_time(table, start_field, end_field, fields=None):
     """
     Geoprocessing tool that populates the values for a specified end time  field with values calculated using the specified start time field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     start_field                           Required Field. Start Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     end_field                             Required Field. End Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Optional Multiple Value. ID Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'start_field': ['start_field', 'required'], 'end_field': ['end_field', 'required'], 'fields': ['fields', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateEndTime', inputs, in_db, out_db)


def convert_time_field(table, input_time_field, input_time_format, output_time_field, output_time_type='date', output_time_format=None):
     """
     Geoprocessing tool to convert timestamps stored in a text or numeric field to a date field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_field                     Required String. Output Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_field                      Required Field. Input Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_format                     Required String. Input Time Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_time_type                      Optional String. Output Time Type. Default value: date. Value choices: date, text, long, short, double, float
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_time_format                    Optional String. Output Time Format. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'output_time_type': ['output_time_type', 'optional'], 'output_time_field': ['output_time_field', 'required'], 'input_time_field': ['input_time_field', 'required'], 'table': ['in_table', 'required'], 'input_time_format': ['input_time_format', 'required'], 'output_time_format': ['output_time_format', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeField', inputs, in_db, out_db)


def convert_time_zone(table, input_time_field, input_time_zone, output_time_field, output_time_zone, input_dst='true', output_dst='true'):
     """
     Geoprocessing tool to convert time values from one time zone to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_field                     Required String. Output Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_field                      Required Field. Input Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_zone                      Required String. Output Time Zone
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_zone                       Required String. Input Time Zone
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_dst                            Optional Boolean. Output time field values will be adjusted for Daylight Saving Time. Default value: true. Value choices: output_adjusted_for_dst, output_not_adjusted_for_dst
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_dst                             Optional Boolean. Input time field values are adjusted for Daylight Saving Time. Default value: true. Value choices: input_adjusted_for_dst, input_not_adjusted_for_dst
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'output_dst': ['output_dst', 'optional'], 'output_time_field': ['output_time_field', 'required'], 'input_time_field': ['input_time_field', 'required'], 'input_time_zone': ['input_time_zone', 'required'], 'table': ['in_table', 'required'], 'input_dst': ['input_dst', 'optional'], 'output_time_zone': ['output_time_zone', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeZone', inputs, in_db, out_db)


def transpose_fields(table, field, transposed_field_name, value_field_name, attribute_fields=None):
     """
     Geoprocessing tool to transpose data values stored in columns  of a table or feature class into rows.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Value Table. Fields To Transpose
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     transposed_field_name                 Required String. Transposed Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     value_field_name                      Required String. Value Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_fields                      Optional Multiple Value. Attribute Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'attribute_fields': ['attribute_fields', 'optional'], 'field': ['in_field', 'required'], 'transposed_field_name': ['in_transposed_field_name', 'required'], 'value_field_name': ['in_value_field_name', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'TransposeFields', inputs, in_db, out_db)


def warp_from_file(raster, link_file, transformation_type='polyorder1', resampling_type='nearest'):
     """
     Geoprocessing tool that performs a transformation on the raster based on a link file, using a polynomial transformation.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Raster Layer or Mosaic Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     link_file                             Required Text File. Link File
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional String. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   Optional String. Transformation Type. Default value: polyorder1. Value choices: polyorder0, polysimilarity, polyorder1, polyorder2, polyorder3, adjust, spline, projective
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'resampling_type': ['resampling_type', 'optional'], 'raster': ['in_raster', 'required'], 'transformation_type': ['transformation_type', 'optional'], 'link_file': ['link_file', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'WarpFromFile', inputs, in_db, out_db)


def import_xml_workspace_document(target_geodatabase, file, import_type='data', config_keyword=None):
     """
     Geoprocessing tool that imports the contents of an XML workspace document into an existing geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file                                  Required File. Import File
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_geodatabase                    Required Workspace. Target Geodatabase
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional String. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     import_type                           Optional String. Import Options. Default value: data. Value choices: data, schema_only
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'optional'], 'file': ['in_file', 'required'], 'import_type': ['import_type', 'optional'], 'target_geodatabase': ['target_geodatabase', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportXMLWorkspaceDocument', inputs, in_db, out_db)


def alter_mosaic_dataset_schema(mosaic_dataset, side_tables=None, raster_type_names=None, editor_tracking='false'):
     """
     Geoprocessing tool to define the editing operations nonowners have when editing a mosaic dataset in an enterprise geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_type_names                     Optional Multiple Value. Raster Types. Default value: none. Value choices: ads, cadrg/ecrg, cib, deimos-2, dmcii, dted, dubaisat-2, formosat-2, frame camera, gf-1 pms, gf-1 wfv, gf-2 pms, gf-4 pmi, grib, geoeye-1, hdf, hj 1a/1b ccd, hre, ikonos, jilin-1, kompsat-2, kompsat-3, las, landsat 1-5 mss, landsat 4-5 tm, landsat 7 etm+, landsat 8, ncdrd, nitf, netcdf, pleiades-1, quickbird, radarsat-2, rapideye, raster process definition, spot 5, spot 6, spot 7, scanned aerial imagery, sentinel-2, th-01, uav/uas, worldview-1, worldview-2, worldview-3, zy1-02c hrc, zy1-02c pms, zy3-cresda, zy3-sasmac
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     side_tables                           Optional Multiple Value. Operations. Default value: none. Value choices: analysis, boundary, cache, color_correction, definition, levels, log, overview, seamline, stereo, view
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     editor_tracking                       Optional Boolean. Enable Editor Tracking. Default value: false. Value choices: editor_tracking, no_editor_tracking
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'raster_type_names': ['raster_type_names', 'optional'], 'side_tables': ['side_tables', 'optional'], 'editor_tracking': ['editor_tracking', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterMosaicDatasetSchema', inputs, in_db, out_db)


def analyze_mosaic_dataset(mosaic_dataset, where_clause=None, checker_keywords=None):
     """
     Geoprocessing tool that checks a mosaic dataset for errors, and possible improvements.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     checker_keywords                      Optional Multiple Value. Checks Performed. Default value: none. Value choices: footprint, function, raster, paths, source_validity, stale, pyramids, statistics, performance, information
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'checker_keywords': ['checker_keywords', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AnalyzeMosaicDataset', inputs, in_db, out_db)


def compact(workspace):
     """
     Geoprocessing tool for compacting a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Required Workspace. Input File or Personal Geodatabase
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
     data                                  Optional Data Element or Layer. Input Workspace. Default value: none
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
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     include_system                        Required Boolean. Include System Tables
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasets                              Optional Multiple Value. Datasets to Analyze. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_archive                       Optional Boolean. Analyze Archive Tables for Selected Dataset(s). Default value: true. Value choices: analyze_archive, no_analyze_archive
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_base                          Optional Boolean. Analyze Base Tables for Selected Dataset(s). Default value: true. Value choices: analyze_base, no_analyze_base
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_delta                         Optional Boolean. Analyze Delta Tables for Selected Dataset(s). Default value: true. Value choices: analyze_delta, no_analyze_delta
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required'], 'analyze_archive': ['analyze_archive', 'optional'], 'analyze_base': ['analyze_base', 'optional'], 'analyze_delta': ['analyze_delta', 'optional'], 'datasets': ['in_datasets', 'optional'], 'include_system': ['include_system', 'required']}
     out_db = {}
     return _execute_tool('management', 'AnalyzeDatasets', inputs, in_db, out_db)


def rebuild_indexes(input_database, include_system, datasets=None, delta_only='true'):
     """
     Geoprocessing tool to update indexes of datasets stored in a database or geodatabase in DB2, Oracle, PostgreSQL, or SQL Server. In geodatabases, indexes  can also be rebuilt on  states and state_lineage geodatabase system tables and the delta tables of versioned datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     include_system                        Required Boolean. Include System Tables
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasets                              Optional Multiple Value. Datasets to Rebuild Indexes For. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delta_only                            Optional Boolean. Rebuild Delta Tables Only. Default value: true. Value choices: only_deltas, all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'datasets': ['in_datasets', 'optional'], 'input_database': ['input_database', 'required'], 'delta_only': ['delta_only', 'optional'], 'include_system': ['include_system', 'required']}
     out_db = {}
     return _execute_tool('management', 'RebuildIndexes', inputs, in_db, out_db)


def check_geometry(features):
     """
     Geoprocessing tool to generate a report of geometry problems in a feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required Multiple Value. Input Features
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'CheckGeometry', inputs, in_db, out_db)


def reconcile_versions(input_database, reconcile_mode, target_version=None, edit_versions=None, acquire_locks='true', abort_if_conflicts='false', conflict_definition='by_object', conflict_resolution='favor_target_version', with_post='false', with_delete='false'):
     """
     Geoprocessing tool that reconciles a version or multiple versions against a target version.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     reconcile_mode                        Required String. Reconcile Mode
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_versions                         Optional Multiple Value. Edit Versions. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     with_delete                           Optional Boolean. Delete Versions After Post. Default value: false. Value choices: delete_version, keep_version
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     abort_if_conflicts                    Optional Boolean. Abort if Conflicts Detected. Default value: false. Value choices: abort_conflicts, no_abort
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     conflict_resolution                   Optional String. Conflict Resolution. Default value: favor_target_version. Value choices: favor_target_version, favor_edit_version
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     acquire_locks                         Optional Boolean. Acquire Locks. Default value: true. Value choices: lock_acquired, no_lock_acquired
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     with_post                             Optional Boolean. Post Versions After Reconcile. Default value: false. Value choices: post, no_post
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        Optional String. Target Version. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     conflict_definition                   Optional String. Conflict Definition. Default value: by_object. Value choices: by_object, by_attribute
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required'], 'edit_versions': ['edit_versions', 'optional'], 'with_delete': ['with_delete', 'optional'], 'abort_if_conflicts': ['abort_if_conflicts', 'optional'], 'conflict_resolution': ['conflict_resolution', 'optional'], 'acquire_locks': ['acquire_locks', 'optional'], 'reconcile_mode': ['reconcile_mode', 'required'], 'with_post': ['with_post', 'optional'], 'target_version': ['target_version', 'optional'], 'conflict_definition': ['conflict_definition', 'optional']}
     out_db = {'log': ['out_log', 'optional', None, None]}
     return _execute_tool('management', 'ReconcileVersions', inputs, in_db, out_db)


def add_attachments(dataset, jofield, match_table, match_jofield, match_path_field, working_folder=None):
     """
     Geoprocessing tool that adds file attachments to the records of a geodatabase feature class or table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     match_table                           Required Table View. Match Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required Table View. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_jofield                         Required Field. Match Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_path_field                      Required Field. Match Path Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     working_folder                        Optional Folder. Working Folder. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'jofield': ['in_join_field', 'required'], 'match_jofield': ['in_match_join_field', 'required'], 'match_path_field': ['in_match_path_field', 'required'], 'match_table': ['in_match_table', 'required'], 'working_folder': ['in_working_folder', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddAttachments', inputs, in_db, out_db)


def disable_attachments(dataset):
     """
     Geoprocessing tool that disables attachments on a geodatabase feature class or table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Table View. Input Dataset
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
     dataset                               Required Table View. Input Dataset
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
     match_table                           Required Table View. Match Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required Table View. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_jofield                         Required Field. Match Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     match_name_field                      Optional Field. Match Name Field. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'match_table': ['in_match_table', 'required'], 'dataset': ['in_dataset', 'required'], 'jofield': ['in_join_field', 'required'], 'match_jofield': ['in_match_join_field', 'required'], 'match_name_field': ['in_match_name_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RemoveAttachments', inputs, in_db, out_db)


def set_mosaic_dataset_properties(mosaic_dataset, rows_maximum_imagesize='4100', columns_maximum_imagesize='15000', allowed_compressions='none;lz77;jpeg;lerc', default_compression_type=None, jpeg_quality='75', lerc_tolerance='0', resampling_type='bilinear', clip_to_footprints='false', footprints_may_contanodata='true', clip_to_boundary='true', color_correction='false', allowed_mensuration_capabilities=None, default_mensuration_capabilities='none', allowed_mosaic_methods='center;northwest;lockraster;byattribute;nadir;viewpoint;seamline;none', default_mosaic_method='center', order_field=None, order_base=None, sorting_order='true', mosaic_operator='first', blend_width='10', view_point_x='600', view_point_y='300', max_num_per_mosaic='20', cell_size_tolerance='0.8', cell_size=None, metadata_level='full', transmission_fields=None, use_time='false', start_time_field=None, end_time_field=None, time_format=None, geographic_transform=None, max_num_of_download_items='20', max_num_of_records_returned='1000', data_source_type='generic', minimum_pixel_contribution='1', processing_templates=None, default_processing_template='none', time_interval=None, time_interval_units=None):
     """
     Geoprocessing tool that sets the default properties of a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     columns_maximum_imagesize             Optional Long. Columns of Maximum Image Size of Requests. Default value: 15000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_compression_type              Optional String. Default Compression Type. Default value: none. Value choices: none, jpeg, lz77, lerc
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_interval_units                   Optional String. Time Interval Units. Default value: none. Value choices: none, milliseconds, seconds, minutes, hours, days, weeks, months, years, decades, centuries
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_compressions                  Optional Multiple Value. Allowed Transmission Compression. Default value: none;lz77;jpeg;lerc. Value choices: none, jpeg, lz77, lerc
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     processing_templates                  Optional Multiple Value. Processing Templates. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_mosaic_method                 Optional String. Default Mosaic Methods. Default value: center. Value choices: none, center, northwest, lockraster, byattribute, nadir, viewpoint, seamline
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_processing_template           Optional String. Default Processing Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_operator                       Optional String. Mosaic Operator. Default value: first. Value choices: first, last, min, max, mean, blend, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sorting_order                         Optional Boolean. Sorting Order Ascending. Default value: true. Value choices: ascending, descending
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional Cell Size XY. Output Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_to_footprints                    Optional Boolean. Clip To Footprints. Default value: false. Value choices: clip, not_clip
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_field                           Optional String. Order Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size_tolerance                   Optional Double. Cell Size Tolerance Factor. Default value: 0.8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     footprints_may_contanodata            Optional Boolean. Footprints May Contain NoData. Default value: true. Value choices: footprints_may_contain_nodata, footprints_do_not_contain_nodata
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_of_download_items             Optional Long. Max Number of Download Items. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     end_time_field                        Optional String. End Time Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     color_correction                      Optional Boolean. Color Correction. Default value: false. Value choices: apply, not_apply
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_interval                         Optional Double. Time Interval. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_format                           Optional String. Time Format. Default value: none. Value choices: yyyy, yyyymm, yyyy/mm, yyyy-mm, yyyymmdd, yyyy/mm/dd, yyyy-mm-dd, yyyymmddhhmmss, yyyy/mm/dd hh:mm:ss, yyyy-mm-dd hh:mm:ss, yyyymmddhhmmss.s, yyyy/mm/dd hh:mm:ss.s, yyyy-mm-dd hh:mm:ss.s
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_to_boundary                      Optional Boolean. Clip To Boundary. Default value: true. Value choices: clip, not_clip
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point_x                          Optional Double. View Point Spacing X. Default value: 600
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows_maximum_imagesize                Optional Long. Rows of Maximum Image Size of Requests. Default value: 4100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point_y                          Optional Double. View Point Spacing Y. Default value: 300
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_mensuration_capabilities      Optional Multiple Value. Allowed Mensuration Capabilities. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jpeg_quality                          Optional Long. JPEG Quality. Default value: 75
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_of_records_returned           Optional Long. Max Number of Records Returned. Default value: 1000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     metadata_level                        Optional String. Metadata Level. Default value: full. Value choices: none, basic, full
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     start_time_field                      Optional String. Start Time Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional String. Resampling Technique. Default value: bilinear. Value choices: nearest, bilinear, cubic, majority
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_mosaic_methods                Optional Multiple Value. Allowed Mosaic Methods. Default value: center;northwest;lockraster;byattribute;nadir;viewpoint;seamline;none. Value choices: none, center, northwest, lockraster, byattribute, nadir, viewpoint, seamline
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_base                            Optional String. Order Base. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_pixel_contribution            Optional Long. Minimum Pixel Contribution. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width                           Optional Long. Blend Width. Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_mensuration_capabilities      Optional String. Default Mensuration. Default value: none. Value choices: none, basic, base-top height, base-top shadow height, top-top shadow height, 3d
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lerc_tolerance                        Optional Double. LERC Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geographic_transform                  Optional Multiple Value. Geographic Transformation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_per_mosaic                    Optional Long. Max Number Per Mosaic. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transmission_fields                   Optional Multiple Value. Allowed Transmission Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_time                              Optional Boolean. Use Time. Default value: false. Value choices: enabled, disabled
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_source_type                      Optional String. Data Source Type. Default value: generic. Value choices: generic, thematic, processed, elevation, scientific, vector_uv, vector_magdir
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'columns_maximum_imagesize': ['columns_maximum_imagesize', 'optional'], 'default_mensuration_capabilities': ['default_mensuration_capabilities', 'optional'], 'time_interval_units': ['time_interval_units', 'optional'], 'allowed_compressions': ['allowed_compressions', 'optional'], 'processing_templates': ['processing_templates', 'optional'], 'default_mosaic_method': ['default_mosaic_method', 'optional'], 'default_processing_template': ['default_processing_template', 'optional'], 'time_interval': ['time_interval', 'optional'], 'mosaic_operator': ['mosaic_operator', 'optional'], 'sorting_order': ['sorting_order', 'optional'], 'cell_size': ['cell_size', 'optional'], 'clip_to_footprints': ['clip_to_footprints', 'optional'], 'order_field': ['order_field', 'optional'], 'cell_size_tolerance': ['cell_size_tolerance', 'optional'], 'footprints_may_contanodata': ['footprints_may_contain_nodata', 'optional'], 'max_num_of_download_items': ['max_num_of_download_items', 'optional'], 'end_time_field': ['end_time_field', 'optional'], 'view_point_x': ['view_point_x', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'time_format': ['time_format', 'optional'], 'clip_to_boundary': ['clip_to_boundary', 'optional'], 'color_correction': ['color_correction', 'optional'], 'rows_maximum_imagesize': ['rows_maximum_imagesize', 'optional'], 'view_point_y': ['view_point_y', 'optional'], 'allowed_mensuration_capabilities': ['allowed_mensuration_capabilities', 'optional'], 'jpeg_quality': ['JPEG_quality', 'optional'], 'max_num_of_records_returned': ['max_num_of_records_returned', 'optional'], 'metadata_level': ['metadata_level', 'optional'], 'start_time_field': ['start_time_field', 'optional'], 'resampling_type': ['resampling_type', 'optional'], 'allowed_mosaic_methods': ['allowed_mosaic_methods', 'optional'], 'order_base': ['order_base', 'optional'], 'minimum_pixel_contribution': ['minimum_pixel_contribution', 'optional'], 'blend_width': ['blend_width', 'optional'], 'default_compression_type': ['default_compression_type', 'optional'], 'lerc_tolerance': ['LERC_Tolerance', 'optional'], 'geographic_transform': ['geographic_transform', 'optional'], 'max_num_per_mosaic': ['max_num_per_mosaic', 'optional'], 'transmission_fields': ['transmission_fields', 'optional'], 'use_time': ['use_time', 'optional'], 'data_source_type': ['data_source_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetMosaicDatasetProperties', inputs, in_db, out_db)


def set_raster_properties(raster, data_type=None, statistics=None, stats_file=None, nodata=None, key_properties=None):
     """
     Geoprocessing tool that sets properties on a raster dataset or mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Mosaic Layer or Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     key_properties                        Optional Value Table. Key Properties. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     stats_file                            Optional File. Import Statistics From File. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics                            Optional Value Table. Statistics Per Band. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional String. Data Source Type. Default value: none. Value choices: generic, elevation, thematic, processed, scientific, vector_uv, vector_magdir
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata                                Optional Value Table. Bands for NoData Value. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'key_properties': ['key_properties', 'optional'], 'stats_file': ['stats_file', 'optional'], 'statistics': ['statistics', 'optional'], 'data_type': ['data_type', 'optional'], 'nodata': ['nodata', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetRasterProperties', inputs, in_db, out_db)


def download_rasters(image_service, out_folder, where_clause=None, selection_feature=None, clipping='false', convert_rasters='false', format='tiff', compression_method=None, compression_quality=None, maintain_folder='false'):
     """
     Geoprocessing tool that downloads source files of the selected rasters from an image service to a designated location.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     image_service                         Required Image Service or String or Mosaic Layer or Raster Layer. Input Image Service
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder                            Required Folder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintain_folder                       Optional Boolean. Maintain Folder Structure. Default value: false. Value choices: maintain_folder, no_maintain_folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_feature                     Optional Extent. Selection Feature. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional Long. Compression Quality. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Expression. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     convert_rasters                       Optional Boolean. Convert Rasters. Default value: false. Value choices: always_convert, convert_as_required
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional String. Output Format. Default value: tiff. Value choices: tiff, bil, bsq, bip, bmp, envi, imagine image, jpeg, gif, jp2, png
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    Optional String. Compression Method. Default value: none. Value choices: none, jpeg, lzw, packbits, rle, ccitt_group3, ccitt_group4, ccitt_1d
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clipping                              Optional Boolean. Clipping Using Selection Feature. Default value: false. Value choices: clipping, no_clipping
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'convert_rasters': ['convert_rasters', 'optional'], 'maintain_folder': ['MAINTAIN_FOLDER', 'optional'], 'selection_feature': ['selection_feature', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'compression_method': ['compression_method', 'optional'], 'where_clause': ['where_clause', 'optional'], 'image_service': ['in_image_service', 'required'], 'out_folder': ['out_folder', 'required'], 'format': ['format', 'optional'], 'clipping': ['clipping', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DownloadRasters', inputs, in_db, out_db)


def create_enterprise_geodatabase(database_platform, instance_name, authorization_file, database_name=None, account_authentication='false', database_admin='sa', database_admpassword=None, sde_schema='true', gdb_admname='sde', gdb_admpassword=None, tablespace_name=None):
     """
     Geoprocessing tool that creates a database, geodatabase, and geodatabase administrator user in a Microsoft SQL Server  or PostgreSQL DBMS and creates a geodatabase, tablespace, and geodatabase administrator user in an Oracle DBMS.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_platform                     Required String. Database Platform
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     instance_name                         Required String. Instance
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     authorization_file                    Required File. Authorization File
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_admpassword                  Optional Encrypted String. Database Administrator Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_name                         Optional String. Database. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gdb_admname                           Optional String. Geodatabase Administrator. Default value: sde
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_admin                        Optional String. Database Administrator. Default value: sa
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tablespace_name                       Optional String. Tablespace Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gdb_admpassword                       Optional Encrypted String. Geodatabase Administrator Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     account_authentication                Optional Boolean. Operating System Authentication. Default value: false. Value choices: operating_system_auth, database_auth
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sde_schema                            Optional Boolean. Sde Owned Schema. Default value: true. Value choices: sde_schema, dbo_schema
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'database_admpassword': ['database_admin_password', 'optional'], 'database_platform': ['database_platform', 'required'], 'database_name': ['database_name', 'optional'], 'instance_name': ['instance_name', 'required'], 'gdb_admname': ['gdb_admin_name', 'optional'], 'database_admin': ['database_admin', 'optional'], 'authorization_file': ['authorization_file', 'required'], 'tablespace_name': ['tablespace_name', 'optional'], 'gdb_admpassword': ['gdb_admin_password', 'optional'], 'account_authentication': ['account_authentication', 'optional'], 'sde_schema': ['sde_schema', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateEnterpriseGeodatabase', inputs, in_db, out_db)


def enable_enterprise_geodatabase(input_database, authorization_file):
     """
     Geoprocessing tool that creates geodatabase system tables, stored procedures, functions, and types in an existing database.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     authorization_file                    Required File. Authorization File
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
     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     single_envelope                       Optional Boolean. Create multipart features. Default value: false. Value choices: multipart, singlepart
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'single_envelope': ['single_envelope', 'optional'], 'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureEnvelopeToPolygon', inputs, in_db, out_db)


def create_database_connection(out_folder_path, out_name, database_platform, instance, account_authentication='true', username=None, password=None, save_user_pass='true', database=None, schema=None, version_type='transactional', version=None, date=None):
     """
     Geoprocessing tool for creating connection files to databases or enterprise, workgroup, or desktop geodatabases.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_platform                     Required String. Database Platform
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required String. Connection File Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder_path                       Required Folder. Connection File Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     instance                              Required String. Instance
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database                              Optional String. Database. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     username                              Optional String. Username. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     password                              Optional Encrypted String. Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     date                                  Optional Date. Date and Time. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_type                          Optional String. Version Type. Default value: transactional. Value choices: transactional, historical, point_in_time
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               Optional String. The following version will be used. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     account_authentication                Optional Boolean. Database Authentication. Default value: true. Value choices: database_auth, operating_system_auth
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     save_user_pass                        Optional Boolean. Save username and password. Default value: true. Value choices: save_username, do_not_save_username
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     schema                                Optional String. Schema (Oracle user schema geodatabases only). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'database_platform': ['database_platform', 'required'], 'version': ['version', 'optional'], 'date': ['date', 'optional'], 'password': ['password', 'optional'], 'schema': ['schema', 'optional'], 'database': ['database', 'optional'], 'out_name': ['out_name', 'required'], 'username': ['username', 'optional'], 'version_type': ['version_type', 'optional'], 'save_user_pass': ['save_user_pass', 'optional'], 'out_folder_path': ['out_folder_path', 'required'], 'account_authentication': ['account_authentication', 'optional'], 'instance': ['instance', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseConnection', inputs, in_db, out_db)


def delete_mosaic_dataset(mosaic_dataset, delete_overview_images='true', delete_item_cache='true'):
     """
     Geoprocessing tool that deletes a mosaic dataset, overviews, and item cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_overview_images                Optional Boolean. Delete Overview Images. Default value: true. Value choices: delete_overview_images, no_delete_overview_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_item_cache                     Optional Boolean. Delete Item Cache. Default value: true. Value choices: delete_item_cache, no_delete_item_cache
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'delete_overview_images': ['delete_overview_images', 'optional'], 'delete_item_cache': ['delete_item_cache', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DeleteMosaicDataset', inputs, in_db, out_db)


def generate_attachment_match_table(dataset, folder, key_field, file_filter=None, use_relative_paths='true'):
     """
     Geoprocessing tool that creates a Match Table to be used with the Add Attachments and Remove Attachment tools.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     folder                                Required Folder. Input Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required Table View. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     key_field                             Required Field. Key Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file_filter                           Optional String. Input Data Filter. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_relative_paths                    Optional Boolean. Store Relative Path. Default value: true. Value choices: relative, absolute
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'folder': ['in_folder', 'required'], 'dataset': ['in_dataset', 'required'], 'use_relative_paths': ['in_use_relative_paths', 'optional'], 'key_field': ['in_key_field', 'required'], 'file_filter': ['in_file_filter', 'optional']}
     out_db = {'match_table': ['out_match_table', 'required', None, None]}
     return _execute_tool('management', 'GenerateAttachmentMatchTable', inputs, in_db, out_db)


def create_database_view(input_database, view_name, view_definition):
     """
     Geoprocessing tool for creating a view in a database or enterprise geodatabase based on an SQL expression.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     view_definition                       Required String. View Definition
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     view_name                             Required String. Output View Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required'], 'view_definition': ['view_definition', 'required'], 'view_name': ['view_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseView', inputs, in_db, out_db)


def sort_coded_value_domain(workspace, domaname, sort_by, sort_order):
     """
     Geoprocessing tool that sorts the code or description of a coded value domain in either ascending or descending order.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_by                               Required String. Sort By
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_order                            Required String. Sort Order
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required Workspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required String. Domain Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'sort_by': ['sort_by', 'required'], 'sort_order': ['sort_order', 'required'], 'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'SortCodedValueDomain', inputs, in_db, out_db)


def disable_editor_tracking(dataset, creator='true', creation_date='true', last_editor='true', last_edit_date='true'):
     """
     Geoprocessing tool to disable editor tracking on a feature class, table, mosaic dataset, or raster catalog.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Dataset. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creator                               Optional Boolean. Disable Creator Tracking. Default value: true. Value choices: disable_creator, no_disable_creator
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_editor                           Optional Boolean. Disable Last Editor Tracking. Default value: true. Value choices: disable_last_editor, no_disable_last_editor
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creation_date                         Optional Boolean. Disable Creation Date Tracking. Default value: true. Value choices: disable_creation_date, no_disable_creation_date
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_edit_date                        Optional Boolean. Disable Last Edit Date Tracking. Default value: true. Value choices: disable_last_edit_date, no_disable_last_edit_date
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'creator': ['creator', 'optional'], 'dataset': ['in_dataset', 'required'], 'last_editor': ['last_editor', 'optional'], 'creation_date': ['creation_date', 'optional'], 'last_edit_date': ['last_edit_date', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DisableEditorTracking', inputs, in_db, out_db)


def enable_editor_tracking(dataset, creator_field=None, creation_date_field=None, last_editor_field=None, last_edit_date_field=None, add_fields=None, record_dates_in='utc'):
     """
     Geoprocessing tool to enable  editor tracking for a feature class, table, mosaic dataset, or raster catalog.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Dataset. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     record_dates_in                       Optional String. Record Dates in. Default value: utc. Value choices: utc, database_time
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creator_field                         Optional String. Creator Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_edit_date_field                  Optional String. Last Edit Date Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creation_date_field                   Optional String. Creation Date Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_editor_field                     Optional String. Last Editor Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     add_fields                            Optional Boolean. Add fields if they don't exist. Default value: none. Value choices: add_fields, no_add_fields
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'record_dates_in': ['record_dates_in', 'optional'], 'dataset': ['in_dataset', 'required'], 'last_edit_date_field': ['last_edit_date_field', 'optional'], 'add_fields': ['add_fields', 'optional'], 'last_editor_field': ['last_editor_field', 'optional'], 'creation_date_field': ['creation_date_field', 'optional'], 'creator_field': ['creator_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'EnableEditorTracking', inputs, in_db, out_db)


def truncate_table(table):
     """
     Geoprocessing tool for truncating a table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
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
     dataset                               Required Parcel Fabric Layer or Mosaic Layer or Network Dataset Layer. Dataset to upgrade
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'UpgradeDataset', inputs, in_db, out_db)


def export_mosaic_dataset_paths(mosaic_dataset, where_clause=None, export_mode='all', types_of_paths=None):
     """
     Geoprocessing tool that creates a table listing the paths to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     types_of_paths                        Optional Multiple Value. Types of paths to export. Default value: none. Value choices: raster, item_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     export_mode                           Optional String. Export Mode. Default value: all. Value choices: all, broken
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'export_mode': ['export_mode', 'optional'], 'types_of_paths': ['types_of_paths', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'ExportMosaicDatasetPaths', inputs, in_db, out_db)


def repair_mosaic_dataset_paths(mosaic_dataset, paths_list, where_clause=None):
     """
     Geoprocessing tool that repairs broken file paths within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     paths_list                            Required Value Table. Paths List
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'paths_list': ['paths_list', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RepairMosaicDatasetPaths', inputs, in_db, out_db)


def create_database_user(input_database, user_name, user_authentication_type='false', user_password=None, role=None, tablespace_name=None):
     """
     Geoprocessing tool to create a database user in an Oracle, PostgreSQL, or Microsoft SQL Server database.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     user_name                             Required String. Database User
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_authentication_type              Optional Boolean. Create Operating System Authenticated User. Default value: false. Value choices: operating_system_user, database_user
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_password                         Optional Encrypted String. Database User Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tablespace_name                       Optional String. Tablespace Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     role                                  Optional String. Role. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'user_authentication_type': ['user_authentication_type', 'optional'], 'tablespace_name': ['tablespace_name', 'optional'], 'input_database': ['input_database', 'required'], 'user_password': ['user_password', 'optional'], 'user_name': ['user_name', 'required'], 'role': ['role', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseUser', inputs, in_db, out_db)


def join_field(data, field, jotable, jofield, fields=None):
     """
     Geoprocessing tool that permanently joins the contents of a table to another table based on a common attribute field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jotable                               Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Join Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jofield                               Required Field. Output Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     data                                  Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Optional Multiple Value. Join Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'jotable': ['join_table', 'required'], 'field': ['in_field', 'required'], 'jofield': ['join_field', 'required'], 'data': ['in_data', 'required'], 'fields': ['fields', 'optional']}
     out_db = {}
     return _execute_tool('management', 'JoinField', inputs, in_db, out_db)


def edit_raster_function(mosaic_dataset, edit_mosaic_dataset_item='false', edit_options='insert', function_chadefinition=None, location_function_name=None):
     """
     Geoprocessing tool that adds, replaces, or removes a raster function template in a mosaic dataset, items in a mosaic dataset, or a raster layer that contains a raster function.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer or Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_options                          Optional String. Edit Options. Default value: insert. Value choices: insert, replace, remove
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_function_name                Optional String. Function Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     function_chadefinition                Optional File. Raster Function Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_mosaic_dataset_item              Optional Boolean. Mosaic Dataset Items. Default value: false. Value choices: edit_mosaic_dataset_item, edit_mosaic_dataset
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'edit_options': ['edit_options', 'optional'], 'location_function_name': ['location_function_name', 'optional'], 'function_chadefinition': ['function_chain_definition', 'optional'], 'edit_mosaic_dataset_item': ['edit_mosaic_dataset_item', 'optional']}
     out_db = {}
     return _execute_tool('management', 'EditRasterFunction', inputs, in_db, out_db)


def build_mosaic_dataset_item_cache(mosaic_dataset, where_clause=None, define_cache='true', generate_cache='true', item_cache_folder=None, compression_method='lossless', compression_quality='80', max_allowed_rows='200000', max_allowed_columns='200000', request_size_type='pixel_size_factor', request_size='1'):
     """
     Geoprocessing tool that inserts the Cached Raster function into the function chain for items within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size_type                     Optional String. Request Size Type. Default value: pixel_size_factor. Value choices: pixel_size, pixel_size_factor
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_cache                        Optional Boolean. Generate Cache. Default value: true. Value choices: generate_cache, no_generate_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          Optional Double. Request Size. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional Long. Compression Quality. Default value: 80
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_allowed_columns                   Optional Long. Maximum Allowed Columns. Default value: 200000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     define_cache                          Optional Boolean. Define Cache. Default value: true. Value choices: define_cache, no_define_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_allowed_rows                      Optional Long. Maximum Allowed Rows. Default value: 200000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     item_cache_folder                     Optional Workspace. Cache Path. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    Optional String. Compression Method. Default value: lossless. Value choices: none, lossless, lossy
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'request_size_type': ['request_size_type', 'optional'], 'generate_cache': ['generate_cache', 'optional'], 'request_size': ['request_size', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'max_allowed_columns': ['max_allowed_columns', 'optional'], 'define_cache': ['define_cache', 'optional'], 'max_allowed_rows': ['max_allowed_rows', 'optional'], 'item_cache_folder': ['item_cache_folder', 'optional'], 'compression_method': ['compression_method', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildMosaicDatasetItemCache', inputs, in_db, out_db)


def batch_build_pyramids(input_raster_datasets, pyramid_levels='-1', skip_first_level='false', pyramid_resampling_technique='nearest', pyramid_compression_type='default', compression_quality='75', skip_existing=None):
     """


     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_raster_datasets                 Required Multiple Value. Input Raster Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_levels                        Optional Long. Pyramid levels. Default value: -1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional Boolean. Skip Existing. Default value: none. Value choices: overwrite, skip_existing
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_resampling_technique          Optional String. Pyramid resampling technique. Default value: nearest. Value choices: nearest, bilinear, cubic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_first_level                      Optional Boolean. Skip first level. Default value: false. Value choices: skip_first, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_compression_type              Optional String. Pyramid compression type. Default value: default. Value choices: default, jpeg, lz77, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional Long. Compression quality. Default value: 75
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['Skip_Existing', 'optional'], 'pyramid_levels': ['Pyramid_levels', 'optional'], 'compression_quality': ['Compression_quality', 'optional'], 'pyramid_resampling_technique': ['Pyramid_resampling_technique', 'optional'], 'pyramid_compression_type': ['Pyramid_compression_type', 'optional'], 'skip_first_level': ['Skip_first_level', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required']}
     out_db = {}
     return _execute_tool('management', 'BatchBuildPyramids', inputs, in_db, out_db)


def batch_calculate_statistics(input_raster_datasets, number_of_columns_to_skip='1', number_of_rows_to_skip='1', ignore_values=None, skip_existing=None):
     """


     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_raster_datasets                 Required Multiple Value. Input Raster Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_columns_to_skip             Optional Long. Number of columns to skip. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional Boolean. Skip Existing. Default value: none. Value choices: overwrite, skip_existing
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_values                         Optional Multiple Value. Ignore values. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_rows_to_skip                Optional Long. Number of rows to skip. Default value: 1
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['Skip_Existing', 'optional'], 'number_of_columns_to_skip': ['Number_of_columns_to_skip', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required'], 'ignore_values': ['Ignore_values', 'optional'], 'number_of_rows_to_skip': ['Number_of_rows_to_skip', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchCalculateStatistics', inputs, in_db, out_db)


def sort(dataset, sort_field, spatial_sort_method='ur'):
     """
     Geoprocessing tool that reorders records in a feature class or table based on field values.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Table View. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_field                            Required Value Table. Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_sort_method                   Optional String. Spatial Sort Method. Default value: ur. Value choices: ul, ur, ll, lr, peano
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'sort_field': ['sort_field', 'required'], 'spatial_sort_method': ['spatial_sort_method', 'optional']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'Sort', inputs, in_db, out_db)


def match_photos_to_rows_by_time(input_folder, input_table, time_field, add_photos_as_attachments='false', time_tolerance='0', clock_offset='0'):
     """


     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_field                            Required Field. Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_folder                          Required Folder. Input Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_table                           Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_tolerance                        Optional Double. Time Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     add_photos_as_attachments             Optional Boolean. Add Photos As Attachments. Default value: false. Value choices: add_attachments, no_attachments
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clock_offset                          Optional Double. Clock Offset. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'time_field': ['Time_Field', 'required'], 'input_folder': ['Input_Folder', 'required'], 'time_tolerance': ['Time_Tolerance', 'optional'], 'add_photos_as_attachments': ['Add_Photos_As_Attachments', 'optional'], 'clock_offset': ['Clock_Offset', 'optional'], 'input_table': ['Input_Table', 'required']}
     out_db = {'output_table': ['Output_Table', 'required', None, None], 'unmatched_photos_table': ['Unmatched_Photos_Table', 'optional', None, None]}
     return _execute_tool('management', 'MatchPhotosToRowsByTime', inputs, in_db, out_db)


def register_raster(raster, register_mode, reference_raster=None, input_link_file=None, transformation_type='polyorder1', maximum_rms_value=None):
     """
     Geoprocessing tool that registers an image to a reference image.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required Raster Dataset or Raster Layer or Mosaic Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     register_mode                         Required String. Register Mode
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_rms_value                     Optional Double. Maximum RMS. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     reference_raster                      Optional Raster Layer or Raster Dataset or Image Service or MapServer or WMS Map or Mosaic Layer or Internet Tiled Layer or Map Server Layer. Reference Raster. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   Optional String. Transformation Type. Default value: polyorder1. Value choices: polyorder0, polysimilarity, polyorder1, polyorder2, polyorder3, projective, spline, adjust
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_link_file                       Optional Text File. Input Link File. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'maximum_rms_value': ['maximum_rms_value', 'optional'], 'reference_raster': ['reference_raster', 'optional'], 'raster': ['in_raster', 'required'], 'register_mode': ['register_mode', 'required'], 'transformation_type': ['transformation_type', 'optional'], 'input_link_file': ['input_link_file', 'optional']}
     out_db = {'output_cpt_link_file': ['output_cpt_link_file', 'optional', None, None]}
     return _execute_tool('management', 'RegisterRaster', inputs, in_db, out_db)


def create_role(input_database, role, grant_revoke='grant', user_name=None):
     """
     Geoprocessing tool to create a database role in an Oracle, PostgreSQL, or Microsoft SQL Server database and add users to or remove them from the role.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     role                                  Required String. Role
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     grant_revoke                          Optional String. Grant To or Revoke From User(s). Default value: grant. Value choices: grant, revoke
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_name                             Optional String. User Name(s). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'grant_revoke': ['grant_revoke', 'optional'], 'input_database': ['input_database', 'required'], 'user_name': ['user_name', 'optional'], 'role': ['role', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateRole', inputs, in_db, out_db)


def export_tile_cache(cache_source, target_cache_folder, target_cache_name, export_cache_type='tile_cache', storage_format_type='compact', scales=None, area_of_interest='in_memory\{5c2a1be5-7672-4ab1-8e1e-8c853cb4de67}'):
     """
     Geoprocessing tool that exports tiles from an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_cache_name                     Required String. Output Tile Cache Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cache_source                          Required Raster Layer or Raster Dataset. Input Tile Cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_cache_folder                   Required Folder. Output Tile Cache Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     storage_format_type                   Optional String. Storage Format. Default value: compact. Value choices: compact, exploded
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional Multiple Value. Scales [Pixel Size] (Estimated Disk Space). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     export_cache_type                     Optional String. Export Cache As. Default value: tile_cache. Value choices: tile_cache, tile_package
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional Feature Set. Area of Interest. Default value: in_memory\{5c2a1be5-7672-4ab1-8e1e-8c853cb4de67}
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'target_cache_name': ['in_target_cache_name', 'required'], 'target_cache_folder': ['in_target_cache_folder', 'required'], 'area_of_interest': ['area_of_interest', 'optional'], 'storage_format_type': ['storage_format_type', 'optional'], 'export_cache_type': ['export_cache_type', 'optional'], 'cache_source': ['in_cache_source', 'required'], 'scales': ['scales', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ExportTileCache', inputs, in_db, out_db)


def generate_tile_cache_tiling_scheme(dataset, tiling_scheme_generation_method, number_of_scales, predefined_tiling_scheme=None, scales=None, scales_type='false', tile_origin='0 0', dpi='96', tile_size='256 x 256', tile_format='mixed', tile_compression_quality='75', storage_format='compact', lerc_error=None):
     """
     Geoprocessing tool that generates an XML tiling scheme file used to create tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Raster Layer or Mosaic Layer or ArcMap Document. Input Data Source
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     tiling_scheme_generation_method       Required String. Generation Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_scales                      Required Long. Number of Scales
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     predefined_tiling_scheme              Optional File. Predefined Tiling Scheme. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dpi                                   Optional Long. Dots (Pixels) Per Inch. Default value: 96
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_origin                           Optional Point. Tile Origin in map units. Default value: 0 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_compression_quality              Optional Long. Tile Compression Quality. Default value: 75
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales_type                           Optional Boolean. Cell Size. Default value: false. Value choices: cell_size, scale
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lerc_error                            Optional Double. LERC Error. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional Value Table. Scales. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_format                           Optional String. Tile Format. Default value: mixed. Value choices: png, png8, png24, png32, jpeg, mixed, lerc
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             Optional String. Tile Size (in pixels). Default value: 256 x 256. Value choices: 128 x 128, 256 x 256, 512 x 512, 1024 x 1024
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     storage_format                        Optional String. Storage Format. Default value: compact. Value choices: compact, exploded
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'tile_format': ['tile_format', 'optional'], 'dpi': ['dpi', 'optional'], 'dataset': ['in_dataset', 'required'], 'lerc_error': ['lerc_error', 'optional'], 'number_of_scales': ['number_of_scales', 'required'], 'predefined_tiling_scheme': ['predefined_tiling_scheme', 'optional'], 'tile_origin': ['tile_origin', 'optional'], 'tile_compression_quality': ['tile_compression_quality', 'optional'], 'scales_type': ['scales_type', 'optional'], 'scales': ['scales', 'optional'], 'tiling_scheme_generation_method': ['tiling_scheme_generation_method', 'required'], 'tile_size': ['tile_size', 'optional'], 'storage_format': ['storage_format', 'optional']}
     out_db = {'tiling_scheme': ['out_tiling_scheme', 'required', None, None]}
     return _execute_tool('management', 'GenerateTileCacheTilingScheme', inputs, in_db, out_db)


def import_tile_cache(cache_target, cache_source, scales=None, area_of_interest='in_memory\{d6ab050f-d3fd-409c-b375-61816774db6c}', overwrite='false'):
     """
     Geoprocessing tool that imports tiles from an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_source                          Required Raster Layer or File. Source Tile Cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cache_target                          Required Raster Layer. Target Tile Cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overwrite                             Optional Boolean. Overwrite Tiles. Default value: false. Value choices: overwrite, merge
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional Multiple Value. Scales [Pixel Size] (Estimated Disk Space). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional Feature Set. Area of Interest. Default value: in_memory\{d6ab050f-d3fd-409c-b375-61816774db6c}
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'overwrite': ['overwrite', 'optional'], 'cache_source': ['in_cache_source', 'required'], 'scales': ['scales', 'optional'], 'cache_target': ['in_cache_target', 'required'], 'area_of_interest': ['area_of_interest', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ImportTileCache', inputs, in_db, out_db)


def manage_tile_cache(cache_location, manage_mode, cache_name=None, datasource=None, tiling_scheme='arcgisonline_scheme', import_tiling_scheme=None, scales=None, area_of_interest='in_memory\{1084126b-abaa-4cb2-b931-966a25bad608}', max_cell_size=None, mcached_scale=None, max_cached_scale=None):
     """
     Geoprocessing tool that creates a tile cache or updates tiles in an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     manage_mode                           Required String. Manage Mode
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cache_location                        Required Raster Layer or Folder. Cache Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasource                            Optional Mosaic Layer or Raster Layer or ArcMap Document. Input Data Source. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tiling_scheme                         Optional String. Input Tiling Scheme. Default value: arcgisonline_scheme. Value choices: arcgisonline_scheme, arcgisonline+_scheme, arcgisonline_elevation_scheme, arcgisonline_elevation+_scheme, import_scheme
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cached_scale                      Optional Double. Maximum Cached Scale. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional Feature Set. Area of Interest. Default value: in_memory\{1084126b-abaa-4cb2-b931-966a25bad608}
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_name                            Optional String. Cache Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional Multiple Value. Scales [Pixel Size] (Estimated Disk Space). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mcached_scale                         Optional Double. Minimum Cached Scale. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     import_tiling_scheme                  Optional File or Image Service or MapServer. Import Tiling Scheme. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cell_size                         Optional Double. Maximum Source Cell Size. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'datasource': ['in_datasource', 'optional'], 'cache_name': ['in_cache_name', 'optional'], 'cache_location': ['in_cache_location', 'required'], 'max_cached_scale': ['max_cached_scale', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'manage_mode': ['manage_mode', 'required'], 'scales': ['scales', 'optional'], 'mcached_scale': ['min_cached_scale', 'optional'], 'tiling_scheme': ['tiling_scheme', 'optional'], 'max_cell_size': ['max_cell_size', 'optional'], 'import_tiling_scheme': ['import_tiling_scheme', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ManageTileCache', inputs, in_db, out_db)


def disable_archiving(dataset, preserve_history='true'):
     """
     Geoprocessing tool that disables archiving on a geodatabase feature class, table, or feature dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Table or Feature Class or Feature Dataset. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     preserve_history                      Optional Boolean. Preserve History Table. Default value: true. Value choices: preserve, delete
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
     dataset                               Required Table or Feature Class or Feature Dataset. Input Dataset
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
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     block_field                           Optional Field. Block Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_rows_per_merged_items             Optional Long. Maximum Allowed Rows Per Merged Item. Default value: 1000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'block_field': ['block_field', 'optional'], 'max_rows_per_merged_items': ['max_rows_per_merged_items', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MergeMosaicDatasetItems', inputs, in_db, out_db)


def split_mosaic_dataset_items(mosaic_dataset, where_clause=None):
     """
     Geoprocessing tool that splits mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
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
     panchromatic_image                    Required Raster Layer. Panchromatic Image
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster                                Required Mosaic Dataset or Mosaic Layer or Raster Dataset or Raster Layer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_indexes                          Optional String. Band Indexes. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'panchromatic_image': ['in_panchromatic_image', 'required'], 'band_indexes': ['band_indexes', 'optional'], 'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'ComputePansharpenWeights', inputs, in_db, out_db)


def project(dataset, out_coor_system, transform_method=None, coor_system=None, preserve_shape='false', max_deviation=None, vertical='false'):
     """
     Geoprocessing tool that projects spatial data from one coordinate system to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required Feature Layer or Feature Dataset. Input Dataset or Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_coor_system                       Required Coordinate System. Output Coordinate System
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_deviation                         Optional Linear unit. Maximum Offset Deviation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     preserve_shape                        Optional Boolean. Preserve Shape. Default value: false. Value choices: preserve_shape, no_preserve_shape
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     vertical                              Optional Boolean. Vertical. Default value: false. Value choices: vertical, no_vertical
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           Optional Coordinate System. Input Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transform_method                      Optional Multiple Value. Geographic Transformation. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'max_deviation': ['max_deviation', 'optional'], 'dataset': ['in_dataset', 'required'], 'out_coor_system': ['out_coor_system', 'required'], 'coor_system': ['in_coor_system', 'optional'], 'transform_method': ['transform_method', 'optional'], 'preserve_shape': ['preserve_shape', 'optional'], 'vertical': ['vertical', 'optional']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'Project', inputs, in_db, out_db)


def batch_project(input_feature_class_or_dataset, output_workspace, output_coordinate_system=None, template_dataset=None, transformation=None):
     """
     Geoprocessing tool to change the coordinate system of a set of input feature classes or feature datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_feature_class_or_dataset        Required Multiple Value. Input Feature Class or Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_workspace                      Required Workspace or Feature Dataset. Output Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation                        Optional String. Transformation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_coordinate_system              Optional Coordinate System. Output Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional Geodataset. Template dataset. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'transformation': ['Transformation', 'optional'], 'output_coordinate_system': ['Output_Coordinate_System', 'optional'], 'input_feature_class_or_dataset': ['Input_Feature_Class_or_Dataset', 'required'], 'output_workspace': ['Output_Workspace', 'required'], 'template_dataset': ['Template_dataset', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchProject', inputs, in_db, out_db)


def add_geometry_attributes(input_features, geometry_properties, length_unit=None, area_unit=None, coordinate_system=None):
     """


     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_properties                   Required Multiple Value. Geometry Properties
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_features                        Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system                     Optional Coordinate System. Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_unit                             Optional String. Area Unit. Default value: none. Value choices: acres, hectares, square_miles_us, square_kilometers, square_meters, square_feet_us, square_yards, square_nautical_miles
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     length_unit                           Optional String. Length Unit. Default value: none. Value choices: feet_us, meters, kilometers, miles_us, nautical_miles, yards
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'coordinate_system': ['Coordinate_System', 'optional'], 'geometry_properties': ['Geometry_Properties', 'required'], 'input_features': ['Input_Features', 'required'], 'area_unit': ['Area_Unit', 'optional'], 'length_unit': ['Length_Unit', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddGeometryAttributes', inputs, in_db, out_db)


def migrate_relationship_class(relationship_class):
     """
     Geoprocessing tool that migrates an ObjectID-based relationship class to a GlobalID-based relationship class

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     relationship_class                    Required Relationship Class. Input Relationship Class
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'relationship_class': ['in_relationship_class', 'required']}
     out_db = {}
     return _execute_tool('management', 'MigrateRelationshipClass', inputs, in_db, out_db)


def export_mosaic_dataset_geometry(mosaic_dataset, where_clause=None, geometry_type='footprint'):
     """
     Geoprocessing tool that exports feature classes for the footprint, boundary, or seamline of a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional String. Geometry Type. Default value: footprint. Value choices: footprint, boundary, seamline, level
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'geometry_type': ['geometry_type', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'ExportMosaicDatasetGeometry', inputs, in_db, out_db)


def export_mosaic_dataset_items(mosaic_dataset, out_folder, out_base_name=None, where_clause=None, format='tiff', nodata_value=None, clip_type=None, template_dataset=None, cell_size=None):
     """
     Geoprocessing tool that creates a copy of your processed images within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Layer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder                            Required Folder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_base_name                         Optional String. . Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_type                             Optional String. Clip Type. Default value: none. Value choices: none, extent, feature_class
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional Point. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional String. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional Extent. Clipping Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional String. Output Format. Default value: tiff. Value choices: tiff, bmp, envi, esri bil, esri bip, esri bsq, gif, grid, imagine image, jp2, jpeg, png
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional SQL Expression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'nodata_value': ['nodata_value', 'optional'], 'out_folder': ['out_folder', 'required'], 'clip_type': ['clip_type', 'optional'], 'cell_size': ['cell_size', 'optional'], 'out_base_name': ['out_base_name', 'optional'], 'template_dataset': ['template_dataset', 'optional'], 'where_clause': ['where_clause', 'optional'], 'format': ['format', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ExportMosaicDatasetItems', inputs, in_db, out_db)


def remove_field_conflict_filter(table, fields):
     """
     Geoprocessing tool for removing a field conflict filter to a geodatabase table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     fields                                Required Multiple Value. Field Name(s)
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
     input_database                        Required Workspace. Input Database Connection
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
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     file                                  Required File. Input File
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required'], 'file': ['in_file', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportGeodatabaseConfigurationKeywords', inputs, in_db, out_db)


def alter_field(table, field, new_field_name=None, new_field_alias=None, field_type='long', field_length=None, field_is_nullable='true', clear_field_alias='false'):
     """
     Geoprocessing tool  to alter the field properties of geodatabase tables and feature classes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required Table View or Raster Layer or Raster Catalog Layer or Mosaic Layer. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_nullable                     Optional Boolean. New Field IsNullable. Default value: true. Value choices: nullable, non_nullable
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_field_name                        Optional String. New Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_type                            Optional String. New Field Type. Default value: long. Value choices: text, float, double, short, long, date, blob, raster, guid
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_field_alias                     Optional Boolean. Clear Alias. Default value: false
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_field_alias                       Optional String. New Field Alias. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_length                          Optional Long. New Field Length. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_is_nullable': ['field_is_nullable', 'optional'], 'new_field_name': ['new_field_name', 'optional'], 'field': ['field', 'required'], 'table': ['in_table', 'required'], 'clear_field_alias': ['clear_field_alias', 'optional'], 'new_field_alias': ['new_field_alias', 'optional'], 'field_type': ['field_type', 'optional'], 'field_length': ['field_length', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterField', inputs, in_db, out_db)


def geodetic_densify(features, geodetic_type, distance='50 kilometers'):
     """
     Geoprocessing tool that replaces segments with densified approximation of geodetic curves.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geodetic_type                         Required String. Geodetic Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance                              Optional Linear unit. Distance. Default value: 50 kilometers
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'geodetic_type': ['geodetic_type', 'required'], 'features': ['in_features', 'required'], 'distance': ['distance', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'GeodeticDensify', inputs, in_db, out_db)


def configure_geodatabase_log_file_tables(input_database, log_file_type, log_file_pool_size=None, use_tempdb='false'):
     """
     Geoprocessing tool that allows you to alter the type of log file tables used by an enterprise geodatabase to maintain lists of records cached by ArcGIS.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     log_file_type                         Required String. Log File Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     log_file_pool_size                    Optional Long. Number of session based log file tables to be owned in a pool by the administrator. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_tempdb                            Optional Boolean. Create session based log files tables owned by each user in the TempDB database (SQL Server only). Default value: false. Value choices: use_tembdb, not_use_tembdb
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'use_tempdb': ['use_tempdb', 'optional'], 'log_file_type': ['log_file_type', 'required'], 'log_file_pool_size': ['log_file_pool_size', 'optional'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConfigureGeodatabaseLogFileTables', inputs, in_db, out_db)


def delete_schema_geodatabase(input_database):
     """
     Geoprocessing tool that deletes a user-schema geodatabase from a geodatabase in Oracle.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required Workspace. Input Database Connection
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
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_tables                          Optional Multiple Value. Input Tables. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        Optional String. Target version. Default value: none
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
     input_database                        Required Workspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_tables                          Optional Multiple Value. Input Tables. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        Optional String. Target Version. Default value: none
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
     input                                 Required File or String. Input
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
     topology                              Required Topology Layer. Input Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_basename                          Required String. Base Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              Required Workspace or Feature Dataset. Output Location
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'topology': ['in_topology', 'required'], 'out_basename': ['out_basename', 'required'], 'out_path': ['out_path', 'required']}
     out_db = {}
     return _execute_tool('management', 'ExportTopologyErrors', inputs, in_db, out_db)


def generate_raster_from_raster_function(raster_function, raster_function_arguments=None, raster_properties=None, format=None):
     """
     Geoprocessing tool that uses raster functions to process raster datasets and write an output.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_function                       Required File or String. Input Raster Function
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_properties                     Optional Value Table. Raster Properties. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional String. Format. Default value: none. Value choices: tiff, imagine image, esri grid, crf, mrf
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_function_arguments             Optional Value Table. Raster Function Arguments. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster_properties': ['raster_properties', 'optional'], 'format': ['format', 'optional'], 'raster_function': ['raster_function', 'required'], 'raster_function_arguments': ['raster_function_arguments', 'optional']}
     out_db = {'raster_dataset': ['out_raster_dataset', 'required', None, None]}
     return _execute_tool('management', 'GenerateRasterFromRasterFunction', inputs, in_db, out_db)


def generate_tessellation(extent, shape_type='hexagon', size=None, spatial_reference=None):
     """
     Geoprocessing tool that generates a feature class of a  tessellated grid of regular polygons to cover a given extent. The shapes can either be triangles, squares, or hexagons.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Required Extent. Extent
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     size                                  Optional Areal unit. Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shape_type                            Optional String. Shape Type. Default value: hexagon. Value choices: square, triangle, hexagon
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional Spatial Reference. Spatial Reference. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'extent': ['Extent', 'required'], 'shape_type': ['Shape_Type', 'optional'], 'size': ['Size', 'optional'], 'spatial_reference': ['Spatial_Reference', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'GenerateTessellation', inputs, in_db, out_db)


def create_fishnet(origcoord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, corner_coord=None, labels='true', template=None, geometry_type='polyline'):
     """
     Geoprocessing tool that creates a fishnet of rectangular cells.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     origcoord                             Required Point. Fishnet Origin Coordinate
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_rows                           Required Long. Number of Rows
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_height                           Required Double. Cell Size Height
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_columns                        Required Long. Number of Columns
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_width                            Required Double. Cell Size Width
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_axis_coord                          Required Point. Y-Axis Coordinate
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     corner_coord                          Optional Point. Opposite corner of Fishnet. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     labels                                Optional Boolean. Create Label Points. Default value: true. Value choices: labels, no_labels
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional Extent. Template Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional String. Geometry Type. Default value: polyline. Value choices: polyline, polygon
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'origcoord': ['origin_coord', 'required'], 'number_rows': ['number_rows', 'required'], 'cell_height': ['cell_height', 'required'], 'number_columns': ['number_columns', 'required'], 'corner_coord': ['corner_coord', 'optional'], 'cell_width': ['cell_width', 'required'], 'geometry_type': ['geometry_type', 'optional'], 'template': ['template', 'optional'], 'y_axis_coord': ['y_axis_coord', 'required'], 'labels': ['labels', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'CreateFishnet', inputs, in_db, out_db)


def create_random_points(out_path, out_name, constraining_feature_class=None, constraining_extent=None, number_of_points_or_field='100', minimum_allowed_distance='0 unknown', create_multipoint_output='false', multipoint_size='10'):
     """
     Geoprocessing tool that creates a specified number of random points in an extent window, inside polygon features, on point features, or along line features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              Required String. Output Point Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_path                              Required Workspace or Feature Dataset. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     multipoint_size                       Optional Long. Maximum Number of Points per Multipoint. Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_allowed_distance              Optional Linear unit or Field. Minimum Allowed Distance [value or field]. Default value: 0 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     constraining_feature_class            Optional Feature Layer. Constraining Feature Class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     constraining_extent                   Optional Extent or Feature Layer or Raster Layer. Constraining Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     create_multipoint_output              Optional Boolean. Create Multipoint Output. Default value: false. Value choices: multipoint, point
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_points_or_field             Optional Long or Field. Number of Points [value or field]. Default value: 100
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'minimum_allowed_distance': ['minimum_allowed_distance', 'optional'], 'constraining_feature_class': ['constraining_feature_class', 'optional'], 'out_path': ['out_path', 'required'], 'create_multipoint_output': ['create_multipoint_output', 'optional'], 'multipoint_size': ['multipoint_size', 'optional'], 'constraining_extent': ['constraining_extent', 'optional'], 'number_of_points_or_field': ['number_of_points_or_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomPoints', inputs, in_db, out_db)


def generate_points_along_lines(input_features, point_placement, distance=None, percentage=None, include_end_points=None):
     """


     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_placement                       Required String. Point Placement
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_features                        Required Feature Layer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_end_points                    Optional Boolean. Include End Points. Default value: none. Value choices: end_points, no_end_points
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage                            Optional Double. Percentage. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance                              Optional Linear unit. Distance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'include_end_points': ['Include_End_Points', 'optional'], 'point_placement': ['Point_Placement', 'required'], 'percentage': ['Percentage', 'optional'], 'input_features': ['Input_Features', 'required'], 'distance': ['Distance', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'GeneratePointsAlongLines', inputs, in_db, out_db)


def append_control_points(master_control_points, input_control_points, z_field=None, tag_field=None, dem=None, xy_accuracy=None, z_accuracy=None):
     """
     Geoprocessing tool that combines tie points and control points.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     master_control_points                 Required Feature Class or Feature Layer. Target Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_control_points                  Required Feature Class or Feature Layer. Input Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_field                               Optional Field. Z Value Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_accuracy                           Optional Double. XY Accuracy. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_accuracy                            Optional Double. Z Accuracy. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tag_field                             Optional Field. Tag Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dem                                   Optional Raster Layer or Mosaic Layer or Raster Dataset or Mosaic Dataset. Input DEM. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'z_field': ['in_z_field', 'optional'], 'master_control_points': ['in_master_control_points', 'required'], 'tag_field': ['in_tag_field', 'optional'], 'input_control_points': ['in_input_control_points', 'required'], 'dem': ['in_dem', 'optional'], 'xy_accuracy': ['in_xy_accuracy', 'optional'], 'z_accuracy': ['in_z_accuracy', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AppendControlPoints', inputs, in_db, out_db)


def apply_block_adjustment(mosaic_dataset, adjustment_operation, input_solution_table=None, pan_to_ms_scaling_factor=None, dem=None, zoffset=None, control_point_table=None, adjust_footprints='false'):
     """
     Geoprocessing tool that applies the geographic adjustments to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     adjustment_operation                  Required String. Adjustment Operation
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pan_to_ms_scaling_factor              Optional Double. Pan-To-MS Scaling Factor. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     adjust_footprints                     Optional Boolean. Adjust Footprints. Default value: false. Value choices: adjust_footprints, no_adjust_footprints
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dem                                   Optional Raster Dataset or Raster Layer or Mosaic Dataset or Mosaic Layer. Input DEM. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_point_table                   Optional Table View. Control Point Table. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     zoffset                               Optional Double. Z offset. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_solution_table                  Optional Table View. Input Solution Table. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'pan_to_ms_scaling_factor': ['pan_to_ms_scaling_factor', 'optional'], 'adjustment_operation': ['adjustment_operation', 'required'], 'dem': ['DEM', 'optional'], 'adjust_footprints': ['adjust_footprints', 'optional'], 'control_point_table': ['control_point_table', 'optional'], 'zoffset': ['zoffset', 'optional'], 'input_solution_table': ['input_solution_table', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ApplyBlockAdjustment', inputs, in_db, out_db)


def compute_block_adjustment(mosaic_dataset, control_points, transformation_type, maximum_residual_value='5', adjustment_options=None, location_accuracy='medium'):
     """
     Geoprocessing tool that computes the adjustments to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     transformation_type                   Required String. Transformation Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     control_points                        Required Feature Layer. Input Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     adjustment_options                    Optional Value Table. Adjustment Options. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     Optional String. Image Location Accuracy. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_residual_value                Optional Double. Maximum Residual. Default value: 5
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'location_accuracy': ['location_accuracy', 'optional'], 'maximum_residual_value': ['maximum_residual_value', 'optional'], 'adjustment_options': ['adjustment_options', 'optional'], 'transformation_type': ['transformation_type', 'required'], 'control_points': ['in_control_points', 'required']}
     out_db = {'quality_table': ['out_quality_table', 'optional', None, None], 'solution_table': ['out_solution_table', 'required', None, None], 'solution_point_table': ['out_solution_point_table', 'optional', None, None]}
     return _execute_tool('management', 'ComputeBlockAdjustment', inputs, in_db, out_db)


def compute_camera_model(mosaic_dataset, gps_accuracy='high', estimate='true', refine='true', apply_adjustment='true', maximum_residual='5', initial_tiepoint_resolution='8', maximum_overlap=None, minimum_coverage='0.2', remove='false', control_points=None, options=None):
     """
     Geoprocessing tool that automatically constructs and refines a camera model for aerial images and, in particular, UAV and UAS images, where the exterior and interior camera models are coarse or undefined.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     apply_adjustment                      Optional Boolean. Apply Adjustment. Default value: true. Value choices: apply, no_apply
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     initial_tiepoint_resolution           Optional Double. Initial Tie Point Resolution. Default value: 8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate                              Optional Boolean. Estimate Camera Model. Default value: true. Value choices: estimate, no_estimate
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     remove                                Optional Boolean. Remove Off-Strip Images. Default value: false. Value choices: remove, no_remove
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     refine                                Optional Boolean. Refine Camera Model. Default value: true. Value choices: refine, no_refine
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gps_accuracy                          Optional String. GPS Location Accuracy. Default value: high. Value choices: high, medium, low, very_low
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_coverage                      Optional Double. Minimum Control Point Coverage. Default value: 0.2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_residual                      Optional Double. Maximum Residual. Default value: 5
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_overlap                       Optional Double. Maximum Area Overlap. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     options                               Optional Value Table. Additional Options. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_points                        Optional Feature Class. Input Tie Point Table. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'apply_adjustment': ['apply_adjustment', 'optional'], 'estimate': ['estimate', 'optional'], 'remove': ['remove', 'optional'], 'gps_accuracy': ['gps_accuracy', 'optional'], 'initial_tiepoint_resolution': ['initial_tiepoint_resolution', 'optional'], 'maximum_overlap': ['maximum_overlap', 'optional'], 'options': ['options', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'minimum_coverage': ['minimum_coverage', 'optional'], 'refine': ['refine', 'optional'], 'maximum_residual': ['maximum_residual', 'optional'], 'control_points': ['in_control_points', 'optional']}
     out_db = {'flight_path': ['out_flight_path', 'optional', None, None], 'control_points': ['out_control_points', 'optional', None, None], 'solution_table': ['out_solution_table', 'optional', None, None], 'solution_point_table': ['out_solution_point_table', 'optional', None, None], 'dsm': ['out_dsm', 'optional', None, None]}
     return _execute_tool('management', 'ComputeCameraModel', inputs, in_db, out_db)


def compute_control_points(mosaic_dataset, reference_images, similarity='high', density='medium', distribution='random', area_of_interest=None, location_accuracy='medium'):
     """
     Geoprocessing tool that computes control points for your mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     reference_images                      Required Raster Layer or Raster Dataset or Image Service or MapServer or WMS Map or Mosaic Layer or Internet Tiled Layer or Map Server Layer. Input Reference Images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     similarity                            Optional String. Similarity. Default value: high. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional Feature Layer. Area of Interest. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          Optional String. Point Distribution. Default value: random. Value choices: random, regular
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     Optional String. Image Location Accuracy. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     density                               Optional String. Point Density. Default value: medium. Value choices: low, medium, high
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'similarity': ['similarity', 'optional'], 'reference_images': ['in_reference_images', 'required'], 'area_of_interest': ['area_of_interest', 'optional'], 'distribution': ['distribution', 'optional'], 'location_accuracy': ['location_accuracy', 'optional'], 'density': ['density', 'optional']}
     out_db = {'image_feature_points': ['out_image_feature_points', 'optional', None, None], 'control_points': ['out_control_points', 'required', None, None]}
     return _execute_tool('management', 'ComputeControlPoints', inputs, in_db, out_db)


def compute_tie_points(mosaic_dataset, similarity='medium', mask_dataset=None, density='medium', distribution='random', location_accuracy='medium'):
     """
     Geoprocessing tool that computes the tie points for the  items within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mask_dataset                          Optional Feature Layer. Input Mask. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     similarity                            Optional String. Similarity. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          Optional String. Point Distribution. Default value: random. Value choices: random, regular
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     Optional String. Image Location Accuracy. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     density                               Optional String. Point Density. Default value: medium. Value choices: low, medium, high
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'similarity': ['similarity', 'optional'], 'mask_dataset': ['in_mask_dataset', 'optional'], 'distribution': ['distribution', 'optional'], 'location_accuracy': ['location_accuracy', 'optional'], 'density': ['density', 'optional']}
     out_db = {'image_features': ['out_image_features', 'optional', None, None], 'control_points': ['out_control_points', 'required', None, None]}
     return _execute_tool('management', 'ComputeTiePoints', inputs, in_db, out_db)


def build_stereo_model(mosaic_dataset, minimum_angle='10', maximum_angle='70', minimum_overlap='0.5', maximum_diff_op=None, maximum_diff_gsd='2'):
     """
     Geoprocessing tool that generates a stereo model on imagery in a  mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_gsd                      Optional Double. Maximum GSD Difference. Default value: 2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_overlap                       Optional Double. Minimum Area Overlap. Default value: 0.5
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_angle                         Optional Double. Minimum Intersection Angle (in degree). Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_op                       Optional Double. Maximum Omega/Phi Difference (in degree). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_angle                         Optional Double. Maximum Intersection Angle (in degree). Default value: 70
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'minimum_angle': ['minimum_angle', 'optional'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'maximum_angle': ['maximum_angle', 'optional'], 'minimum_overlap': ['minimum_overlap', 'optional'], 'maximum_diff_gsd': ['maximum_diff_GSD', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildStereoModel', inputs, in_db, out_db)


def generate_point_cloud(mosaic_dataset, matching_method, object_size='50', ground_spacing=None, minimum_pairs='2', minimum_area='0.6', minimum_adjustment_quality='0.2', maximum_diff_gsd='2', maximum_diff_op='8'):
     """
     Geoprocessing tool that generates a 3D point cloud from stereo images.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     matching_method                       Required String. Matching Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ground_spacing                        Optional Double. DSM Ground Spacing (in meter). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_adjustment_quality            Optional Double. Adjustment Quality Threshold. Default value: 0.2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_op                       Optional Double. Omega/Phi Difference Threshold. Default value: 8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     object_size                           Optional Double. Maximum Object Size (in meter). Default value: 50
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_area                          Optional Double. Overlap Area Threshold. Default value: 0.6
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_gsd                      Optional Double. GSD Difference Threshold. Default value: 2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_pairs                         Optional Double. Number of Image Pairs. Default value: 2
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'matching_method': ['matching_method', 'required'], 'minimum_adjustment_quality': ['minimum_adjustment_quality', 'optional'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'ground_spacing': ['ground_spacing', 'optional'], 'object_size': ['object_size', 'optional'], 'minimum_area': ['minimum_area', 'optional'], 'maximum_diff_gsd': ['maximum_diff_gsd', 'optional'], 'minimum_pairs': ['minimum_pairs', 'optional']}
     out_db = {'folder': ['out_folder', 'required', None, None], 'base_name': ['out_base_name', 'required', None, None]}
     return _execute_tool('management', 'GeneratePointCloud', inputs, in_db, out_db)


def interpolate_from_point_cloud(container, cell_size, interpolation_method, smooth_method, surface_type='dtm', fill_dem=None):
     """
     Geoprocessing tool that interpolates a digital surface model (DSM) or digital elevation model (DEM) from a point cloud.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     interpolation_method                  Required String. Interpolation Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     smooth_method                         Required String. Smoothing Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     container                             Required Folder or File or Feature Layer. Input LAS Folder or Point Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_size                             Required Double. Cellsize
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fill_dem                              Optional Raster Dataset or Raster Layer or Mosaic Dataset or Mosaic Layer. Input Fill DEM. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     surface_type                          Optional String. Surface Type. Default value: dtm. Value choices: dtm, dsm
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fill_dem': ['fill_dem', 'optional'], 'container': ['in_container', 'required'], 'smooth_method': ['smooth_method', 'required'], 'surface_type': ['surface_type', 'optional'], 'interpolation_method': ['interpolation_method', 'required'], 'cell_size': ['cell_size', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'InterpolateFromPointCloud', inputs, in_db, out_db)


def compute_mosaic_candidates(mosaic_dataset, maximum_overlap='0.6', maximum_area_loss='0.05'):
     """
     Geoprocessing tool that finds the image candidates in a mosaic dataset that best represents the mosaic area, and will be used to generate an orthomosaic.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required Mosaic Dataset or Mosaic Layer. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_area_loss                     Optional Double. Maximum Area Loss Allowed. Default value: 0.05
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_overlap                       Optional Double. Maximum Area Overlap. Default value: 0.6
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_area_loss': ['maximum_area_loss', 'optional'], 'maximum_overlap': ['maximum_overlap', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ComputeMosaicCandidates', inputs, in_db, out_db)

