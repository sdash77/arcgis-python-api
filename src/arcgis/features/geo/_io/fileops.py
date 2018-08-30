"""
IO operations for Feature Classes
"""
import os
import sys
import shutil
import datetime

import numpy as np
import pandas as pd

try:
    import arcpy
    from arcpy import da
    HASARCPY = True
except:
    HASARCPY = False

try:
    import fiona
    HASFIONA = True
except:
    HASFIONA = False

try:
    import shapefile
    HASPYSHP = True
except:
    HASPYSHP = False
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
    return "TEXT"
#--------------------------------------------------------------------------
def _geojson_to_esrijson(geojson):
    """converts the geojson spec to esri json spec"""
    if geojson['type'] in ['Polygon', 'MultiPolygon']:
        return {
            'rings' : geojson['coordinates'],
            'spatialReference' : {'wkid' : 4326}
        }
    elif geojson['type'] == "Point":
        return {
            "x" : geojson['coordinates'][0],
            "y" : geojson['coordinates'][1],
            'spatialReference' : {'wkid' : 4326}
        }
    elif geojson['type'] == "MultiPoint":
        return {
            "points" : geojson['coordinates'],
            'spatialReference' : {'wkid' : 4326}
        }
    elif geojson['type'] in ['LineString', 'MultiLineString']:
        return {
            "paths" : geojson['coordinates'],
            'spatialReference' : {'wkid' : 4326}
        }
    return geojson
#--------------------------------------------------------------------------
def _geometry_to_geojson(geom):
    """converts the esri json spec to geojson"""
    if 'rings' in geom and \
       len(geom['rings']) == 1:
        return {
            'type' : "Polygon",
            "coordinates" : geom['rings']
        }
    elif 'rings' in geom and \
       len(geom['rings']) > 1:
        return {
            'type' : "MultiPolygon",
            "coordinates" : geom['rings']
        }
    elif geom['type'] == "Point":
        return {
            "coordinates" : [geom['x'], geom['y']],
            "type" : "Point"
        }
    elif geom['type'] == "MultiPoint":
        return {
            "coordinates" : geom['points'],
            'type' : "MultiPoint"
        }
    elif geom['type'].lower() == "polyline" and \
         len(geom['paths']) <= 1:
        return {
            "coordinates" : geom['paths'],
            'type' : "LineString"
        }
    elif geom['type'].lower() == "polyline" and \
         len(geom['paths']) > 1:
        return {
            "coordinates" : geom['paths'],
            'type' : "MultiLineString"
        }
    return geom
#--------------------------------------------------------------------------
def _from_xy(df, x_column, y_column, sr=None):
    """
    Takes an X/Y Column and Creates a Point Geometry from it.
    """
    from arcgis.geometry import SpatialReference, Geometry
    if sr is None:
        sr = SpatialReference({'wkid' : 4326})
    if not isinstance(sr, SpatialReference):
        if isinstance(sr, dict):
            sr = SpatialReference(sr)
        elif isinstance(sr, int):
            sr = SpatialReference({'wkid' : sr})
        elif isinstance(sr, str):
            sr = SpatialReference({'wkt' : sr})
    geoms = []
    for idx, row in df.iterrows():
        geoms.append(
            Geometry({'x' : row[x_column], 'y' : row[y_column],
             'spatialReference' : sr})
        )
    df['SHAPE'] = geoms
    df.spatial.set_geometry('SHAPE')
    return df

#--------------------------------------------------------------------------
def from_featureclass(filename, **kwargs):
    """
    Returns a GeoDataFrame from a feature class.
    Inputs:
     filename: full path to the feature class
    Optional Parameters:
     sql_clause: sql clause to parse data down
     where_clause: where statement
     sr: spatial reference object
     fields: list of fields to extract from the table
    """
    from arcgis.geometry import _types
    if HASARCPY:
        sql_clause = kwargs.pop('sql_clause', (None,None))
        where_clause = kwargs.pop('where_clause', None)
        sr = kwargs.pop('sr', arcpy.Describe(filename).spatialReference or arcpy.SpatialReference(4326))
        fields = kwargs.pop('fields', None)
        desc = arcpy.Describe(filename)
        if not fields:
            fields = [field.name for field in arcpy.ListFields(filename) \
                      if field.type not in ['Geometry']]

            if hasattr(desc, 'areaFieldName'):
                afn = desc.areaFieldName
                if afn in fields:
                    fields.remove(afn)
            if hasattr(desc, 'lengthFieldName'):
                lfn = desc.lengthFieldName
                if lfn in fields:
                    fields.remove(lfn)
        geom_fields = fields + ['SHAPE@']
        flds = fields + ['SHAPE']
        vals = []
        geoms = []
        geom_idx = flds.index('SHAPE')
        shape_type = desc.shapeType
        default_polygon = _types.Geometry(arcpy.Polygon(arcpy.Array([arcpy.Point(0,0)]* 3)))
        default_polyline = _types.Geometry(arcpy.Polyline(arcpy.Array([arcpy.Point(0,0)]* 2)))
        default_point = _types.Geometry(arcpy.PointGeometry(arcpy.Point()))
        default_multipoint = _types.Geometry(arcpy.Multipoint(arcpy.Array([arcpy.Point()])))
        with arcpy.da.SearchCursor(filename,
                                   field_names=geom_fields,
                                   where_clause=where_clause,
                                   sql_clause=sql_clause,
                                   spatial_reference=sr) as rows:

            for row in rows:
                row = list(row)
                # Prevent curves/arcs
                if row[geom_idx] is None:
                    row.pop(geom_idx)
                    g = {}
                elif row[geom_idx].type in ['polyline', 'polygon']:
                    try:
                        g = _types.Geometry(row.pop(geom_idx))
                    except:
                        g = _types.Geometry(row.pop(geom_idx)).generalize(0)
                else:
                    g = _types.Geometry(row.pop(geom_idx))
                if g == {}:
                    if shape_type.lower() == 'point':
                        g = default_point
                    elif shape_type.lower() == 'polygon':
                        g = default_polygon
                    elif shape_type.lower() == 'polyline':
                        g = default_point
                    elif shape_type.lower() == 'multipoint':
                        g = default_multipoint
                geoms.append(g)
                vals.append(row)
                del row
            del rows
        df = pd.DataFrame(data=vals, columns=fields)
        df.spatial.set_geometry(geoms)
        if df.spatial.sr is None:
            if sr is not None:
                df.spatial.sr = sr
            else:
                df.spatial.sr = df.spatial._date[df.spatial._name][sdf.geometry.first_valid_index()].spatial_reference
        return df
    elif HASARCPY == False and \
         HASPYSHP == True and\
         filename.lower().find('.shp') > -1:
        geoms = []
        records = []
        reader = shapefile.Reader(filename)
        fields = [field[0] for field in reader.fields if field[0] != 'DeletionFlag']
        for r in reader.shapeRecords():
            atr = dict(zip(fields, r.record))
            g = r.shape.__geo_interface__
            g = _geojson_to_esrijson(g)
            geom = _types.Geometry(g)
            atr['SHAPE'] = geom
            records.append(atr)
            del atr
            del r, g
            del geom
        sdf = pd.DataFrame(records)
        sdf.spatial.set_geometry('SHAPE')
        sdf.reset_index(inplace=True)
        return sdf
    elif HASARCPY == False and \
         HASPYSHP == False and \
         HASFIONA == True and \
         (filename.lower().find('.shp') > -1 or \
          os.path.dirname(filename).lower().find('.gdb') > -1):
        is_gdb = os.path.dirname(filename).lower().find('.gdb') > -1
        if is_gdb:
            with fiona.drivers():
                from arcgis.geometry import _types
                fp = os.path.dirname(filename)
                fn = os.path.basename(filename)
                geoms = []
                atts = []
                with fiona.open(path=fp, layer=fn) as source:
                    meta = source.meta
                    cols = list(source.schema['properties'].keys())
                    for idx, row in source.items():
                        geoms.append(_types.Geometry(row['geometry']))
                        atts.append(list(row['properties'].values()))
                        del idx, row
                    df = pd.DataFrame(data=atts, columns=cols)
                    df.spatial.set_geometry(geoms)
                    return df
        else:
            with fiona.drivers():
                from arcgis.geometry import _types
                geoms = []
                atts = []
                with fiona.open(path=filename) as source:
                    meta = source.meta
                    cols = list(source.schema['properties'].keys())
                    for idx, row in source.items():
                        geoms.append(_types.Geometry(row['geometry']))
                        atts.append(list(row['properties'].values()))
                        del idx, row
                    df = pd.DataFrame(data=atts, columns=cols)
                    df.spatial.set_geometry(geoms)
                    return df
    return

def to_featureclass(geo,
                    location,
                    overwrite=True):
    """
    Exports the DataFrame to a Feature class.

    ===============     ====================================================
    **Argument**        **Description**
    ---------------     ----------------------------------------------------
    location            Required string. This is the output location for the
                        feature class. This should be the path and feature
                        class name.
    ---------------     ----------------------------------------------------
    overwrite           Optional Boolean. If overwrite is true, existing
                        data will be deleted and replaced with the spatial
                        dataframe.
    ===============     ====================================================


    :returns: string

    """
    out_location= os.path.dirname(location)
    fc_name = os.path.basename(location)
    df = geo._data
    if geo.name is None:
        raise ValueError("DataFrame must have geometry set.")
    if geo.validate(strict=True) == False:
        raise ValueError(("Mixed geometry types detected, "
                         "cannot export to feature class."))
    if HASARCPY:
        join_dummy = "AEIOUYAJCZ"
        columns = df.columns.tolist()
        columns.pop(columns.index(geo._name))
        attr = df[columns].reset_index(drop=False, inplace=False)
        attr['index'] += 1
        attr = attr.values
        columns = [join_dummy] + columns
        gt = pd.unique(geo._data[geo._name].geom.geometry_type).tolist()[0].upper()
        sr = geo.sr
        geoms = df[geo._name].tolist()
        dtypes = [(join_dummy, np.int64)]

        for col in columns[1:]:
            if col.lower() in ['fid', 'oid', 'objectid']:
                dtypes.append((col, np.int32))
            elif df[col].dtype.name == 'datetime64[ns]':
                dtypes.append((col, '<M8[us]'))
            elif df[col].dtype.name == 'object':
                try:
                    u = type(df[col][df[col].first_valid_index()])
                except:
                    u = pd.unique(df[col].apply(type)).tolist()[0]
                if issubclass(u, str):
                    mlen = df[col].str.len().max()
                    dtypes.append((col, '<U%s' % int(mlen)))
                else:
                    try:
                        dtypes.append((col, type(df[col][s.first_valid_index()])))
                    except:
                        dtypes.append((col, '<U254'))
            elif df[col].dtype.name == 'int64':
                dtypes.append((col, np.int64))
            elif df[col].dtype.name == 'bool':
                dtypes.append((col, np.int32))
            else:
                dtypes.append((col, df[col].dtype.type))
        if arcpy.Exists(location) and overwrite:
            arcpy.Delete_management(location)
        elif arcpy.Exists(location) and overwrite == False:
            raise ValueError("Dataset exists, try another file name")
        from arcgis.geometry._types import SpatialReference
        if isinstance(sr, SpatialReference):
            sr = sr.as_arcpy
        fc = arcpy.CreateFeatureclass_management(out_path=out_location,
                                            out_name=fc_name,
                                            geometry_type=gt,
                                            spatial_reference=sr)[0]
        with da.InsertCursor(fc, ['SHAPE@']) as irows:
            for g in geoms:
                irows.insertRow([g.as_arcpy])
                del g
        if hasattr(da, 'Describe'):
            oidfld = da.Describe(fc)['OIDFieldName']
        else:
            desc = arcpy.Describe(fc)
            oidfld = desc.OIDFieldName
        attr = np.array([tuple(row) for row in attr.tolist()], dtype=dtypes)
        da.ExtendTable(fc, oidfld, attr, join_dummy, append_only=False)
        return fc
    elif HASPYSHP:
        if fc_name.endswith('.shp') == False:
            fc_name = "%s.shp" % fc_name
        return _pyshp_to_shapefile(df=df,
                            out_path=out_location,
                            out_name=fc_name)
    elif HASARCPY == False and HASPYSHP == False:
        raise Exception(("Cannot Export the data without ArcPy or PyShp modules."
                        " Please install them and try again."))
    else:
        return None
#--------------------------------------------------------------------------
def _pyshp_to_shapefile(df, out_path, out_name):
    """
    Saves a SpatialDataFrame to a Shapefile using pyshp

    :Parameters:
     :df: spatial dataframe
     :out_path: folder location to save the data
     :out_name: name of the shapefile
    :Output:
     path to the shapefile or None if pyshp isn't installed or
     spatial dataframe does not have a geometry column.
    """
    from arcgis.geometry._types import Geometry
    if HASPYSHP:
        GEOMTYPELOOKUP = {
            "Polygon" : shapefile.POLYGON,
            "Point" : shapefile.POINT,
            "Polyline" : shapefile.POLYLINE,
            'null' : shapefile.NULL
        }
        if os.path.isdir(out_path) == False:
            os.makedirs(out_path)
        out_fc = os.path.join(out_path, out_name)
        if out_fc.lower().endswith('.shp') == False:
            out_fc += ".shp"
        geom_field = df.spatial._name
        if geom_field is None:
            return
        geom_type = "null"
        idx = df[geom_field].first_valid_index()
        if idx > -1:
            geom_type = df.loc[idx][geom_field].type
        shpfile = shapefile.Writer(GEOMTYPELOOKUP[geom_type])
        shpfile.autoBalance = 1
        dfields = []
        cfields = []
        for c in df.columns:
            idx = df[c].first_valid_index()
            if idx > -1:
                if isinstance(df[c].loc[idx],
                              Geometry):
                    geom_field = (c, "GEOMETRY")
                else:
                    cfields.append(c)
                    if isinstance(df[c].loc[idx], (str)):
                        shpfile.field(name=c, size=255)
                    elif isinstance(df[c].loc[idx], (int)):
                        shpfile.field(name=c, fieldType="N", size=5)
                    elif isinstance(df[c].loc[idx], (np.int, np.int32, np.int64)):
                        shpfile.field(name=c, fieldType="N", size=10)
                    elif isinstance(df[c].loc[idx], (np.float, np.float64)):
                        shpfile.field(name=c, fieldType="F", size=19, decimal=11)
                    elif isinstance(df[c].loc[idx], (datetime.datetime, np.datetime64)) or \
                         df[c].dtype.name == 'datetime64[ns]':
                        shpfile.field(name=c, fieldType="D", size=8)
                        dfields.append(c)
                    elif isinstance(df[c].loc[idx], (bool, np.bool)):
                        shpfile.field(name=c, fieldType="L", size=1)
            del c
            del idx
        for idx, row in df.iterrows():
            geom = row[df.spatial._name]
            if geom.type == "Polygon":
                shpfile.poly(geom['rings'])
            elif geom.type == "Polyline":
                shpfile.line(geom['paths'])
            elif geom.type == "Point":
                shpfile.point(x=geom.x, y=geom.y)
            else:
                shpfile.null()
            row = row[cfields].tolist()
            for fld in dfields:
                idx = df[cfields].columns.tolist().index(fld)
                if row[idx]:
                    row[idx] = row[idx].to_pydatetime()
            shpfile.record(*row)
            del idx
            del row
            del geom
        shpfile.save(out_fc)


        # create the PRJ file
        try:
            wkid = df.spatial.sr['wkid']

            prj_filename = out_fc.replace('.shp', '.prj')

            url = 'http://epsg.io/{}.esriwkt'.format(wkid)

            opener = request.build_opener()
            opener.addheaders = [('User-Agent', 'geosaurus')]
            resp = opener.open(url)

            wkt = resp.read().decode('utf-8')
            if len(wkt) > 0:
                prj = open(prj_filename, "w")
                prj.write(wkt)
                prj.close()
        except:
            # Unable to write PRJ file.
            pass

        del shpfile
        return out_fc
    return None