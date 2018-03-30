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
                                              out_name=random.choice(string.ascii_letters) + \
                                              uuid.uuid4().hex[:5])
               inputs[k] = fc
          elif isinstance(inputs[k], pd.DataFrame):
               t = random.choice(string.ascii_letters) +      \
               uuid.uuid4().hex[:5] + '.csv'
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


def delete_rows(rows):
     """
     Geoprocessing tool that removes all records from a table, unless a selection is defined on the table.
     """
     inputs = locals()
     in_db = {'rows': ['in_rows', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteRows', inputs, in_db, out_db)


def copy_rows(rows, config_keyword=None):
     """
     Geoprocessing tool that duplicates the contents of a table, table view, feature layer, or feature class to another table.
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'optional'], 'rows': ['in_rows', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'CopyRows', inputs, in_db, out_db)


def copy_features(features, config_keyword=None, spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None):
     """
     Geoprocessing tool to copy features to a new feature class.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'CopyFeatures', inputs, in_db, out_db)


def dissolve(features, dissolve_field=None, statistics_fields=None, multi_part=None, unsplit_lines=None):
     """
     Geoprocessing tool used to aggregate features based on specified attributes.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'multi_part': ['multi_part', 'optional'], 'statistics_fields': ['statistics_fields', 'optional'], 'dissolve_field': ['dissolve_field', 'optional'], 'unsplit_lines': ['unsplit_lines', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'Dissolve', inputs, in_db, out_db)


def make_feature_layer(features, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a feature layer from an input feature class or layer.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'workspace': ['workspace', 'optional'], 'where_clause': ['where_clause', 'optional'], 'field_info': ['field_info', 'optional']}
     out_db = {'layer': ['out_layer', 'required']}
     return _execute_tool('management', 'MakeFeatureLayer', inputs, in_db, out_db)


def save_to_layer_file(layer, is_relative_path=None, version=None):
     """
     Geoprocessing tool that creates a layer file (.lyrx) that references geographic data stored on disk.
     """
     inputs = locals()
     in_db = {'version': ['version', 'optional'], 'layer': ['in_layer', 'required'], 'is_relative_path': ['is_relative_path', 'optional']}
     out_db = {'layer': ['out_layer', 'required']}
     return _execute_tool('management', 'SaveToLayerFile', inputs, in_db, out_db)


def add_join(layer_or_view, field, jotable, jofield, jotype=None):
     """
     Geoprocessing tool that  joins a layer to another layer or table (where layer is a feature layer, table view, or raster layer with raster attribute table) based on a common field.
     """
     inputs = locals()
     in_db = {'field': ['in_field', 'required'], 'layer_or_view': ['in_layer_or_view', 'required'], 'jofield': ['join_field', 'required'], 'jotable': ['join_table', 'required'], 'jotype': ['join_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddJoin', inputs, in_db, out_db)


def remove_join(layer_or_view, joname=None):
     """
     Geoprocessing tool that removes a join from a feature layer or table view.
     """
     inputs = locals()
     in_db = {'joname': ['join_name', 'optional'], 'layer_or_view': ['in_layer_or_view', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveJoin', inputs, in_db, out_db)


def copy(data, data_type=None):
     """
     Geoprocessing tool that duplicates all types of geodata as well as most other dataset types.
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'required'], 'data_type': ['data_type', 'optional']}
     out_db = {'data': ['out_data', 'required']}
     return _execute_tool('management', 'Copy', inputs, in_db, out_db)


def delete(data, data_type=None):
     """
     Geoprocessing tool that permanently removes the specified item from disk.
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'required'], 'data_type': ['data_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Delete', inputs, in_db, out_db)


def rename(data, data_type=None):
     """
     Geoprocessing tool that changes the name of a dataset.
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'required'], 'data_type': ['data_type', 'optional']}
     out_db = {'data': ['out_data', 'required']}
     return _execute_tool('management', 'Rename', inputs, in_db, out_db)


def create_personal_gdb(out_folder_path, out_name, out_version=None):
     """
     Geoprocessing tool that outputs a Microsoft Office Access database.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_folder_path': ['out_folder_path', 'required'], 'out_version': ['out_version', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreatePersonalGDB', inputs, in_db, out_db)


def create_arcinfo_workspace(out_folder_path, out_name):
     """
     Geoprocessing tool that outputs a workspace to store coverages and INFO tables.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_folder_path': ['out_folder_path', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateArcInfoWorkspace', inputs, in_db, out_db)


def create_folder(out_folder_path, out_name):
     """
     Geoprocessing tool that creates a folder.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_folder_path': ['out_folder_path', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateFolder', inputs, in_db, out_db)


def create_feature_dataset(out_dataset_path, out_name, spatial_reference=None):
     """
     Geoprocessing tool that creates a feature dataset in a geodatabase.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'out_dataset_path': ['out_dataset_path', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateFeatureDataset', inputs, in_db, out_db)


def pivot_table(table, fields, pivot_field, value_field):
     """
     Geoprocessing tool that uses a pivot and value field to streamline the input table.
     """
     inputs = locals()
     in_db = {'pivot_field': ['pivot_field', 'required'], 'table': ['in_table', 'required'], 'value_field': ['value_field', 'required'], 'fields': ['fields', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'PivotTable', inputs, in_db, out_db)


def create_feature_class(out_path, out_name, geometry_type=None, template=None, has_m=None, has_z=None, spatial_reference=None, config_keyword=None, spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None):
     """
     Geoprocessing tool that creates a feature class, either in an ArcSDE, file geodatabase, or personal geodatabase, or as a shapefile in a folder.
     """
     inputs = locals()
     in_db = {'spatial_grid_2': ['spatial_grid_2', 'optional'], 'geometry_type': ['geometry_type', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'has_m': ['has_m', 'optional'], 'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'has_z': ['has_z', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFeatureClass', inputs, in_db, out_db)


def create_table(out_path, out_name, template=None, config_keyword=None):
     """
     Geoprocessing tool that creates a geodatabase table, an INFO table, or dBASE table.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateTable', inputs, in_db, out_db)


def make_table_view(table, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool to create a table view from an input table or feature class.
     """
     inputs = locals()
     in_db = {'workspace': ['workspace', 'optional'], 'table': ['in_table', 'required'], 'where_clause': ['where_clause', 'optional'], 'field_info': ['field_info', 'optional']}
     out_db = {'view': ['out_view', 'required']}
     return _execute_tool('management', 'MakeTableView', inputs, in_db, out_db)


def add_attribute_index(table, fields, index_name=None, unique=None, ascending=None):
     """
     Geoprocessing tool that adds an attribute index to an existing table, feature class, shapefile, coverage, or attributed relationship class.
     """
     inputs = locals()
     in_db = {'ascending': ['ascending', 'optional'], 'table': ['in_table', 'required'], 'unique': ['unique', 'optional'], 'index_name': ['index_name', 'optional'], 'fields': ['fields', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddAttributeIndex', inputs, in_db, out_db)


def remove_attribute_index(table, index_name):
     """
     Geoprocessing tool that deletes an attribute index from an existing table, feature class, shapefile, coverage, or attributed relationship class.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'index_name': ['index_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveAttributeIndex', inputs, in_db, out_db)


def add_spatial_index(features, spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None):
     """
     Geoprocessing tool that adds a spatial index to a feature class
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'spatial_grid_3': ['spatial_grid_3', 'optional'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddSpatialIndex', inputs, in_db, out_db)


def remove_spatial_index(features):
     """
     Geoprocessing tool that deletes the spatial index from a shapefile, file geodatabase feature class, or enterprise geodatabase feature class.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveSpatialIndex', inputs, in_db, out_db)


def create_domain(workspace, domaname, field_type, domadescription=None, domatype=None, split_policy=None, merge_policy=None):
     """
     Geoprocessing tool that creates an attribute domain in the specified workspace.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'merge_policy': ['merge_policy', 'optional'], 'domadescription': ['domain_description', 'optional'], 'split_policy': ['split_policy', 'optional'], 'domaname': ['domain_name', 'required'], 'field_type': ['field_type', 'required'], 'domatype': ['domain_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateDomain', inputs, in_db, out_db)


def delete_domain(workspace, domaname):
     """
     Geoprocessing tool to delete a domain from a workspace.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteDomain', inputs, in_db, out_db)


def add_coded_value_to_domain(workspace, domaname, code, code_description):
     """
     Geoprocessing tool that adds a value to a domain's coded value list.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required'], 'code_description': ['code_description', 'required'], 'code': ['code', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddCodedValueToDomain', inputs, in_db, out_db)


def delete_coded_value_from_domain(workspace, domaname, code):
     """
     Geoprocessing tool that removes a value from a coded value domain.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required'], 'code': ['code', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteCodedValueFromDomain', inputs, in_db, out_db)


def set_value_for_range_domain(workspace, domaname, mvalue, max_value):
     """
     Geoprocessing tool that sets the minimun and maximum values for an existing Range domain.
     """
     inputs = locals()
     in_db = {'max_value': ['max_value', 'required'], 'workspace': ['in_workspace', 'required'], 'domaname': ['domain_name', 'required'], 'mvalue': ['min_value', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetValueForRangeDomain', inputs, in_db, out_db)


def assign_domain_to_field(table, field_name, domaname, subtype_code=None):
     """
     Geoprocessing tool that sets the domain for a particular field and, optionally, for a subtype.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'field_name': ['field_name', 'required'], 'domaname': ['domain_name', 'required'], 'subtype_code': ['subtype_code', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AssignDomainToField', inputs, in_db, out_db)


def remove_domain_from_field(table, field_name, subtype_code=None):
     """
     Geoprocessing tool that removes an attribute domain association from a feature class or table field.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'field_name': ['field_name', 'required'], 'subtype_code': ['subtype_code', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RemoveDomainFromField', inputs, in_db, out_db)


def table_to_domain(table, code_field, description_field, workspace, domaname, domadescription=None, update_option=None):
     """
     Geoprocessing tool that creates or updates a coded value domain with values from a table.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'table': ['in_table', 'required'], 'update_option': ['update_option', 'optional'], 'code_field': ['code_field', 'required'], 'domadescription': ['domain_description', 'optional'], 'domaname': ['domain_name', 'required'], 'description_field': ['description_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'TableToDomain', inputs, in_db, out_db)


def domain_to_table(workspace, domaname, code_field, description_field, configuration_keyword=None):
     """
     Geoprocessing tool that creates a table from an attribute domain.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'description_field': ['description_field', 'required'], 'domaname': ['domain_name', 'required'], 'code_field': ['code_field', 'required'], 'configuration_keyword': ['configuration_keyword', 'optional']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'DomainToTable', inputs, in_db, out_db)


def add_xy_coordinates(features):
     """
     Geoprocessing tool that appends up to four fields to the point features' attribute table and computes their values.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddXYCoordinates', inputs, in_db, out_db)


def select_layer_by_attribute(layer_or_view, selection_type=None, where_clause=None):
     """
     Geoprocessing tool that adds, updates, or removes a selection on a layer or table view based on an attribute query.
     """
     inputs = locals()
     in_db = {'where_clause': ['where_clause', 'optional'], 'layer_or_view': ['in_layer_or_view', 'required'], 'selection_type': ['selection_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SelectLayerByAttribute', inputs, in_db, out_db)


def select_layer_by_location(layer, overlap_type=None, select_features=None, search_distance=None, selection_type=None, invert_spatial_relationship=None):
     """
     Geoprocessing tool that selects features in a layer based on a spatial relationship to features in another layer.
     """
     inputs = locals()
     in_db = {'overlap_type': ['overlap_type', 'optional'], 'select_features': ['select_features', 'optional'], 'search_distance': ['search_distance', 'optional'], 'layer': ['in_layer', 'required'], 'invert_spatial_relationship': ['invert_spatial_relationship', 'optional'], 'selection_type': ['selection_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SelectLayerByLocation', inputs, in_db, out_db)


def calculate_default_spatial_grid_index(features):
     """
     Geoprocessing tool to calculate a set of valid grid index values for an input feature class
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'CalculateDefaultSpatialGridIndex', inputs, in_db, out_db)


def get_count(rows):
     """
     Geoprocessing tool that reports the number of rows of the input data.
     """
     inputs = locals()
     in_db = {'rows': ['in_rows', 'required']}
     out_db = {}
     return _execute_tool('management', 'GetCount', inputs, in_db, out_db)


def create_version(workspace, parent_version, version_name, access_permission=None):
     """
     Geoprocessing tool to create a new version in a geodatabase.
     """
     inputs = locals()
     in_db = {'version_name': ['version_name', 'required'], 'workspace': ['in_workspace', 'required'], 'parent_version': ['parent_version', 'required'], 'access_permission': ['access_permission', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateVersion', inputs, in_db, out_db)


def delete_version(workspace, version_name):
     """
     Geoprocessing tool to delete a specific version from a geodatabase
     """
     inputs = locals()
     in_db = {'version_name': ['version_name', 'required'], 'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteVersion', inputs, in_db, out_db)


def register_as_versioned(dataset, edit_to_base=None):
     """
     Geoprocessing tool to register enterprise, workgroup, or desktop geodatabase data as versioned.
     """
     inputs = locals()
     in_db = {'edit_to_base': ['edit_to_base', 'optional'], 'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'RegisterAsVersioned', inputs, in_db, out_db)


def unregister_as_versioned(dataset, keep_edit=None, compress_default=None):
     """
     Geoprocessing tool to unregister an enterprise, workgroup, or desktop geodatabase dataset as versioned.
     """
     inputs = locals()
     in_db = {'compress_default': ['compress_default', 'optional'], 'dataset': ['in_dataset', 'required'], 'keep_edit': ['keep_edit', 'optional']}
     out_db = {}
     return _execute_tool('management', 'UnregisterAsVersioned', inputs, in_db, out_db)


def alter_version(workspace, version, name=None, description=None, access=None):
     """
     Geoprocessing tool that alters the database version's properties of name, description, and access permissions.
     """
     inputs = locals()
     in_db = {'version': ['in_version', 'required'], 'workspace': ['in_workspace', 'required'], 'name': ['name', 'optional'], 'description': ['description', 'optional'], 'access': ['access', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterVersion', inputs, in_db, out_db)


def analyze(dataset, components):
     """
     Geoprocessing tool that updates the statistics for the geodatabase input dataset.
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'components': ['components', 'required']}
     out_db = {}
     return _execute_tool('management', 'Analyze', inputs, in_db, out_db)


def create_relationship_class(origtable, destination_table, relationship_type, forward_label, backward_label, message_direction, cardinality, attributed, origprimary_key, origforeign_key, destination_primary_key=None, destination_foreign_key=None):
     """
     Geoprocessing tool that creates a relationship class to store an association between fields or features in the origin table and the destination table
     """
     inputs = locals()
     in_db = {'message_direction': ['message_direction', 'required'], 'backward_label': ['backward_label', 'required'], 'relationship_type': ['relationship_type', 'required'], 'origforeign_key': ['origin_foreign_key', 'required'], 'destination_foreign_key': ['destination_foreign_key', 'optional'], 'destination_primary_key': ['destination_primary_key', 'optional'], 'attributed': ['attributed', 'required'], 'forward_label': ['forward_label', 'required'], 'origprimary_key': ['origin_primary_key', 'required'], 'origtable': ['origin_table', 'required'], 'cardinality': ['cardinality', 'required'], 'destination_table': ['destination_table', 'required']}
     out_db = {'relationship_class': ['out_relationship_class', 'required']}
     return _execute_tool('management', 'CreateRelationshipClass', inputs, in_db, out_db)


def table_to_relationship_class(origtable, destination_table, relationship_type, forward_label, backward_label, message_direction, cardinality, relationship_table, attribute_fields, origprimary_key, origforeign_key, destination_primary_key, destination_foreign_key):
     """
     Geoprocessing tool that creates an attributed relationship class from the Origin, Destination, and Relationship Tables.
     """
     inputs = locals()
     in_db = {'message_direction': ['message_direction', 'required'], 'backward_label': ['backward_label', 'required'], 'relationship_type': ['relationship_type', 'required'], 'origforeign_key': ['origin_foreign_key', 'required'], 'destination_foreign_key': ['destination_foreign_key', 'required'], 'destination_table': ['destination_table', 'required'], 'destination_primary_key': ['destination_primary_key', 'required'], 'attribute_fields': ['attribute_fields', 'required'], 'relationship_table': ['relationship_table', 'required'], 'origprimary_key': ['origin_primary_key', 'required'], 'origtable': ['origin_table', 'required'], 'cardinality': ['cardinality', 'required'], 'forward_label': ['forward_label', 'required']}
     out_db = {'relationship_class': ['out_relationship_class', 'required']}
     return _execute_tool('management', 'TableToRelationshipClass', inputs, in_db, out_db)


def feature_to_point(features, point_location=None):
     """
     Geoprocessing tool that creates a representative point for each input feature.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'point_location': ['point_location', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'FeatureToPoint', inputs, in_db, out_db)


def feature_vertices_to_points(features, point_location=None):
     """
     Geoprocessing tool that creates points from input feature vertices.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'point_location': ['point_location', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'FeatureVerticesToPoints', inputs, in_db, out_db)


def feature_to_line(features, cluster_tolerance=None, attributes=None):
     """
     Geoprocessing tool that creates line features by converting polygon boundaries to lines, or splitting line or polygon features at their intersections.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'attributes': ['attributes', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'FeatureToLine', inputs, in_db, out_db)


def feature_to_polygon(features, cluster_tolerance=None, attributes=None, label_features=None):
     """
     Geoprocessing tool that creates polygons from areas enclosed by line or polygon features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'attributes': ['attributes', 'optional'], 'cluster_tolerance': ['cluster_tolerance', 'optional'], 'label_features': ['label_features', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'FeatureToPolygon', inputs, in_db, out_db)


def polygon_to_line(features, neighbor_option=None):
     """
     Geoprocessing tool that creates a feature class containing lines converted from polygon boundaries with or without considering neighboring polygons.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'neighbor_option': ['neighbor_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'PolygonToLine', inputs, in_db, out_db)


def split_line_at_vertices(features):
     """
     Geoprocessing tool that creates new lines by splitting input lines or polygon boundaries at their vertices.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'SplitLineAtVertices', inputs, in_db, out_db)


def define_projection(dataset, coor_system):
     """
     Geoprocessing tool to record the coordinate system information for the specific input dataset or feature class.
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'coor_system': ['coor_system', 'required']}
     out_db = {}
     return _execute_tool('management', 'DefineProjection', inputs, in_db, out_db)


def eliminate(features, selection=None, ex_where_clause=None, ex_features=None):
     """
     Geoprocessing tool to merge selected polygons with neighboring polygons.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'ex_features': ['ex_features', 'optional'], 'ex_where_clause': ['ex_where_clause', 'optional'], 'selection': ['selection', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'Eliminate', inputs, in_db, out_db)


def repair_geometry(features, delete_null=None):
     """
     Geoprocessing tool that inspects the features for geometry problems, fixes the problems that are found, and then  prints a list of the problems that were fixed.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'delete_null': ['delete_null', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RepairGeometry', inputs, in_db, out_db)


def create_topology(dataset, out_name, cluster_tolerance=None):
     """
     Geoprocessing tool to create a topology.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'cluster_tolerance': ['in_cluster_tolerance', 'optional'], 'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateTopology', inputs, in_db, out_db)


def add_feature_class_to_topology(topology, featureclass, xy_rank, z_rank):
     """
     Geoprocessing tool that adds a feature class to a topology.
     """
     inputs = locals()
     in_db = {'xy_rank': ['xy_rank', 'required'], 'z_rank': ['z_rank', 'required'], 'featureclass': ['in_featureclass', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddFeatureClassToTopology', inputs, in_db, out_db)


def remove_feature_class_from_topology(topology, featureclass):
     """
     Geoprocessing tool to remove a feature class from participating in a topology.
     """
     inputs = locals()
     in_db = {'featureclass': ['in_featureclass', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveFeatureClassFromTopology', inputs, in_db, out_db)


def add_rule_to_topology(topology, rule_type, featureclass, subtype=None, featureclass2=None, subtype2=None):
     """
     Geoprocessing tool to add a rule to a topology.
     """
     inputs = locals()
     in_db = {'featureclass2': ['in_featureclass2', 'optional'], 'topology': ['in_topology', 'required'], 'subtype2': ['subtype2', 'optional'], 'featureclass': ['in_featureclass', 'required'], 'subtype': ['subtype', 'optional'], 'rule_type': ['rule_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddRuleToTopology', inputs, in_db, out_db)


def remove_rule_from_topology(topology, rule):
     """
     Geoprocessing tool to remove rules from a topology.
     """
     inputs = locals()
     in_db = {'rule': ['in_rule', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveRuleFromTopology', inputs, in_db, out_db)


def validate_topology(topology, visible_extent=None):
     """
     Geoprocessing tool that validates a topology.
     """
     inputs = locals()
     in_db = {'visible_extent': ['visible_extent', 'optional'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'ValidateTopology', inputs, in_db, out_db)


def set_cluster_tolerance(topology, cluster_tolerance):
     """
     Geoprocessing tool to set  the cluster tolerance value of a topology.
     """
     inputs = locals()
     in_db = {'cluster_tolerance': ['cluster_tolerance', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetClusterTolerance', inputs, in_db, out_db)


def make_query_table(table, key_field_option, key_field=None, field=None, where_clause=None):
     """
     Geoprocessing tool that applies an SQL query to a database and the results are represented in either a layer or a table view.
     """
     inputs = locals()
     in_db = {'field': ['in_field', 'optional'], 'table': ['in_table', 'required'], 'where_clause': ['where_clause', 'optional'], 'key_field': ['in_key_field', 'optional'], 'key_field_option': ['in_key_field_option', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'MakeQueryTable', inputs, in_db, out_db)


def make_xy_event_layer(table, x_field, y_field, spatial_reference=None, z_field=None):
     """
     Geoprocessing tool that creates a new point feature layer based on x- and y-coordinates defined in a source table.
     """
     inputs = locals()
     in_db = {'table': ['table', 'required'], 'y_field': ['in_y_field', 'required'], 'x_field': ['in_x_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'z_field': ['in_z_field', 'optional']}
     out_db = {'layer': ['out_layer', 'required']}
     return _execute_tool('management', 'MakeXYEventLayer', inputs, in_db, out_db)


def update_annotation_feature_class(features, update_values=None):
     """
     Geoprocessing tool to update an annotation feature class with text attribute fields and optionally populate the value of each new field for every feature.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'update_values': ['update_values', 'optional']}
     out_db = {}
     return _execute_tool('management', 'UpdateAnnotationFeatureClass', inputs, in_db, out_db)


def append_annotation_feature_classes(input_features, reference_scale, create_single_class=None, require_symbol_from_table=None, create_annotation_when_feature_added=None, update_annotation_when_feature_modified=None):
     """
     Geoprocessing tool to create a new geodatabase annotation feature class by combining annotation from multiple input geodatabase annotation feature classes
     """
     inputs = locals()
     in_db = {'create_annotation_when_feature_added': ['create_annotation_when_feature_added', 'optional'], 'create_single_class': ['create_single_class', 'optional'], 'input_features': ['input_features', 'required'], 'update_annotation_when_feature_modified': ['update_annotation_when_feature_modified', 'optional'], 'reference_scale': ['reference_scale', 'required'], 'require_symbol_from_table': ['require_symbol_from_table', 'optional']}
     out_db = {'output_featureclass': ['output_featureclass', 'required']}
     return _execute_tool('management', 'AppendAnnotationFeatureClasses', inputs, in_db, out_db)


def make_raster_layer(raster, where_clause=None, envelope=None, band_index=None):
     """
     Geoprocessing tool that makes a temporary raster layer from a raster dataset that will be available to select as a variable while working in the same application's session.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'where_clause': ['where_clause', 'optional'], 'envelope': ['envelope', 'optional'], 'band_index': ['band_index', 'optional']}
     out_db = {'rasterlayer': ['out_rasterlayer', 'required']}
     return _execute_tool('management', 'MakeRasterLayer', inputs, in_db, out_db)


def flip(raster):
     """
     Geoprocessing tool that reorients the raster by turning it over, from top to bottom, along the horizontal axis through the center of the raster.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Flip', inputs, in_db, out_db)


def mirror(raster):
     """
     Geoprocessing tool that reorients the raster by flipping it, from left to right, along the vertical axis through the center of the raster
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Mirror', inputs, in_db, out_db)


def project_raster(raster, out_coor_system, resampling_type=None, cell_size=None, geographic_transform=None, registration_point=None, coor_system=None):
     """
     Geoprocessing tool that transforms the raster dataset from one projection to another.
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'optional'], 'registration_point': ['Registration_Point', 'optional'], 'out_coor_system': ['out_coor_system', 'required'], 'raster': ['in_raster', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'geographic_transform': ['geographic_transform', 'optional'], 'coor_system': ['in_coor_system', 'optional']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'ProjectRaster', inputs, in_db, out_db)


def rescale(raster, x_scale, y_scale):
     """
     Geoprocessing tool that resizes a raster by the specified x and y scale factors.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'x_scale': ['x_scale', 'required'], 'y_scale': ['y_scale', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Rescale', inputs, in_db, out_db)


def rotate(raster, angle, pivot_point=None, resampling_type=None):
     """
     Geoprocessing tool that turns the raster dataset around the specified pivot point by the angle specified in degrees. The raster dataset will rotate in a clockwise direction.
     """
     inputs = locals()
     in_db = {'angle': ['angle', 'required'], 'raster': ['in_raster', 'required'], 'pivot_point': ['pivot_point', 'optional'], 'resampling_type': ['resampling_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Rotate', inputs, in_db, out_db)


def shift(raster, x_value, y_value, snap_raster=None):
     """
     Geoprocessing tool that moves (slides) the raster to a new geographic location, based on x and y shift values.
     """
     inputs = locals()
     in_db = {'snap_raster': ['in_snap_raster', 'optional'], 'raster': ['in_raster', 'required'], 'x_value': ['x_value', 'required'], 'y_value': ['y_value', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Shift', inputs, in_db, out_db)


def warp(raster, source_control_points, target_control_points, transformation_type=None, resampling_type=None):
     """
     Geoprocessing tool that performs a transformation on the raster based on the source and target control points using a polynomial transformation.
     """
     inputs = locals()
     in_db = {'target_control_points': ['target_control_points', 'required'], 'raster': ['in_raster', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'transformation_type': ['transformation_type', 'optional'], 'source_control_points': ['source_control_points', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Warp', inputs, in_db, out_db)


def append(inputs, target, schema_type=None, field_mapping=None, subtype=None):
     """
     Geoprocessing tool that appends multiple input datasets into an existing target dataset.
     """
     inputs = locals()
     in_db = {'inputs': ['inputs', 'required'], 'schema_type': ['schema_type', 'optional'], 'field_mapping': ['field_mapping', 'optional'], 'subtype': ['subtype', 'optional'], 'target': ['target', 'required']}
     out_db = {}
     return _execute_tool('management', 'Append', inputs, in_db, out_db)


def delete_features(features):
     """
     Geoprocessing tool used to remove features from a feature class or layer.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteFeatures', inputs, in_db, out_db)


def make_raster_catalog_layer(raster_catalog, where_clause=None, workspace=None, field_info=None):
     """
     Geoprocessing tool that makes a temporary raster catalog layer that will be available to select as a variable while working in the same application's session.
     """
     inputs = locals()
     in_db = {'raster_catalog': ['in_raster_catalog', 'required'], 'workspace': ['workspace', 'optional'], 'where_clause': ['where_clause', 'optional'], 'field_info': ['field_info', 'optional']}
     out_db = {'layer_name': ['layer_name', 'required']}
     return _execute_tool('management', 'MakeRasterCatalogLayer', inputs, in_db, out_db)


def add_field(table, field_name, field_type, field_precision=None, field_scale=None, field_length=None, field_alias=None, field_is_nullable=None, field_is_required=None, field_domain=None):
     """
     Geoprocessing tool to add a new field.
     """
     inputs = locals()
     in_db = {'field_length': ['field_length', 'optional'], 'field_is_nullable': ['field_is_nullable', 'optional'], 'table': ['in_table', 'required'], 'field_name': ['field_name', 'required'], 'field_domain': ['field_domain', 'optional'], 'field_is_required': ['field_is_required', 'optional'], 'field_scale': ['field_scale', 'optional'], 'field_precision': ['field_precision', 'optional'], 'field_alias': ['field_alias', 'optional'], 'field_type': ['field_type', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddField', inputs, in_db, out_db)


def assign_default_to_field(table, field_name, default_value=None, subtype_code=None, clear_value=None):
     """
     Geoprocessing tool used to create a default value for a specified field.
     """
     inputs = locals()
     in_db = {'clear_value': ['clear_value', 'optional'], 'table': ['in_table', 'required'], 'field_name': ['field_name', 'required'], 'default_value': ['default_value', 'optional'], 'subtype_code': ['subtype_code', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AssignDefaultToField', inputs, in_db, out_db)


def calculate_field(table, field, expression, expression_type=None, code_block=None):
     """
     Geoprocessing tool used to perform field calculations.
     """
     inputs = locals()
     in_db = {'field': ['field', 'required'], 'code_block': ['code_block', 'optional'], 'table': ['in_table', 'required'], 'expression': ['expression', 'required'], 'expression_type': ['expression_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateField', inputs, in_db, out_db)


def delete_field(table, drop_field):
     """
     Geoprocessing tool used to remove fields from a dataset
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'drop_field': ['drop_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteField', inputs, in_db, out_db)


def multipart_to_singlepart(features):
     """
     Geoprocessing tool that creates singlepart features from multipart features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'MultipartToSinglepart', inputs, in_db, out_db)


def integrate(features, cluster_tolerance=None):
     """
     Geoprocessing tool that updates one or more  feature classes by inserting common coordinate vertices for features that fall within the given x,y tolerance and by adding vertices where feature segments intersect.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'cluster_tolerance': ['cluster_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Integrate', inputs, in_db, out_db)


def merge(inputs, field_mappings=None):
     """
     Geoprocessing tool that combines multiple input datasets of the same data type into a single, new output dataset.
     """
     inputs = locals()
     in_db = {'inputs': ['inputs', 'required'], 'field_mappings': ['field_mappings', 'optional']}
     out_db = {'output': ['output', 'required']}
     return _execute_tool('management', 'Merge', inputs, in_db, out_db)


def feature_compare(base_features, test_features, sort_field, compare_type=None, ignore_options=None, xy_tolerance=None, m_tolerance=None, z_tolerance=None, attribute_tolerances=None, omit_field=None, continue_compare=None):
     """
     Geoprocessing tool that compares two feature classes or layers and returns the comparison results. Feature Compare can report differences with geometry, tabular values, spatial reference, and field definitions.
     """
     inputs = locals()
     in_db = {'continue_compare': ['continue_compare', 'optional'], 'omit_field': ['omit_field', 'optional'], 'attribute_tolerances': ['attribute_tolerances', 'optional'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'ignore_options': ['ignore_options', 'optional'], 'base_features': ['in_base_features', 'required'], 'test_features': ['in_test_features', 'required'], 'm_tolerance': ['m_tolerance', 'optional'], 'compare_type': ['compare_type', 'optional'], 'z_tolerance': ['z_tolerance', 'optional'], 'sort_field': ['sort_field', 'required']}
     out_db = {'compare_file': ['out_compare_file', 'optional']}
     return _execute_tool('management', 'FeatureCompare', inputs, in_db, out_db)


def file_compare(base_file, test_file, file_type=None, continue_compare=None):
     """
     Geoprocessing tool which compares two files and returns the comparison results. File Compare can report differences between two ASCII files or two binary files.
     """
     inputs = locals()
     in_db = {'continue_compare': ['continue_compare', 'optional'], 'test_file': ['in_test_file', 'required'], 'base_file': ['in_base_file', 'required'], 'file_type': ['file_type', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional']}
     return _execute_tool('management', 'FileCompare', inputs, in_db, out_db)


def raster_compare(base_raster, test_raster, compare_type=None, ignore_option=None, continue_compare=None, parameter_tolerances=None, attribute_tolerances=None, omit_field=None):
     """
     Geoprocessing tool that compares the properties of two raster datasets or two mosaic datasets.
     """
     inputs = locals()
     in_db = {'test_raster': ['in_test_raster', 'required'], 'ignore_option': ['ignore_option', 'optional'], 'base_raster': ['in_base_raster', 'required'], 'parameter_tolerances': ['parameter_tolerances', 'optional'], 'attribute_tolerances': ['attribute_tolerances', 'optional'], 'continue_compare': ['continue_compare', 'optional'], 'compare_type': ['compare_type', 'optional'], 'omit_field': ['omit_field', 'optional']}
     out_db = {'compare_file': ['out_compare_file', 'optional']}
     return _execute_tool('management', 'RasterCompare', inputs, in_db, out_db)


def table_compare(base_table, test_table, sort_field, compare_type=None, ignore_options=None, attribute_tolerances=None, omit_field=None, continue_compare=None):
     """
     Geoprocessing tool compares two tables or table views and returns the comparison results.
     """
     inputs = locals()
     in_db = {'omit_field': ['omit_field', 'optional'], 'base_table': ['in_base_table', 'required'], 'ignore_options': ['ignore_options', 'optional'], 'test_table': ['in_test_table', 'required'], 'attribute_tolerances': ['attribute_tolerances', 'optional'], 'continue_compare': ['continue_compare', 'optional'], 'compare_type': ['compare_type', 'optional'], 'sort_field': ['sort_field', 'required']}
     out_db = {'compare_file': ['out_compare_file', 'optional']}
     return _execute_tool('management', 'TableCompare', inputs, in_db, out_db)


def create_custom_geographic_transformation(geot_name, coor_system, custom_geot):
     """
     Geoprocessing tool that creates a transformation method for converting data between two geographic coordinate systems or datums.
     """
     inputs = locals()
     in_db = {'geot_name': ['geot_name', 'required'], 'custom_geot': ['custom_geot', 'required'], 'coor_system': ['in_coor_system', 'required']}
     out_db = {'coor_system': ['out_coor_system', 'required']}
     return _execute_tool('management', 'CreateCustomGeographicTransformation', inputs, in_db, out_db)


def create_file_gdb(out_folder_path, out_name, out_version=None):
     """
     Geoprocessing tool that creates a file geodatabase.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_folder_path': ['out_folder_path', 'required'], 'out_version': ['out_version', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateFileGDB', inputs, in_db, out_db)


def upgrade_spatial_reference(input_dataset, xy_resolution=None, z_resolution=None, m_resolution=None):
     """
     Geoprocessing tool for upgrading a low precision dataset's spatial reference to high precision.
     """
     inputs = locals()
     in_db = {'input_dataset': ['input_dataset', 'required'], 'z_resolution': ['z_resolution', 'optional'], 'm_resolution': ['m_resolution', 'optional'], 'xy_resolution': ['xy_resolution', 'optional']}
     out_db = {}
     return _execute_tool('management', 'UpgradeSpatialReference', inputs, in_db, out_db)


def adjust_3d_z(features, reverse_sign=None, adjust_value=None, from_units=None, to_units=None):
     """
     Geoprocessing tool that modifies all Z-values in a 3D feature class.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'to_units': ['to_units', 'optional'], 'reverse_sign': ['reverse_sign', 'optional'], 'from_units': ['from_units', 'optional'], 'adjust_value': ['adjust_value', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Adjust3DZ', inputs, in_db, out_db)


def compress(workspace):
     """
     Geoprocessing tool to compress an enterprise geodatabase
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'Compress', inputs, in_db, out_db)


def compare_replica_schema(geodatabase, source_file):
     """
     Geoprocessing tool that generates an XML that describes schema differences between a replica geodatabase and the relative replica geodatabase.
     """
     inputs = locals()
     in_db = {'geodatabase': ['in_geodatabase', 'required'], 'source_file': ['in_source_file', 'required']}
     out_db = {'output_replica_schema_changes_file': ['output_replica_schema_changes_file', 'required']}
     return _execute_tool('management', 'CompareReplicaSchema', inputs, in_db, out_db)


def create_replica(data, type, out_geodatabase, out_name, archiving, access_type=None, initial_data_sender=None, expand_feature_classes_and_tables=None, reuse_schema=None, get_related_data=None, geometry_features=None):
     """
     Geoprocessing tool used to create a geodatabase from a specified list of feature classes, layers, datasets, and/or tables in an enterprise geodatabase.
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'required'], 'reuse_schema': ['reuse_schema', 'optional'], 'type': ['in_type', 'required'], 'initial_data_sender': ['initial_data_sender', 'optional'], 'access_type': ['access_type', 'optional'], 'out_name': ['out_name', 'required'], 'get_related_data': ['get_related_data', 'optional'], 'out_geodatabase': ['out_geodatabase', 'required'], 'geometry_features': ['geometry_features', 'optional'], 'expand_feature_classes_and_tables': ['expand_feature_classes_and_tables', 'optional'], 'archiving': ['archiving', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateReplica', inputs, in_db, out_db)


def create_replica_footprints(workspace, out_workspace, output_featureclass_name):
     """
     Geoprocessing tool that creates a feature class that contains the geometries for all the replicas in a geodatabase.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'output_featureclass_name': ['output_featureclass_name', 'required'], 'out_workspace': ['out_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateReplicaFootprints', inputs, in_db, out_db)


def create_replica_from_server(geodataservice, datasets, type, out_geodatabase, out_name, archiving, access_type=None, initial_data_sender=None, expand_feature_classes_and_tables=None, reuse_schema=None, get_related_data=None, geometry_features=None):
     """
     Geoprocessing tool that creates a replica using a specified list of feature classes, layers, feature datasets, and/or tables from a remote geodatabase using a geodata service published on ArcGIS Server.
     """
     inputs = locals()
     in_db = {'type': ['in_type', 'required'], 'initial_data_sender': ['initial_data_sender', 'optional'], 'access_type': ['access_type', 'optional'], 'geodataservice': ['in_geodataservice', 'required'], 'get_related_data': ['get_related_data', 'optional'], 'out_geodatabase': ['out_geodatabase', 'required'], 'datasets': ['datasets', 'required'], 'reuse_schema': ['reuse_schema', 'optional'], 'out_name': ['out_name', 'required'], 'geometry_features': ['geometry_features', 'optional'], 'expand_feature_classes_and_tables': ['expand_feature_classes_and_tables', 'optional'], 'archiving': ['archiving', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateReplicaFromServer', inputs, in_db, out_db)


def export_acknowledgement_message(geodatabase, replica):
     """
     Geoprocessing tool that creates an output acknowledgement file to acknowledge the reception of previously received data change messages.
     """
     inputs = locals()
     in_db = {'geodatabase': ['in_geodatabase', 'required'], 'replica': ['in_replica', 'required']}
     out_db = {'acknowledgement_file': ['out_acknowledgement_file', 'required']}
     return _execute_tool('management', 'ExportAcknowledgementMessage', inputs, in_db, out_db)


def export_data_change_message(geodatabase, replica, switch_to_receiver, include_unacknowledged_changes, include_new_changes):
     """
     Geoprocessing tool that creates an output delta file containing updates from an input replica.
     """
     inputs = locals()
     in_db = {'include_new_changes': ['include_new_changes', 'required'], 'geodatabase': ['in_geodatabase', 'required'], 'switch_to_receiver': ['switch_to_receiver', 'required'], 'replica': ['in_replica', 'required'], 'include_unacknowledged_changes': ['include_unacknowledged_changes', 'required']}
     out_db = {'data_changes_file': ['out_data_changes_file', 'required']}
     return _execute_tool('management', 'ExportDataChangeMessage', inputs, in_db, out_db)


def export_replica_schema(geodatabase, replica):
     """
     Geoprocessing tool that creates a replica schema file with the schema of an input one- or two-way replica.
     """
     inputs = locals()
     in_db = {'geodatabase': ['in_geodatabase', 'required'], 'replica': ['in_replica', 'required']}
     out_db = {'output_replica_schema_file': ['output_replica_schema_file', 'required']}
     return _execute_tool('management', 'ExportReplicaSchema', inputs, in_db, out_db)


def import_message(geodatabase, source_delta_file, conflict_policy=None, conflict_definition=None, reconcile_with_parent_version=None):
     """
     Geoprocessing tool that imports changes from a delta file to a replica geodatabase.
     """
     inputs = locals()
     in_db = {'conflict_definition': ['conflict_definition', 'optional'], 'geodatabase': ['in_geodatabase', 'required'], 'conflict_policy': ['conflict_policy', 'optional'], 'source_delta_file': ['source_delta_file', 'required'], 'reconcile_with_parent_version': ['reconcile_with_parent_version', 'optional']}
     out_db = {'output_acknowledgement_file': ['output_acknowledgement_file', 'optional']}
     return _execute_tool('management', 'ImportMessage', inputs, in_db, out_db)


def import_replica_schema(geodatabase, source):
     """
     Geoprocessing tool that applies replica schema differences using an input replica geodatabase and XML schema file or geodatabase.
     """
     inputs = locals()
     in_db = {'geodatabase': ['in_geodatabase', 'required'], 'source': ['in_source', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportReplicaSchema', inputs, in_db, out_db)


def reexport_unacknowledged_messages(geodatabase, replica, export_option):
     """
     Geoprocessing tool that creates an output delta file containing unacknowledged replica updates from a one-way or two-way replica geodatabase.
     """
     inputs = locals()
     in_db = {'export_option': ['in_export_option', 'required'], 'geodatabase': ['in_geodatabase', 'required'], 'replica': ['in_replica', 'required']}
     out_db = {'output_delta_file': ['output_delta_file', 'required']}
     return _execute_tool('management', 'Re-ExportUnacknowledgedMessages', inputs, in_db, out_db)


def synchronize_changes(geodatabase_1, replica, geodatabase_2, direction, conflict_policy, conflict_definition, reconcile):
     """
     Geoprocessing tool that synchronizes updates between two replica geodatabases in a direction specified by the user.
     """
     inputs = locals()
     in_db = {'conflict_definition': ['conflict_definition', 'required'], 'geodatabase_1': ['geodatabase_1', 'required'], 'conflict_policy': ['conflict_policy', 'required'], 'direction': ['in_direction', 'required'], 'reconcile': ['reconcile', 'required'], 'geodatabase_2': ['geodatabase_2', 'required'], 'replica': ['in_replica', 'required']}
     out_db = {}
     return _execute_tool('management', 'SynchronizeChanges', inputs, in_db, out_db)


def add_subtype(table, subtype_code, subtype_description):
     """
     Geoprocessing tool that adds a new subtype to the subtypes in the input table
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'subtype_description': ['subtype_description', 'required'], 'subtype_code': ['subtype_code', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddSubtype', inputs, in_db, out_db)


def remove_subtype(table, subtype_code):
     """
     Geoprocessing tool that removes a subtype from the input table using its code.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'subtype_code': ['subtype_code', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveSubtype', inputs, in_db, out_db)


def set_default_subtype(table, subtype_code):
     """
     Geoprocessing tool that sets the default subtype value for the input table's subtype.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'subtype_code': ['subtype_code', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetDefaultSubtype', inputs, in_db, out_db)


def set_subtype_field(table, field=None, clear_value=None):
     """
     Geoprocessing tool that defines the field in the input table or feature class that stores the subtype codes.
     """
     inputs = locals()
     in_db = {'field': ['field', 'optional'], 'table': ['in_table', 'required'], 'clear_value': ['clear_value', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetSubtypeField', inputs, in_db, out_db)


def add_colormap(raster, template_raster=None, input_clr_file=None):
     """
     Geoprocessing tool that adds a color map to a raster dataset, if it does not already exist or replaces a color map with the one specified.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'template_raster': ['in_template_raster', 'optional'], 'input_clr_file': ['input_CLR_file', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddColormap', inputs, in_db, out_db)


def build_raster_attribute_table(raster, overwrite=None):
     """
     Geoprocessing tool that adds a raster attribute table to a raster dataset or updates an existing one.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'overwrite': ['overwrite', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildRasterAttributeTable', inputs, in_db, out_db)


def delete_colormap(raster):
     """
     Geoprocessing tool that removes the color map associated with a raster dataset.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteColormap', inputs, in_db, out_db)


def delete_raster_attribute_table(raster):
     """
     Geoprocessing tool that removes the raster attribute table associated with a raster dataset.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteRasterAttributeTable', inputs, in_db, out_db)


def build_pyramids(raster_dataset, pyramid_level=None, skip_first=None, resample_technique=None, compression_type=None, compression_quality=None, skip_existing=None):
     """
     Geoprocessing tool that builds or deletes raster pyramids for a raster dataset.
     """
     inputs = locals()
     in_db = {'compression_type': ['compression_type', 'optional'], 'pyramid_level': ['pyramid_level', 'optional'], 'skip_first': ['SKIP_FIRST', 'optional'], 'skip_existing': ['skip_existing', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'resample_technique': ['resample_technique', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildPyramids', inputs, in_db, out_db)


def calculate_statistics(raster_dataset, x_skip_factor=None, y_skip_factor=None, ignore_values=None, skip_existing=None, area_of_interest=None):
     """
     Geoprocessing tool that calculates statistics for a raster dataset or mosaic dataset.
     """
     inputs = locals()
     in_db = {'area_of_interest': ['area_of_interest', 'optional'], 'y_skip_factor': ['y_skip_factor', 'optional'], 'skip_existing': ['skip_existing', 'optional'], 'x_skip_factor': ['x_skip_factor', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'ignore_values': ['ignore_values', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateStatistics', inputs, in_db, out_db)


def get_raster_properties(raster, property_type=None, band_index=None):
     """
     Geoprocessing tool that returns the properties of a raster dataset, mosaic dataset, or a raster product.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'property_type': ['property_type', 'optional'], 'band_index': ['band_index', 'optional']}
     out_db = {}
     return _execute_tool('management', 'GetRasterProperties', inputs, in_db, out_db)


def copy_raster(raster, config_keyword=None, background_value=None, nodata_value=None, onebit_to_eightbit=None, colormap_to_rgb=None, pixel_type=None, scale_pixel_value=None, rgb_to_colormap=None, format=None, transform=None):
     """
     Geoprocessing tool that makes a copy of a raster dataset.
     """
     inputs = locals()
     in_db = {'background_value': ['background_value', 'optional'], 'rgb_to_colormap': ['RGB_to_Colormap', 'optional'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional'], 'pixel_type': ['pixel_type', 'optional'], 'scale_pixel_value': ['scale_pixel_value', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'raster': ['in_raster', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'format': ['format', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'transform': ['transform', 'optional']}
     out_db = {'rasterdataset': ['out_rasterdataset', 'required']}
     return _execute_tool('management', 'CopyRaster', inputs, in_db, out_db)


def create_random_raster(out_path, out_name, distribution=None, raster_extent=None, cellsize=None):
     """
     Geoprocessing tool that creates a random raster dataset based on a user-specified distribution and extent.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'distribution': ['distribution', 'optional'], 'cellsize': ['cellsize', 'optional'], 'raster_extent': ['raster_extent', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomRaster', inputs, in_db, out_db)


def create_raster_dataset(out_path, out_name, pixel_type, number_of_bands, cellsize=None, raster_spatial_reference=None, config_keyword=None, pyramids=None, tile_size=None, compression=None, pyramid_origin=None):
     """
     Geoprocessing tool that creates a raster dataset as a file or in a geodatabase.
     """
     inputs = locals()
     in_db = {'number_of_bands': ['number_of_bands', 'required'], 'raster_spatial_reference': ['raster_spatial_reference', 'optional'], 'pyramids': ['pyramids', 'optional'], 'pixel_type': ['pixel_type', 'required'], 'tile_size': ['tile_size', 'optional'], 'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'cellsize': ['cellsize', 'optional'], 'compression': ['compression', 'optional'], 'pyramid_origin': ['pyramid_origin', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRasterDataset', inputs, in_db, out_db)


def mosaic(inputs, target, mosaic_type=None, colormap=None, background_value=None, nodata_value=None, onebit_to_eightbit=None, mosaicking_tolerance=None, matching_method=None):
     """
     Geoprocessing tool that mosaics multiple input rasters into an existing raster dataset.
     """
     inputs = locals()
     in_db = {'background_value': ['background_value', 'optional'], 'matching_method': ['MatchingMethod', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'target': ['target', 'required'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional'], 'inputs': ['inputs', 'required'], 'mosaic_type': ['mosaic_type', 'optional'], 'colormap': ['colormap', 'optional']}
     out_db = {}
     return _execute_tool('management', 'Mosaic', inputs, in_db, out_db)


def workspace_to_raster_dataset(workspace, raster_dataset, include_subdirectories=None, mosaic_type=None, colormap=None, background_value=None, nodata_value=None, onebit_to_eightbit=None, mosaicking_tolerance=None, matching_method=None, colormap_to_rgb=None):
     """
     Geoprocessing tool that mosaics all the raster datasets stored within the specified workspace into one raster dataset.
     """
     inputs = locals()
     in_db = {'background_value': ['background_value', 'optional'], 'workspace': ['in_workspace', 'required'], 'matching_method': ['MatchingMethod', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'mosaicking_tolerance': ['mosaicking_tolerance', 'optional'], 'colormap': ['colormap', 'optional'], 'raster_dataset': ['in_raster_dataset', 'required'], 'mosaic_type': ['mosaic_type', 'optional'], 'onebit_to_eightbit': ['onebit_to_eightbit', 'optional'], 'include_subdirectories': ['include_subdirectories', 'optional'], 'colormap_to_rgb': ['colormap_to_RGB', 'optional']}
     out_db = {}
     return _execute_tool('management', 'WorkspaceToRasterDataset', inputs, in_db, out_db)


def copy_raster_catalog_items(raster_catalog, config_keyword=None, spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None):
     """
     Geoprocessing tool that makes a copy of a raster catalog, including all of its contents, or a subset of its contents if there is a selection.
     """
     inputs = locals()
     in_db = {'raster_catalog': ['in_raster_catalog', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'spatial_grid_2': ['spatial_grid_2', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional']}
     out_db = {'raster_catalog': ['out_raster_catalog', 'required']}
     return _execute_tool('management', 'CopyRasterCatalogItems', inputs, in_db, out_db)


def create_raster_catalog(out_path, out_name, raster_spatial_reference=None, spatial_reference=None, config_keyword=None, spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None, raster_management_type=None, template_raster_catalog=None):
     """
     Geoprocessing tool that creates an empty raster catalog in a geodatabase.
     """
     inputs = locals()
     in_db = {'spatial_grid_2': ['spatial_grid_2', 'optional'], 'raster_spatial_reference': ['raster_spatial_reference', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'spatial_grid_1': ['spatial_grid_1', 'optional'], 'template_raster_catalog': ['template_raster_catalog', 'optional'], 'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'raster_management_type': ['raster_management_type', 'optional'], 'spatial_grid_3': ['spatial_grid_3', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRasterCatalog', inputs, in_db, out_db)


def delete_raster_catalog_items(raster_catalog):
     """
     Geoprocessing tool that deletes raster catalog items, including all its contents, or a subset of its contents if there is a selection.
     """
     inputs = locals()
     in_db = {'raster_catalog': ['in_raster_catalog', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteRasterCatalogItems', inputs, in_db, out_db)


def workspace_to_raster_catalog(workspace, raster_catalog, include_subdirectories=None, project=None):
     """
     Geoprocessing tool that loads all the raster datasets stored in the same workspace into an existing raster catalog.
     """
     inputs = locals()
     in_db = {'raster_catalog': ['in_raster_catalog', 'required'], 'workspace': ['in_workspace', 'required'], 'project': ['project', 'optional'], 'include_subdirectories': ['include_subdirectories', 'optional']}
     out_db = {}
     return _execute_tool('management', 'WorkspaceToRasterCatalog', inputs, in_db, out_db)


def create_ortho_corrected_raster_dataset(raster, ortho_type, constant_elevation, dem_raster=None, z_factor=None, z_offset=None, geoid=None):
     """
     Geoprocessing tool that creates an orthocorrected raster dataset using the rational polynomial coefficients (RPC) associated with a raster dataset.
     """
     inputs = locals()
     in_db = {'constant_elevation': ['constant_elevation', 'required'], 'ortho_type': ['Ortho_type', 'required'], 'dem_raster': ['in_DEM_raster', 'optional'], 'raster': ['in_raster', 'required'], 'z_offset': ['ZOffset', 'optional'], 'geoid': ['Geoid', 'optional'], 'z_factor': ['ZFactor', 'optional']}
     out_db = {'raster_dataset': ['out_raster_dataset', 'required']}
     return _execute_tool('management', 'CreateOrthoCorrectedRasterDataset', inputs, in_db, out_db)


def create_pan_sharpened_raster_dataset(raster, red_channel, green_channel, blue_channel, panchromatic_image, pansharpening_type, infrared_channel=None, red_weight=None, green_weight=None, blue_weight=None, infrared_weight=None, sensor=None):
     """
     Geoprocessing tool that fuses a high-resolution panchromatic raster dataset with a lower-resolution multiband raster dataset to create a red-green-blue (RGB) raster with the resolution of the panchromatic raster.
     """
     inputs = locals()
     in_db = {'blue_channel': ['blue_channel', 'required'], 'panchromatic_image': ['in_panchromatic_image', 'required'], 'infrared_weight': ['infrared_weight', 'optional'], 'green_weight': ['green_weight', 'optional'], 'blue_weight': ['blue_weight', 'optional'], 'red_channel': ['red_channel', 'required'], 'red_weight': ['red_weight', 'optional'], 'raster': ['in_raster', 'required'], 'sensor': ['sensor', 'optional'], 'infrared_channel': ['infrared_channel', 'optional'], 'green_channel': ['green_channel', 'required'], 'pansharpening_type': ['pansharpening_type', 'required']}
     out_db = {'raster_dataset': ['out_raster_dataset', 'required']}
     return _execute_tool('management', 'CreatePan-sharpenedRasterDataset', inputs, in_db, out_db)


def clip(raster, rectangle, template_dataset=None, nodata_value=None, clipping_geometry=None, maintaclipping_extent=None):
     """
     Geoprocessing tool that creates a spatial subset of a raster dataset.
     """
     inputs = locals()
     in_db = {'clipping_geometry': ['clipping_geometry', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'raster': ['in_raster', 'required'], 'maintaclipping_extent': ['maintain_clipping_extent', 'optional'], 'rectangle': ['rectangle', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Clip', inputs, in_db, out_db)


def composite_bands(rasters):
     """
     Geoprocessing tool that creates a single raster dataset from multiple bands and can also create a subset of the bands.
     """
     inputs = locals()
     in_db = {'rasters': ['in_rasters', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'CompositeBands', inputs, in_db, out_db)


def resample(raster, cell_size=None, resampling_type=None):
     """
     Geoprocessing tool that alters the raster dataset by changing the cell size and resampling method.
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'optional'], 'raster': ['in_raster', 'required'], 'resampling_type': ['resampling_type', 'optional']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'Resample', inputs, in_db, out_db)


def export_raster_world_file(raster_dataset):
     """
     Geoprocessing tool that creates a world file based on the geographic information of a raster dataset.
     """
     inputs = locals()
     in_db = {'raster_dataset': ['in_raster_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'ExportRasterWorldFile', inputs, in_db, out_db)


def get_cell_value(raster, location_point, band_index=None):
     """
     Geoprocessing tool that retrieves the pixel value at a specific x,y coordinate.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'location_point': ['location_point', 'required'], 'band_index': ['band_index', 'optional']}
     out_db = {}
     return _execute_tool('management', 'GetCellValue', inputs, in_db, out_db)


def raster_catalog_to_raster_dataset(raster_catalog, where_clause=None, mosaic_type=None, colormap=None, order_by_field=None, ascending=None, pixel_type=None, color_balancing=None, matching_method=None, reference_raster=None, oid=None):
     """
     Geoprocessing tool that mosaics the contents of a raster catalog into a new raster dataset.
     """
     inputs = locals()
     in_db = {'order_by_field': ['order_by_field', 'optional'], 'reference_raster': ['ReferenceRaster', 'optional'], 'matching_method': ['MatchingMethod', 'optional'], 'pixel_type': ['pixel_type', 'optional'], 'ascending': ['ascending', 'optional'], 'oid': ['OID', 'optional'], 'raster_catalog': ['in_raster_catalog', 'required'], 'color_balancing': ['ColorBalancing', 'optional'], 'where_clause': ['where_clause', 'optional'], 'mosaic_type': ['mosaic_type', 'optional'], 'colormap': ['colormap', 'optional']}
     out_db = {'raster_dataset': ['out_raster_dataset', 'required']}
     return _execute_tool('management', 'RasterCatalogToRasterDataset', inputs, in_db, out_db)


def extract_subdataset(raster, subdataset_index=None):
     """
     Geoprocessing tool that extracts raster datasets stored within a sub-dataset raster file.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'subdataset_index': ['subdataset_index', 'optional']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'ExtractSubdataset', inputs, in_db, out_db)


def tin_compare(base_tin, test_tin, compare_type=None, continue_compare=None):
     """
     Geoprocessing tool which compares two TINs and returns the comparison results. TIN Compare can report differences with geometry, TIN node and triangle tags, and spatial reference.
     """
     inputs = locals()
     in_db = {'continue_compare': ['continue_compare', 'optional'], 'compare_type': ['compare_type', 'optional'], 'test_tin': ['in_test_tin', 'required'], 'base_tin': ['in_base_tin', 'required']}
     out_db = {'compare_file': ['out_compare_file', 'optional']}
     return _execute_tool('management', 'TINCompare', inputs, in_db, out_db)


def make_image_server_layer(image_service, template=None, band_index=None, mosaic_method=None, order_field=None, order_base_value=None, lock_rasterid=None, cell_size=None, where_clause=None, processing_template=None):
     """
     Geoprocessing tool that creates a temporary raster layer from an image service. The layer that is created by the tool is temporary and will not persist after the session ends unless the document is saved.
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'optional'], 'mosaic_method': ['mosaic_method', 'optional'], 'processing_template': ['processing_template', 'optional'], 'order_field': ['order_field', 'optional'], 'band_index': ['band_index', 'optional'], 'where_clause': ['where_clause', 'optional'], 'lock_rasterid': ['lock_rasterid', 'optional'], 'order_base_value': ['order_base_value', 'optional'], 'template': ['template', 'optional'], 'image_service': ['in_image_service', 'required']}
     out_db = {'imageserver_layer': ['out_imageserver_layer', 'required']}
     return _execute_tool('management', 'MakeImageServerLayer', inputs, in_db, out_db)


def make_wcs_layer(wcs_coverage, template=None, band_index=None):
     """
     Geoprocessing tool that creates a temporary raster layer from a WCS service.
     """
     inputs = locals()
     in_db = {'band_index': ['band_index', 'optional'], 'wcs_coverage': ['in_wcs_coverage', 'required'], 'template': ['template', 'optional']}
     out_db = {'wcs_layer': ['out_wcs_layer', 'required']}
     return _execute_tool('management', 'MakeWCSLayer', inputs, in_db, out_db)


def apply_symbology_from_layer(layer, symbology_layer):
     """
     Geoprocessing tool that applies the symbology from a specified layer to the Input Layer.
     """
     inputs = locals()
     in_db = {'layer': ['in_layer', 'required'], 'symbology_layer': ['in_symbology_layer', 'required']}
     out_db = {}
     return _execute_tool('management', 'ApplySymbologyFromLayer', inputs, in_db, out_db)


def export_raster_catalog_paths(raster_catalog, export_mode):
     """
     Geoprocessing tool that creates a table listing the paths to the raster datasets contained in an unmanaged raster catalog or mosaic dataset.
     """
     inputs = locals()
     in_db = {'raster_catalog': ['in_raster_catalog', 'required'], 'export_mode': ['export_mode', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'ExportRasterCatalogPaths', inputs, in_db, out_db)


def repair_raster_catalog_paths(raster_catalog, repair_mode, original_path=None, new_path=None):
     """
     Geoprocessing tool that repairs broken file paths or deletes broken links within an unmanaged raster catalog or mosaic dataset.
     """
     inputs = locals()
     in_db = {'raster_catalog': ['in_raster_catalog', 'required'], 'original_path': ['original_path', 'optional'], 'new_path': ['new_path', 'optional'], 'repair_mode': ['repair_mode', 'required']}
     out_db = {}
     return _execute_tool('management', 'RepairRasterCatalogPaths', inputs, in_db, out_db)


def migrate_storage(datasets, config_keyword):
     """
     Geoprocessing tool to migrate the spatial, BLOB, and raster storage type based on a configuration keyword.
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'required'], 'datasets': ['in_datasets', 'required']}
     out_db = {}
     return _execute_tool('management', 'MigrateStorage', inputs, in_db, out_db)


def mosaic_to_new_raster(input_rasters, output_location, raster_dataset_name_with_extension, number_of_bands, coordinate_system_for_the_raster=None, pixel_type=None, cellsize=None, mosaic_method=None, mosaic_colormap_mode=None):
     """
     Geoprocessing tool that mosaics multiple raster datasets into a new raster dataset.
     """
     inputs = locals()
     in_db = {'raster_dataset_name_with_extension': ['raster_dataset_name_with_extension', 'required'], 'mosaic_method': ['mosaic_method', 'optional'], 'input_rasters': ['input_rasters', 'required'], 'pixel_type': ['pixel_type', 'optional'], 'mosaic_colormap_mode': ['mosaic_colormap_mode', 'optional'], 'number_of_bands': ['number_of_bands', 'required'], 'coordinate_system_for_the_raster': ['coordinate_system_for_the_raster', 'optional'], 'cellsize': ['cellsize', 'optional'], 'output_location': ['output_location', 'required']}
     out_db = {}
     return _execute_tool('management', 'MosaicToNewRaster', inputs, in_db, out_db)


def dice(features, vertex_limit):
     """
     Geoprocessing tool that subdivides a feature into smaller features based on a specified vertex limit.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'vertex_limit': ['vertex_limit', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'Dice', inputs, in_db, out_db)


def split_line_at_point(features, point_features, search_radius=None):
     """
     Geoprocessing tool to split line features based on intersection or proximity to point features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'point_features': ['point_features', 'required'], 'search_radius': ['search_radius', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'SplitLineatPoint', inputs, in_db, out_db)


def unsplit_line(features, dissolve_field=None, statistics_fields=None):
     """
     Geoprocessing tool that aggregates line features based on specified attributes.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'statistics_fields': ['statistics_fields', 'optional'], 'dissolve_field': ['dissolve_field', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'UnsplitLine', inputs, in_db, out_db)


def split_raster(raster, out_folder, out_base_name, split_method, format, resampling_type=None, num_rasters=None, tile_size=None, overlap=None, units=None, cell_size=None, origin=None, split_polygon_feature_class=None, clip_type=None, template_extent=None, nodata_value=None):
     """
     Geoprocessing tool that creates a tiled output from an input raster dataset.
     """
     inputs = locals()
     in_db = {'num_rasters': ['num_rasters', 'optional'], 'format': ['format', 'required'], 'overlap': ['overlap', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'out_base_name': ['out_base_name', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'cell_size': ['cell_size', 'optional'], 'split_method': ['split_method', 'required'], 'template_extent': ['template_extent', 'optional'], 'clip_type': ['clip_type', 'optional'], 'tile_size': ['tile_size', 'optional'], 'out_folder': ['out_folder', 'required'], 'raster': ['in_raster', 'required'], 'units': ['units', 'optional'], 'origin': ['origin', 'optional'], 'split_polygon_feature_class': ['split_polygon_feature_class', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SplitRaster', inputs, in_db, out_db)


def eliminate_polygon_part(features, condition=None, part_area=None, part_area_percent=None, part_option=None):
     """
     Geoprocessing tool that creates a new output feature class containing the features from input polygons with some parts or holes of a specified size deleted.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'part_area': ['part_area', 'optional'], 'part_option': ['part_option', 'optional'], 'condition': ['condition', 'optional'], 'part_area_percent': ['part_area_percent', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'EliminatePolygonPart', inputs, in_db, out_db)


def make_graph(graph_template_source, datasets):
     """
     Geoprocessing tool that creates a graph using a graph template or an existing graph.
     """
     inputs = locals()
     in_db = {'graph_template_source': ['in_graph_template_source', 'required'], 'datasets': ['in_datasets', 'required']}
     out_db = {'graph_name': ['out_graph_name', 'required']}
     return _execute_tool('management', 'MakeGraph', inputs, in_db, out_db)


def save_graph(graph, maintaimage_aspect=None, image_width=None, image_height=None):
     """
     Geoprocessing tool to save a graph to supported image/vector formats or as a graph file.
     """
     inputs = locals()
     in_db = {'maintaimage_aspect': ['maintain_image_aspect', 'optional'], 'graph': ['in_graph', 'required'], 'image_height': ['image_height', 'optional'], 'image_width': ['image_width', 'optional']}
     out_db = {'graph_file': ['out_graph_file', 'required']}
     return _execute_tool('management', 'SaveGraph', inputs, in_db, out_db)


def points_to_line(input_features, line_field=None, sort_field=None, close_line=None):
     """
     Geoprocessing tool used to create line features from points.
     """
     inputs = locals()
     in_db = {'input_features': ['Input_Features', 'required'], 'close_line': ['Close_Line', 'optional'], 'line_field': ['Line_Field', 'optional'], 'sort_field': ['Sort_Field', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required']}
     return _execute_tool('management', 'PointsToLine', inputs, in_db, out_db)


def change_version(features, version_type, version_name=None, date=None):
     """
     Geoprocessing tool used to change the enterprise geodatabase version you are connected to. Only works when working with feature layers or table views.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'version_type': ['version_type', 'required'], 'version_name': ['version_name', 'optional'], 'date': ['date', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ChangeVersion', inputs, in_db, out_db)


def register_with_geodatabase(dataset, object_id_field=None, shape_field=None, geometry_type=None, spatial_reference=None, extent=None):
     """
     Geoprocessing tool that registers feature classes, tables, views, and raster layers that were created outside of the geodatabase with the geodatabase in order for them to participate in geodatabase functionality.
     """
     inputs = locals()
     in_db = {'geometry_type': ['in_geometry_type', 'optional'], 'shape_field': ['in_shape_field', 'optional'], 'spatial_reference': ['in_spatial_reference', 'optional'], 'extent': ['in_extent', 'optional'], 'dataset': ['in_dataset', 'required'], 'object_id_field': ['in_object_id_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RegisterwithGeodatabase', inputs, in_db, out_db)


def upgrade_geodatabase(input_workspace, input_prerequisite_check, input_upgradegdb_check):
     """
     Geoprocessing tool to upgrade the release version of a geodatabase.
     """
     inputs = locals()
     in_db = {'input_upgradegdb_check': ['input_upgradegdb_check', 'required'], 'input_prerequisite_check': ['input_prerequisite_check', 'required'], 'input_workspace': ['input_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'UpgradeGeodatabase', inputs, in_db, out_db)


def calculate_default_xy_tolerance(features):
     """
     Geoprocessing tool to calculate a default XY tolerance value
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'CalculateDefaultXYTolerance', inputs, in_db, out_db)


def delete_identical(dataset, fields, xy_tolerance=None, z_tolerance=None):
     """
     Geoprocessing tool to delete records in a feature class or table which have identical values in a list of fields.
     """
     inputs = locals()
     in_db = {'z_tolerance': ['z_tolerance', 'optional'], 'dataset': ['in_dataset', 'required'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'fields': ['fields', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteIdentical', inputs, in_db, out_db)


def find_identical(dataset, fields, xy_tolerance=None, z_tolerance=None, output_record_option=None):
     """
     Geoprocessing tool that reports any records in a feature class or table that have identical values in a list of fields, and generates a table listing these identical records.
     """
     inputs = locals()
     in_db = {'z_tolerance': ['z_tolerance', 'optional'], 'output_record_option': ['output_record_option', 'optional'], 'dataset': ['in_dataset', 'required'], 'xy_tolerance': ['xy_tolerance', 'optional'], 'fields': ['fields', 'required']}
     out_db = {'dataset': ['out_dataset', 'required']}
     return _execute_tool('management', 'FindIdentical', inputs, in_db, out_db)


def consolidate_layer(layer, convert_data=None, convert_arcsde_data=None, extent=None, apply_extent_to_arcsde=None, schema_only=None):
     """
     Geoprocessing tool that consolidates one or more layers and all referenced data sources into a single folder.
     """
     inputs = locals()
     in_db = {'convert_arcsde_data': ['convert_arcsde_data', 'optional'], 'extent': ['extent', 'optional'], 'apply_extent_to_arcsde': ['apply_extent_to_arcsde', 'optional'], 'layer': ['in_layer', 'required'], 'convert_data': ['convert_data', 'optional'], 'schema_only': ['schema_only', 'optional']}
     out_db = {'output_folder': ['output_folder', 'required']}
     return _execute_tool('management', 'ConsolidateLayer', inputs, in_db, out_db)


def consolidate_map(map, convert_data=None, convert_arcsde_data=None, extent=None, apply_extent_to_arcsde=None, preserve_sqlite=None):
     """
     Geoprocessing tool that consolidates a map and all referenced data sources to a specified output folder.
     """
     inputs = locals()
     in_db = {'convert_arcsde_data': ['convert_arcsde_data', 'optional'], 'extent': ['extent', 'optional'], 'apply_extent_to_arcsde': ['apply_extent_to_arcsde', 'optional'], 'preserve_sqlite': ['preserve_sqlite', 'optional'], 'convert_data': ['convert_data', 'optional'], 'map': ['in_map', 'required']}
     out_db = {'output_folder': ['output_folder', 'required']}
     return _execute_tool('management', 'ConsolidateMap', inputs, in_db, out_db)


def package_layer(layer, convert_data=None, convert_arcsde_data=None, extent=None, apply_extent_to_arcsde=None, schema_only=None, version=None, additional_files=None, summary=None, tags=None):
     """
     Geoprocessing tool that packages one or more layers to create a single compressed .lpk file.
     """
     inputs = locals()
     in_db = {'version': ['version', 'optional'], 'convert_arcsde_data': ['convert_arcsde_data', 'optional'], 'tags': ['tags', 'optional'], 'extent': ['extent', 'optional'], 'summary': ['summary', 'optional'], 'apply_extent_to_arcsde': ['apply_extent_to_arcsde', 'optional'], 'layer': ['in_layer', 'required'], 'additional_files': ['additional_files', 'optional'], 'convert_data': ['convert_data', 'optional'], 'schema_only': ['schema_only', 'optional']}
     out_db = {'output_file': ['output_file', 'required']}
     return _execute_tool('management', 'PackageLayer', inputs, in_db, out_db)


def package_map(map, convert_data=None, convert_arcsde_data=None, extent=None, apply_extent_to_arcsde=None, arcgisruntime=None, reference_all_data=None, version=None, additional_files=None, summary=None, tags=None):
     """
     Geoprocessing tool that packages a map and all referenced data sources to create a single compressed file.
     """
     inputs = locals()
     in_db = {'version': ['version', 'optional'], 'convert_arcsde_data': ['convert_arcsde_data', 'optional'], 'tags': ['tags', 'optional'], 'extent': ['extent', 'optional'], 'arcgisruntime': ['arcgisruntime', 'optional'], 'reference_all_data': ['reference_all_data', 'optional'], 'apply_extent_to_arcsde': ['apply_extent_to_arcsde', 'optional'], 'additional_files': ['additional_files', 'optional'], 'convert_data': ['convert_data', 'optional'], 'map': ['in_map', 'required'], 'summary': ['summary', 'optional']}
     out_db = {'output_file': ['output_file', 'required']}
     return _execute_tool('management', 'PackageMap', inputs, in_db, out_db)


def change_privileges(dataset, user, view=None, edit=None):
     """
     Geoprocessing tool to change  privileges on a dataset.
     """
     inputs = locals()
     in_db = {'view': ['View', 'optional'], 'edit': ['Edit', 'optional'], 'dataset': ['in_dataset', 'required'], 'user': ['user', 'required']}
     out_db = {}
     return _execute_tool('management', 'ChangePrivileges', inputs, in_db, out_db)


def create_spatial_reference(spatial_reference=None, spatial_reference_template=None, xy_domain=None, z_domain=None, m_domain=None, template=None, expand_ratio=None):
     """
     Geoprocessing tool to create a spatial reference for use in ModelBuilder and scripting.
     """
     inputs = locals()
     in_db = {'spatial_reference_template': ['spatial_reference_template', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'xy_domain': ['xy_domain', 'optional'], 'expand_ratio': ['expand_ratio', 'optional'], 'm_domain': ['m_domain', 'optional'], 'z_domain': ['z_domain', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateSpatialReference', inputs, in_db, out_db)


def raster_to_dted(raster, out_folder, dted_level, resampling_type=None):
     """
     Geoprocessing tool that splits a raster dataset into files based on the DTED tiling structure.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'dted_level': ['dted_level', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'out_folder': ['out_folder', 'required']}
     out_db = {}
     return _execute_tool('management', 'RasterToDTED', inputs, in_db, out_db)


def bearing_distance_to_line(table, x_field, y_field, distance_field, distance_units, bearing_field, bearing_units, line_type=None, id_field=None, spatial_reference=None):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in an x-coordinate field, y-coordinate field, bearing field, and distance field of a table.
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'distance_field': ['distance_field', 'required'], 'table': ['in_table', 'required'], 'y_field': ['y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'distance_units': ['distance_units', 'required'], 'bearing_units': ['bearing_units', 'required'], 'bearing_field': ['bearing_field', 'required'], 'x_field': ['x_field', 'required'], 'line_type': ['line_type', 'optional']}
     out_db = {'featureclass': ['out_featureclass', 'required']}
     return _execute_tool('management', 'BearingDistanceToLine', inputs, in_db, out_db)


def table_to_ellipse(table, x_field, y_field, major_field, minor_field, distance_units, azimuth_field=None, azimuth_units=None, id_field=None, spatial_reference=None):
     """
     Geoprocessing tool that creates a new feature class containing geodetic ellipse features constructed based on the values in an x-coordinate field, y-coordinate field, major-axis field, minor-axis field, and azimuth field of a table.
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'table': ['in_table', 'required'], 'y_field': ['y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'distance_units': ['distance_units', 'required'], 'major_field': ['major_field', 'required'], 'minor_field': ['minor_field', 'required'], 'x_field': ['x_field', 'required'], 'azimuth_units': ['azimuth_units', 'optional'], 'azimuth_field': ['azimuth_field', 'optional']}
     out_db = {'featureclass': ['out_featureclass', 'required']}
     return _execute_tool('management', 'TableToEllipse', inputs, in_db, out_db)


def xy_to_line(table, startx_field, starty_field, endx_field, endy_field, line_type=None, id_field=None, spatial_reference=None):
     """
     Geoprocessing tool that creates a new feature class containing geodetic line features constructed based on the values in a start x-coordinate field, start y-coordinate field, end x-coordinate field, and end y-coordinate field of a table.
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'table': ['in_table', 'required'], 'startx_field': ['startx_field', 'required'], 'endx_field': ['endx_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'starty_field': ['starty_field', 'required'], 'line_type': ['line_type', 'optional'], 'endy_field': ['endy_field', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required']}
     return _execute_tool('management', 'XYToLine', inputs, in_db, out_db)


def convert_coordinate_notation(table, x_field, y_field, input_coordinate_format, output_coordinate_format, exclude_invalid_records, id_field=None, spatial_reference=None, coor_system=None):
     """
     Geoprocessing tool that converts coordinate notations from one format to another.
     """
     inputs = locals()
     in_db = {'id_field': ['id_field', 'optional'], 'table': ['in_table', 'required'], 'y_field': ['y_field', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'exclude_invalid_records': ['exclude_invalid_records', 'required'], 'coor_system': ['in_coor_system', 'optional'], 'x_field': ['x_field', 'required'], 'input_coordinate_format': ['input_coordinate_format', 'required'], 'output_coordinate_format': ['output_coordinate_format', 'required']}
     out_db = {'featureclass': ['out_featureclass', 'required']}
     return _execute_tool('management', 'ConvertCoordinateNotation', inputs, in_db, out_db)


def compress_file_geodatabase_data(data, lossless):
     """
     Geoprocessing tool that compresses all the contents in a geodatabase, all the contents in a feature dataset, or an individual stand-alone feature class or table.
     """
     inputs = locals()
     in_db = {'lossless': ['lossless', 'required'], 'data': ['in_data', 'required']}
     out_db = {}
     return _execute_tool('management', 'CompressFileGeodatabaseData', inputs, in_db, out_db)


def uncompress_file_geodatabase_data(data, config_keyword=None):
     """
     Geoprocessing tool that uncompresses all the contents in a geodatabase, all the contents in a feature dataset, or an individual stand-alone feature class or table.
     """
     inputs = locals()
     in_db = {'config_keyword': ['config_keyword', 'optional'], 'data': ['in_data', 'required']}
     out_db = {}
     return _execute_tool('management', 'UncompressFileGeodatabaseData', inputs, in_db, out_db)


def extract_package(package):
     """
     Geoprocessing tool that   extracts the contents of a package to a specified folder.
     """
     inputs = locals()
     in_db = {'package': ['in_package', 'required']}
     out_db = {'output_folder': ['output_folder', 'required']}
     return _execute_tool('management', 'ExtractPackage', inputs, in_db, out_db)


def share_package(package, username, password, summary, tags, credits=None, public=None, groups=None):
     """
     Geoprocessing tool that shares a package by uploading to ArcGIS online.
     """
     inputs = locals()
     in_db = {'public': ['public', 'optional'], 'groups': ['groups', 'optional'], 'password': ['password', 'required'], 'tags': ['tags', 'required'], 'credits': ['credits', 'optional'], 'username': ['username', 'required'], 'summary': ['summary', 'required'], 'package': ['in_package', 'required']}
     out_db = {}
     return _execute_tool('management', 'SharePackage', inputs, in_db, out_db)


def build_pyramids_and_statistics(workspace, include_subdirectories=None, build_pyramids=None, calculate_statistics=None, build_on_source=None, block_field=None, estimate_statistics=None, x_skip_factor=None, y_skip_factor=None, ignore_values=None, pyramid_level=None, skip_first=None, resample_technique=None, compression_type=None, compression_quality=None, skip_existing=None):
     """
     Geoprocessing tool that traverses a folder structure, building pyramids and calculating statistics for all the raster datasets it contains.
     """
     inputs = locals()
     in_db = {'compression_quality': ['compression_quality', 'optional'], 'skip_existing': ['skip_existing', 'optional'], 'build_on_source': ['BUILD_ON_SOURCE', 'optional'], 'x_skip_factor': ['x_skip_factor', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'include_subdirectories': ['include_subdirectories', 'optional'], 'ignore_values': ['ignore_values', 'optional'], 'compression_type': ['compression_type', 'optional'], 'workspace': ['in_workspace', 'required'], 'pyramid_level': ['pyramid_level', 'optional'], 'y_skip_factor': ['y_skip_factor', 'optional'], 'skip_first': ['SKIP_FIRST', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional'], 'resample_technique': ['resample_technique', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'block_field': ['block_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildPyramidsAndStatistics', inputs, in_db, out_db)


def make_mosaic_layer(mosaic_dataset, where_clause=None, template=None, band_index=None, mosaic_method=None, order_field=None, order_base_value=None, lock_rasterid=None, sort_order=None, mosaic_operator=None, cell_size=None, processing_template=None):
     """
     Geoprocessing tool that makes a temporary mosaic layer that will be available to select as a variable while working in the same application's session.
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'optional'], 'mosaic_method': ['mosaic_method', 'optional'], 'sort_order': ['sort_order', 'optional'], 'order_field': ['order_field', 'optional'], 'order_base_value': ['order_base_value', 'optional'], 'template': ['template', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'processing_template': ['processing_template', 'optional'], 'mosaic_operator': ['mosaic_operator', 'optional'], 'band_index': ['band_index', 'optional'], 'where_clause': ['where_clause', 'optional'], 'lock_rasterid': ['lock_rasterid', 'optional']}
     out_db = {'mosaic_layer': ['out_mosaic_layer', 'required']}
     return _execute_tool('management', 'MakeMosaicLayer', inputs, in_db, out_db)


def minimum_bounding_geometry(features, geometry_type=None, group_option=None, group_field=None, mbg_fields_option=None):
     """
     Geoprocessing tool that creates polygons which represent a specified minimum bounding geometry enclosing each input feature or a group of input features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'geometry_type': ['geometry_type', 'optional'], 'group_option': ['group_option', 'optional'], 'group_field': ['group_field', 'optional'], 'mbg_fields_option': ['mbg_fields_option', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'MinimumBoundingGeometry', inputs, in_db, out_db)


def add_rasters_to_mosaic_dataset(mosaic_dataset, raster_type, input_path, update_cellsize_ranges=None, update_boundary=None, update_overviews=None, maximum_pyramid_levels=None, maximum_cell_size=None, minimum_dimension=None, spatial_reference=None, filter=None, sub_folder=None, duplicate_items_action=None, build_pyramids=None, calculate_statistics=None, build_thumbnails=None, operation_description=None, force_spatial_reference=None, estimate_statistics=None, aux_inputs=None):
     """
     Geoprocessing tool that ingests raster datasets from a file, folder, raster catalog, or image service to a mosaic dataset.
     """
     inputs = locals()
     in_db = {'maximum_cell_size': ['maximum_cell_size', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'estimate_statistics': ['estimate_statistics', 'optional'], 'force_spatial_reference': ['force_spatial_reference', 'optional'], 'filter': ['filter', 'optional'], 'minimum_dimension': ['minimum_dimension', 'optional'], 'maximum_pyramid_levels': ['maximum_pyramid_levels', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'input_path': ['input_path', 'required'], 'calculate_statistics': ['calculate_statistics', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'operation_description': ['operation_description', 'optional'], 'sub_folder': ['sub_folder', 'optional'], 'raster_type': ['raster_type', 'required'], 'update_overviews': ['update_overviews', 'optional'], 'duplicate_items_action': ['duplicate_items_action', 'optional'], 'aux_inputs': ['aux_inputs', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddRastersToMosaicDataset', inputs, in_db, out_db)


def build_boundary(mosaic_dataset, where_clause=None, append_to_existing=None, simplification_method=None):
     """
     Geoprocessing tool that updates the extent of the boundary of  a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'simplification_method': ['simplification_method', 'optional'], 'append_to_existing': ['append_to_existing', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildBoundary', inputs, in_db, out_db)


def build_footprints(mosaic_dataset, where_clause=None, reset_footprint=None, mdata_value=None, max_data_value=None, approx_num_vertices=None, shrink_distance=None, maintaedges=None, skip_derived_images=None, update_boundary=None, request_size=None, mregion_size=None, simplification_method=None, edge_tolerance=None, max_sliver_size=None, mthinness_ratio=None):
     """
     Geoprocessing tool that computes the footprints for the rasters in a mosaic dataset.
     """
     inputs = locals()
     in_db = {'max_sliver_size': ['max_sliver_size', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'shrink_distance': ['shrink_distance', 'optional'], 'simplification_method': ['simplification_method', 'optional'], 'max_data_value': ['max_data_value', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'skip_derived_images': ['skip_derived_images', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'reset_footprint': ['reset_footprint', 'optional'], 'mdata_value': ['min_data_value', 'optional'], 'edge_tolerance': ['edge_tolerance', 'optional'], 'request_size': ['request_size', 'optional'], 'approx_num_vertices': ['approx_num_vertices', 'optional'], 'where_clause': ['where_clause', 'optional'], 'maintaedges': ['maintain_edges', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildFootprints', inputs, in_db, out_db)


def build_overviews(mosaic_dataset, where_clause=None, define_missing_tiles=None, generate_overviews=None, generate_missing_images=None, regenerate_stale_images=None):
     """
     Geoprocessing tool that defines and generates overviews for a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'generate_missing_images': ['generate_missing_images', 'optional'], 'regenerate_stale_images': ['regenerate_stale_images', 'optional'], 'where_clause': ['where_clause', 'optional'], 'define_missing_tiles': ['define_missing_tiles', 'optional'], 'generate_overviews': ['generate_overviews', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildOverviews', inputs, in_db, out_db)


def build_seamlines(mosaic_dataset, cell_size=None, sort_method=None, sort_order=None, order_by_attribute=None, order_by_base_value=None, view_point=None, computation_method=None, blend_width=None, blend_type=None, request_size=None, request_size_type=None, blend_width_units=None, area_of_interest=None, where_clause=None, update_existing=None, mregion_size=None, mthinness_ratio=None, max_sliver_size=None):
     """
     Geoprocessing tool that generates seamlines for your mosaic dataset.
     """
     inputs = locals()
     in_db = {'max_sliver_size': ['max_sliver_size', 'optional'], 'cell_size': ['cell_size', 'optional'], 'blend_width': ['blend_width', 'optional'], 'mregion_size': ['min_region_size', 'optional'], 'sort_order': ['sort_order', 'optional'], 'update_existing': ['update_existing', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'sort_method': ['sort_method', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'request_size_type': ['request_size_type', 'optional'], 'mthinness_ratio': ['min_thinness_ratio', 'optional'], 'blend_width_units': ['blend_width_units', 'optional'], 'request_size': ['request_size', 'optional'], 'order_by_base_value': ['order_by_base_value', 'optional'], 'blend_type': ['blend_type', 'optional'], 'view_point': ['view_point', 'optional'], 'order_by_attribute': ['order_by_attribute', 'optional'], 'where_clause': ['where_clause', 'optional'], 'computation_method': ['computation_method', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildSeamlines', inputs, in_db, out_db)


def calculate_cell_size_ranges(mosaic_dataset, where_clause=None, do_compute_min=None, do_compute_max=None, max_range_factor=None, cell_size_tolerance_factor=None, update_missing_only=None):
     """
     Geoprocessing tool that computes the minimum and maximum cell sizes for the rasters in a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'do_compute_max': ['do_compute_max', 'optional'], 'do_compute_min': ['do_compute_min', 'optional'], 'max_range_factor': ['max_range_factor', 'optional'], 'update_missing_only': ['update_missing_only', 'optional'], 'where_clause': ['where_clause', 'optional'], 'cell_size_tolerance_factor': ['cell_size_tolerance_factor', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateCellSizeRanges', inputs, in_db, out_db)


def color_balance_mosaic_dataset(mosaic_dataset, balancing_method=None, color_surface_type=None, target_raster=None, exclude_raster=None, stretch_type=None, gamma=None, block_field=None):
     """
     Geoprocessing tool that color balances a mosaic dataset so the tiles appear seamless.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'target_raster': ['target_raster', 'optional'], 'color_surface_type': ['color_surface_type', 'optional'], 'exclude_raster': ['exclude_raster', 'optional'], 'gamma': ['gamma', 'optional'], 'balancing_method': ['balancing_method', 'optional'], 'block_field': ['block_field', 'optional'], 'stretch_type': ['stretch_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ColorBalanceMosaicDataset', inputs, in_db, out_db)


def compute_dirty_area(mosaic_dataset, timestamp, where_clause=None):
     """
     Geoprocessing tool that identifies an area within a mosaic dataset that has changed since a specified point in time.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'timestamp': ['timestamp', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'ComputeDirtyArea', inputs, in_db, out_db)


def create_mosaic_dataset(workspace, mosaicdataset_name, coordinate_system, num_bands=None, pixel_type=None, product_definition=None, product_band_definitions=None):
     """
     Geoprocessing tool that makes an empty mosaic dataset in a geodatabase.
     """
     inputs = locals()
     in_db = {'mosaicdataset_name': ['in_mosaicdataset_name', 'required'], 'workspace': ['in_workspace', 'required'], 'pixel_type': ['pixel_type', 'optional'], 'coordinate_system': ['coordinate_system', 'required'], 'num_bands': ['num_bands', 'optional'], 'product_band_definitions': ['product_band_definitions', 'optional'], 'product_definition': ['product_definition', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateMosaicDataset', inputs, in_db, out_db)


def create_referenced_mosaic_dataset(dataset, coordinate_system=None, number_of_bands=None, pixel_type=None, where_clause=None, template_dataset=None, extent=None, select_using_features=None, lod_field=None, minps_field=None, maxps_field=None, pixel_size=None, build_boundary=None):
     """
     Geoprocessing tool that creates a new mosaic dataset from a selection set of a raster catalog, or a mosaic dataset.
     """
     inputs = locals()
     in_db = {'pixel_type': ['pixel_type', 'optional'], 'select_using_features': ['select_using_features', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'build_boundary': ['build_boundary', 'optional'], 'pixel_size': ['pixelSize', 'optional'], 'lod_field': ['lod_field', 'optional'], 'dataset': ['in_dataset', 'required'], 'extent': ['extent', 'optional'], 'minps_field': ['minPS_field', 'optional'], 'number_of_bands': ['number_of_bands', 'optional'], 'coordinate_system': ['coordinate_system', 'optional'], 'where_clause': ['where_clause', 'optional'], 'maxps_field': ['maxPS_field', 'optional']}
     out_db = {'mosaic_dataset': ['out_mosaic_dataset', 'required']}
     return _execute_tool('management', 'CreateReferencedMosaicDataset', inputs, in_db, out_db)


def define_mosaic_dataset_nodata(mosaic_dataset, num_bands, bands_for_nodata_value=None, bands_for_valid_data_range=None, where_clause=None, composite_nodata_value=None):
     """
     Geoprocessing tool that allows you to specify one or more NoData values for a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'bands_for_nodata_value': ['bands_for_nodata_value', 'optional'], 'composite_nodata_value': ['Composite_nodata_value', 'optional'], 'num_bands': ['num_bands', 'required'], 'bands_for_valid_data_range': ['bands_for_valid_data_range', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DefineMosaicDatasetNoData', inputs, in_db, out_db)


def define_overviews(mosaic_dataset, overview_image_folder=None, template_dataset=None, extent=None, pixel_size=None, number_of_levels=None, tile_rows=None, tile_cols=None, overview_factor=None, force_overview_tiles=None, resampling_method=None, compression_method=None, compression_quality=None):
     """
     Geoprocessing tool that defines the tiling schema and properties of the preprocessed raster datasets that will cover part or all of a mosaic dataset at varying resolutions.
     """
     inputs = locals()
     in_db = {'compression_quality': ['compression_quality', 'optional'], 'template_dataset': ['in_template_dataset', 'optional'], 'resampling_method': ['resampling_method', 'optional'], 'pixel_size': ['pixel_size', 'optional'], 'tile_rows': ['tile_rows', 'optional'], 'overview_factor': ['overview_factor', 'optional'], 'overview_image_folder': ['overview_image_folder', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'extent': ['extent', 'optional'], 'compression_method': ['compression_method', 'optional'], 'number_of_levels': ['number_of_levels', 'optional'], 'tile_cols': ['tile_cols', 'optional'], 'force_overview_tiles': ['force_overview_tiles', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DefineOverviews', inputs, in_db, out_db)


def generate_exclude_area(raster, pixel_type, generate_method, max_red=None, max_green=None, max_blue=None, max_white=None, max_black=None, max_magenta=None, max_cyan=None, max_yellow=None, percentage_low=None, percentage_high=None):
     """
     Geoprocessing tool that generates exclude areas to use within the Color Balance Mosaic Dataset tool.
     """
     inputs = locals()
     in_db = {'pixel_type': ['pixel_type', 'required'], 'max_magenta': ['max_magenta', 'optional'], 'max_blue': ['max_blue', 'optional'], 'max_green': ['max_green', 'optional'], 'percentage_high': ['percentage_high', 'optional'], 'max_red': ['max_red', 'optional'], 'max_cyan': ['max_cyan', 'optional'], 'generate_method': ['generate_method', 'required'], 'raster': ['in_raster', 'required'], 'max_white': ['max_white', 'optional'], 'max_yellow': ['max_yellow', 'optional'], 'max_black': ['max_black', 'optional'], 'percentage_low': ['percentage_low', 'optional']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'GenerateExcludeArea', inputs, in_db, out_db)


def import_mosaic_dataset_geometry(mosaic_dataset, target_featureclass_type, target_jofield, input_featureclass, input_jofield):
     """
     Geoprocessing tool that imports geometry to a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'target_featureclass_type': ['target_featureclass_type', 'required'], 'input_featureclass': ['input_featureclass', 'required'], 'target_jofield': ['target_join_field', 'required'], 'input_jofield': ['input_join_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportMosaicDatasetGeometry', inputs, in_db, out_db)


def remove_rasters_from_mosaic_dataset(mosaic_dataset, where_clause=None, update_boundary=None, mark_overviews_items=None, delete_overview_images=None, delete_item_cache=None, remove_items=None, update_cellsize_ranges=None):
     """
     Geoprocessing tool that removes rasters from a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'mark_overviews_items': ['mark_overviews_items', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'remove_items': ['remove_items', 'optional'], 'delete_overview_images': ['delete_overview_images', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'where_clause': ['where_clause', 'optional'], 'delete_item_cache': ['delete_item_cache', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RemoveRastersFromMosaicDataset', inputs, in_db, out_db)


def synchronize_mosaic_dataset(mosaic_dataset, where_clause=None, new_items=None, sync_only_stale=None, update_cellsize_ranges=None, update_boundary=None, update_overviews=None, build_pyramids=None, calculate_statistics=None, build_thumbnails=None, build_item_cache=None, rebuild_raster=None, update_fields=None, fields_to_update=None, existing_items=None, broken_items=None, skip_existing_items=None, refresh_aggregate_info=None, estimate_statistics=None):
     """
     Geoprocessing tool that rebuilds the raster item and updates affected fields in the mosaic dataset using the raster type and options that were used when it was originally added.
     """
     inputs = locals()
     in_db = {'estimate_statistics': ['estimate_statistics', 'optional'], 'fields_to_update': ['fields_to_update', 'optional'], 'refresh_aggregate_info': ['refresh_aggregate_info', 'optional'], 'existing_items': ['existing_items', 'optional'], 'build_thumbnails': ['build_thumbnails', 'optional'], 'build_pyramids': ['build_pyramids', 'optional'], 'update_boundary': ['update_boundary', 'optional'], 'rebuild_raster': ['rebuild_raster', 'optional'], 'new_items': ['new_items', 'optional'], 'calculate_statistics': ['calculate_statistics', 'optional'], 'update_overviews': ['update_overviews', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'broken_items': ['broken_items', 'optional'], 'update_fields': ['update_fields', 'optional'], 'update_cellsize_ranges': ['update_cellsize_ranges', 'optional'], 'where_clause': ['where_clause', 'optional'], 'sync_only_stale': ['sync_only_stale', 'optional'], 'build_item_cache': ['build_item_cache', 'optional'], 'skip_existing_items': ['skip_existing_items', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SynchronizeMosaicDataset', inputs, in_db, out_db)


def calculate_end_time(table, start_field, end_field, fields=None):
     """
     Geoprocessing tool that populates the values for a specified end time  field with values calculated using the specified start time field.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'end_field': ['end_field', 'required'], 'start_field': ['start_field', 'required'], 'fields': ['fields', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CalculateEndTime', inputs, in_db, out_db)


def convert_time_field(table, input_time_field, input_time_format, output_time_field, output_time_type=None, output_time_format=None):
     """
     Geoprocessing tool to convert timestamps stored in a text or numeric field to a date field.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'output_time_format': ['output_time_format', 'optional'], 'input_time_format': ['input_time_format', 'required'], 'output_time_type': ['output_time_type', 'optional'], 'input_time_field': ['input_time_field', 'required'], 'output_time_field': ['output_time_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeField', inputs, in_db, out_db)


def convert_time_zone(table, input_time_field, input_time_zone, output_time_field, output_time_zone, input_dst=None, output_dst=None):
     """
     Geoprocessing tool to convert time values from one time zone to another.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'input_time_zone': ['input_time_zone', 'required'], 'output_dst': ['output_dst', 'optional'], 'input_dst': ['input_dst', 'optional'], 'input_time_field': ['input_time_field', 'required'], 'output_time_zone': ['output_time_zone', 'required'], 'output_time_field': ['output_time_field', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConvertTimeZone', inputs, in_db, out_db)


def transpose_fields(table, field, transposed_field_name, value_field_name, attribute_fields=None):
     """
     Geoprocessing tool to transpose data values stored in columns  of a table or feature class into rows.
     """
     inputs = locals()
     in_db = {'field': ['in_field', 'required'], 'table': ['in_table', 'required'], 'value_field_name': ['in_value_field_name', 'required'], 'attribute_fields': ['attribute_fields', 'optional'], 'transposed_field_name': ['in_transposed_field_name', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'TransposeFields', inputs, in_db, out_db)


def add_global_ids(datasets):
     """
     Geoprocessing tool used to add global IDs to a list of geodatabase feature classes, tables, and/or feature datasets.
     """
     inputs = locals()
     in_db = {'datasets': ['in_datasets', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddGlobalIDs', inputs, in_db, out_db)


def warp_from_file(raster, link_file, transformation_type=None, resampling_type=None):
     """
     Geoprocessing tool that performs a transformation on the raster based on a link file, using a polynomial transformation.
     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'resampling_type': ['resampling_type', 'optional'], 'transformation_type': ['transformation_type', 'optional'], 'link_file': ['link_file', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'WarpFromFile', inputs, in_db, out_db)


def export_xml_workspace_document(data, export_type=None, storage_type=None, export_metadata=None):
     """
     Geoprocessing tool that creates a readable XML document of the geodatabase contents.
     """
     inputs = locals()
     in_db = {'export_type': ['export_type', 'optional'], 'storage_type': ['storage_type', 'optional'], 'data': ['in_data', 'required'], 'export_metadata': ['export_metadata', 'optional']}
     out_db = {'file': ['out_file', 'required']}
     return _execute_tool('management', 'ExportXMLWorkspaceDocument', inputs, in_db, out_db)


def import_xml_workspace_document(target_geodatabase, file, import_type=None, config_keyword=None):
     """
     Geoprocessing tool that imports the contents of an XML workspace document into an existing geodatabase.
     """
     inputs = locals()
     in_db = {'target_geodatabase': ['target_geodatabase', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'file': ['in_file', 'required'], 'import_type': ['import_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ImportXMLWorkspaceDocument', inputs, in_db, out_db)


def alter_mosaic_dataset_schema(mosaic_dataset, side_tables=None, raster_type_names=None, editor_tracking=None):
     """
     Geoprocessing tool to define the editing operations nonowners have when editing a mosaic dataset in an enterprise geodatabase.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'raster_type_names': ['raster_type_names', 'optional'], 'editor_tracking': ['editor_tracking', 'optional'], 'side_tables': ['side_tables', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterMosaicDatasetSchema', inputs, in_db, out_db)


def analyze_mosaic_dataset(mosaic_dataset, where_clause=None, checker_keywords=None):
     """
     Geoprocessing tool that checks a mosaic dataset for errors, and possible improvements.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'checker_keywords': ['checker_keywords', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AnalyzeMosaicDataset', inputs, in_db, out_db)


def compact(workspace):
     """
     Geoprocessing tool for compacting a geodatabase.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required']}
     out_db = {}
     return _execute_tool('management', 'Compact', inputs, in_db, out_db)


def clear_workspace_cache(data=None):
     """
     Geoprocessing tool clears any enterprise geodatabase workspaces from the enterprise geodatabase workspace cache.
     """
     inputs = locals()
     in_db = {'data': ['in_data', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ClearWorkspaceCache', inputs, in_db, out_db)


def analyze_datasets(input_database, include_system, datasets=None, analyze_base=None, analyze_delta=None, analyze_archive=None):
     """
     Geoprocessing tool to  update  database statistics of base tables, delta tables, and archive tables, along with the statistics on those tables' indexes.
     """
     inputs = locals()
     in_db = {'datasets': ['in_datasets', 'optional'], 'include_system': ['include_system', 'required'], 'analyze_base': ['analyze_base', 'optional'], 'analyze_delta': ['analyze_delta', 'optional'], 'analyze_archive': ['analyze_archive', 'optional'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'AnalyzeDatasets', inputs, in_db, out_db)


def rebuild_indexes(input_database, include_system, datasets=None, delta_only=None):
     """
     Geoprocessing tool to update indexes of datasets stored in a database or geodatabase in DB2, Oracle, PostgreSQL, or SQL Server. In geodatabases, indexes  can also be rebuilt on  states and state_lineage geodatabase system tables and the delta tables of versioned datasets.
     """
     inputs = locals()
     in_db = {'datasets': ['in_datasets', 'optional'], 'include_system': ['include_system', 'required'], 'input_database': ['input_database', 'required'], 'delta_only': ['delta_only', 'optional']}
     out_db = {}
     return _execute_tool('management', 'RebuildIndexes', inputs, in_db, out_db)


def check_geometry(features):
     """
     Geoprocessing tool to generate a report of geometry problems in a feature class.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'CheckGeometry', inputs, in_db, out_db)


def reconcile_versions(input_database, reconcile_mode, target_version=None, edit_versions=None, acquire_locks=None, abort_if_conflicts=None, conflict_definition=None, conflict_resolution=None, with_post=None, with_delete=None):
     """
     Geoprocessing tool that reconciles a version or multiple versions against a target version.
     """
     inputs = locals()
     in_db = {'conflict_definition': ['conflict_definition', 'optional'], 'with_post': ['with_post', 'optional'], 'acquire_locks': ['acquire_locks', 'optional'], 'conflict_resolution': ['conflict_resolution', 'optional'], 'reconcile_mode': ['reconcile_mode', 'required'], 'edit_versions': ['edit_versions', 'optional'], 'with_delete': ['with_delete', 'optional'], 'abort_if_conflicts': ['abort_if_conflicts', 'optional'], 'input_database': ['input_database', 'required'], 'target_version': ['target_version', 'optional']}
     out_db = {'log': ['out_log', 'optional']}
     return _execute_tool('management', 'ReconcileVersions', inputs, in_db, out_db)


def create_arcsde_connection_file(out_folder_path, out_name, server, service, database=None, account_authentication=None, username=None, password=None, save_username_password=None, version=None, save_version_info=None):
     """
     Geoprocessing tool that creates a database connection file for use in connecting to enterprise geodatabases using an ArcSDE service.
     """
     inputs = locals()
     in_db = {'server': ['server', 'required'], 'database': ['database', 'optional'], 'password': ['password', 'optional'], 'out_folder_path': ['out_folder_path', 'required'], 'save_version_info': ['save_version_info', 'optional'], 'out_name': ['out_name', 'required'], 'save_username_password': ['save_username_password', 'optional'], 'service': ['service', 'required'], 'account_authentication': ['account_authentication', 'optional'], 'version': ['version', 'optional'], 'username': ['username', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateArcSDEConnectionFile', inputs, in_db, out_db)


def add_edge_connectivity_rule_to_geometric_network(geometric_network, from_edge_feature_class, from_edge_subtype, to_edge_feature_class, to_edge_subtype, junction_subtypes, default_junction_subtype):
     """
     Geoprocessing tool to add an edge-edge connectivity rule to a geometric network.
     """
     inputs = locals()
     in_db = {'to_edge_feature_class': ['in_to_edge_feature_class', 'required'], 'from_edge_feature_class': ['in_from_edge_feature_class', 'required'], 'default_junction_subtype': ['default_junction_subtype', 'required'], 'geometric_network': ['in_geometric_network', 'required'], 'from_edge_subtype': ['from_edge_subtype', 'required'], 'junction_subtypes': ['in_junction_subtypes', 'required'], 'to_edge_subtype': ['to_edge_subtype', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddEdge-EdgeConnectivityRuleToGeometricNetwork', inputs, in_db, out_db)


def add_edge_junction_connectivity_rule_to_geometric_network(geometric_network, edge_feature_class, edge_subtype, junction_feature_class, junction_subtype, default_junction=None, edge_min=None, edge_max=None, junction_min=None, junction_max=None):
     """
     Geoprocessing tool to add an edge_junction connectivity rule to a geometric network.
     """
     inputs = locals()
     in_db = {'edge_max': ['edge_max', 'optional'], 'edge_feature_class': ['in_edge_feature_class', 'required'], 'junction_min': ['junction_min', 'optional'], 'edge_subtype': ['edge_subtype', 'required'], 'junction_max': ['junction_max', 'optional'], 'junction_subtype': ['junction_subtype', 'required'], 'geometric_network': ['in_geometric_network', 'required'], 'junction_feature_class': ['in_junction_feature_class', 'required'], 'edge_min': ['edge_min', 'optional'], 'default_junction': ['default_junction', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddEdge_JunctionConnectivityRuleToGeometricNetwork', inputs, in_db, out_db)


def create_geometric_network(feature_dataset, out_name, source_feature_classes, snap_tolerance=None, weights=None, weight_associations=None, z_snap_tolerance=None, preserve_enabled_values=None):
     """
     Geoprocessing tool to create a geometric network.
     """
     inputs = locals()
     in_db = {'preserve_enabled_values': ['preserve_enabled_values', 'optional'], 'source_feature_classes': ['in_source_feature_classes', 'required'], 'snap_tolerance': ['snap_tolerance', 'optional'], 'feature_dataset': ['in_feature_dataset', 'required'], 'weights': ['weights', 'optional'], 'weight_associations': ['weight_associations', 'optional'], 'out_name': ['out_name', 'required'], 'z_snap_tolerance': ['z_snap_tolerance', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateGeometricNetwork', inputs, in_db, out_db)


def remove_connectivity_rule_from_geometric_network(geometric_network, connectivity_rules):
     """
     Geoprocessing tool to remove a connectivity rule from a geometric network.
     """
     inputs = locals()
     in_db = {'connectivity_rules': ['in_connectivity_rules', 'required'], 'geometric_network': ['in_geometric_network', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveConnectivityRuleFromGeometricNetwork', inputs, in_db, out_db)


def remove_empty_feature_class_from_geometric_network(geometric_network, feature_class):
     """
     Geoprocessing tool to remove an empty feature class from a geometric network.
     """
     inputs = locals()
     in_db = {'geometric_network': ['in_geometric_network', 'required'], 'feature_class': ['in_feature_class', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveEmptyFeatureClassFromGeometricNetwork', inputs, in_db, out_db)


def trace_geometric_network(geometric_network, flags, trace_task_type, barriers=None, junction_weight=None, edge_along_digitized_weight=None, edge_against_digitized_weight=None, disable_from_trace=None, trace_ends=None, trace_indeterminate_flow=None, junction_weight_filter=None, junction_weight_range=None, junction_weight_range_not=None, edge_along_digitized_weight_filter=None, edge_against_digitized_weight_filter=None, edge_weight_range=None, edge_weight_range_not=None):
     """
     Geoprocessing tool to trace a geometric network.
     """
     inputs = locals()
     in_db = {'flags': ['in_flags', 'required'], 'junction_weight_filter': ['in_junction_weight_filter', 'optional'], 'barriers': ['in_barriers', 'optional'], 'junction_weight_range_not': ['in_junction_weight_range_not', 'optional'], 'trace_ends': ['in_trace_ends', 'optional'], 'edge_along_digitized_weight': ['in_edge_along_digitized_weight', 'optional'], 'disable_from_trace': ['in_disable_from_trace', 'optional'], 'trace_indeterminate_flow': ['in_trace_indeterminate_flow', 'optional'], 'junction_weight': ['in_junction_weight', 'optional'], 'edge_against_digitized_weight_filter': ['in_edge_against_digitized_weight_filter', 'optional'], 'edge_along_digitized_weight_filter': ['in_edge_along_digitized_weight_filter', 'optional'], 'edge_weight_range_not': ['in_edge_weight_range_not', 'optional'], 'edge_weight_range': ['in_edge_weight_range', 'optional'], 'geometric_network': ['in_geometric_network', 'required'], 'edge_against_digitized_weight': ['in_edge_against_digitized_weight', 'optional'], 'junction_weight_range': ['in_junction_weight_range', 'optional'], 'trace_task_type': ['in_trace_task_type', 'required']}
     out_db = {'network_layer': ['out_network_layer', 'required']}
     return _execute_tool('management', 'TraceGeometricNetwork', inputs, in_db, out_db)


def add_attachments(dataset, jofield, match_table, match_jofield, match_path_field, working_folder=None):
     """
     Geoprocessing tool that adds file attachments to the records of a geodatabase feature class or table.
     """
     inputs = locals()
     in_db = {'match_path_field': ['in_match_path_field', 'required'], 'match_jofield': ['in_match_join_field', 'required'], 'match_table': ['in_match_table', 'required'], 'jofield': ['in_join_field', 'required'], 'dataset': ['in_dataset', 'required'], 'working_folder': ['in_working_folder', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddAttachments', inputs, in_db, out_db)


def disable_attachments(dataset):
     """
     Geoprocessing tool that disables attachments on a geodatabase feature class or table.
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'DisableAttachments', inputs, in_db, out_db)


def enable_attachments(dataset):
     """
     Geoprocessing tool that enables attachments on a geodatabase feature class or table.
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'EnableAttachments', inputs, in_db, out_db)


def remove_attachments(dataset, jofield, match_table, match_jofield, match_name_field=None):
     """
     Geoprocessing tool that removes attachments from geodatabase feature class or table records.
     """
     inputs = locals()
     in_db = {'match_jofield': ['in_match_join_field', 'required'], 'match_name_field': ['in_match_name_field', 'optional'], 'jofield': ['in_join_field', 'required'], 'dataset': ['in_dataset', 'required'], 'match_table': ['in_match_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveAttachments', inputs, in_db, out_db)


def set_mosaic_dataset_properties(mosaic_dataset, rows_maximum_imagesize=None, columns_maximum_imagesize=None, allowed_compressions=None, default_compression_type=None, jpeg_quality=None, lerc_tolerance=None, resampling_type=None, clip_to_footprints=None, footprints_may_contanodata=None, clip_to_boundary=None, color_correction=None, allowed_mensuration_capabilities=None, default_mensuration_capabilities=None, allowed_mosaic_methods=None, default_mosaic_method=None, order_field=None, order_base=None, sorting_order=None, mosaic_operator=None, blend_width=None, view_point_x=None, view_point_y=None, max_num_per_mosaic=None, cell_size_tolerance=None, cell_size=None, metadata_level=None, transmission_fields=None, use_time=None, start_time_field=None, end_time_field=None, time_format=None, geographic_transform=None, max_num_of_download_items=None, max_num_of_records_returned=None, data_source_type=None, minimum_pixel_contribution=None, processing_templates=None, default_processing_template=None, time_interval=None, time_interval_units=None):
     """
     Geoprocessing tool that sets the default properties of a mosaic dataset.
     """
     inputs = locals()
     in_db = {'resampling_type': ['resampling_type', 'optional'], 'time_interval_units': ['time_interval_units', 'optional'], 'rows_maximum_imagesize': ['rows_maximum_imagesize', 'optional'], 'max_num_per_mosaic': ['max_num_per_mosaic', 'optional'], 'mosaic_operator': ['mosaic_operator', 'optional'], 'data_source_type': ['data_source_type', 'optional'], 'max_num_of_download_items': ['max_num_of_download_items', 'optional'], 'default_mensuration_capabilities': ['default_mensuration_capabilities', 'optional'], 'lerc_tolerance': ['LERC_Tolerance', 'optional'], 'max_num_of_records_returned': ['max_num_of_records_returned', 'optional'], 'color_correction': ['color_correction', 'optional'], 'cell_size_tolerance': ['cell_size_tolerance', 'optional'], 'end_time_field': ['end_time_field', 'optional'], 'order_base': ['order_base', 'optional'], 'jpeg_quality': ['JPEG_quality', 'optional'], 'default_processing_template': ['default_processing_template', 'optional'], 'allowed_mosaic_methods': ['allowed_mosaic_methods', 'optional'], 'use_time': ['use_time', 'optional'], 'metadata_level': ['metadata_level', 'optional'], 'view_point_y': ['view_point_y', 'optional'], 'view_point_x': ['view_point_x', 'optional'], 'cell_size': ['cell_size', 'optional'], 'blend_width': ['blend_width', 'optional'], 'clip_to_footprints': ['clip_to_footprints', 'optional'], 'clip_to_boundary': ['clip_to_boundary', 'optional'], 'order_field': ['order_field', 'optional'], 'geographic_transform': ['geographic_transform', 'optional'], 'default_compression_type': ['default_compression_type', 'optional'], 'processing_templates': ['processing_templates', 'optional'], 'default_mosaic_method': ['default_mosaic_method', 'optional'], 'transmission_fields': ['transmission_fields', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'allowed_compressions': ['allowed_compressions', 'optional'], 'footprints_may_contanodata': ['footprints_may_contain_nodata', 'optional'], 'allowed_mensuration_capabilities': ['allowed_mensuration_capabilities', 'optional'], 'time_interval': ['time_interval', 'optional'], 'columns_maximum_imagesize': ['columns_maximum_imagesize', 'optional'], 'minimum_pixel_contribution': ['minimum_pixel_contribution', 'optional'], 'start_time_field': ['start_time_field', 'optional'], 'time_format': ['time_format', 'optional'], 'sorting_order': ['sorting_order', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetMosaicDatasetProperties', inputs, in_db, out_db)


def set_raster_properties(raster, data_type=None, statistics=None, stats_file=None, nodata=None, key_properties=None):
     """
     Geoprocessing tool that sets properties on a raster dataset or mosaic dataset.
     """
     inputs = locals()
     in_db = {'key_properties': ['key_properties', 'optional'], 'nodata': ['nodata', 'optional'], 'raster': ['in_raster', 'required'], 'stats_file': ['stats_file', 'optional'], 'statistics': ['statistics', 'optional'], 'data_type': ['data_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SetRasterProperties', inputs, in_db, out_db)


def make_las_dataset_layer(las_dataset, class_code=None, return_values=None, no_flag=None, synthetic=None, keypoint=None, withheld=None, surface_constraints=None):
     """
     Geoprocessing tool for creating a LAS dataset layer that can apply filters to LAS points and control the enforcement of surface constraint features.
     """
     inputs = locals()
     in_db = {'return_values': ['return_values', 'optional'], 'surface_constraints': ['surface_constraints', 'optional'], 'las_dataset': ['in_las_dataset', 'required'], 'keypoint': ['keypoint', 'optional'], 'withheld': ['withheld', 'optional'], 'class_code': ['class_code', 'optional'], 'synthetic': ['synthetic', 'optional'], 'no_flag': ['no_flag', 'optional']}
     out_db = {'layer': ['out_layer', 'required']}
     return _execute_tool('management', 'MakeLASDatasetLayer', inputs, in_db, out_db)


def download_rasters(image_service, out_folder, where_clause=None, selection_feature=None, clipping=None, convert_rasters=None, format=None, compression_method=None, compression_quality=None, maintain_folder=None):
     """
     Geoprocessing tool that downloads source files of the selected rasters from an image service to a designated location.
     """
     inputs = locals()
     in_db = {'format': ['format', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'out_folder': ['out_folder', 'required'], 'selection_feature': ['selection_feature', 'optional'], 'convert_rasters': ['convert_rasters', 'optional'], 'where_clause': ['where_clause', 'optional'], 'clipping': ['clipping', 'optional'], 'maintain_folder': ['MAINTAIN_FOLDER', 'optional'], 'compression_method': ['compression_method', 'optional'], 'image_service': ['in_image_service', 'required']}
     out_db = {}
     return _execute_tool('management', 'DownloadRasters', inputs, in_db, out_db)


def create_enterprise_geodatabase(database_platform, instance_name, authorization_file, database_name=None, account_authentication=None, database_admin=None, database_admpassword=None, sde_schema=None, gdb_admname=None, gdb_admpassword=None, tablespace_name=None):
     """
     Geoprocessing tool that creates a database, geodatabase, and geodatabase administrator user in a Microsoft SQL Server  or PostgreSQL DBMS and creates a geodatabase, tablespace, and geodatabase administrator user in an Oracle DBMS.
     """
     inputs = locals()
     in_db = {'authorization_file': ['authorization_file', 'required'], 'gdb_admname': ['gdb_admin_name', 'optional'], 'database_name': ['database_name', 'optional'], 'sde_schema': ['sde_schema', 'optional'], 'database_admin': ['database_admin', 'optional'], 'instance_name': ['instance_name', 'required'], 'tablespace_name': ['tablespace_name', 'optional'], 'database_platform': ['database_platform', 'required'], 'gdb_admpassword': ['gdb_admin_password', 'optional'], 'account_authentication': ['account_authentication', 'optional'], 'database_admpassword': ['database_admin_password', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateEnterpriseGeodatabase', inputs, in_db, out_db)


def enable_enterprise_geodatabase(input_database, authorization_file):
     """
     Geoprocessing tool that creates geodatabase system tables, stored procedures, functions, and types in an existing database.
     """
     inputs = locals()
     in_db = {'authorization_file': ['authorization_file', 'required'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'EnableEnterpriseGeodatabase', inputs, in_db, out_db)


def feature_envelope_to_polygon(features, single_envelope=None):
     """
     Geoprocessing tool that creates polygon features representing the envelopes of input features.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'single_envelope': ['single_envelope', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'FeatureEnvelopeToPolygon', inputs, in_db, out_db)


def make_query_layer(input_database, out_layer_name, query, oid_fields=None, shape_type=None, srid=None, spatial_reference=None):
     """
     Geoprocessing tool for creating a Query Layer from a DBMS table based on an input SQL select statement.
     """
     inputs = locals()
     in_db = {'out_layer_name': ['out_layer_name', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'input_database': ['input_database', 'required'], 'shape_type': ['shape_type', 'optional'], 'oid_fields': ['oid_fields', 'optional'], 'query': ['query', 'required'], 'srid': ['srid', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MakeQueryLayer', inputs, in_db, out_db)


def set_flow_direction(geometric_network, flow_option):
     """
     Geoprocessing tool to set flow direction for a geometric network.
     """
     inputs = locals()
     in_db = {'geometric_network': ['in_geometric_network', 'required'], 'flow_option': ['flow_option', 'required']}
     out_db = {}
     return _execute_tool('management', 'SetFlowDirection', inputs, in_db, out_db)


def create_database_connection(out_folder_path, out_name, database_platform, instance, account_authentication=None, username=None, password=None, save_user_pass=None, database=None, schema=None, version_type=None, version=None, date=None):
     """
     Geoprocessing tool for creating connection files to databases or enterprise, workgroup, or desktop geodatabases.
     """
     inputs = locals()
     in_db = {'database': ['database', 'optional'], 'date': ['date', 'optional'], 'password': ['password', 'optional'], 'instance': ['instance', 'required'], 'save_user_pass': ['save_user_pass', 'optional'], 'username': ['username', 'optional'], 'version': ['version', 'optional'], 'version_type': ['version_type', 'optional'], 'out_folder_path': ['out_folder_path', 'required'], 'out_name': ['out_name', 'required'], 'schema': ['schema', 'optional'], 'database_platform': ['database_platform', 'required'], 'account_authentication': ['account_authentication', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseConnection', inputs, in_db, out_db)


def delete_mosaic_dataset(mosaic_dataset, delete_overview_images=None, delete_item_cache=None):
     """
     Geoprocessing tool that deletes a mosaic dataset, overviews, and item cache.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'delete_item_cache': ['delete_item_cache', 'optional'], 'delete_overview_images': ['delete_overview_images', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DeleteMosaicDataset', inputs, in_db, out_db)


def create_spatial_type(input_database, sde_user_password, tablespace_name=None, st_shape_library_path=None):
     """
     Geoprocessing tool that adds the ST_Geometry SQL type to an Oracle or PostgreSQL database and creates its functions and subtypes.
     """
     inputs = locals()
     in_db = {'tablespace_name': ['tablespace_name', 'optional'], 'st_shape_library_path': ['st_shape_library_path', 'optional'], 'input_database': ['input_database', 'required'], 'sde_user_password': ['sde_user_password', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateSpatialType', inputs, in_db, out_db)


def generate_attachment_match_table(dataset, folder, key_field, file_filter=None, use_relative_paths=None):
     """
     Geoprocessing tool that creates a Match Table to be used with the Add Attachments and Remove Attachment tools.
     """
     inputs = locals()
     in_db = {'key_field': ['in_key_field', 'required'], 'file_filter': ['in_file_filter', 'optional'], 'dataset': ['in_dataset', 'required'], 'folder': ['in_folder', 'required'], 'use_relative_paths': ['in_use_relative_paths', 'optional']}
     out_db = {'match_table': ['out_match_table', 'required']}
     return _execute_tool('management', 'GenerateAttachmentMatchTable', inputs, in_db, out_db)


def consolidate_locator(locator, copy_arcsde_locator=None):
     """
     Geoprocessing tool to consolidate a locator or composite locator  by copying all locator files into a single folder.
     """
     inputs = locals()
     in_db = {'locator': ['in_locator', 'required'], 'copy_arcsde_locator': ['copy_arcsde_locator', 'optional']}
     out_db = {'output_folder': ['output_folder', 'required']}
     return _execute_tool('management', 'ConsolidateLocator', inputs, in_db, out_db)


def package_locator(locator, copy_arcsde_locator=None, additional_files=None, summary=None, tags=None):
     """
     Geoprocessing tool to package a locator or composite locator and create a single compressed .gcpk file.
     """
     inputs = locals()
     in_db = {'locator': ['in_locator', 'required'], 'tags': ['tags', 'optional'], 'additional_files': ['additional_files', 'optional'], 'copy_arcsde_locator': ['copy_arcsde_locator', 'optional'], 'summary': ['summary', 'optional']}
     out_db = {'output_file': ['output_file', 'required']}
     return _execute_tool('management', 'PackageLocator', inputs, in_db, out_db)


def create_database_view(input_database, view_name, view_definition):
     """
     Geoprocessing tool for creating a view in a database or enterprise geodatabase based on an SQL expression.
     """
     inputs = locals()
     in_db = {'view_definition': ['view_definition', 'required'], 'view_name': ['view_name', 'required'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseView', inputs, in_db, out_db)


def sort_coded_value_domain(workspace, domaname, sort_by, sort_order):
     """
     Geoprocessing tool that sorts the code or description of a coded value domain in either ascending or descending order.
     """
     inputs = locals()
     in_db = {'workspace': ['in_workspace', 'required'], 'sort_by': ['sort_by', 'required'], 'domaname': ['domain_name', 'required'], 'sort_order': ['sort_order', 'required']}
     out_db = {}
     return _execute_tool('management', 'SortCodedValueDomain', inputs, in_db, out_db)


def disable_editor_tracking(dataset, creator=None, creation_date=None, last_editor=None, last_edit_date=None):
     """
     Geoprocessing tool to disable editor tracking on a feature class, table, mosaic dataset, or raster catalog.
     """
     inputs = locals()
     in_db = {'creator': ['creator', 'optional'], 'creation_date': ['creation_date', 'optional'], 'dataset': ['in_dataset', 'required'], 'last_edit_date': ['last_edit_date', 'optional'], 'last_editor': ['last_editor', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DisableEditorTracking', inputs, in_db, out_db)


def enable_editor_tracking(dataset, creator_field=None, creation_date_field=None, last_editor_field=None, last_edit_date_field=None, add_fields=None, record_dates_in=None):
     """
     Geoprocessing tool to enable  editor tracking for a feature class, table, mosaic dataset, or raster catalog.
     """
     inputs = locals()
     in_db = {'last_editor_field': ['last_editor_field', 'optional'], 'creator_field': ['creator_field', 'optional'], 'add_fields': ['add_fields', 'optional'], 'record_dates_in': ['record_dates_in', 'optional'], 'creation_date_field': ['creation_date_field', 'optional'], 'dataset': ['in_dataset', 'required'], 'last_edit_date_field': ['last_edit_date_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'EnableEditorTracking', inputs, in_db, out_db)


def truncate_table(table):
     """
     Geoprocessing tool for truncating a table or feature class.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required']}
     out_db = {}
     return _execute_tool('management', 'TruncateTable', inputs, in_db, out_db)


def consolidate_result(result, convert_data=None, convert_arcsde_data=None, extent=None, apply_extent_to_arcsde=None, schema_only=None):
     """
     Geoprocessing tool that consolidates a geoprocessing result into a single folder.
     """
     inputs = locals()
     in_db = {'convert_arcsde_data': ['convert_arcsde_data', 'optional'], 'extent': ['extent', 'optional'], 'apply_extent_to_arcsde': ['apply_extent_to_arcsde', 'optional'], 'convert_data': ['convert_data', 'optional'], 'schema_only': ['schema_only', 'optional'], 'result': ['in_result', 'required']}
     out_db = {'output_folder': ['output_folder', 'required']}
     return _execute_tool('management', 'ConsolidateResult', inputs, in_db, out_db)


def package_result(result, convert_data=None, convert_arcsde_data=None, extent=None, apply_extent_to_arcsde=None, schema_only=None, arcgisruntime=None, additional_files=None, summary=None, tags=None, version=None):
     """
     Geoprocessing tool that creates a geoprocessing package from a result or result file.
     """
     inputs = locals()
     in_db = {'version': ['version', 'optional'], 'convert_arcsde_data': ['convert_arcsde_data', 'optional'], 'tags': ['tags', 'optional'], 'extent': ['extent', 'optional'], 'summary': ['summary', 'optional'], 'arcgisruntime': ['arcgisruntime', 'optional'], 'apply_extent_to_arcsde': ['apply_extent_to_arcsde', 'optional'], 'additional_files': ['additional_files', 'optional'], 'convert_data': ['convert_data', 'optional'], 'schema_only': ['schema_only', 'optional'], 'result': ['in_result', 'required']}
     out_db = {'output_file': ['output_file', 'required']}
     return _execute_tool('management', 'PackageResult', inputs, in_db, out_db)


def upgrade_dataset(dataset):
     """
     Geoprocessing tool that will upgrade mosaic datasets, network datasets, and parcel fabrics to the current ArcGIS release.
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'UpgradeDataset', inputs, in_db, out_db)


def add_files_to_las_dataset(las_dataset, files=None, folder_recursion=None, surface_constraints=None):
     """
     Geoprocessing tool that adds one or more LAS files and surface constraint features to a LAS dataset.
     """
     inputs = locals()
     in_db = {'surface_constraints': ['in_surface_constraints', 'optional'], 'folder_recursion': ['folder_recursion', 'optional'], 'files': ['in_files', 'optional'], 'las_dataset': ['in_las_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddFilestoLASDataset', inputs, in_db, out_db)


def create_las_dataset(input, folder_recursion=None, surface_constraints=None, spatial_reference=None, compute_stats=None, relative_paths=None, create_las_prj=None):
     """
     Geoprocessing tool that creates a LAS dataset referencing one or more LAS files and optional surface constraint features.
     """
     inputs = locals()
     in_db = {'create_las_prj': ['create_las_prj', 'optional'], 'input': ['input', 'required'], 'spatial_reference': ['spatial_reference', 'optional'], 'surface_constraints': ['in_surface_constraints', 'optional'], 'relative_paths': ['relative_paths', 'optional'], 'folder_recursion': ['folder_recursion', 'optional'], 'compute_stats': ['compute_stats', 'optional']}
     out_db = {'las_dataset': ['out_las_dataset', 'required']}
     return _execute_tool('management', 'CreateLASDataset', inputs, in_db, out_db)


def las_dataset_statistics(las_dataset, calculation_type=None, summary_level=None, delimiter=None, decimal_separator=None):
     """
     Geoprocessing tool that calculates or updates statistics for a LAS dataset.
     """
     inputs = locals()
     in_db = {'summary_level': ['summary_level', 'optional'], 'decimal_separator': ['decimal_separator', 'optional'], 'calculation_type': ['calculation_type', 'optional'], 'las_dataset': ['in_las_dataset', 'required'], 'delimiter': ['delimiter', 'optional']}
     out_db = {'file': ['out_file', 'optional']}
     return _execute_tool('management', 'LASDatasetStatistics', inputs, in_db, out_db)


def las_point_statistics_as_raster(las_dataset, method=None, sampling_type=None, sampling_value=None):
     """
     Geoprocessing tool that creates a raster storing statistical information about measurements from LAS files referenced by a LAS dataset.
     """
     inputs = locals()
     in_db = {'method': ['method', 'optional'], 'sampling_type': ['sampling_type', 'optional'], 'las_dataset': ['in_las_dataset', 'required'], 'sampling_value': ['sampling_value', 'optional']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'LASPointStatisticsasRaster', inputs, in_db, out_db)


def remove_files_from_las_dataset(las_dataset, files=None, surface_constraints=None):
     """
     Geoprocessing tool that removes selected lidar files and surface constraints referenced by a LAS dataset.
     """
     inputs = locals()
     in_db = {'surface_constraints': ['in_surface_constraints', 'optional'], 'files': ['in_files', 'optional'], 'las_dataset': ['in_las_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveFilesfromLASDataset', inputs, in_db, out_db)


def export_mosaic_dataset_paths(mosaic_dataset, where_clause=None, export_mode=None, types_of_paths=None):
     """
     Geoprocessing tool that creates a table listing the paths to the mosaic dataset items.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'types_of_paths': ['types_of_paths', 'optional'], 'export_mode': ['export_mode', 'optional']}
     out_db = {'table': ['out_table', 'required']}
     return _execute_tool('management', 'ExportMosaicDatasetPaths', inputs, in_db, out_db)


def repair_mosaic_dataset_paths(mosaic_dataset, paths_list, where_clause=None):
     """
     Geoprocessing tool that repairs broken file paths within a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'paths_list': ['paths_list', 'required']}
     out_db = {}
     return _execute_tool('management', 'RepairMosaicDatasetPaths', inputs, in_db, out_db)


def create_database_user(input_database, user_name, user_authentication_type=None, user_password=None, role=None, tablespace_name=None):
     """
     Geoprocessing tool to create a database user in an Oracle, PostgreSQL, or Microsoft SQL Server database.
     """
     inputs = locals()
     in_db = {'user_name': ['user_name', 'required'], 'input_database': ['input_database', 'required'], 'role': ['role', 'optional'], 'user_authentication_type': ['user_authentication_type', 'optional'], 'tablespace_name': ['tablespace_name', 'optional'], 'user_password': ['user_password', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateDatabaseUser', inputs, in_db, out_db)


def join_field(data, field, jotable, jofield, fields=None):
     """
     Geoprocessing tool that permanently joins the contents of a table to another table based on a common attribute field.
     """
     inputs = locals()
     in_db = {'field': ['in_field', 'required'], 'data': ['in_data', 'required'], 'jofield': ['join_field', 'required'], 'jotable': ['join_table', 'required'], 'fields': ['fields', 'optional']}
     out_db = {}
     return _execute_tool('management', 'JoinField', inputs, in_db, out_db)


def edit_raster_function(mosaic_dataset, edit_mosaic_dataset_item=None, edit_options=None, function_chadefinition=None, location_function_name=None):
     """
     Geoprocessing tool that adds, replaces, or removes a raster function template in a mosaic dataset, items in a mosaic dataset, or a raster layer that contains a raster function.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'edit_options': ['edit_options', 'optional'], 'location_function_name': ['location_function_name', 'optional'], 'edit_mosaic_dataset_item': ['edit_mosaic_dataset_item', 'optional'], 'function_chadefinition': ['function_chain_definition', 'optional']}
     out_db = {}
     return _execute_tool('management', 'EditRasterFunction', inputs, in_db, out_db)


def build_mosaic_dataset_item_cache(mosaic_dataset, where_clause=None, define_cache=None, generate_cache=None, item_cache_folder=None, compression_method=None, compression_quality=None, max_allowed_rows=None, max_allowed_columns=None, request_size_type=None, request_size=None):
     """
     Geoprocessing tool that inserts the Cached Raster function into the function chain for items within a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'request_size': ['request_size', 'optional'], 'compression_quality': ['compression_quality', 'optional'], 'compression_method': ['compression_method', 'optional'], 'request_size_type': ['request_size_type', 'optional'], 'where_clause': ['where_clause', 'optional'], 'item_cache_folder': ['item_cache_folder', 'optional'], 'define_cache': ['define_cache', 'optional'], 'max_allowed_columns': ['max_allowed_columns', 'optional'], 'generate_cache': ['generate_cache', 'optional'], 'max_allowed_rows': ['max_allowed_rows', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildMosaicDatasetItemCache', inputs, in_db, out_db)


def create_unregistered_feature_class(out_path, out_name, geometry_type=None, template=None, has_m=None, has_z=None, spatial_reference=None, config_keyword=None):
     """
     Geoprocessing tool that creates an empty, unregistered feature class in an enterprise database.
     """
     inputs = locals()
     in_db = {'geometry_type': ['geometry_type', 'optional'], 'spatial_reference': ['spatial_reference', 'optional'], 'has_m': ['has_m', 'optional'], 'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'has_z': ['has_z', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateUnregisteredFeatureClass', inputs, in_db, out_db)


def create_unregistered_table(out_path, out_name, template=None, config_keyword=None):
     """
     Geoprocessing tool that creates an empty table in a database or enterprise geodatabase. The table is not registered with the geodatabase.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'config_keyword': ['config_keyword', 'optional'], 'template': ['template', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateUnregisteredTable', inputs, in_db, out_db)


def batch_build_pyramids(input_raster_datasets, pyramid_levels=None, skip_first_level=None, pyramid_resampling_technique=None, pyramid_compression_type=None, compression_quality=None, skip_existing=None):
     """

     """
     inputs = locals()
     in_db = {'pyramid_compression_type': ['Pyramid_compression_type', 'optional'], 'pyramid_levels': ['Pyramid_levels', 'optional'], 'skip_existing': ['Skip_Existing', 'optional'], 'compression_quality': ['Compression_quality', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required'], 'pyramid_resampling_technique': ['Pyramid_resampling_technique', 'optional'], 'skip_first_level': ['Skip_first_level', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchBuildPyramids', inputs, in_db, out_db)


def batch_calculate_statistics(input_raster_datasets, number_of_columns_to_skip=None, number_of_rows_to_skip=None, ignore_values=None, skip_existing=None):
     """

     """
     inputs = locals()
     in_db = {'number_of_columns_to_skip': ['Number_of_columns_to_skip', 'optional'], 'input_raster_datasets': ['Input_Raster_Datasets', 'required'], 'ignore_values': ['Ignore_values', 'optional'], 'number_of_rows_to_skip': ['Number_of_rows_to_skip', 'optional'], 'skip_existing': ['Skip_Existing', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BatchCalculateStatistics', inputs, in_db, out_db)


def recover_file_geodatabase(input_file_gdb, output_location, out_name):
     """
     Geoprocessing tool to recover data from a corrupt file geodatabase.
     """
     inputs = locals()
     in_db = {'out_name': ['out_name', 'required'], 'input_file_gdb': ['input_file_gdb', 'required'], 'output_location': ['output_location', 'required']}
     out_db = {}
     return _execute_tool('management', 'RecoverFileGeodatabase', inputs, in_db, out_db)


def sort(dataset, sort_field, spatial_sort_method=None):
     """
     Geoprocessing tool that reorders records in a feature class or table based on field values.
     """
     inputs = locals()
     in_db = {'spatial_sort_method': ['spatial_sort_method', 'optional'], 'dataset': ['in_dataset', 'required'], 'sort_field': ['sort_field', 'required']}
     out_db = {'dataset': ['out_dataset', 'required']}
     return _execute_tool('management', 'Sort', inputs, in_db, out_db)


def create_map_tile_package(map, service_type, format_type, level_of_detail, service_file=None, summary=None, tags=None, extent=None):
     """
     Geoprocessing tool that generates tiles from a map and packages the tiles to create a single compressed .tpk file.
     """
     inputs = locals()
     in_db = {'service_file': ['service_file', 'optional'], 'tags': ['tags', 'optional'], 'level_of_detail': ['level_of_detail', 'required'], 'format_type': ['format_type', 'required'], 'service_type': ['service_type', 'required'], 'extent': ['extent', 'optional'], 'map': ['in_map', 'required'], 'summary': ['summary', 'optional']}
     out_db = {'output_file': ['output_file', 'required']}
     return _execute_tool('management', 'CreateMapTilePackage', inputs, in_db, out_db)


def match_photos_to_rows_by_time(input_folder, input_table, time_field, add_photos_as_attachments=None, time_tolerance=None, clock_offset=None):
     """

     """
     inputs = locals()
     in_db = {'input_folder': ['Input_Folder', 'required'], 'clock_offset': ['Clock_Offset', 'optional'], 'time_tolerance': ['Time_Tolerance', 'optional'], 'add_photos_as_attachments': ['Add_Photos_As_Attachments', 'optional'], 'input_table': ['Input_Table', 'required'], 'time_field': ['Time_Field', 'required']}
     out_db = {'unmatched_photos_table': ['Unmatched_Photos_Table', 'optional'], 'output_table': ['Output_Table', 'required']}
     return _execute_tool('management', 'MatchPhotosToRowsByTime', inputs, in_db, out_db)


def geotagged_photos_to_points(input_folder, include_non_geotagged_photos=None, add_photos_as_attachments=None):
     """

     """
     inputs = locals()
     in_db = {'input_folder': ['Input_Folder', 'required'], 'include_non-geotagged_photos': ['Include_Non-GeoTagged_Photos', 'optional'], 'add_photos_as_attachments': ['Add_Photos_As_Attachments', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required'], 'invalid_photos_table': ['Invalid_Photos_Table', 'optional']}
     return _execute_tool('management', 'GeoTaggedPhotosToPoints', inputs, in_db, out_db)


def register_raster(raster, register_mode, reference_raster=None, input_link_file=None, transformation_type=None, maximum_rms_value=None):
     """
     Geoprocessing tool that registers an image to a reference image.
     """
     inputs = locals()
     in_db = {'transformation_type': ['transformation_type', 'optional'], 'maximum_rms_value': ['maximum_rms_value', 'optional'], 'input_link_file': ['input_link_file', 'optional'], 'raster': ['in_raster', 'required'], 'reference_raster': ['reference_raster', 'optional'], 'register_mode': ['register_mode', 'required']}
     out_db = {'output_cpt_link_file': ['output_cpt_link_file', 'optional']}
     return _execute_tool('management', 'RegisterRaster', inputs, in_db, out_db)


def add_incrementing_id_field(table, field_name=None):
     """
     Geoprocessing tool that adds a database-maintained, incrementing ID field to a database table.
     """
     inputs = locals()
     in_db = {'table': ['in_table', 'required'], 'field_name': ['field_name', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AddIncrementingIDField', inputs, in_db, out_db)


def create_role(input_database, role, grant_revoke=None, user_name=None):
     """
     Geoprocessing tool to create a database role in an Oracle, PostgreSQL, or Microsoft SQL Server database and add users to or remove them from the role.
     """
     inputs = locals()
     in_db = {'role': ['role', 'required'], 'grant_revoke': ['grant_revoke', 'optional'], 'user_name': ['user_name', 'optional'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateRole', inputs, in_db, out_db)


def export_tile_cache(cache_source, target_cache_folder, target_cache_name, export_cache_type=None, storage_format_type=None, scales=None, area_of_interest=None):
     """
     Geoprocessing tool that exports tiles from an existing tile cache.
     """
     inputs = locals()
     in_db = {'area_of_interest': ['area_of_interest', 'optional'], 'cache_source': ['in_cache_source', 'required'], 'storage_format_type': ['storage_format_type', 'optional'], 'target_cache_name': ['in_target_cache_name', 'required'], 'export_cache_type': ['export_cache_type', 'optional'], 'scales': ['scales', 'optional'], 'target_cache_folder': ['in_target_cache_folder', 'required']}
     out_db = {}
     return _execute_tool('management', 'ExportTileCache', inputs, in_db, out_db)


def generate_tile_cache_tiling_scheme(dataset, tiling_scheme_generation_method, number_of_scales, predefined_tiling_scheme=None, scales=None, scales_type=None, tile_origin=None, dpi=None, tile_size=None, tile_format=None, tile_compression_quality=None, storage_format=None, lerc_error=None):
     """
     Geoprocessing tool that generates an XML tiling scheme file used to create tile cache.
     """
     inputs = locals()
     in_db = {'tiling_scheme_generation_method': ['tiling_scheme_generation_method', 'required'], 'tile_compression_quality': ['tile_compression_quality', 'optional'], 'tile_origin': ['tile_origin', 'optional'], 'scales_type': ['scales_type', 'optional'], 'scales': ['scales', 'optional'], 'predefined_tiling_scheme': ['predefined_tiling_scheme', 'optional'], 'number_of_scales': ['number_of_scales', 'required'], 'tile_format': ['tile_format', 'optional'], 'dpi': ['dpi', 'optional'], 'dataset': ['in_dataset', 'required'], 'lerc_error': ['lerc_error', 'optional'], 'tile_size': ['tile_size', 'optional'], 'storage_format': ['storage_format', 'optional']}
     out_db = {'tiling_scheme': ['out_tiling_scheme', 'required']}
     return _execute_tool('management', 'GenerateTileCacheTilingScheme', inputs, in_db, out_db)


def import_tile_cache(cache_target, cache_source, scales=None, area_of_interest=None, overwrite=None):
     """
     Geoprocessing tool that imports tiles from an existing tile cache.
     """
     inputs = locals()
     in_db = {'overwrite': ['overwrite', 'optional'], 'cache_source': ['in_cache_source', 'required'], 'cache_target': ['in_cache_target', 'required'], 'area_of_interest': ['area_of_interest', 'optional'], 'scales': ['scales', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ImportTileCache', inputs, in_db, out_db)


def manage_tile_cache(cache_location, manage_mode, cache_name=None, datasource=None, tiling_scheme=None, import_tiling_scheme=None, scales=None, area_of_interest=None, max_cell_size=None, mcached_scale=None, max_cached_scale=None):
     """
     Geoprocessing tool that creates a tile cache or updates tiles in an existing tile cache.
     """
     inputs = locals()
     in_db = {'mcached_scale': ['min_cached_scale', 'optional'], 'area_of_interest': ['area_of_interest', 'optional'], 'max_cached_scale': ['max_cached_scale', 'optional'], 'manage_mode': ['manage_mode', 'required'], 'scales': ['scales', 'optional'], 'tiling_scheme': ['tiling_scheme', 'optional'], 'cache_name': ['in_cache_name', 'optional'], 'cache_location': ['in_cache_location', 'required'], 'import_tiling_scheme': ['import_tiling_scheme', 'optional'], 'datasource': ['in_datasource', 'optional'], 'max_cell_size': ['max_cell_size', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ManageTileCache', inputs, in_db, out_db)


def disable_archiving(dataset, preserve_history=None):
     """
     Geoprocessing tool that disables archiving on a geodatabase feature class, table, or feature dataset.
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required'], 'preserve_history': ['preserve_history', 'optional']}
     out_db = {}
     return _execute_tool('management', 'DisableArchiving', inputs, in_db, out_db)


def enable_archiving(dataset):
     """
     Geoprocessing tool that enables archiving on a table, feature class, or feature dataset.
     """
     inputs = locals()
     in_db = {'dataset': ['in_dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'EnableArchiving', inputs, in_db, out_db)


def merge_mosaic_dataset_items(mosaic_dataset, where_clause=None, block_field=None, max_rows_per_merged_items=None):
     """
     Geoprocessing tool that merges together two or more mosaic dataset items.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional'], 'block_field': ['block_field', 'optional'], 'max_rows_per_merged_items': ['max_rows_per_merged_items', 'optional']}
     out_db = {}
     return _execute_tool('management', 'MergeMosaicDatasetItems', inputs, in_db, out_db)


def split_mosaic_dataset_items(mosaic_dataset, where_clause=None):
     """
     Geoprocessing tool that splits mosaic dataset items.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'where_clause': ['where_clause', 'optional']}
     out_db = {}
     return _execute_tool('management', 'SplitMosaicDatasetItems', inputs, in_db, out_db)


def compute_pansharpen_weights(raster, panchromatic_image, band_indexes=None):
     """

     """
     inputs = locals()
     in_db = {'raster': ['in_raster', 'required'], 'panchromatic_image': ['in_panchromatic_image', 'required'], 'band_indexes': ['band_indexes', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ComputePansharpenWeights', inputs, in_db, out_db)


def detect_feature_changes(update_features, base_features, search_distance, match_fields=None, change_tolerance=None, compare_fields=None, compare_line_direction=None):
     """
     Geoprocessing tool that detects spatial and attribute changes between the corresponding update and base line features and outputs a line feature class with the change information.
     """
     inputs = locals()
     in_db = {'match_fields': ['match_fields', 'optional'], 'compare_fields': ['compare_fields', 'optional'], 'base_features': ['base_features', 'required'], 'search_distance': ['search_distance', 'required'], 'update_features': ['update_features', 'required'], 'change_tolerance': ['change_tolerance', 'optional'], 'compare_line_direction': ['compare_line_direction', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required'], 'match_table': ['out_match_table', 'optional']}
     return _execute_tool('management', 'DetectFeatureChanges', inputs, in_db, out_db)


def project(dataset, out_coor_system, transform_method=None, coor_system=None, preserve_shape=None, max_deviation=None, vertical=None):
     """
     Geoprocessing tool that projects spatial data from one coordinate system to another.
     """
     inputs = locals()
     in_db = {'transform_method': ['transform_method', 'optional'], 'coor_system': ['in_coor_system', 'optional'], 'vertical': ['vertical', 'optional'], 'out_coor_system': ['out_coor_system', 'required'], 'dataset': ['in_dataset', 'required'], 'preserve_shape': ['preserve_shape', 'optional'], 'max_deviation': ['max_deviation', 'optional']}
     out_db = {'dataset': ['out_dataset', 'required']}
     return _execute_tool('management', 'Project', inputs, in_db, out_db)


def batch_project(input_feature_class_or_dataset, output_workspace, output_coordinate_system=None, template_dataset=None, transformation=None):
     """
     Geoprocessing tool to change the coordinate system of a set of input feature classes or feature datasets.
     """
     inputs = locals()
     in_db = {'output_coordinate_system': ['Output_Coordinate_System', 'optional'], 'template_dataset': ['Template_dataset', 'optional'], 'transformation': ['Transformation', 'optional'], 'output_workspace': ['Output_Workspace', 'required'], 'input_feature_class_or_dataset': ['Input_Feature_Class_or_Dataset', 'required']}
     out_db = {}
     return _execute_tool('management', 'BatchProject', inputs, in_db, out_db)


def add_geometry_attributes(input_features, geometry_properties, length_unit=None, area_unit=None, coordinate_system=None):
     """

     """
     inputs = locals()
     in_db = {'area_unit': ['Area_Unit', 'optional'], 'input_features': ['Input_Features', 'required'], 'coordinate_system': ['Coordinate_System', 'optional'], 'length_unit': ['Length_Unit', 'optional'], 'geometry_properties': ['Geometry_Properties', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddGeometryAttributes', inputs, in_db, out_db)


def migrate_relationship_class(relationship_class):
     """
     Geoprocessing tool that migrates an ObjectID-based relationship class to a GlobalID-based relationship class
     """
     inputs = locals()
     in_db = {'relationship_class': ['in_relationship_class', 'required']}
     out_db = {}
     return _execute_tool('management', 'MigrateRelationshipClass', inputs, in_db, out_db)


def find_disconnected_features_in_geometric_network(layer):
     """
     Geoprocessing tool for identifying disconnected features in a geometric network.
     """
     inputs = locals()
     in_db = {'layer': ['in_layer', 'required']}
     out_db = {'layer': ['out_layer', 'required']}
     return _execute_tool('management', 'FindDisconnectedFeaturesinGeometricNetwork', inputs, in_db, out_db)


def export_mosaic_dataset_geometry(mosaic_dataset, where_clause=None, geometry_type=None):
     """
     Geoprocessing tool that exports feature classes for the footprint, boundary, or seamline of a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'geometry_type': ['geometry_type', 'optional'], 'where_clause': ['where_clause', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'ExportMosaicDatasetGeometry', inputs, in_db, out_db)


def export_mosaic_dataset_items(mosaic_dataset, out_folder, out_base_name=None, where_clause=None, format=None, nodata_value=None, clip_type=None, template_dataset=None, cell_size=None):
     """
     Geoprocessing tool that creates a copy of your processed images within a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'cell_size': ['cell_size', 'optional'], 'clip_type': ['clip_type', 'optional'], 'nodata_value': ['nodata_value', 'optional'], 'out_folder': ['out_folder', 'required'], 'out_base_name': ['out_base_name', 'optional'], 'template_dataset': ['template_dataset', 'optional'], 'where_clause': ['where_clause', 'optional'], 'format': ['format', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ExportMosaicDatasetItems', inputs, in_db, out_db)


def create_runtime_content(map, service_type, format_type, level_of_detail, basemap=None, locator=None, extent=None, options=None, optimize=None, service_file=None):
     """
     Geoprocessing tool that consolidates feature layers, basemaps, network datasets, and locators into a single folder and prepares it for use within applications built with ArcGIS Runtime SDKs.
     """
     inputs = locals()
     in_db = {'locator': ['in_locator', 'optional'], 'options': ['options', 'optional'], 'optimize': ['optimize', 'optional'], 'extent': ['extent', 'optional'], 'service_file': ['service_file', 'optional'], 'format_type': ['format_type', 'required'], 'service_type': ['service_type', 'required'], 'level_of_detail': ['level_of_detail', 'required'], 'basemap': ['in_basemap', 'optional'], 'map': ['in_map', 'required']}
     out_db = {'output_folder': ['output_folder', 'required']}
     return _execute_tool('management', 'CreateRuntimeContent', inputs, in_db, out_db)


def rebuild_geometric_network(geometric_network):
     """
     Geoprocessing tool  for rebuilding a geometric network.
     """
     inputs = locals()
     in_db = {'geometric_network': ['geometric_network', 'required']}
     out_db = {'log': ['out_log', 'required']}
     return _execute_tool('management', 'RebuildGeometricNetwork', inputs, in_db, out_db)


def verify_and_repair_geometric_network_connectivity(geometric_network, verify_or_repair=None, exhaustive_check=None, extent=None):
     """
     Geoprocessing tool for verifying and repairing geometric network connectivity.
     """
     inputs = locals()
     in_db = {'geometric_network': ['geometric_network', 'required'], 'exhaustive_check': ['exhaustive_check', 'optional'], 'extent': ['extent', 'optional'], 'verify_or_repair': ['verify_or_repair', 'optional']}
     out_db = {'log': ['out_log', 'required']}
     return _execute_tool('management', 'VerifyAndRepairGeometricNetworkConnectivity', inputs, in_db, out_db)


def add_field_conflict_filter(table, fields):
     """
     Geoprocessing tool for adding a field conflict filter to a geodatabase table or feature class.
     """
     inputs = locals()
     in_db = {'table': ['table', 'required'], 'fields': ['fields', 'required']}
     out_db = {}
     return _execute_tool('management', 'AddFieldConflictFilter', inputs, in_db, out_db)


def remove_field_conflict_filter(table, fields):
     """
     Geoprocessing tool for removing a field conflict filter to a geodatabase table or feature class.
     """
     inputs = locals()
     in_db = {'table': ['table', 'required'], 'fields': ['fields', 'required']}
     out_db = {}
     return _execute_tool('management', 'RemoveFieldConflictFilter', inputs, in_db, out_db)


def generate_file_geodatabase_license(lic_def_file, allow_export=None, exp_date=None):
     """
     Geoprocessing tool that generates a data license for use with a licensed file geodatabase.
     """
     inputs = locals()
     in_db = {'lic_def_file': ['in_lic_def_file', 'required'], 'exp_date': ['exp_date', 'optional'], 'allow_export': ['allow_export', 'optional']}
     out_db = {'lic_file': ['out_lic_file', 'required']}
     return _execute_tool('management', 'GenerateFileGeodatabaseLicense', inputs, in_db, out_db)


def generate_licensed_file_geodatabase(fgdb):
     """
     Geoprocessing tool that generates a licensed file geodatabase and the license definition file required to generate license files for distribution.
     """
     inputs = locals()
     in_db = {'fgdb': ['in_fgdb', 'required']}
     out_db = {'fgdb': ['out_fgdb', 'required'], 'lic_def': ['out_lic_def', 'required']}
     return _execute_tool('management', 'GenerateLicensedFileGeodatabase', inputs, in_db, out_db)


def export_geodatabase_configuration_keywords(input_database):
     """
     Geoprocessing tool that exports the configuration keywords, parameters, and values from the specified enterprise geodatabase to an editable file.
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required']}
     out_db = {'file': ['out_file', 'required']}
     return _execute_tool('management', 'ExportGeodatabaseConfigurationKeywords', inputs, in_db, out_db)


def import_geodatabase_configuration_keywords(input_database, file):
     """
     Geoprocessing tool that allows you to define data storage parameters for an enterprise geodatabase by importing a file containing storage keywords and parameters.
     """
     inputs = locals()
     in_db = {'file': ['in_file', 'required'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'ImportGeodatabaseConfigurationKeywords', inputs, in_db, out_db)


def alter_field(table, field, new_field_name=None, new_field_alias=None, field_type=None, field_length=None, field_is_nullable=None, clear_field_alias=None):
     """
     Geoprocessing tool  to alter the field properties of geodatabase tables and feature classes.
     """
     inputs = locals()
     in_db = {'field': ['field', 'required'], 'field_length': ['field_length', 'optional'], 'table': ['in_table', 'required'], 'new_field_name': ['new_field_name', 'optional'], 'clear_field_alias': ['clear_field_alias', 'optional'], 'new_field_alias': ['new_field_alias', 'optional'], 'field_is_nullable': ['field_is_nullable', 'optional'], 'field_type': ['field_type', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AlterField', inputs, in_db, out_db)


def geodetic_densify(features, geodetic_type, distance=None):
     """
     Geoprocessing tool that replaces segments with densified approximation of geodetic curves.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required'], 'geodetic_type': ['geodetic_type', 'required'], 'distance': ['distance', 'optional']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'GeodeticDensify', inputs, in_db, out_db)


def configure_geodatabase_log_file_tables(input_database, log_file_type, log_file_pool_size=None, use_tempdb=None):
     """
     Geoprocessing tool that allows you to alter the type of log file tables used by an enterprise geodatabase to maintain lists of records cached by ArcGIS.
     """
     inputs = locals()
     in_db = {'use_tempdb': ['use_tempdb', 'optional'], 'log_file_type': ['log_file_type', 'required'], 'log_file_pool_size': ['log_file_pool_size', 'optional'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'ConfigureGeodatabaseLogFileTables', inputs, in_db, out_db)


def create_raster_type(input_database):
     """
     Geoprocessing tool to  install the ST_Raster data type in a geodatabase stored in Oracle, Microsoft SQL Server, or PostgreSQL
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'CreateRasterType', inputs, in_db, out_db)


def delete_schema_geodatabase(input_database):
     """
     Geoprocessing tool that deletes a user-schema geodatabase from a geodatabase in Oracle.
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'DeleteSchemaGeodatabase', inputs, in_db, out_db)


def diagnose_version_metadata(input_database):
     """
     Geoprocessing tool that identifies inconsistencies within the system tables used to manage versions and states in a versioned geodatabase.
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required']}
     out_db = {'log': ['out_log', 'required']}
     return _execute_tool('management', 'DiagnoseVersionMetadata', inputs, in_db, out_db)


def diagnose_version_tables(input_database, target_version=None, input_tables=None):
     """
     Geoprocessing tool to identify inconsistencies in the delta (A and D) tables of a versioned geodatabase.
     """
     inputs = locals()
     in_db = {'input_tables': ['input_tables', 'optional'], 'target_version': ['target_version', 'optional'], 'input_database': ['input_database', 'required']}
     out_db = {'log': ['out_log', 'required']}
     return _execute_tool('management', 'DiagnoseVersionTables', inputs, in_db, out_db)


def repair_version_metadata(input_database):
     """
     Geoprocessing tool that repairs inconsistencies within the versioning system tables of a versioned geodatabase
     """
     inputs = locals()
     in_db = {'input_database': ['input_database', 'required']}
     out_db = {'log': ['out_log', 'required']}
     return _execute_tool('management', 'RepairVersionMetadata', inputs, in_db, out_db)


def repair_version_tables(input_database, target_version=None, input_tables=None):
     """
     Geoprocessing tool to repair inconsistencies in the delta (A and D) tables of a versioned geodatabase.
     """
     inputs = locals()
     in_db = {'input_tables': ['input_tables', 'optional'], 'target_version': ['target_version', 'optional'], 'input_database': ['input_database', 'required']}
     out_db = {'log': ['out_log', 'required']}
     return _execute_tool('management', 'RepairVersionTables', inputs, in_db, out_db)


def analyze_tools_for_pro(input):
     """
     Geoprocessing tool that analyzes Python scripts and custom geoprocessing tools for functionality that is not supported in ArcGIS Pro.
     """
     inputs = locals()
     in_db = {'input': ['input', 'required']}
     out_db = {'report': ['report', 'optional']}
     return _execute_tool('management', 'AnalyzeToolsForPro', inputs, in_db, out_db)


def export_topology_errors(topology, out_path, out_basename):
     """
     Geoprocessing tool to export errors and exceptions from a topology.
     """
     inputs = locals()
     in_db = {'out_path': ['out_path', 'required'], 'out_basename': ['out_basename', 'required'], 'topology': ['in_topology', 'required']}
     out_db = {}
     return _execute_tool('management', 'ExportTopologyErrors', inputs, in_db, out_db)


def create_sqlite_database(spatial_type=None):
     """
     Geoprocessing tool that creates an ST_Geometry, SpatiaLite or GeoPackage database.
     """
     inputs = locals()
     in_db = {'spatial_type': ['spatial_type', 'optional']}
     out_db = {'database_name': ['out_database_name', 'required']}
     return _execute_tool('management', 'CreateSQLiteDatabase', inputs, in_db, out_db)


def generate_raster_from_raster_function(raster_function, raster_function_arguments=None, raster_properties=None, format=None):
     """
     Geoprocessing tool that uses raster functions to process raster datasets and write an output.
     """
     inputs = locals()
     in_db = {'format': ['format', 'optional'], 'raster_function': ['raster_function', 'required'], 'raster_function_arguments': ['raster_function_arguments', 'optional'], 'raster_properties': ['raster_properties', 'optional']}
     out_db = {'raster_dataset': ['out_raster_dataset', 'required']}
     return _execute_tool('management', 'GenerateRasterFromRasterFunction', inputs, in_db, out_db)


def recalculate_feature_class_extent(features):
     """
     Geoprocessing tool that recalculates the XY, M, and Z extent for a feature class.
     """
     inputs = locals()
     in_db = {'features': ['in_features', 'required']}
     out_db = {}
     return _execute_tool('management', 'RecalculateFeatureClassExtent', inputs, in_db, out_db)


def generate_tessellation(extent, shape_type=None, size=None, spatial_reference=None):
     """
     Geoprocessing tool that generates a feature class of a  tessellated grid of regular polygons to cover a given extent. The shapes can either be triangles, squares, or hexagons.
     """
     inputs = locals()
     in_db = {'spatial_reference': ['Spatial_Reference', 'optional'], 'extent': ['Extent', 'required'], 'size': ['Size', 'optional'], 'shape_type': ['Shape_Type', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required']}
     return _execute_tool('management', 'GenerateTessellation', inputs, in_db, out_db)


def create_fishnet(origcoord, y_axis_coord, cell_width, cell_height, number_rows, number_columns, corner_coord=None, labels=None, template=None, geometry_type=None):
     """
     Geoprocessing tool that creates a fishnet of rectangular cells.
     """
     inputs = locals()
     in_db = {'geometry_type': ['geometry_type', 'optional'], 'number_rows': ['number_rows', 'required'], 'number_columns': ['number_columns', 'required'], 'corner_coord': ['corner_coord', 'optional'], 'cell_height': ['cell_height', 'required'], 'template': ['template', 'optional'], 'labels': ['labels', 'optional'], 'cell_width': ['cell_width', 'required'], 'y_axis_coord': ['y_axis_coord', 'required'], 'origcoord': ['origin_coord', 'required']}
     out_db = {'feature_class': ['out_feature_class', 'required']}
     return _execute_tool('management', 'CreateFishnet', inputs, in_db, out_db)


def create_random_points(out_path, out_name, constraining_feature_class=None, constraining_extent=None, number_of_points_or_field=None, minimum_allowed_distance=None, create_multipoint_output=None, multipoint_size=None):
     """
     Geoprocessing tool that creates a specified number of random points in an extent window, inside polygon features, on point features, or along line features.
     """
     inputs = locals()
     in_db = {'number_of_points_or_field': ['number_of_points_or_field', 'optional'], 'constraining_extent': ['constraining_extent', 'optional'], 'multipoint_size': ['multipoint_size', 'optional'], 'create_multipoint_output': ['create_multipoint_output', 'optional'], 'minimum_allowed_distance': ['minimum_allowed_distance', 'optional'], 'out_name': ['out_name', 'required'], 'out_path': ['out_path', 'required'], 'constraining_feature_class': ['constraining_feature_class', 'optional']}
     out_db = {}
     return _execute_tool('management', 'CreateRandomPoints', inputs, in_db, out_db)


def generate_points_along_lines(input_features, point_placement, distance=None, percentage=None, include_end_points=None):
     """

     """
     inputs = locals()
     in_db = {'point_placement': ['Point_Placement', 'required'], 'input_features': ['Input_Features', 'required'], 'include_end_points': ['Include_End_Points', 'optional'], 'distance': ['Distance', 'optional'], 'percentage': ['Percentage', 'optional']}
     out_db = {'output_feature_class': ['Output_Feature_Class', 'required']}
     return _execute_tool('management', 'GeneratePointsAlongLines', inputs, in_db, out_db)


def update_enterprise_geodatabase_license(input_database, authorization_file):
     """
     Geoprocessing tool that allows the geodatabase administrator to update the ArcGIS Server authorization information in the geodatabase before it expires.
     """
     inputs = locals()
     in_db = {'authorization_file': ['authorization_file', 'required'], 'input_database': ['input_database', 'required']}
     out_db = {}
     return _execute_tool('management', 'UpdateEnterpriseGeodatabaseLicense', inputs, in_db, out_db)


def analyze_control_points(mosaic_dataset, control_points, mask_dataset=None, minimum_area=None, maximum_level=None):
     """
     Geoprocessing tool that analyzes the tie points and control points.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'mask_dataset': ['in_mask_dataset', 'optional'], 'maximum_level': ['maximum_level', 'optional'], 'control_points': ['in_control_points', 'required'], 'minimum_area': ['minimum_area', 'optional']}
     out_db = {'coverage_table': ['out_coverage_table', 'required'], 'overlap_table': ['out_overlap_table', 'optional']}
     return _execute_tool('management', 'AnalyzeControlPoints', inputs, in_db, out_db)


def append_control_points(master_control_points, input_control_points, z_field=None, tag_field=None, dem=None, xy_accuracy=None, z_accuracy=None):
     """
     Geoprocessing tool that combines tie points and control points.
     """
     inputs = locals()
     in_db = {'z_accuracy': ['in_z_accuracy', 'optional'], 'xy_accuracy': ['in_xy_accuracy', 'optional'], 'tag_field': ['in_tag_field', 'optional'], 'dem': ['in_dem', 'optional'], 'master_control_points': ['in_master_control_points', 'required'], 'input_control_points': ['in_input_control_points', 'required'], 'z_field': ['in_z_field', 'optional']}
     out_db = {}
     return _execute_tool('management', 'AppendControlPoints', inputs, in_db, out_db)


def apply_block_adjustment(mosaic_dataset, adjustment_operation, input_solution_table=None, pan_to_ms_scaling_factor=None, dem=None, zoffset=None, control_point_table=None, adjust_footprints=None):
     """
     Geoprocessing tool that applies the geographic adjustments to the mosaic dataset items.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'control_point_table': ['control_point_table', 'optional'], 'adjust_footprints': ['adjust_footprints', 'optional'], 'adjustment_operation': ['adjustment_operation', 'required'], 'input_solution_table': ['input_solution_table', 'optional'], 'pan_to_ms_scaling_factor': ['pan_to_ms_scaling_factor', 'optional'], 'zoffset': ['zoffset', 'optional'], 'dem': ['DEM', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ApplyBlockAdjustment', inputs, in_db, out_db)


def compute_block_adjustment(mosaic_dataset, control_points, transformation_type, maximum_residual_value=None, adjustment_options=None, location_accuracy=None):
     """
     Geoprocessing tool that computes the adjustments to the mosaic dataset items.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_residual_value': ['maximum_residual_value', 'optional'], 'transformation_type': ['transformation_type', 'required'], 'location_accuracy': ['location_accuracy', 'optional'], 'control_points': ['in_control_points', 'required'], 'adjustment_options': ['adjustment_options', 'optional']}
     out_db = {'quality_table': ['out_quality_table', 'optional'], 'solution_point_table': ['out_solution_point_table', 'optional'], 'solution_table': ['out_solution_table', 'required']}
     return _execute_tool('management', 'ComputeBlockAdjustment', inputs, in_db, out_db)


def compute_camera_model(mosaic_dataset, gps_accuracy=None, estimate=None, refine=None, apply_adjustment=None, maximum_residual=None, initial_tiepoint_resolution=None, maximum_overlap=None, minimum_coverage=None, remove=None, control_points=None, options=None):
     """
     Geoprocessing tool that automatically constructs and refines a camera model for aerial images and, in particular, UAV and UAS images, where the exterior and interior camera models are coarse or undefined.
     """
     inputs = locals()
     in_db = {'initial_tiepoint_resolution': ['initial_tiepoint_resolution', 'optional'], 'remove': ['remove', 'optional'], 'gps_accuracy': ['gps_accuracy', 'optional'], 'refine': ['refine', 'optional'], 'maximum_residual': ['maximum_residual', 'optional'], 'options': ['options', 'optional'], 'estimate': ['estimate', 'optional'], 'control_points': ['in_control_points', 'optional'], 'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'apply_adjustment': ['apply_adjustment', 'optional'], 'minimum_coverage': ['minimum_coverage', 'optional'], 'maximum_overlap': ['maximum_overlap', 'optional']}
     out_db = {'dsm': ['out_dsm', 'optional'], 'control_points': ['out_control_points', 'optional'], 'solution_point_table': ['out_solution_point_table', 'optional'], 'solution_table': ['out_solution_table', 'optional'], 'flight_path': ['out_flight_path', 'optional']}
     return _execute_tool('management', 'ComputeCameraModel', inputs, in_db, out_db)


def compute_control_points(mosaic_dataset, reference_images, similarity=None, density=None, distribution=None, area_of_interest=None, location_accuracy=None):
     """
     Geoprocessing tool that computes control points for your mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'area_of_interest': ['area_of_interest', 'optional'], 'density': ['density', 'optional'], 'similarity': ['similarity', 'optional'], 'reference_images': ['in_reference_images', 'required'], 'location_accuracy': ['location_accuracy', 'optional'], 'distribution': ['distribution', 'optional']}
     out_db = {'image_feature_points': ['out_image_feature_points', 'optional'], 'control_points': ['out_control_points', 'required']}
     return _execute_tool('management', 'ComputeControlPoints', inputs, in_db, out_db)


def compute_tie_points(mosaic_dataset, similarity=None, mask_dataset=None, density=None, distribution=None, location_accuracy=None):
     """
     Geoprocessing tool that computes the tie points for the  items within a mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'density': ['density', 'optional'], 'similarity': ['similarity', 'optional'], 'location_accuracy': ['location_accuracy', 'optional'], 'mask_dataset': ['in_mask_dataset', 'optional'], 'distribution': ['distribution', 'optional']}
     out_db = {'image_features': ['out_image_features', 'optional'], 'control_points': ['out_control_points', 'required']}
     return _execute_tool('management', 'ComputeTiePoints', inputs, in_db, out_db)


def build_stereo_model(mosaic_dataset, minimum_angle=None, maximum_angle=None, minimum_overlap=None, maximum_diff_op=None, maximum_diff_gsd=None):
     """
     Geoprocessing tool that generates a stereo model on imagery in a  mosaic dataset.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_diff_gsd': ['maximum_diff_GSD', 'optional'], 'minimum_angle': ['minimum_angle', 'optional'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'maximum_angle': ['maximum_angle', 'optional'], 'minimum_overlap': ['minimum_overlap', 'optional']}
     out_db = {}
     return _execute_tool('management', 'BuildStereoModel', inputs, in_db, out_db)


def generate_point_cloud(mosaic_dataset, matching_method, object_size=None, ground_spacing=None, minimum_pairs=None, minimum_area=None, minimum_adjustment_quality=None, maximum_diff_gsd=None, maximum_diff_op=None):
     """
     Geoprocessing tool that generates a 3D point cloud from stereo images.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'matching_method': ['matching_method', 'required'], 'maximum_diff_gsd': ['maximum_diff_gsd', 'optional'], 'minimum_area': ['minimum_area', 'optional'], 'maximum_diff_op': ['maximum_diff_OP', 'optional'], 'minimum_pairs': ['minimum_pairs', 'optional'], 'object_size': ['object_size', 'optional'], 'minimum_adjustment_quality': ['minimum_adjustment_quality', 'optional'], 'ground_spacing': ['ground_spacing', 'optional']}
     out_db = {'base_name': ['out_base_name', 'required'], 'folder': ['out_folder', 'required']}
     return _execute_tool('management', 'GeneratePointCloud', inputs, in_db, out_db)


def interpolate_from_point_cloud(container, cell_size, interpolation_method, smooth_method, surface_type=None, fill_dem=None):
     """
     Geoprocessing tool that interpolates a digital surface model (DSM) or digital elevation model (DEM) from a point cloud.
     """
     inputs = locals()
     in_db = {'cell_size': ['cell_size', 'required'], 'container': ['in_container', 'required'], 'smooth_method': ['smooth_method', 'required'], 'fill_dem': ['fill_dem', 'optional'], 'surface_type': ['surface_type', 'optional'], 'interpolation_method': ['interpolation_method', 'required']}
     out_db = {'raster': ['out_raster', 'required']}
     return _execute_tool('management', 'InterpolateFromPointCloud', inputs, in_db, out_db)


def compute_mosaic_candidates(mosaic_dataset, maximum_overlap=None, maximum_area_loss=None):
     """
     Geoprocessing tool that finds the image candidates in a mosaic dataset that best represents the mosaic area, and will be used to generate an orthomosaic.
     """
     inputs = locals()
     in_db = {'mosaic_dataset': ['in_mosaic_dataset', 'required'], 'maximum_overlap': ['maximum_overlap', 'optional'], 'maximum_area_loss': ['maximum_area_loss', 'optional']}
     out_db = {}
     return _execute_tool('management', 'ComputeMosaicCandidates', inputs, in_db, out_db)

