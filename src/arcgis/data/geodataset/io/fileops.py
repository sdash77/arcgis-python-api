"""
Reads shapefiles, feature classes, table into a spatial dataframe
"""
from __future__ import print_function
from __future__ import division
import os
import six
import copy
import numpy as np
import pandas as pd
from six import iteritems
from datetime import datetime
from ..utils import NUMERIC_TYPES, STRING_TYPES, DATETIME_TYPES
import arcpy
from arcpy import da

def from_featureclass(filename, **kwargs):
    """
    Returns a GeoDataFrame from a feature class.
    Inputs:
     filename: full path to the feature class
    Optional Parameters:
     sql_clause: sql clause to parse data down
     where_clause: where statement
     sr: spatial reference object

    """
    from arcgis import SpatialDataFrame
    sql_clause = kwargs.pop('sql_clause', (None,None))
    where_clause = kwargs.pop('where_clause', None)
    sr = kwargs.pop('sr', None)

    fields = [field.name for field in arcpy.ListFields(filename) \
              if field.type not in ['Geometry']]
    geom_fields = fields + ['SHAPE@']
    flds = fields + ['SHAPE']
    vals = []
    with arcpy.da.SearchCursor(filename,
                               field_names=geom_fields,
                               where_clause=where_clause,
                               sql_clause=sql_clause,
                               spatial_reference=sr) as rows:
        for row in rows:
            vals.append(dict(zip(flds, row)))
            del row
        del rows
    sdf = SpatialDataFrame.from_dict(data=vals)
    if sr is None:
        sdf.sr = sr
    else:
        sdf.sr = sdf.geometry[0].spatialReference
    return sdf
#--------------------------------------------------------------------------
def to_featureclass(df, out_location, out_name, overwrite=True):
    """
    converts a SpatialDataFrame to a feature class

    Parameters:
     :out_location: path to the workspace
     :out_name: name of the output feature class table
     :overwrite: True, the data will be erased then replaced, else the
      table will be appended to an existing table.
    Returns:
     path to the feature class
    """
    cols = []
    dt_idx = []
    idx = 0
    if out_name.lower().endswith('.shp'):
        for col in df.columns:
            col = arcpy.ValidateFieldName(col, workspace=out_location)
            if len(col) > 10:
                col = col[:10]
            cols.append(col)#col.replace(' ', "_"))
    else:
        for col in df.columns:
            cols.append(arcpy.ValidateFieldName(col, workspace=out_location))#col.replace(" ", "_"))
    df.columns = cols

    for  col in df.columns:
        if df[col].dtype.type in NUMERIC_TYPES:
            df[col] = df[col].fillna(0)
        elif df[col].dtype.type in DATETIME_TYPES:
            dt_idx.append(idx)
        else:
            df.loc[df[col].isnull(), col] = ""
        idx += 1
    fc = os.path.join(out_location, out_name)
    if arcpy.Exists(os.path.join(out_location, out_name)) and \
       overwrite:
        arcpy.Delete_management(fc)
    fc = arcpy.CreateFeatureclass_management(out_path=out_location,
                                             out_name=out_name,
                                             geometry_type=df.geometry_type.upper(),
                                             spatial_reference=df.sr)[0]
    oidField = arcpy.Describe(fc).oidFieldName
    col_insert = copy.copy(df.columns).tolist()
    lower_col_names = [f.lower() for f in col_insert]
    if "SHAPE" in df.columns:
        idx = col_insert.index("SHAPE")
        col_insert[idx] = "SHAPE@"
    if oidField.lower() in lower_col_names:
        val = col_insert.pop(lower_col_names.index(oidField.lower()))
        del df[val]
    existing_fields = [field.name.lower() for field in arcpy.ListFields(fc)]
    for col in col_insert:
        if col.lower().find('shape') == -1 and \
           col.lower not in existing_fields:
            arcpy.AddField_management(in_table=fc, field_name=col,
                                      field_type=_infer_type(df, col))
    icur = da.InsertCursor(fc, col_insert)
    for index, row in df.iterrows():
        if len(dt_idx) > 0:
            row = row.tolist()
            for i in dt_idx:
                row[i] = row[i].to_pydatetime()
                del i
            icur.insertRow(row)
        else:
            icur.insertRow(row.tolist())
        del row
    del icur
    return fc
#--------------------------------------------------------------------------
def _infer_type(df, col):
    """
    internal function used to get the datatypes for the feature class if
    the dataframe's _field_reference is NULL or there is a column that does
    not have a dtype assigned to it.

    Input:
     dataframe - spatialdataframe object
    Ouput:
      field type name
    """
    nn = df[col].notnull()
    nn = list(df[nn].index)
    if len(nn) > 0:
        val = df[col][nn[0]]
        if isinstance(val, six.string_types):
            return "TEXT"
        elif isinstance(val, tuple(list(six.integer_types) + [np.int32])):
            return "INTEGER"
        elif isinstance(val, (float, np.int64 )):
            return "FLOAT"
        elif isinstance(val, datetime):
            return "DATE"
        #else:
        #    print type(val), val, col
    return "TEXT"

