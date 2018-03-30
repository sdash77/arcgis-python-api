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
     rows                                  Required GPTableView. Input Rows
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
     rows                                  Required GPComposite. Input Rows
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional GPString. Configuration Keyword. Default value: none
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
     features                              Required GPComposite. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional GPString. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        Optional GPDouble. Output Spatial Grid 2. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        Optional GPDouble. Output Spatial Grid 1. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        Optional GPDouble. Output Spatial Grid 3. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'optional'], 'features': ['in_features', 'required'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'CopyFeatures', inputs, in_db, out_db)

          
def dissolve(features, dissolve_field=None, statistics_fields=None, multi_part='true', unsplit_lines='false'):
     """
     Geoprocessing tool used to aggregate features based on specified attributes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     multi_part                            Optional GPBoolean. Create multipart features. Default value: true. Value choices: multi_part, single_part
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     unsplit_lines                         Optional GPBoolean. Unsplit lines. Default value: false. Value choices: unsplit_lines, dissolve_lines
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics_fields                     Optional GPValueTable. Statistics Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        Optional GPMultiValue. Dissolve_Field(s). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'multi_part': ['multi_part', 'optional'], 'unsplit_lines': ['unsplit_lines', 'optional'], 'statistics_fields': ['statistics_fields', 'optional'], 'features': ['in_features', 'required'], 'dissolve_field': ['dissolve_field', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'Dissolve', inputs, in_db, out_db)

          
def make_feature_layer(features, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a feature layer from an input feature class or layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_info                            Optional GPFieldInfo. Field Info. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Expression. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Optional GPComposite. Workspace or Feature Dataset. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_info': ['field_info', 'optional'], 'features': ['in_features', 'required'], 'where_clause': ['where_clause', 'optional'], 'workspace': ['workspace', 'optional']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeFeatureLayer', inputs, in_db, out_db)

          
def save_to_layer_file(layer, is_relative_path=None, version='current'):
     """
     Geoprocessing tool that creates a layer file (.lyrx) that references geographic data stored on disk.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer                                 Required GPLayer. Input Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     is_relative_path                      Optional GPBoolean. Store Relative Path. Default value: none. Value choices: relative, absolute
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               Optional GPString. Layer Version. Default value: current. Value choices: current, 10.4, 10.3, 10.2, 10.1, 10, 9.3, 9.2, 9.1, 9.0, 8.3
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
     jofield                               Required Field. Output Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     layer_or_view                         Required GPComposite. Layer Name or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jotable                               Required GPComposite. Join Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jotype                                Optional GPBoolean. Keep All Target Features. Default value: true. Value choices: keep_all, keep_common
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'jotype': ['join_type', 'optional'], 'jofield': ['join_field', 'required'], 'layer_or_view': ['in_layer_or_view', 'required'], 'jotable': ['join_table', 'required'], 'field': ['in_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddJoin', inputs, in_db, out_db)

          
def remove_join(layer_or_view, joname=None):
     """
     Geoprocessing tool that removes a join from a feature layer or table view.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer_or_view                         Required GPComposite. Layer Name or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     joname                                Optional GPString. Join. Default value: none
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
     data                                  Required DEType. Input Data
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional GPString. Data type. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'required'], 'data_type': ['data_type', 'optional']}
     out_db = {'data': ['out_data', 'required', None, None]}
     return _execute_tool('management', 'Copy', inputs, in_db, out_db)

          
def delete(data, data_type=None):
     """
     Geoprocessing tool that permanently removes the specified item from disk.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data                                  Required GPComposite. Input Data Element
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional GPString. Data type. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'required'], 'data_type': ['data_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Delete', inputs, in_db, out_db)

          
def rename(data, data_type=None):
     """
     Geoprocessing tool that changes the name of a dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data                                  Required DEType. Input Data Element
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional GPString. Data type. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'required'], 'data_type': ['data_type', 'optional']}
     out_db = {'data': ['out_data', 'required', None, None]}
     return _execute_tool('management', 'Rename', inputs, in_db, out_db)

          
def create_folder(out_folder_path, out_name):
     """
     Geoprocessing tool that creates a folder.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder_path                       Required DEFolder. Folder Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. Folder Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_folder_path': ['out_folder_path', 'required'], 'out_name': ['out_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateFolder', inputs, in_db, out_db)

          
def create_feature_dataset(out_dataset_path, out_name, spatial_reference=None):
     """
     Geoprocessing tool that creates a feature dataset in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              Required GPString. Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_dataset_path                      Required DEWorkspace. Output Geodatabase
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Coordinate System. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_dataset_path': ['out_dataset_path', 'required'], 'spatial_reference': ['spatial_reference', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFeatureDataset', inputs, in_db, out_db)

          
def pivot_table(table, fields, pivot_field, value_field):
     """
     Geoprocessing tool that uses a pivot and value field to streamline the input table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Required GPMultiValue. Input Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     value_field                           Required Field. Value Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     pivot_field                           Required Field. Pivot Field
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fields': ['fields', 'required'], 'table': ['in_table', 'required'], 'value_field': ['value_field', 'required'], 'pivot_field': ['pivot_field', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'PivotTable', inputs, in_db, out_db)

          
def create_feature_class(out_path, out_name, geometry_type='polygon', template=None, has_m='disabled', has_z='disabled', spatial_reference=None, config_keyword=None, spatial_grid_1='1000', spatial_grid_2='0', spatial_grid_3='0'):
     """
     Geoprocessing tool that creates a feature class, either in an ArcSDE, file geodatabase, or personal geodatabase, or as a shapefile in a folder.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_path                              Required GPComposite. Feature Class Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. Feature Class Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional GPString. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional GPString. Geometry Type. Default value: polygon. Value choices: point, multipoint, polygon, polyline, multipatch
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     has_z                                 Optional GPString. Has Z. Default value: disabled. Value choices: disabled, same_as_template, enabled
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional GPMultiValue. Template Feature Class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        Optional GPDouble. Output Spatial Grid 2. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     has_m                                 Optional GPString. Has M. Default value: disabled. Value choices: disabled, same_as_template, enabled
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        Optional GPDouble. Output Spatial Grid 1. Default value: 1000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        Optional GPDouble. Output Spatial Grid 3. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Coordinate System. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'has_z': ['has_z', 'optional'], 'template': ['template', 'optional'], 'out_path': ['out_path', 'required'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'has_m': ['has_m', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional'], 'geometry_type': ['geometry_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFeatureClass', inputs, in_db, out_db)

          
def create_table(out_path, out_name, template=None, config_keyword=None):
     """
     Geoprocessing tool that creates a geodatabase table, an INFO table, or dBASE table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_path                              Required DEWorkspace. Table Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. Table Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional GPString. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional GPMultiValue. Template Table Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_path': ['out_path', 'required'], 'out_name': ['out_name', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateTable', inputs, in_db, out_db)

          
def make_table_view(table, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a table view from an input table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_info                            Optional GPFieldInfo. Field Info. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Expression. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Optional DEWorkspace. Output Workspace. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_info': ['field_info', 'optional'], 'table': ['in_table', 'required'], 'where_clause': ['where_clause', 'optional'], 'workspace': ['workspace', 'optional']}
     out_db = {'view': ['out_view', 'required', None, None]}
     return _execute_tool('management', 'MakeTableView', inputs, in_db, out_db)

          
def add_spatial_index(features, spatial_grid_1='0', spatial_grid_2='0', spatial_grid_3='0'):
     """
     Geoprocessing tool that adds a spatial index to a feature class

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPComposite. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_2                        Optional GPDouble. Spatial Grid 2. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_1                        Optional GPDouble. Spatial Grid 1. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_grid_3                        Optional GPDouble. Spatial Grid 3. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddSpatialIndex', inputs, in_db, out_db)

          
def remove_spatial_index(features):
     """
     Geoprocessing tool that deletes the spatial index from a shapefile, file geodatabase feature class, or enterprise geodatabase feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPComposite. Input Features
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
     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_type                            Required GPString. Field Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_policy                          Optional GPString. Split Policy. Default value: default. Value choices: default, duplicate, geometry_ratio
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domadescription                       Optional GPString. Domain Description. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     merge_policy                          Optional GPString. Merge Policy. Default value: default. Value choices: default, sum_values, area_weighted
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domatype                              Optional GPString. Domain Type. Default value: coded. Value choices: coded, range
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'domadescription': ['domain_description', 'optional'], 'domatype': ['domain_type', 'optional'], 'merge_policy': ['merge_policy', 'optional'], 'split_policy': ['split_policy', 'optional'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required'], 'field_type': ['field_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDomain', inputs, in_db, out_db)

          
def delete_domain(workspace, domaname):
     """
     Geoprocessing tool to delete a domain from a workspace.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
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
     code                                  Required GPString. Code Value
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code_description                      Required GPString. Code Description
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'code': ['code', 'required'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required'], 'code_description': ['code_description', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddCodedValueToDomain', inputs, in_db, out_db)

          
def delete_coded_value_from_domain(workspace, domaname, code):
     """
     Geoprocessing tool that removes a value from a coded value domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code                                  Required GPMultiValue. Code Value
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'code': ['code', 'required'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteCodedValueFromDomain', inputs, in_db, out_db)

          
def set_value_for_range_domain(workspace, domaname, mvalue, max_value):
     """
     Geoprocessing tool that sets the minimun and maximum values for an existing Range domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_value                             Required GPString. Maximum Value
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mvalue                                Required GPString. Minimum Value
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'max_value': ['max_value', 'required'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required'], 'mvalue': ['min_value', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetValueForRangeDomain', inputs, in_db, out_db)

          
def assign_domain_to_field(table, field_name, domaname, subtype_code=None):
     """
     Geoprocessing tool that sets the domain for a particular field and, optionally, for a subtype.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          Optional GPMultiValue. Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype_code': ['subtype_code', 'optional'], 'table': ['in_table', 'required'], 'field_name': ['field_name', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'AssignDomainToField', inputs, in_db, out_db)

          
def remove_domain_from_field(table, field_name, subtype_code=None):
     """
     Geoprocessing tool that removes an attribute domain association from a feature class or table field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          Optional GPMultiValue. Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype_code': ['subtype_code', 'optional'], 'table': ['in_table', 'required'], 'field_name': ['field_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveDomainFromField', inputs, in_db, out_db)

          
def table_to_domain(table, code_field, description_field, workspace, domaname, domadescription=None, update_option='append'):
     """
     Geoprocessing tool that creates or updates a coded value domain with values from a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     description_field                     Required Field. Description Field 
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code_field                            Required Field. Code Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_option                         Optional GPString. Update Option. Default value: append. Value choices: append, replace
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     domadescription                       Optional GPString. Domain Description. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_option': ['update_option', 'optional'], 'domadescription': ['domain_description', 'optional'], 'table': ['in_table', 'required'], 'description_field': ['description_field', 'required'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required'], 'code_field': ['code_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'TableToDomain', inputs, in_db, out_db)

          
def domain_to_table(workspace, domaname, code_field, description_field, configuration_keyword=None):
     """
     Geoprocessing tool that creates a table from an attribute domain.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     description_field                     Required GPString. Field Description
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     code_field                            Required GPString. Code Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     configuration_keyword                 Optional GPString. Configuration Keyword. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'configuration_keyword': ['configuration_keyword', 'optional'], 'description_field': ['description_field', 'required'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required'], 'code_field': ['code_field', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'DomainToTable', inputs, in_db, out_db)

          
def select_layer_by_attribute(layer_or_view, selection_type='new_selection', where_clause=None):
     """
     Geoprocessing tool that adds, updates, or removes a selection on a layer or table view based on an attribute query.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     layer_or_view                         Required GPComposite. Layer Name or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_type                        Optional GPString. Selection type. Default value: new_selection. Value choices: new_selection, add_to_selection, remove_from_selection, subset_selection, switch_selection, clear_selection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Expression. Default value: none
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
     layer                                 Required GPComposite. Input Feature Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_type                        Optional GPString. Selection type. Default value: new_selection. Value choices: new_selection, add_to_selection, remove_from_selection, subset_selection, switch_selection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     invert_spatial_relationship           Optional GPBoolean. Invert Spatial Relationship. Default value: false. Value choices: invert, not_invert
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_distance                       Optional GPLinearUnit. Search Distance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     select_features                       Optional GPFeatureLayer. Selecting Features. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overlap_type                          Optional GPString. Relationship. Default value: intersect. Value choices: intersect, intersect_3d, within_a_distance_geodesic, within_a_distance, within_a_distance_3d, contains, completely_contains, contains_clementini, within, completely_within, within_clementini, are_identical_to, boundary_touches, share_a_line_segment_with, crossed_by_the_outline_of, have_their_center_in
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'layer': ['in_layer', 'required'], 'invert_spatial_relationship': ['invert_spatial_relationship', 'optional'], 'search_distance': ['search_distance', 'optional'], 'selection_type': ['selection_type', 'optional'], 'select_features': ['select_features', 'optional'], 'overlap_type': ['overlap_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SelectLayerByLocation', inputs, in_db, out_db)

          
def get_count(rows):
     """
     Geoprocessing tool that reports the number of rows of the input data.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows                                  Required GPComposite. Input Rows
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'rows': ['in_rows', 'required']}
     out_db = {}
     return _execute_tool('management', 'GetCount', inputs, in_db, out_db)

          
def create_version(workspace, parent_version, version_name, access_permission='private'):
     """
     Geoprocessing tool to create a new version in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     parent_version                        Required GPString. Parent Version
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     version_name                          Required GPString. Version Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     access_permission                     Optional GPString. Access Permission. Default value: private. Value choices: private, public, protected
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'parent_version': ['parent_version', 'required'], 'access_permission': ['access_permission', 'optional'], 'version_name': ['version_name', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateVersion', inputs, in_db, out_db)

          
def delete_version(workspace, version_name):
     """
     Geoprocessing tool to delete a specific version from a geodatabase

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_name                          Required GPString. Version Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Database Connection
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
     dataset                               Required GPComposite. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_to_base                          Optional GPBoolean. Register the selected objects with the option to move edits to base. Default value: false. Value choices: edits_to_base, no_edits_to_base
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'edit_to_base': ['edit_to_base', 'optional'], 'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'RegisterAsVersioned', inputs, in_db, out_db)

          
def unregister_as_versioned(dataset, keep_edit='true', compress_default='false'):
     """
     Geoprocessing tool to unregister an enterprise, workgroup, or desktop geodatabase dataset as versioned.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPComposite. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     keep_edit                             Optional GPBoolean. Do not run if there are edits in the delta tables. Default value: true. Value choices: keep_edit, no_keep_edit
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compress_default                      Optional GPBoolean. Compress all edits in the Default version into the base table. Default value: false. Value choices: compress_default, no_compress_default
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'keep_edit': ['keep_edit', 'optional'], 'compress_default': ['compress_default', 'optional'], 'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'UnregisterAsVersioned', inputs, in_db, out_db)

          
def alter_version(workspace, version, name=None, description=None, access='private'):
     """
     Geoprocessing tool that alters the database version's properties of name, description, and access permissions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               Required GPString. Input Version
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     description                           Optional GPString. Version Description. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     access                                Optional GPString. Access Permission. Default value: private. Value choices: private, public, protected
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     name                                  Optional GPString. Version Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'description': ['description', 'optional'], 'version': ['in_version', 'required'], 'access': ['access', 'optional'], 'name': ['name', 'optional'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'AlterVersion', inputs, in_db, out_db)

          
def table_to_relationship_class(origtable, destination_table, relationship_type, forward_label, backward_label, message_direction, cardinality, relationship_table, attribute_fields, origprimary_key, origforeign_key, destination_primary_key, destination_foreign_key):
     """
     Geoprocessing tool that creates an attributed relationship class from the Origin, Destination, and Relationship Tables.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     backward_label                        Required GPString. Backward Path Label
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_foreign_key               Required GPString. Destination Foreign Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     forward_label                         Required GPString. Forward Path Label
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origforeign_key                       Required GPString. Origin Foreign Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_table                     Required GPTableView. Destination Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     relationship_type                     Required GPString. Relationship Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     message_direction                     Required GPString. Message Direction
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cardinality                           Required GPString. Cardinality
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     destination_primary_key               Required GPString. Destination Primary Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     attribute_fields                      Required GPMultiValue. Attribute Fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origprimary_key                       Required GPString. Origin Primary Key
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     origtable                             Required GPTableView. Origin Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     relationship_table                    Required GPTableView. Relationship Table
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'backward_label': ['backward_label', 'required'], 'destination_foreign_key': ['destination_foreign_key', 'required'], 'forward_label': ['forward_label', 'required'], 'origforeign_key': ['origin_foreign_key', 'required'], 'destination_table': ['destination_table', 'required'], 'relationship_type': ['relationship_type', 'required'], 'message_direction': ['message_direction', 'required'], 'cardinality': ['cardinality', 'required'], 'destination_primary_key': ['destination_primary_key', 'required'], 'attribute_fields': ['attribute_fields', 'required'], 'origprimary_key': ['origin_primary_key', 'required'], 'origtable': ['origin_table', 'required'], 'relationship_table': ['relationship_table', 'required']}
     out_db = {'relationship_class': ['out_relationship_class', 'required', None, None]}
     return _execute_tool('management', 'TableToRelationshipClass', inputs, in_db, out_db)

          
def feature_to_point(features, point_location='false'):
     """
     Geoprocessing tool that creates a representative point for each input feature.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_location                        Optional GPBoolean. Inside. Default value: false. Value choices: inside, centroid
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'point_location': ['point_location', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToPoint', inputs, in_db, out_db)

          
def feature_vertices_to_points(features, point_location='all'):
     """
     Geoprocessing tool that creates points from input feature vertices.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     point_location                        Optional GPString. Point Type. Default value: all. Value choices: all, mid, start, end, both_ends, dangle
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'point_location': ['point_location', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureVerticesToPoints', inputs, in_db, out_db)

          
def feature_to_line(features, cluster_tolerance=None, attributes='true'):
     """
     Geoprocessing tool that creates line features by converting polygon boundaries to lines, or splitting line or polygon features at their intersections.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPMultiValue. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attributes                            Optional GPBoolean. Preserve attributes. Default value: true. Value choices: attributes, no_attributes
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
     features                              Required GPMultiValue. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attributes                            Optional GPBoolean. Preserve attributes. Default value: true. Value choices: attributes, no_attributes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     label_features                        Optional GPFeatureLayer. Label Features. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'optional'], 'features': ['in_features', 'required'], 'attributes': ['attributes', 'optional'], 'label_features': ['label_features', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureToPolygon', inputs, in_db, out_db)

          
def polygon_to_line(features, neighbor_option='true'):
     """
     Geoprocessing tool that creates a feature class containing lines converted from polygon boundaries with or without considering neighboring polygons.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     neighbor_option                       Optional GPBoolean. Identify and store polygon neighboring information. Default value: true. Value choices: identify_neighbors, ignore_neighbors
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
     dataset                               Required GPComposite. Input Dataset or Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     coor_system                           Required GPCoordinateSystem. Coordinate System
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
     features                              Required GPFeatureLayer. Input Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ex_where_clause                       Optional GPSQLExpression. Exclusion Expression. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ex_features                           Optional GPFeatureLayer. Exclusion Layer. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection                             Optional GPBoolean. Eliminating polygon by border. Default value: true. Value choices: length, area
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
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_null                           Optional GPBoolean. Delete Features with Null Geometry. Default value: true. Value choices: delete_null, keep_null
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'delete_null': ['delete_null', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RepairGeometry', inputs, in_db, out_db)

          
def create_topology(dataset, out_name, cluster_tolerance=None):
     """
     Geoprocessing tool to create a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_name                              Required GPString. Output Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required DEFeatureDataset. Input Feature Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPDouble. Cluster Tolerance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'cluster_tolerance': ['in_cluster_tolerance', 'optional'], 'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateTopology', inputs, in_db, out_db)

          
def remove_feature_class_from_topology(topology, featureclass):
     """
     Geoprocessing tool to remove a feature class from participating in a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     featureclass                          Required GPString. Feature Class to Remove
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     topology                              Required DETopology. Input Topology
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'featureclass': ['in_featureclass', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveFeatureClassFromTopology', inputs, in_db, out_db)

          
def add_rule_to_topology(topology, rule_type, featureclass, subtype=None, featureclass2=None, subtype2=None):
     """
     Geoprocessing tool to add a rule to a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     featureclass                          Required GPFeatureLayer. Input Feature class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     topology                              Required GPTopologyLayer. Input Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     rule_type                             Required GPString. Rule Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype                               Optional GPString. Input Subtype. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     featureclass2                         Optional GPFeatureLayer. Input Feature class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype2                              Optional GPString. Input Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'featureclass': ['in_featureclass', 'required'], 'featureclass2': ['in_featureclass2', 'optional'], 'rule_type': ['rule_type', 'required'], 'subtype2': ['subtype2', 'optional'], 'subtype': ['subtype', 'optional'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddRuleToTopology', inputs, in_db, out_db)

          
def validate_topology(topology, visible_extent='false'):
     """
     Geoprocessing tool that validates a topology.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     topology                              Required GPTopologyLayer. Input Topology
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     visible_extent                        Optional GPBoolean. Visible Extent. Default value: false. Value choices: visible_extent, full_extent
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
     cluster_tolerance                     Required GPDouble. Cluster Tolerance
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     topology                              Required GPTopologyLayer. Input Topology
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
     table                                 Required GPMultiValue. Input Tables
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     key_field_option                      Required GPString. Key Field Options
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Expression. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     key_field                             Optional GPMultiValue. Key Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 Optional GPValueTable. Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'where_clause': ['where_clause', 'optional'], 'table': ['in_table', 'required'], 'key_field': ['in_key_field', 'optional'], 'key_field_option': ['in_key_field_option', 'required'], 'field': ['in_field', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'MakeQueryTable', inputs, in_db, out_db)

          
def make_xy_event_layer(table, x_field, y_field, spatial_reference=None, z_field=None):
     """
     Geoprocessing tool that creates a new point feature layer based on x- and y-coordinates defined in a source table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPTableView. XY Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               Required Field. Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               Required Field. X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_field                               Optional Field. Z Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Spatial Reference. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'z_field': ['in_z_field', 'optional'], 'table': ['table', 'required'], 'y_field': ['in_y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'x_field': ['in_x_field', 'required']}
     out_db = {'layer': ['out_layer', 'required', None, None]}
     return _execute_tool('management', 'MakeXYEventLayer', inputs, in_db, out_db)

          
def make_raster_layer(raster, where_clause=None, envelope=None, band_index=None):
     """
     Geoprocessing tool that makes a temporary raster layer from a raster dataset that will be available to select as a variable while working in the same application's session.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPSAGeoData. Input raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional GPValueTable. Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Where clause. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     envelope                              Optional GPExtent. Envelope. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'band_index': ['band_index', 'optional'], 'where_clause': ['where_clause', 'optional'], 'envelope': ['envelope', 'optional']}
     out_db = {'rasterlayer': ['out_rasterlayer', 'required', None, None]}
     return _execute_tool('management', 'MakeRasterLayer', inputs, in_db, out_db)

          
def flip(raster):
     """
     Geoprocessing tool that reorients the raster by turning it over, from top to bottom, along the horizontal axis through the center of the raster.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
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
     raster                                Required GPComposite. Input Raster
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
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_coor_system                       Required GPCoordinateSystem. Output Coordinate System
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional GPCellSizeXY. Output Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           Optional GPCoordinateSystem. Input Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     registration_point                    Optional GPPoint. Registration Point. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geographic_transform                  Optional GPMultiValue. Geographic Transformation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional GPString. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'coor_system': ['in_coor_system', 'optional'], 'registration_point': ['Registration_Point', 'optional'], 'out_coor_system': ['out_coor_system', 'required'], 'geographic_transform': ['geographic_transform', 'optional'], 'cell_size': ['cell_size', 'optional'], 'resampling_type': ['resampling_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'ProjectRaster', inputs, in_db, out_db)

          
def rescale(raster, x_scale, y_scale):
     """
     Geoprocessing tool that resizes a raster by the specified x and y scale factors.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_scale                               Required GPDouble. Y Scale Factor
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_scale                               Required GPDouble. X Scale Factor
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'y_scale': ['y_scale', 'required'], 'x_scale': ['x_scale', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Rescale', inputs, in_db, out_db)

          
def shift(raster, x_value, y_value, snap_raster=None):
     """
     Geoprocessing tool that moves (slides) the raster to a new geographic location, based on x and y shift values.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_value                               Required GPDouble. Shift X Coordinates by
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_value                               Required GPDouble. Shift Y Coordinates by
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     snap_raster                           Optional GPRasterLayer. Input Snap Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'snap_raster': ['in_snap_raster', 'optional'], 'x_value': ['x_value', 'required'], 'y_value': ['y_value', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Shift', inputs, in_db, out_db)

          
def warp(raster, source_control_points, target_control_points, transformation_type='polyorder1', resampling_type='nearest'):
     """
     Geoprocessing tool that performs a transformation on the raster based on the source and target control points using a polynomial transformation.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     source_control_points                 Required GPMultiValue. Source Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_control_points                 Required GPMultiValue. Target Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   Optional GPString. Transformation Type. Default value: polyorder1. Value choices: polyorder0, polysimilarity, polyorder1, polyorder2, polyorder3, adjust, spline, projective
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional GPString. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'transformation_type': ['transformation_type', 'optional'], 'source_control_points': ['source_control_points', 'required'], 'target_control_points': ['target_control_points', 'required'], 'resampling_type': ['resampling_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Warp', inputs, in_db, out_db)

          
def append(inputs, target, schema_type='test', field_mapping=None, subtype=None):
     """
     Geoprocessing tool that appends multiple input datasets into an existing target dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target                                Required GPComposite. Target Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     inputs                                Required GPMultiValue. Input Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     schema_type                           Optional GPString. Schema Type. Default value: test. Value choices: test, no_test
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mapping                         Optional GPFieldMapping. Field Map. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype                               Optional GPString. Subtype. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'schema_type': ['schema_type', 'optional'], 'field_mapping': ['field_mapping', 'optional'], 'target': ['target', 'required'], 'subtype': ['subtype', 'optional'], 'inputs': ['inputs', 'required']}
     out_db = {}
     return _execute_tool('management', 'Append', inputs, in_db, out_db)

          
def delete_features(features):
     """
     Geoprocessing tool used to remove features from a feature class or layer.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
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
     table                                 Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required GPString. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_type                            Required GPString. Field Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_scale                           Optional GPLong. Field Scale. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_required                     Optional GPBoolean. Field IsRequired. Default value: false. Value choices: required, non_required
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_length                          Optional GPLong. Field Length. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_alias                           Optional GPString. Field Alias. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_nullable                     Optional GPBoolean. Field IsNullable. Default value: true. Value choices: nullable, non_nullable
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_domain                          Optional GPString. Field Domain. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_precision                       Optional GPLong. Field Precision. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_scale': ['field_scale', 'optional'], 'field_is_required': ['field_is_required', 'optional'], 'field_length': ['field_length', 'optional'], 'field_alias': ['field_alias', 'optional'], 'field_is_nullable': ['field_is_nullable', 'optional'], 'table': ['in_table', 'required'], 'field_domain': ['field_domain', 'optional'], 'field_name': ['field_name', 'required'], 'field_precision': ['field_precision', 'optional'], 'field_type': ['field_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddField', inputs, in_db, out_db)

          
def assign_default_to_field(table, field_name, default_value=None, subtype_code=None, clear_value='false'):
     """
     Geoprocessing tool used to create a default value for a specified field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field_name                            Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          Optional GPMultiValue. Subtype. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_value                           Optional GPBoolean. Clear Value. Default value: false
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_value                         Optional GPString. Default Value. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'clear_value': ['clear_value', 'optional'], 'subtype_code': ['subtype_code', 'optional'], 'table': ['in_table', 'required'], 'field_name': ['field_name', 'required'], 'default_value': ['default_value', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AssignDefaultToField', inputs, in_db, out_db)

          
def calculate_field(table, field, expression, expression_type='vb', code_block=None):
     """
     Geoprocessing tool used to perform field calculations.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     expression                            Required GPSQLExpression. Expression
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     code_block                            Optional GPString. Code Block. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     expression_type                       Optional GPString. Expression Type. Default value: vb. Value choices: vb, python, python_9.3
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'expression_type': ['expression_type', 'optional'], 'code_block': ['code_block', 'optional'], 'table': ['in_table', 'required'], 'expression': ['expression', 'required'], 'field': ['field', 'required']}
     out_db = {}
     return _execute_tool('management', 'CalculateField', inputs, in_db, out_db)

          
def delete_field(table, drop_field):
     """
     Geoprocessing tool used to remove fields from a dataset

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     drop_field                            Required GPMultiValue. Drop Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPComposite. Input Table
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
     features                              Required GPFeatureLayer. Input Features
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
     features                              Required GPValueTable. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cluster_tolerance                     Optional GPLinearUnit. XY Tolerance. Default value: none
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
     inputs                                Required GPMultiValue. Input Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_mappings                        Optional GPFieldMapping. Field Map. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'field_mappings': ['field_mappings', 'optional'], 'inputs': ['inputs', 'required']}
     out_db = {'output': ['output', 'required', None, None]}
     return _execute_tool('management', 'Merge', inputs, in_db, out_db)

          
def feature_compare(base_features, test_features, sort_field, compare_type='all', ignore_options=None, xy_tolerance=None, m_tolerance='0', z_tolerance='0', attribute_tolerances=None, omit_field=None, continue_compare='false'):
     """
     Geoprocessing tool that compares two feature classes or layers and returns the comparison results. Feature Compare can report differences with geometry, tabular values, spatial reference, and field definitions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_field                            Required GPValueTable. Sort Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_features                         Required GPFeatureLayer. Input Test Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     base_features                         Required GPFeatureLayer. Input Base Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional GPBoolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           Optional GPDouble. Z Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     m_tolerance                           Optional GPDouble. M Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_options                        Optional GPMultiValue. Ignore Options. Default value: none. Value choices: ignore_m, ignore_z, ignore_pointid, ignore_extension_properties, ignore_subtypes, ignore_relationshipclasses, ignore_representationclasses, ignore_fieldalias
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  Optional GPValueTable. Attribute Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            Optional GPMultiValue. Omit Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          Optional GPString. Compare Type. Default value: all. Value choices: all, geometry_only, attributes_only, schema_only, spatial_reference_only
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'sort_field': ['sort_field', 'required'], 'continue_compare': ['continue_compare', 'optional'], 'z_tolerance': ['z_tolerance', 'optional'], 'attribute_tolerances': ['attribute_tolerances', 'optional'], 'test_features': ['in_test_features', 'required'], 'm_tolerance': ['m_tolerance', 'optional'], 'ignore_options': ['ignore_options', 'optional'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'base_features': ['in_base_features', 'required'], 'omit_field': ['omit_field', 'optional'], 'compare_type': ['compare_type', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'FeatureCompare', inputs, in_db, out_db)

          
def file_compare(base_file, test_file, file_type='ascii', continue_compare='false'):
     """
     Geoprocessing tool which compares two files and returns the comparison results. File Compare can report differences between two ASCII files or two binary files.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     test_file                             Required DEFile. Input Test File
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     base_file                             Required DEFile. Input Base File
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional GPBoolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file_type                             Optional GPString. File Type. Default value: ascii. Value choices: ascii, binary
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'continue_compare': ['continue_compare', 'optional'], 'file_type': ['file_type', 'optional'], 'test_file': ['in_test_file', 'required'], 'base_file': ['in_base_file', 'required']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'FileCompare', inputs, in_db, out_db)

          
def raster_compare(base_raster, test_raster, compare_type='raster_dataset', ignore_option=None, continue_compare='false', parameter_tolerances=None, attribute_tolerances=None, omit_field=None):
     """
     Geoprocessing tool that compares the properties of two raster datasets or two mosaic datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     base_raster                           Required GPComposite. Input Base Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_raster                           Required GPComposite. Input Test Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  Optional GPValueTable. Attribute Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional GPBoolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            Optional GPMultiValue. Omit Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_option                         Optional GPMultiValue. Ignore Options. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     parameter_tolerances                  Optional GPValueTable. Parameter Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          Optional GPString. Compare Type. Default value: raster_dataset. Value choices: raster_dataset, gdb_raster_dataset, gdb_raster_catalog, mosaic_dataset
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'attribute_tolerances': ['attribute_tolerances', 'optional'], 'test_raster': ['in_test_raster', 'required'], 'continue_compare': ['continue_compare', 'optional'], 'omit_field': ['omit_field', 'optional'], 'ignore_option': ['ignore_option', 'optional'], 'parameter_tolerances': ['parameter_tolerances', 'optional'], 'base_raster': ['in_base_raster', 'required'], 'compare_type': ['compare_type', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'RasterCompare', inputs, in_db, out_db)

          
def table_compare(base_table, test_table, sort_field, compare_type='all', ignore_options=None, attribute_tolerances=None, omit_field=None, continue_compare='false'):
     """
     Geoprocessing tool compares two tables or table views and returns the comparison results.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_field                            Required GPValueTable. Sort Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     base_table                            Required GPComposite. Input Base Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     test_table                            Required GPComposite. Input Test Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     continue_compare                      Optional GPBoolean. Continue Comparison. Default value: false. Value choices: continue_compare, no_continue_compare
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_options                        Optional GPMultiValue. Ignore Options. Default value: none. Value choices: ignore_extension_properties, ignore_subtypes, ignore_relationshipclasses, ignore_fieldalias
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     omit_field                            Optional GPMultiValue. Omit Fields. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_tolerances                  Optional GPValueTable. Attribute Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compare_type                          Optional GPString. Compare Type. Default value: all. Value choices: all, attributes_only, schema_only
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'sort_field': ['sort_field', 'required'], 'base_table': ['in_base_table', 'required'], 'test_table': ['in_test_table', 'required'], 'continue_compare': ['continue_compare', 'optional'], 'ignore_options': ['ignore_options', 'optional'], 'omit_field': ['omit_field', 'optional'], 'attribute_tolerances': ['attribute_tolerances', 'optional'], 'compare_type': ['compare_type', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional', None, None]}
     return _execute_tool('management', 'TableCompare', inputs, in_db, out_db)

          
def create_file_gdb(out_folder_path, out_name, out_version='current'):
     """
     Geoprocessing tool that creates a file geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder_path                       Required DEFolder. File GDB Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. File GDB Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_version                           Optional GPString. File GDB Version. Default value: current. Value choices: current, 10.0, 9.3, 9.2
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_folder_path': ['out_folder_path', 'required'], 'out_name': ['out_name', 'required'], 'out_version': ['out_version', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFileGDB', inputs, in_db, out_db)

          
def compress(workspace):
     """
     Geoprocessing tool to compress an enterprise geodatabase

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     workspace                             Required DEWorkspace. Input Database Connection
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
     subtype_code                          Required GPLong. Subtype Code
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     subtype_description                   Required GPString. Subtype Name
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'subtype_code': ['subtype_code', 'required'], 'table': ['in_table', 'required'], 'subtype_description': ['subtype_description', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddSubtype', inputs, in_db, out_db)

          
def remove_subtype(table, subtype_code):
     """
     Geoprocessing tool that removes a subtype from the input table using its code.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     subtype_code                          Required GPMultiValue. Subtype Code
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
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
     subtype_code                          Required GPLong. Subtype Code
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
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
     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_value                           Optional GPBoolean. Clear Value. Default value: false
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field                                 Optional Field. Field Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'clear_value': ['clear_value', 'optional'], 'table': ['in_table', 'required'], 'field': ['field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetSubtypeField', inputs, in_db, out_db)

          
def add_colormap(raster, template_raster=None, input_clr_file=None):
     """
     Geoprocessing tool that adds a color map to a raster dataset, if it does not already exist or replaces a color map with the one specified.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPRasterLayer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_clr_file                        Optional DEFile. Input .clr or .act File. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_raster                       Optional GPRasterLayer. Input Template Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'input_clr_file': ['input_CLR_file', 'optional'], 'template_raster': ['in_template_raster', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddColormap', inputs, in_db, out_db)

          
def build_raster_attribute_table(raster, overwrite='false'):
     """
     Geoprocessing tool that adds a raster attribute table to a raster dataset or updates an existing one.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPRasterLayer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overwrite                             Optional GPBoolean. Overwrite. Default value: false. Value choices: overwrite, none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'overwrite': ['overwrite', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildRasterAttributeTable', inputs, in_db, out_db)

          
def delete_colormap(raster):
     """
     Geoprocessing tool that removes the color map associated with a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPRasterLayer. Input Raster
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
     raster                                Required GPRasterLayer. Input Raster
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
     raster_dataset                        Required GPComposite. Input Raster Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional GPBoolean. Skip Existing. Default value: false. Value choices: skip_existing, overwrite
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_first                            Optional GPBoolean. Skip first level. Default value: false. Value choices: skip_first, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_type                      Optional GPString. Pyramid compression type. Default value: default. Value choices: default, jpeg, lz77, none, jpeg_ycbcr
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resample_technique                    Optional GPString. Pyramid resampling technique. Default value: nearest. Value choices: nearest, bilinear, cubic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_level                         Optional GPLong. Pyramid levels. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional GPLong. Compression quality (1-100). Default value: 75
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['skip_existing', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'compression_type': ['compression_type', 'optional'], 'resample_technique': ['resample_technique', 'optional'], 'pyramid_level': ['pyramid_level', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'skip_first': ['SKIP_FIRST', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildPyramids', inputs, in_db, out_db)

          
def calculate_statistics(raster_dataset, x_skip_factor=None, y_skip_factor=None, ignore_values=None, skip_existing='false', area_of_interest='in_memory\{bc80ecfe-15b0-41c3-8fa1-a0a41602275c}'):
     """
     Geoprocessing tool that calculates statistics for a raster dataset or mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        Required GPComposite. Input Raster Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional GPBoolean. Skip Existing. Default value: false. Value choices: skip_existing, overwrite
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     y_skip_factor                         Optional GPLong. Number of Rows to Skip. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_values                         Optional GPMultiValue. Ignore Values. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional GPFeatureRecordSetLayer. Area of Interest. Default value: in_memory\{bc80ecfe-15b0-41c3-8fa1-a0a41602275c}
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     x_skip_factor                         Optional GPLong. Number of Columns to Skip. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['skip_existing', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'ignore_values': ['ignore_values', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'y_skip_factor': ['y_skip_factor', 'optional'], 'x_skip_factor': ['x_skip_factor', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateStatistics', inputs, in_db, out_db)

          
def get_raster_properties(raster, property_type='minimum', band_index=None):
     """
     Geoprocessing tool that returns the properties of a raster dataset, mosaic dataset, or a raster product.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPSAGeoData. Input raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     property_type                         Optional GPString. Property type. Default value: minimum. Value choices: maximum, minimum, mean, std, uniquevaluecount, top, left, right, bottom, cellsizex, cellsizey, valuetype, columncount, rowcount, bandcount, allnodata, anynodata, sensorname, productname, acquisitiondate, sourcetype, cloudcover, sunazimuth, sunelevation, sensorazimuth, sensorelevation, offnadir, wavelength
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional GPString. Band Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'property_type': ['property_type', 'optional'], 'band_index': ['band_index', 'optional']}
     out_db = {}
     return _execute_tool('management', 'GetRasterProperties', inputs, in_db, out_db)

          
def copy_raster(raster, config_keyword=None, background_value=None, nodata_value=None, onebit_to_eightbit='false', colormap_to_rgb='false', pixel_type=None, scale_pixel_value='false', rgb_to_colormap='false', format=None, transform='false'):
     """
     Geoprocessing tool that makes a copy of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional GPString. Format. Default value: none. Value choices: tiff, imagine image, bmp, gif, png, jpeg, jpeg2000, esri grid, esri bil, esri bsq, esri bip, envi, crf, mrf
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional GPString. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transform                             Optional GPBoolean. Apply Transformation. Default value: false. Value choices: transform, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scale_pixel_value                     Optional GPBoolean. Scale Pixel Value. Default value: false. Value choices: scalepixelvalue, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      Optional GPDouble. Ignore Background Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rgb_to_colormap                       Optional GPBoolean. RGB To Colormap. Default value: false. Value choices: rgbtocolormap, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional GPString. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional GPString. Pixel Type. Default value: none. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    Optional GPBoolean. Convert 1 bit data to 8 bit. Default value: false. Value choices: onebitto8bit, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap_to_rgb                       Optional GPBoolean. Colormap to RGB. Default value: false. Value choices: colormaptorgb, none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'transform': ['transform', 'optional'], 'scale_pixel_value': ['scale_pixel_value', 'optional'], 'background_value': ['background_value', 'optional'], 'format': ['format', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'rgb_to_colormap': ['RGB_to_Colormap', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'pixel_type': ['pixel_type', 'optional'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional']}
     out_db = {'rasterdataset': ['out_rasterdataset', 'required', None, None]}
     return _execute_tool('management', 'CopyRaster', inputs, in_db, out_db)

          
def create_random_raster(out_path, out_name, distribution='uniform 0.0 1.0', raster_extent=None, cellsize=None):
     """
     Geoprocessing tool that creates a random raster dataset based on a user-specified distribution and extent.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_path                              Required GPComposite. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. Raster Dataset Name with Extension
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_extent                         Optional GPExtent. Output extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              Optional GPDouble. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          Optional GPString. Distribution. Default value: uniform 0.0 1.0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_path': ['out_path', 'required'], 'out_name': ['out_name', 'required'], 'cellsize': ['cellsize', 'optional'], 'distribution': ['distribution', 'optional'], 'raster_extent': ['raster_extent', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomRaster', inputs, in_db, out_db)

          
def create_raster_dataset(out_path, out_name, pixel_type, number_of_bands, cellsize=None, raster_spatial_reference=None, config_keyword=None, pyramids='pyramids -1 nearest default 75 no_skip', tile_size='128 128', compression='lz77', pyramid_origin=None):
     """
     Geoprocessing tool that creates a raster dataset as a file or in a geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_path                              Required GPComposite. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. Raster Dataset Name with Extension
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_bands                       Required GPLong. Number of Bands
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     pixel_type                            Required GPString. Pixel Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional GPString. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              Optional GPDouble. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramids                              Optional GPSAGDBEnvPyramid. Create pyramids. Default value: pyramids -1 nearest default 75 no_skip
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression                           Optional GPSAGDBEnvCompression. Compression. Default value: lz77
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_spatial_reference              Optional GPCoordinateSystem. Spatial Reference for Raster. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             Optional GPSAGDBEnvTileSize. Tile size. Default value: 128 128
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_origin                        Optional GPPoint. Pyramid Reference Point. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'cellsize': ['cellsize', 'optional'], 'pyramid_origin': ['pyramid_origin', 'optional'], 'pyramids': ['pyramids', 'optional'], 'out_path': ['out_path', 'required'], 'number_of_bands': ['number_of_bands', 'required'], 'compression': ['compression', 'optional'], 'raster_spatial_reference': ['raster_spatial_reference', 'optional'], 'tile_size': ['tile_size', 'optional'], 'pixel_type': ['pixel_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateRasterDataset', inputs, in_db, out_db)

          
def mosaic(inputs, target, mosaic_type='last', colormap='first', background_value=None, nodata_value=None, onebit_to_eightbit='false', mosaicking_tolerance='0', matching_method=None):
     """
     Geoprocessing tool that mosaics multiple input rasters into an existing raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target                                Required DERasterDataset. Target Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     inputs                                Required GPMultiValue. Input Rasters
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    Optional GPBoolean. Convert 1 bit data to 8 bit. Default value: false. Value choices: onebitto8bit, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap                              Optional GPString. Mosaic Colormap Mode. Default value: first. Value choices: reject, first, last, match
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      Optional GPDouble. Ignore Background Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional GPDouble. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_type                           Optional GPString. Mosaic Operator. Default value: last. Value choices: first, last, blend, mean, minimum, maximum, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     matching_method                       Optional GPString. Color Matching Method. Default value: none. Value choices: none, statistic_matching, histogram_matching, linearcorrelation_matching
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicking_tolerance                  Optional GPDouble. Mosaicking Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional'], 'colormap': ['colormap', 'optional'], 'background_value': ['background_value', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'mosaic_type': ['mosaic_type', 'optional'], 'target': ['target', 'required'], 'matching_method': ['MatchingMethod', 'optional'], 'inputs': ['inputs', 'required']}
     out_db = {}
     return _execute_tool('management', 'Mosaic', inputs, in_db, out_db)

          
def workspace_to_raster_dataset(workspace, raster_dataset, include_subdirectories='false', mosaic_type='last', colormap='first', background_value=None, nodata_value=None, onebit_to_eightbit='false', mosaicking_tolerance='0', matching_method=None, colormap_to_rgb='false'):
     """
     Geoprocessing tool that mosaics all the raster datasets stored within the specified workspace into one raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        Required DERasterDataset. Target Raster Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     onebit_to_eightbit                    Optional GPBoolean. Convert 1 bit data to 8 bit. Default value: false. Value choices: onebitto8bit, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap                              Optional GPString. Mosaic Colormap Mode. Default value: first. Value choices: reject, first, last, match
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     colormap_to_rgb                       Optional GPBoolean. Colormap to RGB. Default value: false. Value choices: colormaptorgb, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     background_value                      Optional GPDouble. Ignore Background Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional GPDouble. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_type                           Optional GPString. Mosaic Operator. Default value: last. Value choices: first, last, blend, mean, minimum, maximum, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_subdirectories                Optional GPBoolean. Include Sub-directories. Default value: false. Value choices: include_subdirectories, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     matching_method                       Optional GPString. Color Matching Method. Default value: none. Value choices: none, statistic_matching, histogram_matching, linearcorrelation_matching
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaicking_tolerance                  Optional GPDouble. Mosaicking Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'matching_method': ['MatchingMethod', 'optional'], 'colormap': ['colormap', 'optional'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional'], 'background_value': ['background_value', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'mosaic_type': ['mosaic_type', 'optional'], 'include_subdirectories': ['include_subdirectories', 'optional'], 'workspace': ['in_workspace', 'required'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'WorkspaceToRasterDataset', inputs, in_db, out_db)

          
def clip(raster, rectangle, template_dataset=None, nodata_value=None, clipping_geometry='false', maintaclipping_extent='false'):
     """
     Geoprocessing tool that creates a spatial subset of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     rectangle                             Required GPEnvelope. Rectangle
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional GPString. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional GPComposite. Output Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintaclipping_extent                 Optional GPBoolean. Maintain Clipping Extent. Default value: false. Value choices: maintain_extent, no_maintain_extent
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clipping_geometry                     Optional GPBoolean. Use Input Features for Clipping Geometry. Default value: false. Value choices: clippinggeometry, none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'clipping_geometry': ['clipping_geometry', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'maintaclipping_extent': ['maintain_clipping_extent', 'optional'], 'rectangle': ['rectangle', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Clip', inputs, in_db, out_db)

          
def composite_bands(rasters):
     """
     Geoprocessing tool that creates a single raster dataset from multiple bands and can also create a subset of the bands.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rasters                               Required GPMultiValue. Input Rasters
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
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional GPCellSizeXY. Output Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional GPString. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'cell_size': ['cell_size', 'optional'], 'resampling_type': ['resampling_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'Resample', inputs, in_db, out_db)

          
def export_raster_world_file(raster_dataset):
     """
     Geoprocessing tool that creates a world file based on the geographic information of a raster dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_dataset                        Required DERasterDataset. Input Raster Dataset
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
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     location_point                        Required GPPoint. Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional GPValueTable. Bands. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'location_point': ['location_point', 'required'], 'band_index': ['band_index', 'optional']}
     out_db = {}
     return _execute_tool('management', 'GetCellValue', inputs, in_db, out_db)

          
def make_wcs_layer(wcs_coverage, template=None, band_index=None):
     """
     Geoprocessing tool that creates a temporary raster layer from a WCS service.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     wcs_coverage                          Required GPComposite. Input WCS Coverage
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_index                            Optional GPValueTable. Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional GPExtent. Template Extent. Default value: none
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
     symbology_layer                       Required GPLayer. Symbology Layer
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     layer                                 Required GPLayer. Input Layer
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
     output_location                       Required GPComposite. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster_dataset_name_with_extension    Required GPString. Raster Dataset Name with Extension
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_bands                       Required GPLong. Number of Bands
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_rasters                         Required GPMultiValue. Input Rasters
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system_for_the_raster      Optional GPCoordinateSystem. Spatial Reference for Raster. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_method                         Optional GPString. Mosaic Operator. Default value: last. Value choices: first, last, blend, mean, minimum, maximum, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cellsize                              Optional GPDouble. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_colormap_mode                  Optional GPString. Mosaic Colormap Mode. Default value: first. Value choices: reject, first, last, match
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional GPString. Pixel Type. Default value: 8_bit_unsigned. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'coordinate_system_for_the_raster': ['coordinate_system_for_the_raster', 'optional'], 'output_location': ['output_location', 'required'], 'raster_dataset_name_with_extension': ['raster_dataset_name_with_extension', 'required'], 'mosaic_colormap_mode': ['mosaic_colormap_mode', 'optional'], 'input_rasters': ['input_rasters', 'required'], 'cellsize': ['cellsize', 'optional'], 'mosaic_method': ['mosaic_method', 'optional'], 'number_of_bands': ['number_of_bands', 'required'], 'pixel_type': ['pixel_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MosaicToNewRaster', inputs, in_db, out_db)

          
def dice(features, vertex_limit):
     """
     Geoprocessing tool that subdivides a feature into smaller features based on a specified vertex limit.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     vertex_limit                          Required GPLong. Vertex Limit
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required GPFeatureLayer. Input Features
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
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     point_features                        Required GPFeatureLayer. Point Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     search_radius                         Optional GPLinearUnit. Search Radius. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'search_radius': ['search_radius', 'optional'], 'features': ['in_features', 'required'], 'point_features': ['point_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'SplitLineatPoint', inputs, in_db, out_db)

          
def unsplit_line(features, dissolve_field=None, statistics_fields=None):
     """
     Geoprocessing tool that aggregates line features based on specified attributes.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics_fields                     Optional GPValueTable. Statistics Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dissolve_field                        Optional GPMultiValue. Dissolve_Field(s). Default value: none
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
     raster                                Required GPRasterLayer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     format                                Required GPString. Output Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_base_name                         Required GPString. 
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder                            Required DEFolder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     split_method                          Required GPString. Split Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overlap                               Optional GPDouble. Overlap. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     origin                                Optional GPPoint. Lower left origin. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     units                                 Optional GPString. Units for Output Raster Size and Overlap. Default value: pixels. Value choices: pixels, meters, feet, degrees, kilometers, miles
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_type                             Optional GPString. Clip Type. Default value: none. Value choices: none, extent, feature_class
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional GPPoint. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional GPString. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     num_rasters                           Optional GPPoint. Number of Output Rasters. Default value: 1 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_extent                       Optional GPExtent. Template Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     split_polygon_feature_class           Optional GPFeatureLayer. Split Polygon Feature Class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             Optional GPPoint. Size of Output Rasters. Default value: 2048 2048
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional GPString. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'out_base_name': ['out_base_name', 'required'], 'overlap': ['overlap', 'optional'], 'split_method': ['split_method', 'required'], 'clip_type': ['clip_type', 'optional'], 'cell_size': ['cell_size', 'optional'], 'origin': ['origin', 'optional'], 'template_extent': ['template_extent', 'optional'], 'tile_size': ['tile_size', 'optional'], 'split_polygon_feature_class': ['split_polygon_feature_class', 'optional'], 'format': ['format', 'required'], 'units': ['units', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'num_rasters': ['num_rasters', 'optional'], 'out_folder': ['out_folder', 'required'], 'resampling_type': ['resampling_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SplitRaster', inputs, in_db, out_db)

          
def eliminate_polygon_part(features, condition='area', part_area='0 unknown', part_area_percent='0', part_option='true'):
     """
     Geoprocessing tool that creates a new output feature class containing the features from input polygons with some parts or holes of a specified size deleted.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_area_percent                     Optional GPDouble. Percentage. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_area                             Optional GPArealUnit. Area. Default value: 0 unknown
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     condition                             Optional GPString. Condition. Default value: area. Value choices: area, percent, area_and_percent, area_or_percent
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     part_option                           Optional GPBoolean. Eliminate contained parts only. Default value: true. Value choices: contained_only, any
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'part_area_percent': ['part_area_percent', 'optional'], 'features': ['in_features', 'required'], 'part_area': ['part_area', 'optional'], 'condition': ['condition', 'optional'], 'part_option': ['part_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'EliminatePolygonPart', inputs, in_db, out_db)

          
def points_to_line(input_features, line_field=None, sort_field=None, close_line='false'):
     """
     Geoprocessing tool used to create line features from points.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_features                        Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_field                            Optional Field. Sort Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_field                            Optional Field. Line Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     close_line                            Optional GPBoolean. Close Line. Default value: false. Value choices: close, no_close
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'sort_field': ['Sort_Field', 'optional'], 'line_field': ['Line_Field', 'optional'], 'input_features': ['Input_Features', 'required'], 'close_line': ['Close_Line', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'PointsToLine', inputs, in_db, out_db)

          
def change_version(features, version_type, version_name=None, date=None):
     """
     Geoprocessing tool used to change the enterprise geodatabase version you are connected to. Only works when working with feature layers or table views.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_type                          Required GPString. Version Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     features                              Required GPComposite. Input Feature Layer or Table View
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     date                                  Optional GPDate. Date and Time. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_name                          Optional GPString. Version Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'version_type': ['version_type', 'required'], 'features': ['in_features', 'required'], 'date': ['date', 'optional'], 'version_name': ['version_name', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ChangeVersion', inputs, in_db, out_db)

          
def register_with_geodatabase(dataset, object_id_field=None, shape_field=None, geometry_type=None, spatial_reference=None, extent=None):
     """
     Geoprocessing tool that registers feature classes, tables, views, and raster layers that were created outside of the geodatabase with the geodatabase in order for them to participate in geodatabase functionality.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPComposite. Input Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shape_field                           Optional Field. Shape Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     object_id_field                       Optional Field. Object ID Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional GPString. Geometry Type. Default value: none. Value choices: point, multipoint, polygon, polyline
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Optional GPEnvelope. Extent. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'object_id_field': ['in_object_id_field', 'optional'], 'dataset': ['in_dataset', 'required'], 'geometry_type': ['in_geometry_type', 'optional'], 'shape_field': ['in_shape_field', 'optional'], 'extent': ['in_extent', 'optional'], 'spatial_reference': ['in_spatial_reference', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RegisterwithGeodatabase', inputs, in_db, out_db)

          
def delete_identical(dataset, fields, xy_tolerance=None, z_tolerance='0'):
     """
     Geoprocessing tool to delete records in a feature class or table which have identical values in a list of fields.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Required GPMultiValue. Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required GPTableView. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           Optional GPDouble. Z Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fields': ['fields', 'required'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'dataset': ['in_dataset', 'required'], 'z_tolerance': ['z_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DeleteIdentical', inputs, in_db, out_db)

          
def find_identical(dataset, fields, xy_tolerance=None, z_tolerance='0', output_record_option='false'):
     """
     Geoprocessing tool that reports any records in a feature class or table that have identical values in a list of fields, and generates a table listing these identical records.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Required GPMultiValue. Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required GPTableView. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_tolerance                          Optional GPLinearUnit. XY Tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_record_option                  Optional GPBoolean. Output only duplicated records. Default value: false. Value choices: only_duplicates, all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_tolerance                           Optional GPDouble. Z Tolerance. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fields': ['fields', 'required'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'dataset': ['in_dataset', 'required'], 'output_record_option': ['output_record_option', 'optional'], 'z_tolerance': ['z_tolerance', 'optional']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'FindIdentical', inputs, in_db, out_db)

          
def change_privileges(dataset, user, view=None, edit=None):
     """
     Geoprocessing tool to change  privileges on a dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPMultiValue. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     user                                  Required GPString. User
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view                                  Optional GPString. View (Select). Default value: none. Value choices: as_is, grant, revoke
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit                                  Optional GPString. Edit (Update/Insert/Delete). Default value: none. Value choices: as_is, grant, revoke
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'view': ['View', 'optional'], 'dataset': ['in_dataset', 'required'], 'user': ['user', 'required'], 'edit': ['Edit', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ChangePrivileges', inputs, in_db, out_db)

          
def create_spatial_reference(spatial_reference=None, spatial_reference_template=None, xy_domain=None, z_domain=None, m_domain=None, template=None, expand_ratio='0'):
     """
     Geoprocessing tool to create a spatial reference for use in ModelBuilder and scripting.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     expand_ratio                          Optional GPDouble. Grow XYDomain By Percentage. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     m_domain                              Optional GPString. M Domain (min max). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_domain                              Optional GPString. Z Domain (min max). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference_template            Optional GPComposite. Spatial Reference Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_domain                             Optional GPEnvelope. XY Domain. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional GPMultiValue. Template XYDomains. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Spatial Reference. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'expand_ratio': ['expand_ratio', 'optional'], 'm_domain': ['m_domain', 'optional'], 'z_domain': ['z_domain', 'optional'], 'spatial_reference_template': ['spatial_reference_template', 'optional'], 'xy_domain': ['xy_domain', 'optional'], 'template': ['template', 'optional'], 'spatial_reference': ['spatial_reference', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateSpatialReference', inputs, in_db, out_db)

          
def raster_to_dted(raster, out_folder, dted_level, resampling_type='bilinear'):
     """
     Geoprocessing tool that splits a raster dataset into files based on the DTED tiling structure.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPRasterLayer. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder                            Required DEFolder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dted_level                            Required GPString. DTED Level
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional GPString. Resampling Technique. Default value: bilinear. Value choices: bilinear, nearest, cubic
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'out_folder': ['out_folder', 'required'], 'dted_level': ['dted_level', 'required']}
     out_db = {}
     return _execute_tool('management', 'RasterToDTED', inputs, in_db, out_db)

          
def bearing_distance_to_line(table, x_field, y_field, distance_field, distance_units, bearing_field, bearing_units, line_type='0', id_field=None, spatial_reference='{b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in an x-coordinate field, y-coordinate field, bearing field, and distance field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     bearing_units                         Required GPString. Bearing Units
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               Required Field. X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     bearing_field                         Required Field. Bearing Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     distance_field                        Required Field. Distance Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     distance_units                        Required GPString. Distance Units
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               Required Field. Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_type                             Optional GPString. Line Type. Default value: 0. Value choices: geodesic, great_circle, rhumb_line, normal_section
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Spatial Reference. Default value: {b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'bearing_units': ['bearing_units', 'required'], 'table': ['in_table', 'required'], 'line_type': ['line_type', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'x_field': ['x_field', 'required'], 'bearing_field': ['bearing_field', 'required'], 'distance_field': ['distance_field', 'required'], 'distance_units': ['distance_units', 'required'], 'id_field': ['id_field', 'optional'], 'y_field': ['y_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'BearingDistanceToLine', inputs, in_db, out_db)

          
def table_to_ellipse(table, x_field, y_field, major_field, minor_field, distance_units, azimuth_field=None, azimuth_units='9102', id_field=None, spatial_reference='{b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic ellipse features constructed based on the values in an x-coordinate field, y-coordinate field, major-axis field, minor-axis field, and azimuth field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance_units                        Required GPString. Distance Units
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     major_field                           Required Field. Major Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     x_field                               Required Field. X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     minor_field                           Required Field. Minor Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               Required Field. Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     azimuth_units                         Optional GPString. Azimuth Units. Default value: 9102. Value choices: degrees, mils, rads, grads
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Spatial Reference. Default value: {b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     azimuth_field                         Optional Field. Azimuth Field. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'azimuth_units': ['azimuth_units', 'optional'], 'distance_units': ['distance_units', 'required'], 'major_field': ['major_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'x_field': ['x_field', 'required'], 'minor_field': ['minor_field', 'required'], 'table': ['in_table', 'required'], 'azimuth_field': ['azimuth_field', 'optional'], 'y_field': ['y_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'TableToEllipse', inputs, in_db, out_db)

          
def xy_to_line(table, startx_field, starty_field, endx_field, endy_field, line_type='0', id_field=None, spatial_reference='{b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision'):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in a start x-coordinate field, start y-coordinate field, end x-coordinate field, and end y-coordinate field of a table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     endx_field                            Required Field. End X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     startx_field                          Required Field. Start X Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     endy_field                            Required Field. End Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     starty_field                          Required Field. Start Y Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     line_type                             Optional GPString. Line Type. Default value: 0. Value choices: geodesic, great_circle, rhumb_line, normal_section
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Spatial Reference. Default value: {b286c06b-0879-11d2-aaca-00c04fa33c20};ishighprecision
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'table': ['in_table', 'required'], 'line_type': ['line_type', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'endx_field': ['endx_field', 'required'], 'startx_field': ['startx_field', 'required'], 'endy_field': ['endy_field', 'required'], 'starty_field': ['starty_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'XYToLine', inputs, in_db, out_db)

          
def convert_coordinate_notation(table, x_field, y_field, input_coordinate_format, output_coordinate_format, exclude_invalid_records, id_field=None, spatial_reference=None, coor_system=None):
     """
     Geoprocessing tool that converts coordinate notations from one format to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     x_field                               Required Field. X Field (Longitude)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_coordinate_format              Required GPString. Output Coordinate Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     exclude_invalid_records               Required GPBoolean. Exclude records with invalid notation
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_coordinate_format               Required GPString. Input Coordinate Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_field                               Required Field. Y Field (Latitude)
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     id_field                              Optional Field. ID. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           Optional GPCoordinateSystem. Input Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Output Coordinate System. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'coor_system': ['in_coor_system', 'optional'], 'x_field': ['x_field', 'required'], 'output_coordinate_format': ['output_coordinate_format', 'required'], 'exclude_invalid_records': ['exclude_invalid_records', 'required'], 'table': ['in_table', 'required'], 'input_coordinate_format': ['input_coordinate_format', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'y_field': ['y_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required', None, None]}
     return _execute_tool('management', 'ConvertCoordinateNotation', inputs, in_db, out_db)

          
def minimum_bounding_geometry(features, geometry_type='rectangle_by_area', group_option=None, group_field=None, mbg_fields_option='false'):
     """
     Geoprocessing tool that creates polygons which represent a specified minimum bounding geometry enclosing each input feature or a group of input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     group_field                           Optional GPMultiValue. Group Field(s). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     group_option                          Optional GPString. Group Option. Default value: none. Value choices: none, all, list
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional GPString. Geometry Type. Default value: rectangle_by_area. Value choices: rectangle_by_area, rectangle_by_width, convex_hull, circle, envelope
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mbg_fields_option                     Optional GPBoolean. Add geometry characteristics as attributes to output. Default value: false. Value choices: mbg_fields, no_mbg_fields
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'group_field': ['group_field', 'optional'], 'features': ['in_features', 'required'], 'group_option': ['group_option', 'optional'], 'geometry_type': ['geometry_type', 'optional'], 'mbg_fields_option': ['mbg_fields_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'MinimumBoundingGeometry', inputs, in_db, out_db)

          
def add_rasters_to_mosaic_dataset(mosaic_dataset, raster_type, input_path, update_cellsize_ranges='true', update_boundary='true', update_overviews='false', maximum_pyramid_levels=None, maximum_cell_size='0', minimum_dimension='1500', spatial_reference=None, filter=None, sub_folder='true', duplicate_items_action='allow_duplicates', build_pyramids='false', calculate_statistics='false', build_thumbnails='false', operation_description=None, force_spatial_reference='false', estimate_statistics='false', aux_inputs=None):
     """
     Geoprocessing tool that ingests raster datasets from a file, folder, raster catalog, or image service to a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_path                            Required GPMultiValue. Input Data
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     raster_type                           Required GPRasterBuilder. Raster Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_dimension                     Optional GPLong. Minimum Pyramid Rows or Columns. Default value: 1500
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     filter                                Optional GPString. Input Data Filter. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate_statistics                   Optional GPBoolean. Estimate Mosaic Dataset Statistics. Default value: false. Value choices: estimate_statistics, no_statistics
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     aux_inputs                            Optional GPValueTable. Auxiliary Inputs. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_overviews                      Optional GPBoolean. Update Overviews. Default value: false. Value choices: update_overviews, no_overviews
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional GPBoolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_thumbnails                      Optional GPBoolean. Build Thumbnails. Default value: false. Value choices: build_thumbnails, no_thumbnails
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     duplicate_items_action                Optional GPString. Add New Datasets Only. Default value: allow_duplicates. Value choices: allow_duplicates, exclude_duplicates, overwrite_duplicates
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_pyramid_levels                Optional GPLong. Maximum Pyramid Levels Used. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_pyramids                        Optional GPBoolean. Build Raster Pyramids. Default value: false. Value choices: build_pyramids, no_pyramids
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     operation_description                 Optional GPString. Operation Description. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     force_spatial_reference               Optional GPBoolean. Force this Coordinate System for Input Data. Default value: false. Value choices: force_spatial_reference, no_force_spatial_reference
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_cell_size                     Optional GPDouble. Maximum Pyramid Cell Size. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sub_folder                            Optional GPBoolean. Include Sub Folders. Default value: true. Value choices: subfolders, no_subfolders
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                Optional GPBoolean. Update Cell Size Ranges. Default value: true. Value choices: update_cell_sizes, no_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Coordinate System for Input Data. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     calculate_statistics                  Optional GPBoolean. Calculate Statistics. Default value: false. Value choices: calculate_statistics, no_statistics
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'minimum_dimension': ['minimum_dimension', 'optional'], 'filter': ['filter', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'aux_inputs': ['aux_inputs', 'optional'], 'update_overviews': ['update_overviews', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'duplicate_items_action': ['duplicate_items_action', 'optional'], 'input_path': ['input_path', 'required'], 'maximum_pyramid_levels': ['maximum_pyramid_levels', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'operation_description': ['operation_description', 'optional'], 'force_spatial_reference': ['force_spatial_reference', 'optional'], 'raster_type': ['raster_type', 'required'], 'maximum_cell_size': ['maximum_cell_size', 'optional'], 'sub_folder': ['sub_folder', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddRastersToMosaicDataset', inputs, in_db, out_db)

          
def build_boundary(mosaic_dataset, where_clause=None, append_to_existing='false', simplification_method=None):
     """
     Geoprocessing tool that updates the extent of the boundary of  a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     append_to_existing                    Optional GPBoolean. Append To Existing Boundary. Default value: false. Value choices: append, overwrite
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     simplification_method                 Optional GPString. Simplification Method. Default value: none. Value choices: none, convex_hull, envelope
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'append_to_existing': ['append_to_existing', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'simplification_method': ['simplification_method', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildBoundary', inputs, in_db, out_db)

          
def build_footprints(mosaic_dataset, where_clause=None, reset_footprint='radiometry', mdata_value='1', max_data_value='254', approx_num_vertices='80', shrink_distance='0', maintaedges='false', skip_derived_images='true', update_boundary='true', request_size='2000', mregion_size='100', simplification_method=None, edge_tolerance=None, max_sliver_size='20', mthinness_ratio='0.05'):
     """
     Geoprocessing tool that computes the footprints for the rasters in a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_data_value                        Optional GPDouble. Maximum Data Value. Default value: 254
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional GPBoolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     simplification_method                 Optional GPString. Simplification Method. Default value: none. Value choices: none, convex_hull, envelope
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_derived_images                   Optional GPBoolean. Skip overviews. Default value: true. Value choices: skip_derived_images, no_skip_derived_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintaedges                           Optional GPBoolean. Maintain sheet edges. Default value: false. Value choices: maintain_edges, no_maintain_edges
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mdata_value                           Optional GPDouble. Minimum Data Value. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          Optional GPLong. Request Size. Default value: 2000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edge_tolerance                        Optional GPDouble. Edge tolerance. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mregion_size                          Optional GPLong. Minimum Region Size. Default value: 100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_sliver_size                       Optional GPLong. Maximum Sliver Size. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shrink_distance                       Optional GPDouble. Shrink distance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mthinness_ratio                       Optional GPDouble. Minimum Thinness Ratio. Default value: 0.05
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     reset_footprint                       Optional GPComposite. Computation Method. Default value: radiometry. Value choices: none, geometry, radiometry, copy_to_sibling
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     approx_num_vertices                   Optional GPLong. Approximate number of vertices. Default value: 80
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'update_boundary': ['update_boundary', 'optional'], 'simplification_method': ['simplification_method', 'optional'], 'skip_derived_images': ['skip_derived_images', 'optional'], 'maintaedges': ['maintain_edges', 'optional'], 'mdata_value': ['min_data_value', 'optional'], 'request_size': ['request_size', 'optional'], 'max_data_value': ['max_data_value', 'optional'], 'edge_tolerance': ['edge_tolerance', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'where_clause': ['where_clause', 'optional'], 'max_sliver_size': ['max_sliver_size', 'optional'], 'shrink_distance': ['shrink_distance', 'optional'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'reset_footprint': ['reset_footprint', 'optional'], 'approx_num_vertices': ['approx_num_vertices', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildFootprints', inputs, in_db, out_db)

          
def build_overviews(mosaic_dataset, where_clause=None, define_missing_tiles='true', generate_overviews='true', generate_missing_images='true', regenerate_stale_images='true'):
     """
     Geoprocessing tool that defines and generates overviews for a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     define_missing_tiles                  Optional GPBoolean. Define Missing Overview Tiles. Default value: true. Value choices: define_missing_tiles, no_define_missing_tiles
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     regenerate_stale_images               Optional GPBoolean. Regenerate Stale Overview Images Only. Default value: true. Value choices: regenerate_stale_images, ignore_stale_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_missing_images               Optional GPBoolean. Generate Missing Overview Images Only. Default value: true. Value choices: generate_missing_images, ignore_missing_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_overviews                    Optional GPBoolean. Generate Overviews. Default value: true. Value choices: generate_overviews, no_generate_overviews
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'generate_missing_images': ['generate_missing_images', 'optional'], 'define_missing_tiles': ['define_missing_tiles', 'optional'], 'regenerate_stale_images': ['regenerate_stale_images', 'optional'], 'generate_overviews': ['generate_overviews', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildOverviews', inputs, in_db, out_db)

          
def build_seamlines(mosaic_dataset, cell_size=None, sort_method='north_west', sort_order='true', order_by_attribute=None, order_by_base_value=None, view_point=None, computation_method='radiometry', blend_width=None, blend_type='both', request_size='1000', request_size_type='pixels', blend_width_units='pixels', area_of_interest='in_memory\{18b3c9c4-be24-4d7f-b8a9-fae3bd65574a}', where_clause=None, update_existing='false', mregion_size='100', mthinness_ratio='0.05', max_sliver_size='20'):
     """
     Geoprocessing tool that generates seamlines for your mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width_units                     Optional GPString. Blend Width Units. Default value: pixels. Value choices: pixels, ground_units
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mthinness_ratio                       Optional GPDouble. Minimum Thinness Ratio. Default value: 0.05
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional GPFeatureRecordSetLayer. Area of Interest. Default value: in_memory\{18b3c9c4-be24-4d7f-b8a9-fae3bd65574a}
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mregion_size                          Optional GPLong. Minimum Region Size. Default value: 100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point                            Optional GPPoint. View Point. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_by_base_value                   Optional GPVariant. Sort Base Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          Optional GPLong. Request Size. Default value: 1000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_sliver_size                       Optional GPLong. Maximum Sliver Size. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width                           Optional GPDouble. Blend Width. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_method                           Optional GPString. Sort Method. Default value: north_west. Value choices: north_west, closest_to_viewpoint, by_attribute
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_by_attribute                    Optional Field. Sort Attribute. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional GPMultiValue. Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_existing                       Optional GPBoolean. Update Existing Seamlines. Default value: false. Value choices: update_existing, ignore_existing
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_order                            Optional GPBoolean. Sort Ascending. Default value: true. Value choices: ascending, descending
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_type                            Optional GPString. Blend Type. Default value: both. Value choices: both, inside, outside
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     computation_method                    Optional GPString. Computation Method. Default value: radiometry. Value choices: geometry, radiometry, copy_footprint, copy_to_sibling, edge_detection, voronoi, disparity
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size_type                     Optional GPString. Request Size Type. Default value: pixels. Value choices: pixels, pixelsize_factor
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'blend_width_units': ['blend_width_units', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'view_point': ['view_point', 'optional'], 'order_by_base_value': ['order_by_base_value', 'optional'], 'request_size': ['request_size', 'optional'], 'max_sliver_size': ['max_sliver_size', 'optional'], 'blend_width': ['blend_width', 'optional'], 'sort_method': ['sort_method', 'optional'], 'order_by_attribute': ['order_by_attribute', 'optional'], 'cell_size': ['cell_size', 'optional'], 'update_existing': ['update_existing', 'optional'], 'sort_order': ['sort_order', 'optional'], 'blend_type': ['blend_type', 'optional'], 'computation_method': ['computation_method', 'optional'], 'request_size_type': ['request_size_type', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildSeamlines', inputs, in_db, out_db)

          
def calculate_cell_size_ranges(mosaic_dataset, where_clause=None, do_compute_min='true', do_compute_max='true', max_range_factor='10', cell_size_tolerance_factor='0.8', update_missing_only='false'):
     """
     Geoprocessing tool that computes the minimum and maximum cell sizes for the rasters in a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     do_compute_min                        Optional GPBoolean. Compute Minimum Cell Sizes. Default value: true. Value choices: min_cell_sizes, no_min_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size_tolerance_factor            Optional GPDouble. Cell Size Tolerance Factor. Default value: 0.8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_range_factor                      Optional GPDouble. Maximum Cell Size Range Factor. Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     do_compute_max                        Optional GPBoolean. Compute Maximum Cell Sizes. Default value: true. Value choices: max_cell_sizes, no_max_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_missing_only                   Optional GPBoolean. Update Missing Values Only. Default value: false. Value choices: update_missing_only, update_all
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'update_missing_only': ['update_missing_only', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'cell_size_tolerance_factor': ['cell_size_tolerance_factor', 'optional'], 'max_range_factor': ['max_range_factor', 'optional'], 'do_compute_min': ['do_compute_min', 'optional'], 'do_compute_max': ['do_compute_max', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateCellSizeRanges', inputs, in_db, out_db)

          
def color_balance_mosaic_dataset(mosaic_dataset, balancing_method='dodging', color_surface_type='single_color', target_raster=None, exclude_raster=None, stretch_type=None, gamma='1', block_field=None):
     """
     Geoprocessing tool that color balances a mosaic dataset so the tiles appear seamless.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     balancing_method                      Optional GPString. Balance Method. Default value: dodging. Value choices: dodging, histogram, standard_deviation
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     stretch_type                          Optional GPString. Stretch Type. Default value: none. Value choices: none, standard_deviation, minimum_maximum, adaptive
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gamma                                 Optional GPDouble. Gamma. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_raster                         Optional GPComposite. Target Raster. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     exclude_raster                        Optional GPRasterLayer. Exclude Area Raster. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     block_field                           Optional GPString. Block Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     color_surface_type                    Optional GPString. Color Surface Type. Default value: single_color. Value choices: single_color, color_grid, first_order, second_order, third_order
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'balancing_method': ['balancing_method', 'optional'], 'stretch_type': ['stretch_type', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'target_raster': ['target_raster', 'optional'], 'exclude_raster': ['exclude_raster', 'optional'], 'block_field': ['block_field', 'optional'], 'color_surface_type': ['color_surface_type', 'optional'], 'gamma': ['gamma', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ColorBalanceMosaicDataset', inputs, in_db, out_db)

          
def compute_dirty_area(mosaic_dataset, timestamp, where_clause=None):
     """
     Geoprocessing tool that identifies an area within a mosaic dataset that has changed since a specified point in time.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     timestamp                             Required GPString. Start Date and Time
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
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
     mosaicdataset_name                    Required GPString. Mosaic Dataset Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     coordinate_system                     Required GPSpatialReference. Coordinate System
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     num_bands                             Optional GPLong. Number of Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     product_band_definitions              Optional GPValueTable. Product Band Definitions. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     product_definition                    Optional GPString. Product Definition. Default value: none. Value choices: none, natural_color_rgb, natural_color_rgbi, false_color_irg, vector_field_uv, vector_field_magnitude_direction, deimos2_4bands, dmcii_3bands, dubaisat-2_4bands, formosat-2_4bands, geoeye-1_4bands, gf-1 pms_4bands, gf-1 wfv_4bands, gf-2 pms_4bands, gf-4 pmi_4bands, hj 1a/1b ccd_4bands, ikonos_4bands, jilin-1_3bands, kompsat-2_4bands, kompsat-3_4bands, landsat_6bands, landsat_mss_4bands, landsat_8bands, pleiades-1_4bands, quickbird_4bands, rapideye_5bands, sentinel2_13bands, spot-5_4bands, spot-6_4bands, spot-7_4bands, th-01_4bands, worldview-2_8bands, worldview-3_8bands, zy1-02c pms_3bands, zy3-cresda_4bands, zy3-sasmac_4bands, custom
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional GPString. Pixel Type. Default value: none. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaicdataset_name': ['in_mosaicdataset_name', 'required'], 'workspace': ['in_workspace', 'required'], 'num_bands': ['num_bands', 'optional'], 'product_band_definitions': ['product_band_definitions', 'optional'], 'product_definition': ['product_definition', 'optional'], 'coordinate_system': ['coordinate_system', 'required'], 'pixel_type': ['pixel_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateMosaicDataset', inputs, in_db, out_db)

          
def create_referenced_mosaic_dataset(dataset, coordinate_system=None, number_of_bands=None, pixel_type=None, where_clause=None, template_dataset=None, extent=None, select_using_features='true', lod_field=None, minps_field=None, maxps_field=None, pixel_size=None, build_boundary='true'):
     """
     Geoprocessing tool that creates a new mosaic dataset from a selection set of a raster catalog, or a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPComposite. Input Raster Catalog or Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_size                            Optional GPDouble. Maximum Visible Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_boundary                        Optional GPBoolean. Build Boundary. Default value: true. Value choices: build_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lod_field                             Optional Field. Scale Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_bands                       Optional GPLong. Number of Bands. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Optional GPEnvelope. Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system                     Optional GPSpatialReference. Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional GPComposite. Extent from Dataset. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maxps_field                           Optional Field. Maximum Cell Size Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minps_field                           Optional Field. Minimum Cell Size Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     select_using_features                 Optional GPBoolean. Using Input Geometry for Selection. Default value: true. Value choices: select_using_features, no_select_using_features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_type                            Optional GPString. Pixel Type. Default value: none. Value choices: 1_bit, 2_bit, 4_bit, 8_bit_unsigned, 8_bit_signed, 16_bit_unsigned, 16_bit_signed, 32_bit_unsigned, 32_bit_signed, 32_bit_float, 64_bit
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'pixel_size': ['pixelSize', 'optional'], 'build_boundary': ['build_boundary', 'optional'], 'lod_field': ['lod_field', 'optional'], 'number_of_bands': ['number_of_bands', 'optional'], 'extent': ['extent', 'optional'], 'coordinate_system': ['coordinate_system', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'maxps_field': ['maxPS_field', 'optional'], 'minps_field': ['minPS_field', 'optional'], 'where_clause': ['where_clause', 'optional'], 'select_using_features': ['select_using_features', 'optional'], 'pixel_type': ['pixel_type', 'optional']}
     out_db = {'mosaic_dataset': ['out_mosaic_dataset', 'required', None, None]}
     return _execute_tool('management', 'CreateReferencedMosaicDataset', inputs, in_db, out_db)

          
def define_overviews(mosaic_dataset, overview_image_folder=None, template_dataset=None, extent=None, pixel_size=None, number_of_levels=None, tile_rows='5120', tile_cols='5120', overview_factor='3', force_overview_tiles='false', resampling_method='bilinear', compression_method='jpeg', compression_quality='80'):
     """
     Geoprocessing tool that defines the tiling schema and properties of the preprocessed raster datasets that will cover part or all of a mosaic dataset at varying resolutions.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional GPLong. Compression Quality. Default value: 80
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pixel_size                            Optional GPDouble. Pixel Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overview_image_folder                 Optional DEWorkspace. Output Location. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overview_factor                       Optional GPLong. Overview Sampling Factor. Default value: 3
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Optional GPEnvelope. Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional GPComposite. Extent from Dataset. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_cols                             Optional GPLong. Number Of Columns. Default value: 5120
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_levels                      Optional GPLong. Number Of Levels. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_rows                             Optional GPLong. Number Of Rows. Default value: 5120
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_method                     Optional GPString. Resampling Method. Default value: bilinear. Value choices: nearest, bilinear, cubic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    Optional GPString. Compression Method. Default value: jpeg
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     force_overview_tiles                  Optional GPBoolean. Force Overview Tiles. Default value: false. Value choices: force_overview_tiles, no_force_overview_tiles
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'pixel_size': ['pixel_size', 'optional'], 'overview_image_folder': ['overview_image_folder', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'overview_factor': ['overview_factor', 'optional'], 'extent': ['extent', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'tile_cols': ['tile_cols', 'optional'], 'number_of_levels': ['number_of_levels', 'optional'], 'tile_rows': ['tile_rows', 'optional'], 'resampling_method': ['resampling_method', 'optional'], 'compression_method': ['compression_method', 'optional'], 'force_overview_tiles': ['force_overview_tiles', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DefineOverviews', inputs, in_db, out_db)

          
def generate_exclude_area(raster, pixel_type, generate_method, max_red='255', max_green='255', max_blue='255', max_white='255', max_black='0', max_magenta='255', max_cyan='255', max_yellow='255', percentage_low='0', percentage_high='100'):
     """
     Geoprocessing tool that generates exclude areas to use within the Color Balance Mosaic Dataset tool.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     generate_method                       Required GPString. Generate Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     pixel_type                            Required GPString. Pixel Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_black                             Optional GPDouble. Maximum Black. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_yellow                            Optional GPDouble. Maximum Yellow. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cyan                              Optional GPDouble. Maximum Cyan. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_magenta                           Optional GPDouble. Maximum Magenta. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_red                               Optional GPDouble. Maximum Red. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_green                             Optional GPDouble. Maximum Green. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage_high                       Optional GPDouble. High Percentage. Default value: 100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage_low                        Optional GPDouble. Low Percentage. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_blue                              Optional GPDouble. Maximum Blue. Default value: 255
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_white                             Optional GPDouble. Maximum White. Default value: 255
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'max_yellow': ['max_yellow', 'optional'], 'max_cyan': ['max_cyan', 'optional'], 'max_red': ['max_red', 'optional'], 'percentage_high': ['percentage_high', 'optional'], 'max_white': ['max_white', 'optional'], 'max_blue': ['max_blue', 'optional'], 'max_black': ['max_black', 'optional'], 'max_magenta': ['max_magenta', 'optional'], 'max_green': ['max_green', 'optional'], 'pixel_type': ['pixel_type', 'required'], 'percentage_low': ['percentage_low', 'optional'], 'generate_method': ['generate_method', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'GenerateExcludeArea', inputs, in_db, out_db)

          
def import_mosaic_dataset_geometry(mosaic_dataset, target_featureclass_type, target_jofield, input_featureclass, input_jofield):
     """
     Geoprocessing tool that imports geometry to a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_featureclass                    Required GPComposite. Input Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_featureclass_type              Required GPString. Target Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_jofield                        Required Field. Target Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_jofield                         Required Field. Input Join Field
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_featureclass': ['input_featureclass', 'required'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'target_featureclass_type': ['target_featureclass_type', 'required'], 'target_jofield': ['target_join_field', 'required'], 'input_jofield': ['input_join_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportMosaicDatasetGeometry', inputs, in_db, out_db)

          
def remove_rasters_from_mosaic_dataset(mosaic_dataset, where_clause=None, update_boundary='true', mark_overviews_items='true', delete_overview_images='true', delete_item_cache='true', remove_items='true', update_cellsize_ranges='true'):
     """
     Geoprocessing tool that removes rasters from a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_overview_images                Optional GPBoolean. Delete Overview Images. Default value: true. Value choices: delete_overview_images, no_delete_overview_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_item_cache                     Optional GPBoolean. Delete Item Cache. Default value: true. Value choices: delete_item_cache, no_delete_item_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mark_overviews_items                  Optional GPBoolean. Mark Affected Overviews. Default value: true. Value choices: mark_overview_items, no_mark_overview_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional GPBoolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                Optional GPBoolean. Update Cell Size Ranges. Default value: true. Value choices: update_cell_sizes, no_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     remove_items                          Optional GPBoolean. Remove Mosaic Dataset Items. Default value: true. Value choices: remove_mosaicdataset_items, no_remove_mosaicdataset_items
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'delete_overview_images': ['delete_overview_images', 'optional'], 'delete_item_cache': ['delete_item_cache', 'optional'], 'where_clause': ['where_clause', 'optional'], 'mark_overviews_items': ['mark_overviews_items', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'remove_items': ['remove_items', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RemoveRastersFromMosaicDataset', inputs, in_db, out_db)

          
def synchronize_mosaic_dataset(mosaic_dataset, where_clause=None, new_items='false', sync_only_stale='true', update_cellsize_ranges='true', update_boundary='true', update_overviews='false', build_pyramids='false', calculate_statistics='false', build_thumbnails='false', build_item_cache='false', rebuild_raster='true', update_fields='true', fields_to_update=None, existing_items='true', broken_items='false', skip_existing_items='true', refresh_aggregate_info='false', estimate_statistics='false'):
     """
     Geoprocessing tool that rebuilds the raster item and updates affected fields in the mosaic dataset using the raster type and options that were used when it was originally added.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rebuild_raster                        Optional GPBoolean. Rebuild Raster From Data Source. Default value: true. Value choices: rebuild_raster, no_raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_items                             Optional GPBoolean. Update With New Items. Default value: false. Value choices: update_with_new_items, no_new_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     broken_items                          Optional GPBoolean. Remove Items With Broken Data Source. Default value: false. Value choices: remove_broken_items, ignore_broken_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     refresh_aggregate_info                Optional GPBoolean. Refresh Aggregate Information. Default value: false. Value choices: refresh_info, no_refresh_info
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_item_cache                      Optional GPBoolean. Build Item Cache. Default value: false. Value choices: build_item_cache, no_item_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_boundary                       Optional GPBoolean. Update Boundary. Default value: true. Value choices: update_boundary, no_boundary
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing_items                   Optional GPBoolean. Skip Existing Items. Default value: true. Value choices: skip_existing_items, overwrite_existing_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_thumbnails                      Optional GPBoolean. Build Thumbnails. Default value: false. Value choices: build_thumbnails, no_thumbnails
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_cellsize_ranges                Optional GPBoolean. Update Cell Size Ranges. Default value: true. Value choices: update_cell_sizes, no_cell_sizes
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields_to_update                      Optional GPMultiValue. Fields To Update. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     existing_items                        Optional GPBoolean. Update Existing Items. Default value: true. Value choices: update_existing_items, ignore_existing_items
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     build_pyramids                        Optional GPBoolean. Build Raster Pyramids. Default value: false. Value choices: build_pyramids, no_pyramids
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate_statistics                   Optional GPBoolean. Estimate Mosaic Dataset Statistics. Default value: false. Value choices: estimate_statistics, no_statistics
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_fields                         Optional GPBoolean. Update Fields. Default value: true. Value choices: update_fields, no_fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sync_only_stale                       Optional GPBoolean. Synchronize Stale Items Only. Default value: true. Value choices: sync_stale, sync_all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     update_overviews                      Optional GPBoolean. Update Overviews. Default value: false. Value choices: update_overviews, no_overviews
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     calculate_statistics                  Optional GPBoolean. Calculate Statistics. Default value: false. Value choices: calculate_statistics, no_statistics
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'rebuild_raster': ['rebuild_raster', 'optional'], 'new_items': ['new_items', 'optional'], 'broken_items': ['broken_items', 'optional'], 'refresh_aggregate_info': ['refresh_aggregate_info', 'optional'], 'build_item_cache': ['build_item_cache', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'skip_existing_items': ['skip_existing_items', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'fields_to_update': ['fields_to_update', 'optional'], 'existing_items': ['existing_items', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'where_clause': ['where_clause', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'update_fields': ['update_fields', 'optional'], 'sync_only_stale': ['sync_only_stale', 'optional'], 'update_overviews': ['update_overviews', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SynchronizeMosaicDataset', inputs, in_db, out_db)

          
def calculate_end_time(table, start_field, end_field, fields=None):
     """
     Geoprocessing tool that populates the values for a specified end time  field with values calculated using the specified start time field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     end_field                             Required Field. End Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     start_field                           Required Field. Start Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Optional GPMultiValue. ID Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'end_field': ['end_field', 'required'], 'fields': ['fields', 'optional'], 'start_field': ['start_field', 'required'], 'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'CalculateEndTime', inputs, in_db, out_db)

          
def convert_time_field(table, input_time_field, input_time_format, output_time_field, output_time_type='date', output_time_format=None):
     """
     Geoprocessing tool to convert timestamps stored in a text or numeric field to a date field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_time_format                     Required GPString. Input Time Format
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_field                     Required GPString. Output Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_field                      Required Field. Input Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_time_type                      Optional GPString. Output Time Type. Default value: date. Value choices: date, text, long, short, double, float
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_time_format                    Optional GPString. Output Time Format. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_time_format': ['input_time_format', 'required'], 'output_time_format': ['output_time_format', 'optional'], 'output_time_type': ['output_time_type', 'optional'], 'table': ['in_table', 'required'], 'output_time_field': ['output_time_field', 'required'], 'input_time_field': ['input_time_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeField', inputs, in_db, out_db)

          
def convert_time_zone(table, input_time_field, input_time_zone, output_time_field, output_time_zone, input_dst='true', output_dst='true'):
     """
     Geoprocessing tool to convert time values from one time zone to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_zone                      Required GPString. Output Time Zone
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_time_field                     Required GPString. Output Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_zone                       Required GPString. Input Time Zone
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_time_field                      Required Field. Input Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_dst                            Optional GPBoolean. Output time field values will be adjusted for Daylight Saving Time. Default value: true. Value choices: output_adjusted_for_dst, output_not_adjusted_for_dst
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_dst                             Optional GPBoolean. Input time field values are adjusted for Daylight Saving Time. Default value: true. Value choices: input_adjusted_for_dst, input_not_adjusted_for_dst
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'input_dst': ['input_dst', 'optional'], 'input_time_zone': ['input_time_zone', 'required'], 'output_dst': ['output_dst', 'optional'], 'table': ['in_table', 'required'], 'output_time_zone': ['output_time_zone', 'required'], 'output_time_field': ['output_time_field', 'required'], 'input_time_field': ['input_time_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeZone', inputs, in_db, out_db)

          
def transpose_fields(table, field, transposed_field_name, value_field_name, attribute_fields=None):
     """
     Geoprocessing tool to transpose data values stored in columns  of a table or feature class into rows.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     transposed_field_name                 Required GPString. Transposed Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     value_field_name                      Required GPString. Value Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required GPValueTable. Fields To Transpose
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     attribute_fields                      Optional GPMultiValue. Attribute Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'attribute_fields': ['attribute_fields', 'optional'], 'table': ['in_table', 'required'], 'transposed_field_name': ['in_transposed_field_name', 'required'], 'value_field_name': ['in_value_field_name', 'required'], 'field': ['in_field', 'required']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'TransposeFields', inputs, in_db, out_db)

          
def warp_from_file(raster, link_file, transformation_type='polyorder1', resampling_type='nearest'):
     """
     Geoprocessing tool that performs a transformation on the raster based on a link file, using a polynomial transformation.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     link_file                             Required DETextFile. Link File
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   Optional GPString. Transformation Type. Default value: polyorder1. Value choices: polyorder0, polysimilarity, polyorder1, polyorder2, polyorder3, adjust, spline, projective
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional GPString. Resampling Technique. Default value: nearest. Value choices: nearest, bilinear, cubic, majority
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'link_file': ['link_file', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'transformation_type': ['transformation_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'WarpFromFile', inputs, in_db, out_db)

          
def import_xml_workspace_document(target_geodatabase, file, import_type='data', config_keyword=None):
     """
     Geoprocessing tool that imports the contents of an XML workspace document into an existing geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_geodatabase                    Required DEWorkspace. Target Geodatabase
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     file                                  Required DEFile. Import File
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     config_keyword                        Optional GPString. Configuration Keyword. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     import_type                           Optional GPString. Import Options. Default value: data. Value choices: data, schema_only
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'target_geodatabase': ['target_geodatabase', 'required'], 'import_type': ['import_type', 'optional'], 'file': ['in_file', 'required'], 'config_keyword': ['config_keyword', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ImportXMLWorkspaceDocument', inputs, in_db, out_db)

          
def alter_mosaic_dataset_schema(mosaic_dataset, side_tables=None, raster_type_names=None, editor_tracking='false'):
     """
     Geoprocessing tool to define the editing operations nonowners have when editing a mosaic dataset in an enterprise geodatabase.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_type_names                     Optional GPMultiValue. Raster Types. Default value: none. Value choices: ads, cadrg/ecrg, cib, deimos-2, dmcii, dted, dubaisat-2, formosat-2, frame camera, gf-1 pms, gf-1 wfv, gf-2 pms, gf-4 pmi, grib, geoeye-1, hdf, hj 1a/1b ccd, hre, ikonos, jilin-1, kompsat-2, kompsat-3, las, landsat 1-5 mss, landsat 4-5 tm, landsat 7 etm+, landsat 8, ncdrd, nitf, netcdf, pleiades-1, quickbird, radarsat-2, rapideye, raster process definition, spot 5, spot 6, spot 7, scanned aerial imagery, sentinel-2, th-01, uav/uas, worldview-1, worldview-2, worldview-3, zy1-02c hrc, zy1-02c pms, zy3-cresda, zy3-sasmac
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     side_tables                           Optional GPMultiValue. Operations. Default value: none. Value choices: analysis, boundary, cache, color_correction, definition, levels, log, overview, seamline, stereo, view
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     editor_tracking                       Optional GPBoolean. Enable Editor Tracking. Default value: false. Value choices: editor_tracking, no_editor_tracking
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster_type_names': ['raster_type_names', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'side_tables': ['side_tables', 'optional'], 'editor_tracking': ['editor_tracking', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterMosaicDatasetSchema', inputs, in_db, out_db)

          
def analyze_mosaic_dataset(mosaic_dataset, where_clause=None, checker_keywords=None):
     """
     Geoprocessing tool that checks a mosaic dataset for errors, and possible improvements.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     checker_keywords                      Optional GPMultiValue. Checks Performed. Default value: none. Value choices: footprint, function, raster, paths, source_validity, stale, pyramids, statistics, performance, information
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
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
     workspace                             Required DEWorkspace. Input File or Personal Geodatabase
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
     data                                  Optional GPComposite. Input Workspace. Default value: none
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
     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     include_system                        Required GPBoolean. Include System Tables
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_archive                       Optional GPBoolean. Analyze Archive Tables for Selected Dataset(s). Default value: true. Value choices: analyze_archive, no_analyze_archive
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_delta                         Optional GPBoolean. Analyze Delta Tables for Selected Dataset(s). Default value: true. Value choices: analyze_delta, no_analyze_delta
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasets                              Optional GPMultiValue. Datasets to Analyze. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     analyze_base                          Optional GPBoolean. Analyze Base Tables for Selected Dataset(s). Default value: true. Value choices: analyze_base, no_analyze_base
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'analyze_archive': ['analyze_archive', 'optional'], 'input_database': ['input_database', 'required'], 'analyze_delta': ['analyze_delta', 'optional'], 'datasets': ['in_datasets', 'optional'], 'analyze_base': ['analyze_base', 'optional'], 'include_system': ['include_system', 'required']}
     out_db = {}
     return _execute_tool('management', 'AnalyzeDatasets', inputs, in_db, out_db)

          
def rebuild_indexes(input_database, include_system, datasets=None, delta_only='true'):
     """
     Geoprocessing tool to update indexes of datasets stored in a database or geodatabase in DB2, Oracle, PostgreSQL, or SQL Server. In geodatabases, indexes  can also be rebuilt on  states and state_lineage geodatabase system tables and the delta tables of versioned datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     include_system                        Required GPBoolean. Include System Tables
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delta_only                            Optional GPBoolean. Rebuild Delta Tables Only. Default value: true. Value choices: only_deltas, all
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasets                              Optional GPMultiValue. Datasets to Rebuild Indexes For. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'datasets': ['in_datasets', 'optional'], 'delta_only': ['delta_only', 'optional'], 'input_database': ['input_database', 'required'], 'include_system': ['include_system', 'required']}
     out_db = {}
     return _execute_tool('management', 'RebuildIndexes', inputs, in_db, out_db)

          
def check_geometry(features):
     """
     Geoprocessing tool to generate a report of geometry problems in a feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPMultiValue. Input Features
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
     reconcile_mode                        Required GPString. Reconcile Mode
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     with_post                             Optional GPBoolean. Post Versions After Reconcile. Default value: false. Value choices: post, no_post
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     acquire_locks                         Optional GPBoolean. Acquire Locks. Default value: true. Value choices: lock_acquired, no_lock_acquired
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     with_delete                           Optional GPBoolean. Delete Versions After Post. Default value: false. Value choices: delete_version, keep_version
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        Optional GPString. Target Version. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     abort_if_conflicts                    Optional GPBoolean. Abort if Conflicts Detected. Default value: false. Value choices: abort_conflicts, no_abort
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     conflict_resolution                   Optional GPString. Conflict Resolution. Default value: favor_target_version. Value choices: favor_target_version, favor_edit_version
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_versions                         Optional GPMultiValue. Edit Versions. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     conflict_definition                   Optional GPString. Conflict Definition. Default value: by_object. Value choices: by_object, by_attribute
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'with_post': ['with_post', 'optional'], 'acquire_locks': ['acquire_locks', 'optional'], 'with_delete': ['with_delete', 'optional'], 'abort_if_conflicts': ['abort_if_conflicts', 'optional'], 'target_version': ['target_version', 'optional'], 'conflict_resolution': ['conflict_resolution', 'optional'], 'input_database': ['input_database', 'required'], 'reconcile_mode': ['reconcile_mode', 'required'], 'edit_versions': ['edit_versions', 'optional'], 'conflict_definition': ['conflict_definition', 'optional']}
     out_db = {'log': ['out_log', 'optional', None, None]}
     return _execute_tool('management', 'ReconcileVersions', inputs, in_db, out_db)

          
def add_attachments(dataset, jofield, match_table, match_jofield, match_path_field, working_folder=None):
     """
     Geoprocessing tool that adds file attachments to the records of a geodatabase feature class or table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jofield                               Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required GPTableView. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_path_field                      Required Field. Match Path Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_table                           Required GPTableView. Match Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_jofield                         Required Field. Match Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     working_folder                        Optional DEFolder. Working Folder. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'working_folder': ['in_working_folder', 'optional'], 'dataset': ['in_dataset', 'required'], 'match_path_field': ['in_match_path_field', 'required'], 'jofield': ['in_join_field', 'required'], 'match_jofield': ['in_match_join_field', 'required'], 'match_table': ['in_match_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddAttachments', inputs, in_db, out_db)

          
def disable_attachments(dataset):
     """
     Geoprocessing tool that disables attachments on a geodatabase feature class or table.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPTableView. Input Dataset
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
     dataset                               Required GPTableView. Input Dataset
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
     jofield                               Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required GPTableView. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_table                           Required GPTableView. Match Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     match_jofield                         Required Field. Match Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     match_name_field                      Optional Field. Match Name Field. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'jofield': ['in_join_field', 'required'], 'dataset': ['in_dataset', 'required'], 'match_table': ['in_match_table', 'required'], 'match_name_field': ['in_match_name_field', 'optional'], 'match_jofield': ['in_match_join_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveAttachments', inputs, in_db, out_db)

          
def set_mosaic_dataset_properties(mosaic_dataset, rows_maximum_imagesize='4100', columns_maximum_imagesize='15000', allowed_compressions='none;lz77;jpeg;lerc', default_compression_type=None, jpeg_quality='75', lerc_tolerance='0', resampling_type='bilinear', clip_to_footprints='false', footprints_may_contanodata='true', clip_to_boundary='true', color_correction='false', allowed_mensuration_capabilities=None, default_mensuration_capabilities='none', allowed_mosaic_methods='center;northwest;lockraster;byattribute;nadir;viewpoint;seamline;none', default_mosaic_method='center', order_field=None, order_base=None, sorting_order='true', mosaic_operator='first', blend_width='10', view_point_x='600', view_point_y='300', max_num_per_mosaic='20', cell_size_tolerance='0.8', cell_size=None, metadata_level='full', transmission_fields=None, use_time='false', start_time_field=None, end_time_field=None, time_format=None, geographic_transform=None, max_num_of_download_items='20', max_num_of_records_returned='1000', data_source_type='generic', minimum_pixel_contribution='1', processing_templates=None, default_processing_template='none', time_interval=None, time_interval_units=None):
     """
     Geoprocessing tool that sets the default properties of a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_per_mosaic                    Optional GPLong. Max Number Per Mosaic. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     columns_maximum_imagesize             Optional GPLong. Columns of Maximum Image Size of Requests. Default value: 15000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_mosaic_method                 Optional GPString. Default Mosaic Methods. Default value: center. Value choices: none, center, northwest, lockraster, byattribute, nadir, viewpoint, seamline
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_to_footprints                    Optional GPBoolean. Clip To Footprints. Default value: false. Value choices: clip, not_clip
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point_y                          Optional GPDouble. View Point Spacing Y. Default value: 300
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lerc_tolerance                        Optional GPDouble. LERC Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_processing_template           Optional GPString. Default Processing Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     footprints_may_contanodata            Optional GPBoolean. Footprints May Contain NoData. Default value: true. Value choices: footprints_may_contain_nodata, footprints_do_not_contain_nodata
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_point_x                          Optional GPDouble. View Point Spacing X. Default value: 600
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_interval                         Optional GPDouble. Time Interval. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_of_download_items             Optional GPLong. Max Number of Download Items. Default value: 20
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transmission_fields                   Optional GPMultiValue. Allowed Transmission Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     end_time_field                        Optional GPString. End Time Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     color_correction                      Optional GPBoolean. Color Correction. Default value: false. Value choices: apply, not_apply
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_base                            Optional GPString. Order Base. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_mensuration_capabilities      Optional GPString. Default Mensuration. Default value: none. Value choices: none, basic, base-top height, base-top shadow height, top-top shadow height, 3d
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_pixel_contribution            Optional GPLong. Minimum Pixel Contribution. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size_tolerance                   Optional GPDouble. Cell Size Tolerance Factor. Default value: 0.8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jpeg_quality                          Optional GPLong. JPEG Quality. Default value: 75
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     metadata_level                        Optional GPString. Metadata Level. Default value: full. Value choices: none, basic, full
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geographic_transform                  Optional GPMultiValue. Geographic Transformation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_time                              Optional GPBoolean. Use Time. Default value: false. Value choices: enabled, disabled
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_source_type                      Optional GPString. Data Source Type. Default value: generic. Value choices: generic, thematic, processed, elevation, scientific, vector_uv, vector_magdir
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_format                           Optional GPString. Time Format. Default value: none. Value choices: yyyy, yyyymm, yyyy/mm, yyyy-mm, yyyymmdd, yyyy/mm/dd, yyyy-mm-dd, yyyymmddhhmmss, yyyy/mm/dd hh:mm:ss, yyyy-mm-dd hh:mm:ss, yyyymmddhhmmss.s, yyyy/mm/dd hh:mm:ss.s, yyyy-mm-dd hh:mm:ss.s
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_to_boundary                      Optional GPBoolean. Clip To Boundary. Default value: true. Value choices: clip, not_clip
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_compressions                  Optional GPMultiValue. Allowed Transmission Compression. Default value: none;lz77;jpeg;lerc. Value choices: none, jpeg, lz77, lerc
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_mensuration_capabilities      Optional GPMultiValue. Allowed Mensuration Capabilities. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     rows_maximum_imagesize                Optional GPLong. Rows of Maximum Image Size of Requests. Default value: 4100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     default_compression_type              Optional GPString. Default Compression Type. Default value: none. Value choices: none, jpeg, lz77, lerc
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     processing_templates                  Optional GPMultiValue. Processing Templates. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     allowed_mosaic_methods                Optional GPMultiValue. Allowed Mosaic Methods. Default value: center;northwest;lockraster;byattribute;nadir;viewpoint;seamline;none. Value choices: none, center, northwest, lockraster, byattribute, nadir, viewpoint, seamline
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     order_field                           Optional GPString. Order Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional GPCellSizeXY. Output Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_interval_units                   Optional GPString. Time Interval Units. Default value: none. Value choices: none, milliseconds, seconds, minutes, hours, days, weeks, months, years, decades, centuries
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     blend_width                           Optional GPLong. Blend Width. Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_operator                       Optional GPString. Mosaic Operator. Default value: first. Value choices: first, last, min, max, mean, blend, sum
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     start_time_field                      Optional GPString. Start Time Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_num_of_records_returned           Optional GPLong. Max Number of Records Returned. Default value: 1000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sorting_order                         Optional GPBoolean. Sorting Order Ascending. Default value: true. Value choices: ascending, descending
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     resampling_type                       Optional GPString. Resampling Technique. Default value: bilinear. Value choices: nearest, bilinear, cubic, majority
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'max_num_per_mosaic': ['max_num_per_mosaic', 'optional'], 'columns_maximum_imagesize': ['columns_maximum_imagesize', 'optional'], 'default_mosaic_method': ['default_mosaic_method', 'optional'], 'clip_to_footprints': ['clip_to_footprints', 'optional'], 'view_point_y': ['view_point_y', 'optional'], 'lerc_tolerance': ['LERC_Tolerance', 'optional'], 'default_processing_template': ['default_processing_template', 'optional'], 'footprints_may_contanodata': ['footprints_may_contain_nodata', 'optional'], 'minimum_pixel_contribution': ['minimum_pixel_contribution', 'optional'], 'view_point_x': ['view_point_x', 'optional'], 'time_interval': ['time_interval', 'optional'], 'max_num_of_download_items': ['max_num_of_download_items', 'optional'], 'transmission_fields': ['transmission_fields', 'optional'], 'end_time_field': ['end_time_field', 'optional'], 'color_correction': ['color_correction', 'optional'], 'order_base': ['order_base', 'optional'], 'default_mensuration_capabilities': ['default_mensuration_capabilities', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'cell_size_tolerance': ['cell_size_tolerance', 'optional'], 'jpeg_quality': ['JPEG_quality', 'optional'], 'metadata_level': ['metadata_level', 'optional'], 'geographic_transform': ['geographic_transform', 'optional'], 'use_time': ['use_time', 'optional'], 'data_source_type': ['data_source_type', 'optional'], 'time_format': ['time_format', 'optional'], 'clip_to_boundary': ['clip_to_boundary', 'optional'], 'allowed_compressions': ['allowed_compressions', 'optional'], 'allowed_mensuration_capabilities': ['allowed_mensuration_capabilities', 'optional'], 'rows_maximum_imagesize': ['rows_maximum_imagesize', 'optional'], 'default_compression_type': ['default_compression_type', 'optional'], 'processing_templates': ['processing_templates', 'optional'], 'allowed_mosaic_methods': ['allowed_mosaic_methods', 'optional'], 'order_field': ['order_field', 'optional'], 'cell_size': ['cell_size', 'optional'], 'time_interval_units': ['time_interval_units', 'optional'], 'blend_width': ['blend_width', 'optional'], 'mosaic_operator': ['mosaic_operator', 'optional'], 'start_time_field': ['start_time_field', 'optional'], 'max_num_of_records_returned': ['max_num_of_records_returned', 'optional'], 'sorting_order': ['sorting_order', 'optional'], 'resampling_type': ['resampling_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetMosaicDatasetProperties', inputs, in_db, out_db)

          
def set_raster_properties(raster, data_type=None, statistics=None, stats_file=None, nodata=None, key_properties=None):
     """
     Geoprocessing tool that sets properties on a raster dataset or mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata                                Optional GPValueTable. Bands for NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     key_properties                        Optional GPValueTable. Key Properties. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     statistics                            Optional GPValueTable. Statistics Per Band. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     stats_file                            Optional DEFile. Import Statistics From File. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     data_type                             Optional GPString. Data Source Type. Default value: none. Value choices: generic, elevation, thematic, processed, scientific, vector_uv, vector_magdir
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'nodata': ['nodata', 'optional'], 'stats_file': ['stats_file', 'optional'], 'key_properties': ['key_properties', 'optional'], 'data_type': ['data_type', 'optional'], 'statistics': ['statistics', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetRasterProperties', inputs, in_db, out_db)

          
def download_rasters(image_service, out_folder, where_clause=None, selection_feature=None, clipping='false', convert_rasters='false', format='tiff', compression_method=None, compression_quality=None, maintain_folder='false'):
     """
     Geoprocessing tool that downloads source files of the selected rasters from an image service to a designated location.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     image_service                         Required GPComposite. Input Image Service
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder                            Required DEFolder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clipping                              Optional GPBoolean. Clipping Using Selection Feature. Default value: false. Value choices: clipping, no_clipping
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional GPLong. Compression Quality. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maintain_folder                       Optional GPBoolean. Maintain Folder Structure. Default value: false. Value choices: maintain_folder, no_maintain_folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     selection_feature                     Optional GPExtent. Selection Feature. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Expression. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    Optional GPString. Compression Method. Default value: none. Value choices: none, jpeg, lzw, packbits, rle, ccitt_group3, ccitt_group4, ccitt_1d
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     convert_rasters                       Optional GPBoolean. Convert Rasters. Default value: false. Value choices: always_convert, convert_as_required
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional GPString. Output Format. Default value: tiff. Value choices: tiff, bil, bsq, bip, bmp, envi, imagine image, jpeg, gif, jp2, png
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'compression_quality': ['compression_quality', 'optional'], 'clipping': ['clipping', 'optional'], 'image_service': ['in_image_service', 'required'], 'maintain_folder': ['MAINTAIN_FOLDER', 'optional'], 'selection_feature': ['selection_feature', 'optional'], 'where_clause': ['where_clause', 'optional'], 'compression_method': ['compression_method', 'optional'], 'convert_rasters': ['convert_rasters', 'optional'], 'out_folder': ['out_folder', 'required'], 'format': ['format', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DownloadRasters', inputs, in_db, out_db)

          
def create_enterprise_geodatabase(database_platform, instance_name, authorization_file, database_name=None, account_authentication='false', database_admin='sa', database_admpassword=None, sde_schema='true', gdb_admname='sde', gdb_admpassword=None, tablespace_name=None):
     """
     Geoprocessing tool that creates a database, geodatabase, and geodatabase administrator user in a Microsoft SQL Server  or PostgreSQL DBMS and creates a geodatabase, tablespace, and geodatabase administrator user in an Oracle DBMS.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     instance_name                         Required GPString. Instance
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     authorization_file                    Required DEFile. Authorization File
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     database_platform                     Required GPString. Database Platform
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_name                         Optional GPString. Database. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tablespace_name                       Optional GPString. Tablespace Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_admin                        Optional GPString. Database Administrator. Default value: sa
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gdb_admname                           Optional GPString. Geodatabase Administrator. Default value: sde
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gdb_admpassword                       Optional GPEncryptedString. Geodatabase Administrator Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     account_authentication                Optional GPBoolean. Operating System Authentication. Default value: false. Value choices: operating_system_auth, database_auth
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database_admpassword                  Optional GPEncryptedString. Database Administrator Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sde_schema                            Optional GPBoolean. Sde Owned Schema. Default value: true. Value choices: sde_schema, dbo_schema
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'instance_name': ['instance_name', 'required'], 'tablespace_name': ['tablespace_name', 'optional'], 'database_admin': ['database_admin', 'optional'], 'sde_schema': ['sde_schema', 'optional'], 'gdb_admpassword': ['gdb_admin_password', 'optional'], 'authorization_file': ['authorization_file', 'required'], 'gdb_admname': ['gdb_admin_name', 'optional'], 'account_authentication': ['account_authentication', 'optional'], 'database_name': ['database_name', 'optional'], 'database_platform': ['database_platform', 'required'], 'database_admpassword': ['database_admin_password', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateEnterpriseGeodatabase', inputs, in_db, out_db)

          
def enable_enterprise_geodatabase(input_database, authorization_file):
     """
     Geoprocessing tool that creates geodatabase system tables, stored procedures, functions, and types in an existing database.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     authorization_file                    Required DEFile. Authorization File
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        Required DEWorkspace. Input Database Connection
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'authorization_file': ['authorization_file', 'required'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'EnableEnterpriseGeodatabase', inputs, in_db, out_db)

          
def feature_envelope_to_polygon(features, single_envelope='false'):
     """
     Geoprocessing tool that creates polygon features representing the envelopes of input features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     single_envelope                       Optional GPBoolean. Create multipart features. Default value: false. Value choices: multipart, singlepart
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'single_envelope': ['single_envelope', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'FeatureEnvelopeToPolygon', inputs, in_db, out_db)

          
def create_database_connection(out_folder_path, out_name, database_platform, instance, account_authentication='true', username=None, password=None, save_user_pass='true', database=None, schema=None, version_type='transactional', version=None, date=None):
     """
     Geoprocessing tool for creating connection files to databases or enterprise, workgroup, or desktop geodatabases.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_folder_path                       Required DEFolder. Connection File Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. Connection File Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     instance                              Required GPString. Instance
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     database_platform                     Required GPString. Database Platform
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     save_user_pass                        Optional GPBoolean. Save username and password. Default value: true. Value choices: save_username, do_not_save_username
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version                               Optional GPString. The following version will be used. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     password                              Optional GPEncryptedString. Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     version_type                          Optional GPString. Version Type. Default value: transactional. Value choices: transactional, historical, point_in_time
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     database                              Optional GPString. Database. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     username                              Optional GPString. Username. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     account_authentication                Optional GPBoolean. Database Authentication. Default value: true. Value choices: database_auth, operating_system_auth
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     schema                                Optional GPString. Schema (Oracle user schema geodatabases only). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     date                                  Optional GPDate. Date and Time. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'version': ['version', 'optional'], 'password': ['password', 'optional'], 'instance': ['instance', 'required'], 'date': ['date', 'optional'], 'save_user_pass': ['save_user_pass', 'optional'], 'out_folder_path': ['out_folder_path', 'required'], 'database': ['database', 'optional'], 'schema': ['schema', 'optional'], 'version_type': ['version_type', 'optional'], 'username': ['username', 'optional'], 'account_authentication': ['account_authentication', 'optional'], 'database_platform': ['database_platform', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseConnection', inputs, in_db, out_db)

          
def delete_mosaic_dataset(mosaic_dataset, delete_overview_images='true', delete_item_cache='true'):
     """
     Geoprocessing tool that deletes a mosaic dataset, overviews, and item cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_overview_images                Optional GPBoolean. Delete Overview Images. Default value: true. Value choices: delete_overview_images, no_delete_overview_images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     delete_item_cache                     Optional GPBoolean. Delete Item Cache. Default value: true. Value choices: delete_item_cache, no_delete_item_cache
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'delete_item_cache': ['delete_item_cache', 'optional'], 'delete_overview_images': ['delete_overview_images', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DeleteMosaicDataset', inputs, in_db, out_db)

          
def generate_attachment_match_table(dataset, folder, key_field, file_filter=None, use_relative_paths='true'):
     """
     Geoprocessing tool that creates a Match Table to be used with the Add Attachments and Remove Attachment tools.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     folder                                Required DEFolder. Input Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required GPTableView. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     key_field                             Required Field. Key Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_relative_paths                    Optional GPBoolean. Store Relative Path. Default value: true. Value choices: relative, absolute
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     file_filter                           Optional GPString. Input Data Filter. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'folder': ['in_folder', 'required'], 'dataset': ['in_dataset', 'required'], 'key_field': ['in_key_field', 'required'], 'file_filter': ['in_file_filter', 'optional'], 'use_relative_paths': ['in_use_relative_paths', 'optional']}
     out_db = {'match_table': ['out_match_table', 'required', None, None]}
     return _execute_tool('management', 'GenerateAttachmentMatchTable', inputs, in_db, out_db)

          
def create_database_view(input_database, view_name, view_definition):
     """
     Geoprocessing tool for creating a view in a database or enterprise geodatabase based on an SQL expression.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     view_name                             Required GPString. Output View Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     view_definition                       Required GPString. View Definition
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        Required DEWorkspace. Input Database Connection
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'view_name': ['view_name', 'required'], 'view_definition': ['view_definition', 'required'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseView', inputs, in_db, out_db)

          
def sort_coded_value_domain(workspace, domaname, sort_by, sort_order):
     """
     Geoprocessing tool that sorts the code or description of a coded value domain in either ascending or descending order.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_by                               Required GPString. Sort By
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     sort_order                            Required GPString. Sort Order
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     domaname                              Required GPString. Domain Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     workspace                             Required DEWorkspace. Input Workspace
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'sort_by': ['sort_by', 'required'], 'sort_order': ['sort_order', 'required'], 'domaname': ['domain_name', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'SortCodedValueDomain', inputs, in_db, out_db)

          
def disable_editor_tracking(dataset, creator='true', creation_date='true', last_editor='true', last_edit_date='true'):
     """
     Geoprocessing tool to disable editor tracking on a feature class, table, mosaic dataset, or raster catalog.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required DEDatasetType. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_edit_date                        Optional GPBoolean. Disable Last Edit Date Tracking. Default value: true. Value choices: disable_last_edit_date, no_disable_last_edit_date
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creator                               Optional GPBoolean. Disable Creator Tracking. Default value: true. Value choices: disable_creator, no_disable_creator
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creation_date                         Optional GPBoolean. Disable Creation Date Tracking. Default value: true. Value choices: disable_creation_date, no_disable_creation_date
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_editor                           Optional GPBoolean. Disable Last Editor Tracking. Default value: true. Value choices: disable_last_editor, no_disable_last_editor
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'last_edit_date': ['last_edit_date', 'optional'], 'creator': ['creator', 'optional'], 'dataset': ['in_dataset', 'required'], 'creation_date': ['creation_date', 'optional'], 'last_editor': ['last_editor', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DisableEditorTracking', inputs, in_db, out_db)

          
def enable_editor_tracking(dataset, creator_field=None, creation_date_field=None, last_editor_field=None, last_edit_date_field=None, add_fields=None, record_dates_in='utc'):
     """
     Geoprocessing tool to enable  editor tracking for a feature class, table, mosaic dataset, or raster catalog.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required DEDatasetType. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_editor_field                     Optional GPString. Last Editor Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     record_dates_in                       Optional GPString. Record Dates in. Default value: utc. Value choices: utc, database_time
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     add_fields                            Optional GPBoolean. Add fields if they don't exist. Default value: none. Value choices: add_fields, no_add_fields
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     last_edit_date_field                  Optional GPString. Last Edit Date Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creation_date_field                   Optional GPString. Creation Date Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     creator_field                         Optional GPString. Creator Field. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'last_editor_field': ['last_editor_field', 'optional'], 'dataset': ['in_dataset', 'required'], 'add_fields': ['add_fields', 'optional'], 'last_edit_date_field': ['last_edit_date_field', 'optional'], 'creation_date_field': ['creation_date_field', 'optional'], 'creator_field': ['creator_field', 'optional'], 'record_dates_in': ['record_dates_in', 'optional']}
     out_db = {}
     return _execute_tool('management', 'EnableEditorTracking', inputs, in_db, out_db)

          
def truncate_table(table):
     """
     Geoprocessing tool for truncating a table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     table                                 Required GPTableView. Input Table
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
     dataset                               Required GPComposite. Dataset to upgrade
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
     mosaic_dataset                        Required GPMosaicLayer. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     types_of_paths                        Optional GPMultiValue. Types of paths to export. Default value: none. Value choices: raster, item_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     export_mode                           Optional GPString. Export Mode. Default value: all. Value choices: all, broken
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'types_of_paths': ['types_of_paths', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'export_mode': ['export_mode', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'table': ['out_table', 'required', None, None]}
     return _execute_tool('management', 'ExportMosaicDatasetPaths', inputs, in_db, out_db)

          
def repair_mosaic_dataset_paths(mosaic_dataset, paths_list, where_clause=None):
     """
     Geoprocessing tool that repairs broken file paths within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     paths_list                            Required GPValueTable. Paths List
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'paths_list': ['paths_list', 'required']}
     out_db = {}
     return _execute_tool('management', 'RepairMosaicDatasetPaths', inputs, in_db, out_db)

          
def create_database_user(input_database, user_name, user_authentication_type='false', user_password=None, role=None, tablespace_name=None):
     """
     Geoprocessing tool to create a database user in an Oracle, PostgreSQL, or Microsoft SQL Server database.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_name                             Required GPString. Database User
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     role                                  Optional GPString. Role. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_password                         Optional GPEncryptedString. Database User Password. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_authentication_type              Optional GPBoolean. Create Operating System Authenticated User. Default value: false. Value choices: operating_system_user, database_user
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tablespace_name                       Optional GPString. Tablespace Name. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'tablespace_name': ['tablespace_name', 'optional'], 'role': ['role', 'optional'], 'input_database': ['input_database', 'required'], 'user_password': ['user_password', 'optional'], 'user_authentication_type': ['user_authentication_type', 'optional'], 'user_name': ['user_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseUser', inputs, in_db, out_db)

          
def join_field(data, field, jotable, jofield, fields=None):
     """
     Geoprocessing tool that permanently joins the contents of a table to another table based on a common attribute field.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     jofield                               Required Field. Output Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     jotable                               Required GPComposite. Join Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     data                                  Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Input Join Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Optional GPMultiValue. Join Fields. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'jofield': ['join_field', 'required'], 'jotable': ['join_table', 'required'], 'data': ['in_data', 'required'], 'fields': ['fields', 'optional'], 'field': ['in_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'JoinField', inputs, in_db, out_db)

          
def edit_raster_function(mosaic_dataset, edit_mosaic_dataset_item='false', edit_options='insert', function_chadefinition=None, location_function_name=None):
     """
     Geoprocessing tool that adds, replaces, or removes a raster function template in a mosaic dataset, items in a mosaic dataset, or a raster layer that contains a raster function.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_function_name                Optional GPString. Function Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     function_chadefinition                Optional DEFile. Raster Function Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_options                          Optional GPString. Edit Options. Default value: insert. Value choices: insert, replace, remove
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     edit_mosaic_dataset_item              Optional GPBoolean. Mosaic Dataset Items. Default value: false. Value choices: edit_mosaic_dataset_item, edit_mosaic_dataset
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'location_function_name': ['location_function_name', 'optional'], 'function_chadefinition': ['function_chain_definition', 'optional'], 'edit_options': ['edit_options', 'optional'], 'edit_mosaic_dataset_item': ['edit_mosaic_dataset_item', 'optional']}
     out_db = {}
     return _execute_tool('management', 'EditRasterFunction', inputs, in_db, out_db)

          
def build_mosaic_dataset_item_cache(mosaic_dataset, where_clause=None, define_cache='true', generate_cache='true', item_cache_folder=None, compression_method='lossless', compression_quality='80', max_allowed_rows='200000', max_allowed_columns='200000', request_size_type='pixel_size_factor', request_size='1'):
     """
     Geoprocessing tool that inserts the Cached Raster function into the function chain for items within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     define_cache                          Optional GPBoolean. Define Cache. Default value: true. Value choices: define_cache, no_define_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_method                    Optional GPString. Compression Method. Default value: lossless. Value choices: none, lossless, lossy
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional GPLong. Compression Quality. Default value: 80
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     generate_cache                        Optional GPBoolean. Generate Cache. Default value: true. Value choices: generate_cache, no_generate_cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_allowed_columns                   Optional GPLong. Maximum Allowed Columns. Default value: 200000
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     item_cache_folder                     Optional DEWorkspace. Cache Path. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size_type                     Optional GPString. Request Size Type. Default value: pixel_size_factor. Value choices: pixel_size, pixel_size_factor
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     request_size                          Optional GPDouble. Request Size. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_allowed_rows                      Optional GPLong. Maximum Allowed Rows. Default value: 200000
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'define_cache': ['define_cache', 'optional'], 'compression_method': ['compression_method', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'generate_cache': ['generate_cache', 'optional'], 'max_allowed_columns': ['max_allowed_columns', 'optional'], 'where_clause': ['where_clause', 'optional'], 'item_cache_folder': ['item_cache_folder', 'optional'], 'request_size_type': ['request_size_type', 'optional'], 'request_size': ['request_size', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'max_allowed_rows': ['max_allowed_rows', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildMosaicDatasetItemCache', inputs, in_db, out_db)

          
def batch_build_pyramids(input_raster_datasets, pyramid_levels='-1', skip_first_level='false', pyramid_resampling_technique='nearest', pyramid_compression_type='default', compression_quality='75', skip_existing=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_raster_datasets                 Required GPMultiValue. Input Raster Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional GPBoolean. Skip Existing. Default value: none. Value choices: overwrite, skip_existing
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_resampling_technique          Optional GPString. Pyramid resampling technique. Default value: nearest. Value choices: nearest, bilinear, cubic
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_compression_type              Optional GPString. Pyramid compression type. Default value: default. Value choices: default, jpeg, lz77, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_first_level                      Optional GPBoolean. Skip first level. Default value: false. Value choices: skip_first, none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     compression_quality                   Optional GPLong. Compression quality. Default value: 75
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pyramid_levels                        Optional GPLong. Pyramid levels. Default value: -1
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['Skip_Existing', 'optional'], 'pyramid_resampling_technique': ['Pyramid_resampling_technique', 'optional'], 'pyramid_compression_type': ['Pyramid_compression_type', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required'], 'skip_first_level': ['Skip_first_level', 'optional'], 'compression_quality': ['Compression_quality', 'optional'], 'pyramid_levels': ['Pyramid_levels', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchBuildPyramids', inputs, in_db, out_db)

          
def batch_calculate_statistics(input_raster_datasets, number_of_columns_to_skip='1', number_of_rows_to_skip='1', ignore_values=None, skip_existing=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_raster_datasets                 Required GPMultiValue. Input Raster Datasets
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     skip_existing                         Optional GPBoolean. Skip Existing. Default value: none. Value choices: overwrite, skip_existing
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_rows_to_skip                Optional GPLong. Number of rows to skip. Default value: 1
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ignore_values                         Optional GPMultiValue. Ignore values. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_columns_to_skip             Optional GPLong. Number of columns to skip. Default value: 1
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'skip_existing': ['Skip_Existing', 'optional'], 'number_of_rows_to_skip': ['Number_of_rows_to_skip', 'optional'], 'ignore_values': ['Ignore_values', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required'], 'number_of_columns_to_skip': ['Number_of_columns_to_skip', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchCalculateStatistics', inputs, in_db, out_db)

          
def sort(dataset, sort_field, spatial_sort_method='ur'):
     """
     Geoprocessing tool that reorders records in a feature class or table based on field values.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     sort_field                            Required GPValueTable. Field(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     dataset                               Required GPTableView. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_sort_method                   Optional GPString. Spatial Sort Method. Default value: ur. Value choices: ul, ur, ll, lr, peano
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'sort_field': ['sort_field', 'required'], 'spatial_sort_method': ['spatial_sort_method', 'optional'], 'dataset': ['in_dataset', 'required']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'Sort', inputs, in_db, out_db)

          
def match_photos_to_rows_by_time(input_folder, input_table, time_field, add_photos_as_attachments='false', time_tolerance='0', clock_offset='0'):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_field                            Required Field. Time Field
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_table                           Required GPTableView. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_folder                          Required DEFolder. Input Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     time_tolerance                        Optional GPDouble. Time Tolerance. Default value: 0
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     add_photos_as_attachments             Optional GPBoolean. Add Photos As Attachments. Default value: false. Value choices: add_attachments, no_attachments
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clock_offset                          Optional GPDouble. Clock Offset. Default value: 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'time_tolerance': ['Time_Tolerance', 'optional'], 'add_photos_as_attachments': ['Add_Photos_As_Attachments', 'optional'], 'input_folder': ['Input_Folder', 'required'], 'time_field': ['Time_Field', 'required'], 'input_table': ['Input_Table', 'required'], 'clock_offset': ['Clock_Offset', 'optional']}
     out_db = {'unmatched_photos_table': ['Unmatched_Photos_Table', 'optional', None, None], 'output_table': ['Output_Table', 'required', None, None]}
     return _execute_tool('management', 'MatchPhotosToRowsByTime', inputs, in_db, out_db)

          
def register_raster(raster, register_mode, reference_raster=None, input_link_file=None, transformation_type='polyorder1', maximum_rms_value=None):
     """
     Geoprocessing tool that registers an image to a reference image.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     register_mode                         Required GPString. Register Mode
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation_type                   Optional GPString. Transformation Type. Default value: polyorder1. Value choices: polyorder0, polysimilarity, polyorder1, polyorder2, polyorder3, projective, spline, adjust
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_rms_value                     Optional GPDouble. Maximum RMS. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_link_file                       Optional DETextFile. Input Link File. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     reference_raster                      Optional GPComposite. Reference Raster. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'transformation_type': ['transformation_type', 'optional'], 'reference_raster': ['reference_raster', 'optional'], 'register_mode': ['register_mode', 'required'], 'maximum_rms_value': ['maximum_rms_value', 'optional'], 'input_link_file': ['input_link_file', 'optional']}
     out_db = {'output_cpt_link_file': ['output_cpt_link_file', 'optional', None, None]}
     return _execute_tool('management', 'RegisterRaster', inputs, in_db, out_db)

          
def create_role(input_database, role, grant_revoke='grant', user_name=None):
     """
     Geoprocessing tool to create a database role in an Oracle, PostgreSQL, or Microsoft SQL Server database and add users to or remove them from the role.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     role                                  Required GPString. Role
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     grant_revoke                          Optional GPString. Grant To or Revoke From User(s). Default value: grant. Value choices: grant, revoke
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     user_name                             Optional GPString. User Name(s). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'role': ['role', 'required'], 'user_name': ['user_name', 'optional'], 'grant_revoke': ['grant_revoke', 'optional'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateRole', inputs, in_db, out_db)

          
def export_tile_cache(cache_source, target_cache_folder, target_cache_name, export_cache_type='tile_cache', storage_format_type='compact', scales=None, area_of_interest='in_memory\{5c2a1be5-7672-4ab1-8e1e-8c853cb4de67}'):
     """
     Geoprocessing tool that exports tiles from an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_source                          Required GPComposite. Input Tile Cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_cache_name                     Required GPString. Output Tile Cache Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     target_cache_folder                   Required DEFolder. Output Tile Cache Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional GPFeatureRecordSetLayer. Area of Interest. Default value: in_memory\{5c2a1be5-7672-4ab1-8e1e-8c853cb4de67}
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     export_cache_type                     Optional GPString. Export Cache As. Default value: tile_cache. Value choices: tile_cache, tile_package
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     storage_format_type                   Optional GPString. Storage Format. Default value: compact. Value choices: compact, exploded
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional GPMultiValue. Scales [Pixel Size] (Estimated Disk Space). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cache_source': ['in_cache_source', 'required'], 'target_cache_name': ['in_target_cache_name', 'required'], 'export_cache_type': ['export_cache_type', 'optional'], 'scales': ['scales', 'optional'], 'storage_format_type': ['storage_format_type', 'optional'], 'target_cache_folder': ['in_target_cache_folder', 'required'], 'area_of_interest': ['area_of_interest', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ExportTileCache', inputs, in_db, out_db)

          
def generate_tile_cache_tiling_scheme(dataset, tiling_scheme_generation_method, number_of_scales, predefined_tiling_scheme=None, scales=None, scales_type='false', tile_origin='0 0', dpi='96', tile_size='256 x 256', tile_format='mixed', tile_compression_quality='75', storage_format='compact', lerc_error=None):
     """
     Geoprocessing tool that generates an XML tiling scheme file used to create tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPComposite. Input Data Source
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     tiling_scheme_generation_method       Required GPString. Generation Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_of_scales                      Required GPLong. Number of Scales
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales_type                           Optional GPBoolean. Cell Size. Default value: false. Value choices: cell_size, scale
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     predefined_tiling_scheme              Optional DEFile. Predefined Tiling Scheme. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional GPValueTable. Scales. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     lerc_error                            Optional GPDouble. LERC Error. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     storage_format                        Optional GPString. Storage Format. Default value: compact. Value choices: compact, exploded
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_format                           Optional GPString. Tile Format. Default value: mixed. Value choices: png, png8, png24, png32, jpeg, mixed, lerc
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_compression_quality              Optional GPLong. Tile Compression Quality. Default value: 75
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dpi                                   Optional GPLong. Dots (Pixels) Per Inch. Default value: 96
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_size                             Optional GPString. Tile Size (in pixels). Default value: 256 x 256. Value choices: 128 x 128, 256 x 256, 512 x 512, 1024 x 1024
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tile_origin                           Optional GPPoint. Tile Origin in map units. Default value: 0 0
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'predefined_tiling_scheme': ['predefined_tiling_scheme', 'optional'], 'lerc_error': ['lerc_error', 'optional'], 'dpi': ['dpi', 'optional'], 'tile_size': ['tile_size', 'optional'], 'tile_origin': ['tile_origin', 'optional'], 'scales_type': ['scales_type', 'optional'], 'tile_compression_quality': ['tile_compression_quality', 'optional'], 'scales': ['scales', 'optional'], 'storage_format': ['storage_format', 'optional'], 'tile_format': ['tile_format', 'optional'], 'number_of_scales': ['number_of_scales', 'required'], 'tiling_scheme_generation_method': ['tiling_scheme_generation_method', 'required']}
     out_db = {'tiling_scheme': ['out_tiling_scheme', 'required', None, None]}
     return _execute_tool('management', 'GenerateTileCacheTilingScheme', inputs, in_db, out_db)

          
def import_tile_cache(cache_target, cache_source, scales=None, area_of_interest='in_memory\{d6ab050f-d3fd-409c-b375-61816774db6c}', overwrite='false'):
     """
     Geoprocessing tool that imports tiles from an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_source                          Required GPComposite. Source Tile Cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cache_target                          Required GPRasterLayer. Target Tile Cache
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     overwrite                             Optional GPBoolean. Overwrite Tiles. Default value: false. Value choices: overwrite, merge
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional GPMultiValue. Scales [Pixel Size] (Estimated Disk Space). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional GPFeatureRecordSetLayer. Area of Interest. Default value: in_memory\{d6ab050f-d3fd-409c-b375-61816774db6c}
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'cache_source': ['in_cache_source', 'required'], 'cache_target': ['in_cache_target', 'required'], 'overwrite': ['overwrite', 'optional'], 'scales': ['scales', 'optional'], 'area_of_interest': ['area_of_interest', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ImportTileCache', inputs, in_db, out_db)

          
def manage_tile_cache(cache_location, manage_mode, cache_name=None, datasource=None, tiling_scheme='arcgisonline_scheme', import_tiling_scheme=None, scales=None, area_of_interest='in_memory\{1084126b-abaa-4cb2-b931-966a25bad608}', max_cell_size=None, mcached_scale=None, max_cached_scale=None):
     """
     Geoprocessing tool that creates a tile cache or updates tiles in an existing tile cache.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     manage_mode                           Required GPString. Manage Mode
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cache_location                        Required GPComposite. Cache Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     datasource                            Optional GPComposite. Input Data Source. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tiling_scheme                         Optional GPString. Input Tiling Scheme. Default value: arcgisonline_scheme. Value choices: arcgisonline_scheme, arcgisonline+_scheme, arcgisonline_elevation_scheme, arcgisonline_elevation+_scheme, import_scheme
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cached_scale                      Optional GPDouble. Maximum Cached Scale. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cache_name                            Optional GPString. Cache Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     import_tiling_scheme                  Optional GPComposite. Import Tiling Scheme. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_cell_size                         Optional GPDouble. Maximum Source Cell Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional GPFeatureRecordSetLayer. Area of Interest. Default value: in_memory\{1084126b-abaa-4cb2-b931-966a25bad608}
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mcached_scale                         Optional GPDouble. Minimum Cached Scale. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     scales                                Optional GPMultiValue. Scales [Pixel Size] (Estimated Disk Space). Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'datasource': ['in_datasource', 'optional'], 'tiling_scheme': ['tiling_scheme', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'cache_location': ['in_cache_location', 'required'], 'max_cached_scale': ['max_cached_scale', 'optional'], 'cache_name': ['in_cache_name', 'optional'], 'import_tiling_scheme': ['import_tiling_scheme', 'optional'], 'max_cell_size': ['max_cell_size', 'optional'], 'manage_mode': ['manage_mode', 'required'], 'mcached_scale': ['min_cached_scale', 'optional'], 'scales': ['scales', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ManageTileCache', inputs, in_db, out_db)

          
def disable_archiving(dataset, preserve_history='true'):
     """
     Geoprocessing tool that disables archiving on a geodatabase feature class, table, or feature dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPComposite. Input Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     preserve_history                      Optional GPBoolean. Preserve History Table. Default value: true. Value choices: preserve, delete
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
     dataset                               Required GPComposite. Input Dataset
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
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     block_field                           Optional Field. Block Field. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_rows_per_merged_items             Optional GPLong. Maximum Allowed Rows Per Merged Item. Default value: 1000
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'block_field': ['block_field', 'optional'], 'where_clause': ['where_clause', 'optional'], 'max_rows_per_merged_items': ['max_rows_per_merged_items', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MergeMosaicDatasetItems', inputs, in_db, out_db)

          
def split_mosaic_dataset_items(mosaic_dataset, where_clause=None):
     """
     Geoprocessing tool that splits mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
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
     raster                                Required GPComposite. Input Raster
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     panchromatic_image                    Required GPRasterLayer. Panchromatic Image
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     band_indexes                          Optional GPString. Band Indexes. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'band_indexes': ['band_indexes', 'optional'], 'panchromatic_image': ['in_panchromatic_image', 'required']}
     out_db = {}
     return _execute_tool('management', 'ComputePansharpenWeights', inputs, in_db, out_db)

          
def project(dataset, out_coor_system, transform_method=None, coor_system=None, preserve_shape='false', max_deviation=None, vertical='false'):
     """
     Geoprocessing tool that projects spatial data from one coordinate system to another.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dataset                               Required GPComposite. Input Dataset or Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_coor_system                       Required GPCoordinateSystem. Output Coordinate System
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     vertical                              Optional GPBoolean. Vertical. Default value: false. Value choices: vertical, no_vertical
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     max_deviation                         Optional GPLinearUnit. Maximum Offset Deviation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     preserve_shape                        Optional GPBoolean. Preserve Shape. Default value: false. Value choices: preserve_shape, no_preserve_shape
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coor_system                           Optional GPCoordinateSystem. Input Coordinate System. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transform_method                      Optional GPMultiValue. Geographic Transformation. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'vertical': ['vertical', 'optional'], 'preserve_shape': ['preserve_shape', 'optional'], 'dataset': ['in_dataset', 'required'], 'coor_system': ['in_coor_system', 'optional'], 'out_coor_system': ['out_coor_system', 'required'], 'max_deviation': ['max_deviation', 'optional'], 'transform_method': ['transform_method', 'optional']}
     out_db = {'dataset': ['out_dataset', 'required', None, None]}
     return _execute_tool('management', 'Project', inputs, in_db, out_db)

          
def batch_project(input_feature_class_or_dataset, output_workspace, output_coordinate_system=None, template_dataset=None, transformation=None):
     """
     Geoprocessing tool to change the coordinate system of a set of input feature classes or feature datasets.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_feature_class_or_dataset        Required GPMultiValue. Input Feature Class or Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     output_workspace                      Required GPComposite. Output Workspace
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     transformation                        Optional GPString. Transformation. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional DEGeoDatasetType. Template dataset. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     output_coordinate_system              Optional GPCoordinateSystem. Output Coordinate System. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'transformation': ['Transformation', 'optional'], 'input_feature_class_or_dataset': ['Input_Feature_Class_or_Dataset', 'required'], 'output_coordinate_system': ['Output_Coordinate_System', 'optional'], 'output_workspace': ['Output_Workspace', 'required'], 'template_dataset': ['Template_dataset', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchProject', inputs, in_db, out_db)

          
def add_geometry_attributes(input_features, geometry_properties, length_unit=None, area_unit=None, coordinate_system=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_properties                   Required GPMultiValue. Geometry Properties
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     input_features                        Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     length_unit                           Optional GPString. Length Unit. Default value: none. Value choices: feet_us, meters, kilometers, miles_us, nautical_miles, yards
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_unit                             Optional GPString. Area Unit. Default value: none. Value choices: acres, hectares, square_miles_us, square_kilometers, square_meters, square_feet_us, square_yards, square_nautical_miles
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     coordinate_system                     Optional GPCoordinateSystem. Coordinate System. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'length_unit': ['Length_Unit', 'optional'], 'area_unit': ['Area_Unit', 'optional'], 'geometry_properties': ['Geometry_Properties', 'required'], 'input_features': ['Input_Features', 'required'], 'coordinate_system': ['Coordinate_System', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddGeometryAttributes', inputs, in_db, out_db)

          
def migrate_relationship_class(relationship_class):
     """
     Geoprocessing tool that migrates an ObjectID-based relationship class to a GlobalID-based relationship class

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     relationship_class                    Required DERelationshipClass. Input Relationship Class
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
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional GPString. Geometry Type. Default value: footprint. Value choices: footprint, boundary, seamline, level
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'geometry_type': ['geometry_type', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'ExportMosaicDatasetGeometry', inputs, in_db, out_db)

          
def export_mosaic_dataset_items(mosaic_dataset, out_folder, out_base_name=None, where_clause=None, format='tiff', nodata_value=None, clip_type=None, template_dataset=None, cell_size=None):
     """
     Geoprocessing tool that creates a copy of your processed images within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_folder                            Required DEFolder. Output Folder
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_base_name                         Optional GPString. . Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     where_clause                          Optional GPSQLExpression. Query Definition. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clip_type                             Optional GPString. Clip Type. Default value: none. Value choices: none, extent, feature_class
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     cell_size                             Optional GPPoint. Cellsize. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     nodata_value                          Optional GPString. NoData Value. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template_dataset                      Optional GPExtent. Clipping Template. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional GPString. Output Format. Default value: tiff. Value choices: tiff, bmp, envi, esri bil, esri bip, esri bsq, gif, grid, imagine image, jp2, jpeg, png
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'template_dataset': ['template_dataset', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'out_base_name': ['out_base_name', 'optional'], 'format': ['format', 'optional'], 'clip_type': ['clip_type', 'optional'], 'cell_size': ['cell_size', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'out_folder': ['out_folder', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ExportMosaicDatasetItems', inputs, in_db, out_db)

          
def remove_field_conflict_filter(table, fields):
     """
     Geoprocessing tool for removing a field conflict filter to a geodatabase table or feature class.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fields                                Required GPMultiValue. Field Name(s)
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     table                                 Required GPTableView. Input Table
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'fields': ['fields', 'required'], 'table': ['table', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveFieldConflictFilter', inputs, in_db, out_db)

          
def export_geodatabase_configuration_keywords(input_database):
     """
     Geoprocessing tool that exports the configuration keywords, parameters, and values from the specified enterprise geodatabase to an editable file.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required DEWorkspace. Input Database Connection
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
     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     file                                  Required DEFile. Input File
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
     table                                 Required GPComposite. Input Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     field                                 Required Field. Field Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_field_name                        Optional GPString. New Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_length                          Optional GPLong. New Field Length. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_is_nullable                     Optional GPBoolean. New Field IsNullable. Default value: true. Value choices: nullable, non_nullable
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     new_field_alias                       Optional GPString. New Field Alias. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     clear_field_alias                     Optional GPBoolean. Clear Alias. Default value: false
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     field_type                            Optional GPString. New Field Type. Default value: long. Value choices: text, float, double, short, long, date, blob, raster, guid
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'new_field_name': ['new_field_name', 'optional'], 'field_length': ['field_length', 'optional'], 'field_is_nullable': ['field_is_nullable', 'optional'], 'field': ['field', 'required'], 'table': ['in_table', 'required'], 'new_field_alias': ['new_field_alias', 'optional'], 'clear_field_alias': ['clear_field_alias', 'optional'], 'field_type': ['field_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterField', inputs, in_db, out_db)

          
def geodetic_densify(features, geodetic_type, distance='50 kilometers'):
     """
     Geoprocessing tool that replaces segments with densified approximation of geodetic curves.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     features                              Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     geodetic_type                         Required GPString. Geodetic Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance                              Optional GPLinearUnit. Distance. Default value: 50 kilometers
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'distance': ['distance', 'optional'], 'features': ['in_features', 'required'], 'geodetic_type': ['geodetic_type', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'GeodeticDensify', inputs, in_db, out_db)

          
def configure_geodatabase_log_file_tables(input_database, log_file_type, log_file_pool_size=None, use_tempdb='false'):
     """
     Geoprocessing tool that allows you to alter the type of log file tables used by an enterprise geodatabase to maintain lists of records cached by ArcGIS.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     log_file_type                         Required GPString. Log File Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     log_file_pool_size                    Optional GPLong. Number of session based log file tables to be owned in a pool by the administrator. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     use_tempdb                            Optional GPBoolean. Create session based log files tables owned by each user in the TempDB database (SQL Server only). Default value: false. Value choices: use_tembdb, not_use_tembdb
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'log_file_pool_size': ['log_file_pool_size', 'optional'], 'input_database': ['input_database', 'required'], 'use_tempdb': ['use_tempdb', 'optional'], 'log_file_type': ['log_file_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConfigureGeodatabaseLogFileTables', inputs, in_db, out_db)

          
def delete_schema_geodatabase(input_database):
     """
     Geoprocessing tool that deletes a user-schema geodatabase from a geodatabase in Oracle.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_database                        Required DEWorkspace. Input Database Connection
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
     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_tables                          Optional GPMultiValue. Input Tables. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        Optional GPString. Target version. Default value: none
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
     input_database                        Required DEWorkspace. Input Database Connection
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_tables                          Optional GPMultiValue. Input Tables. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     target_version                        Optional GPString. Target Version. Default value: none
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
     input                                 Required GPComposite. Input
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
     out_path                              Required GPComposite. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_basename                          Required GPString. Base Name
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     topology                              Required GPTopologyLayer. Input Topology
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_path': ['out_path', 'required'], 'out_basename': ['out_basename', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'ExportTopologyErrors', inputs, in_db, out_db)

          
def generate_raster_from_raster_function(raster_function, raster_function_arguments=None, raster_properties=None, format=None):
     """
     Geoprocessing tool that uses raster functions to process raster datasets and write an output.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_function                       Required GPComposite. Input Raster Function
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_function_arguments             Optional GPValueTable. Raster Function Arguments. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     raster_properties                     Optional GPValueTable. Raster Properties. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     format                                Optional GPString. Format. Default value: none. Value choices: tiff, imagine image, esri grid, crf, mrf
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'raster_function_arguments': ['raster_function_arguments', 'optional'], 'raster_properties': ['raster_properties', 'optional'], 'raster_function': ['raster_function', 'required'], 'format': ['format', 'optional']}
     out_db = {'raster_dataset': ['out_raster_dataset', 'required', None, None]}
     return _execute_tool('management', 'GenerateRasterFromRasterFunction', inputs, in_db, out_db)

          
def generate_tessellation(extent, shape_type='hexagon', size=None, spatial_reference=None):
     """
     Geoprocessing tool that generates a feature class of a  tessellated grid of regular polygons to cover a given extent. The shapes can either be triangles, squares, or hexagons.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     extent                                Required GPExtent. Extent
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     size                                  Optional GPArealUnit. Size. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     spatial_reference                     Optional GPSpatialReference. Spatial Reference. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     shape_type                            Optional GPString. Shape Type. Default value: hexagon. Value choices: square, triangle, hexagon
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'spatial_reference': ['Spatial_Reference', 'optional'], 'size': ['Size', 'optional'], 'extent': ['Extent', 'required'], 'shape_type': ['Shape_Type', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'GenerateTessellation', inputs, in_db, out_db)

          
def create_fishnet(origcoord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, corner_coord=None, labels='true', template=None, geometry_type='polyline'):
     """
     Geoprocessing tool that creates a fishnet of rectangular cells.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     origcoord                             Required GPPoint. Fishnet Origin Coordinate 
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_rows                           Required GPLong. Number of Rows
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_height                           Required GPDouble. Cell Size Height
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     y_axis_coord                          Required GPPoint. Y-Axis Coordinate 
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     number_columns                        Required GPLong. Number of Columns
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_width                            Required GPDouble. Cell Size Width
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     corner_coord                          Optional GPPoint. Opposite corner of Fishnet. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     labels                                Optional GPBoolean. Create Label Points. Default value: true. Value choices: labels, no_labels
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     geometry_type                         Optional GPString. Geometry Type. Default value: polyline. Value choices: polyline, polygon
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     template                              Optional GPExtent. Template Extent. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'origcoord': ['origin_coord', 'required'], 'number_rows': ['number_rows', 'required'], 'corner_coord': ['corner_coord', 'optional'], 'geometry_type': ['geometry_type', 'optional'], 'cell_height': ['cell_height', 'required'], 'y_axis_coord': ['y_axis_coord', 'required'], 'number_columns': ['number_columns', 'required'], 'labels': ['labels', 'optional'], 'cell_width': ['cell_width', 'required'], 'template': ['template', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required', None, None]}
     return _execute_tool('management', 'CreateFishnet', inputs, in_db, out_db)

          
def create_random_points(out_path, out_name, constraining_feature_class=None, constraining_extent=None, number_of_points_or_field='100', minimum_allowed_distance='0 unknown', create_multipoint_output='false', multipoint_size='10'):
     """
     Geoprocessing tool that creates a specified number of random points in an extent window, inside polygon features, on point features, or along line features.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     out_path                              Required GPComposite. Output Location
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     out_name                              Required GPString. Output Point Feature Class
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     constraining_feature_class            Optional GPFeatureLayer. Constraining Feature Class. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     constraining_extent                   Optional GPComposite. Constraining Extent. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     multipoint_size                       Optional GPLong. Maximum Number of Points per Multipoint. Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     number_of_points_or_field             Optional GPComposite. Number of Points [value or field]. Default value: 100
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     create_multipoint_output              Optional GPBoolean. Create Multipoint Output. Default value: false. Value choices: multipoint, point
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_allowed_distance              Optional GPComposite. Minimum Allowed Distance [value or field]. Default value: 0 unknown
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'constraining_feature_class': ['constraining_feature_class', 'optional'], 'constraining_extent': ['constraining_extent', 'optional'], 'multipoint_size': ['multipoint_size', 'optional'], 'number_of_points_or_field': ['number_of_points_or_field', 'optional'], 'out_path': ['out_path', 'required'], 'create_multipoint_output': ['create_multipoint_output', 'optional'], 'minimum_allowed_distance': ['minimum_allowed_distance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomPoints', inputs, in_db, out_db)

          
def generate_points_along_lines(input_features, point_placement, distance=None, percentage=None, include_end_points=None):
     """
     

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_features                        Required GPFeatureLayer. Input Features
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     point_placement                       Required GPString. Point Placement
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     include_end_points                    Optional GPBoolean. Include End Points. Default value: none. Value choices: end_points, no_end_points
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     percentage                            Optional GPDouble. Percentage. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distance                              Optional GPLinearUnit. Distance. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'include_end_points': ['Include_End_Points', 'optional'], 'percentage': ['Percentage', 'optional'], 'input_features': ['Input_Features', 'required'], 'point_placement': ['Point_Placement', 'required'], 'distance': ['Distance', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required', None, None]}
     return _execute_tool('management', 'GeneratePointsAlongLines', inputs, in_db, out_db)

          
def append_control_points(master_control_points, input_control_points, z_field=None, tag_field=None, dem=None, xy_accuracy=None, z_accuracy=None):
     """
     Geoprocessing tool that combines tie points and control points.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_control_points                  Required GPComposite. Input Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     master_control_points                 Required GPComposite. Target Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_field                               Optional Field. Z Value Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     tag_field                             Optional Field. Tag Field Name. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     z_accuracy                            Optional GPDouble. Z Accuracy. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     xy_accuracy                           Optional GPDouble. XY Accuracy. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dem                                   Optional GPComposite. Input DEM. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'tag_field': ['in_tag_field', 'optional'], 'z_accuracy': ['in_z_accuracy', 'optional'], 'z_field': ['in_z_field', 'optional'], 'input_control_points': ['in_input_control_points', 'required'], 'xy_accuracy': ['in_xy_accuracy', 'optional'], 'dem': ['in_dem', 'optional'], 'master_control_points': ['in_master_control_points', 'required']}
     out_db = {}
     return _execute_tool('management', 'AppendControlPoints', inputs, in_db, out_db)

          
def apply_block_adjustment(mosaic_dataset, adjustment_operation, input_solution_table=None, pan_to_ms_scaling_factor=None, dem=None, zoffset=None, control_point_table=None, adjust_footprints='false'):
     """
     Geoprocessing tool that applies the geographic adjustments to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     adjustment_operation                  Required GPString. Adjustment Operation
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     zoffset                               Optional GPDouble. Z offset. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     adjust_footprints                     Optional GPBoolean. Adjust Footprints. Default value: false. Value choices: adjust_footprints, no_adjust_footprints
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_point_table                   Optional GPTableView. Control Point Table. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     pan_to_ms_scaling_factor              Optional GPDouble. Pan-To-MS Scaling Factor. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     input_solution_table                  Optional GPTableView. Input Solution Table. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     dem                                   Optional GPComposite. Input DEM. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'zoffset': ['zoffset', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'adjust_footprints': ['adjust_footprints', 'optional'], 'input_solution_table': ['input_solution_table', 'optional'], 'pan_to_ms_scaling_factor': ['pan_to_ms_scaling_factor', 'optional'], 'control_point_table': ['control_point_table', 'optional'], 'dem': ['DEM', 'optional'], 'adjustment_operation': ['adjustment_operation', 'required']}
     out_db = {}
     return _execute_tool('management', 'ApplyBlockAdjustment', inputs, in_db, out_db)

          
def compute_block_adjustment(mosaic_dataset, control_points, transformation_type, maximum_residual_value='5', adjustment_options=None, location_accuracy='medium'):
     """
     Geoprocessing tool that computes the adjustments to the mosaic dataset items.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_points                        Required GPFeatureLayer. Input Control Points
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     transformation_type                   Required GPString. Transformation Type
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     adjustment_options                    Optional GPValueTable. Adjustment Options. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     Optional GPString. Image Location Accuracy. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_residual_value                Optional GPDouble. Maximum Residual. Default value: 5
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'transformation_type': ['transformation_type', 'required'], 'control_points': ['in_control_points', 'required'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'adjustment_options': ['adjustment_options', 'optional'], 'location_accuracy': ['location_accuracy', 'optional'], 'maximum_residual_value': ['maximum_residual_value', 'optional']}
     out_db = {'solution_table': ['out_solution_table', 'required', None, None], 'quality_table': ['out_quality_table', 'optional', None, None], 'solution_point_table': ['out_solution_point_table', 'optional', None, None]}
     return _execute_tool('management', 'ComputeBlockAdjustment', inputs, in_db, out_db)

          
def compute_camera_model(mosaic_dataset, gps_accuracy='high', estimate='true', refine='true', apply_adjustment='true', maximum_residual='5', initial_tiepoint_resolution='8', maximum_overlap=None, minimum_coverage='0.2', remove='false', control_points=None, options=None):
     """
     Geoprocessing tool that automatically constructs and refines a camera model for aerial images and, in particular, UAV and UAS images, where the exterior and interior camera models are coarse or undefined.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     control_points                        Optional DEFeatureClass. Input Tie Point Table. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_overlap                       Optional GPDouble. Maximum Area Overlap. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     refine                                Optional GPBoolean. Refine Camera Model. Default value: true. Value choices: refine, no_refine
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_residual                      Optional GPDouble. Maximum Residual. Default value: 5
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     remove                                Optional GPBoolean. Remove Off-Strip Images. Default value: false. Value choices: remove, no_remove
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     gps_accuracy                          Optional GPString. GPS Location Accuracy. Default value: high. Value choices: high, medium, low, very_low
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     options                               Optional GPValueTable. Additional Options. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_coverage                      Optional GPDouble. Minimum Control Point Coverage. Default value: 0.2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     initial_tiepoint_resolution           Optional GPDouble. Initial Tie Point Resolution. Default value: 8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     estimate                              Optional GPBoolean. Estimate Camera Model. Default value: true. Value choices: estimate, no_estimate
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     apply_adjustment                      Optional GPBoolean. Apply Adjustment. Default value: true. Value choices: apply, no_apply
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_overlap': ['maximum_overlap', 'optional'], 'refine': ['refine', 'optional'], 'gps_accuracy': ['gps_accuracy', 'optional'], 'minimum_coverage': ['minimum_coverage', 'optional'], 'initial_tiepoint_resolution': ['initial_tiepoint_resolution', 'optional'], 'estimate': ['estimate', 'optional'], 'apply_adjustment': ['apply_adjustment', 'optional'], 'control_points': ['in_control_points', 'optional'], 'options': ['options', 'optional'], 'maximum_residual': ['maximum_residual', 'optional'], 'remove': ['remove', 'optional']}
     out_db = {'control_points': ['out_control_points', 'optional', None, None], 'dsm': ['out_dsm', 'optional', None, None], 'flight_path': ['out_flight_path', 'optional', None, None], 'solution_point_table': ['out_solution_point_table', 'optional', None, None], 'solution_table': ['out_solution_table', 'optional', None, None]}
     return _execute_tool('management', 'ComputeCameraModel', inputs, in_db, out_db)

          
def compute_control_points(mosaic_dataset, reference_images, similarity='high', density='medium', distribution='random', area_of_interest=None, location_accuracy='medium'):
     """
     Geoprocessing tool that computes control points for your mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     reference_images                      Required GPComposite. Input Reference Images
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     density                               Optional GPString. Point Density. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     similarity                            Optional GPString. Similarity. Default value: high. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     area_of_interest                      Optional GPFeatureLayer. Area of Interest. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          Optional GPString. Point Distribution. Default value: random. Value choices: random, regular
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     Optional GPString. Image Location Accuracy. Default value: medium. Value choices: low, medium, high
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'location_accuracy': ['location_accuracy', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'area_of_interest': ['area_of_interest', 'optional'], 'density': ['density', 'optional'], 'similarity': ['similarity', 'optional'], 'distribution': ['distribution', 'optional'], 'reference_images': ['in_reference_images', 'required']}
     out_db = {'control_points': ['out_control_points', 'required', None, None], 'image_feature_points': ['out_image_feature_points', 'optional', None, None]}
     return _execute_tool('management', 'ComputeControlPoints', inputs, in_db, out_db)

          
def compute_tie_points(mosaic_dataset, similarity='medium', mask_dataset=None, density='medium', distribution='random', location_accuracy='medium'):
     """
     Geoprocessing tool that computes the tie points for the  items within a mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mask_dataset                          Optional GPFeatureLayer. Input Mask. Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     density                               Optional GPString. Point Density. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     similarity                            Optional GPString. Similarity. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     location_accuracy                     Optional GPString. Image Location Accuracy. Default value: medium. Value choices: low, medium, high
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     distribution                          Optional GPString. Point Distribution. Default value: random. Value choices: random, regular
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'location_accuracy': ['location_accuracy', 'optional'], 'mask_dataset': ['in_mask_dataset', 'optional'], 'density': ['density', 'optional'], 'similarity': ['similarity', 'optional'], 'distribution': ['distribution', 'optional']}
     out_db = {'control_points': ['out_control_points', 'required', None, None], 'image_features': ['out_image_features', 'optional', None, None]}
     return _execute_tool('management', 'ComputeTiePoints', inputs, in_db, out_db)

          
def build_stereo_model(mosaic_dataset, minimum_angle='10', maximum_angle='70', minimum_overlap='0.5', maximum_diff_op=None, maximum_diff_gsd='2'):
     """
     Geoprocessing tool that generates a stereo model on imagery in a  mosaic dataset.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_op                       Optional GPDouble. Maximum Omega/Phi Difference (in degree). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_gsd                      Optional GPDouble. Maximum GSD Difference. Default value: 2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_angle                         Optional GPDouble. Minimum Intersection Angle (in degree). Default value: 10
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_overlap                       Optional GPDouble. Minimum Area Overlap. Default value: 0.5
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_angle                         Optional GPDouble. Maximum Intersection Angle (in degree). Default value: 70
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_diff_gsd': ['maximum_diff_GSD', 'optional'], 'minimum_overlap': ['minimum_overlap', 'optional'], 'minimum_angle': ['minimum_angle', 'optional'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'maximum_angle': ['maximum_angle', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildStereoModel', inputs, in_db, out_db)

          
def generate_point_cloud(mosaic_dataset, matching_method, object_size='50', ground_spacing=None, minimum_pairs='2', minimum_area='0.6', minimum_adjustment_quality='0.2', maximum_diff_gsd='2', maximum_diff_op='8'):
     """
     Geoprocessing tool that generates a 3D point cloud from stereo images.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     matching_method                       Required GPString. Matching Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_area                          Optional GPDouble. Overlap Area Threshold. Default value: 0.6
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     ground_spacing                        Optional GPDouble. DSM Ground Spacing (in meter). Default value: none
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_gsd                      Optional GPDouble. GSD Difference Threshold. Default value: 2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     object_size                           Optional GPDouble. Maximum Object Size (in meter). Default value: 50
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_diff_op                       Optional GPDouble. Omega/Phi Difference Threshold. Default value: 8
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_pairs                         Optional GPDouble. Number of Image Pairs. Default value: 2
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     minimum_adjustment_quality            Optional GPDouble. Adjustment Quality Threshold. Default value: 0.2
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'minimum_area': ['minimum_area', 'optional'], 'ground_spacing': ['ground_spacing', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_diff_gsd': ['maximum_diff_gsd', 'optional'], 'object_size': ['object_size', 'optional'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'minimum_pairs': ['minimum_pairs', 'optional'], 'minimum_adjustment_quality': ['minimum_adjustment_quality', 'optional'], 'matching_method': ['matching_method', 'required']}
     out_db = {'folder': ['out_folder', 'required', None, None], 'base_name': ['out_base_name', 'required', None, None]}
     return _execute_tool('management', 'GeneratePointCloud', inputs, in_db, out_db)

          
def interpolate_from_point_cloud(container, cell_size, interpolation_method, smooth_method, surface_type='dtm', fill_dem=None):
     """
     Geoprocessing tool that interpolates a digital surface model (DSM) or digital elevation model (DEM) from a point cloud.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     container                             Required GPComposite. Input LAS Folder or Point Table
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     interpolation_method                  Required GPString. Interpolation Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     smooth_method                         Required GPString. Smoothing Method
     -----------------------------------   ------------------------------------------------------------------------------------------------------

     cell_size                             Required GPDouble. Cellsize
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     surface_type                          Optional GPString. Surface Type. Default value: dtm. Value choices: dtm, dsm
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     fill_dem                              Optional GPComposite. Input Fill DEM. Default value: none
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'surface_type': ['surface_type', 'optional'], 'fill_dem': ['fill_dem', 'optional'], 'cell_size': ['cell_size', 'required'], 'container': ['in_container', 'required'], 'interpolation_method': ['interpolation_method', 'required'], 'smooth_method': ['smooth_method', 'required']}
     out_db = {'raster': ['out_raster', 'required', None, None]}
     return _execute_tool('management', 'InterpolateFromPointCloud', inputs, in_db, out_db)

          
def compute_mosaic_candidates(mosaic_dataset, maximum_overlap='0.6', maximum_area_loss='0.05'):
     """
     Geoprocessing tool that finds the image candidates in a mosaic dataset that best represents the mosaic area, and will be used to generate an orthomosaic.

     ===================================   ======================================================================================================
     **Argument**                          **Description**
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     mosaic_dataset                        Required GPComposite. Input Mosaic Dataset
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_area_loss                     Optional GPDouble. Maximum Area Loss Allowed. Default value: 0.05
     -----------------------------------   ------------------------------------------------------------------------------------------------------
     maximum_overlap                       Optional GPDouble. Maximum Area Overlap. Default value: 0.6
     ===================================   ======================================================================================================
     """
     inputs = locals()
     in_db = {'maximum_area_loss': ['maximum_area_loss', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_overlap': ['maximum_overlap', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ComputeMosaicCandidates', inputs, in_db, out_db)

          