"""
Reads shapefiles, feature classes, table into a spatial dataframe
"""
from __future__ import print_function
from __future__ import division
import os
import copy
from datetime import datetime
import pandas as pd
import numpy as np
import six
from six import iteritems
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
    """converts a SpatialDataFrame to a feature class"""
    fc = os.path.join(out_location, out_name)
    if arcpy.Exists(os.path.join(out_location, out_name)):
        arcpy.Delete_management(fc)
    fc = arcpy.CreateFeatureclass_management(out_path=out_location, out_name=out_name,
                                             geometry_type=df.geometry_type.upper(),
                                             spatial_reference=df.sr)[0]
    oidField = arcpy.Describe(fc).oidFieldName
    # add fields
    col_insert = copy.copy(df.columns).tolist()
    if "SHAPE" in df.columns:
        idx = col_insert.index("SHAPE")
        col_insert[idx] = "SHAPE@"
    if oidField in col_insert:
        del col_insert[col_insert.index(oidField)]
        del df[oidField]
    existing_fields = [field.name.lower() for field in arcpy.ListFields(fc)]
    for col in col_insert:
        if col.lower().find('shape') == -1 and \
           col.lower not in existing_fields:
            arcpy.AddField_management(in_table=fc, field_name=col,
                                      field_type=_infer_type(df, col))
    icur = da.InsertCursor(fc, col_insert)
    for index, row in df.iterrows():
        icur.insertRow(row.tolist())
        del row
    del icur
    return fc
#--------------------------------------------------------------------------
#TODO: REFERENCE NUMPY DOCUMENTATION TO ENSURE ALL NUMPY DTYPES ARE CAPTURED.
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

