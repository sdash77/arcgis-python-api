import os, sys
#sys.path.append(r"D:\SVN\git_hub\ArcGIS\geo_public")
import shutil, datetime
import tempfile
from arcgis.features.geo._array import GeoArray, GeoType
from arcgis.features.geo import from_featureclass
from arcgis.geometry import Geometry
import copy
from arcgis.features.geo import _io
import pandas as pd
from pandas.core.internals import ExtensionBlock
import pandas.util.testing as tm
try:
    import arcpy
    HASARCPY = True
except:
    HASARCPY = False
try:
    HASPYSHP = True
    import shapefile
except:
    HASPYSHP = False
try:
    import fiona
    HASFIONA = True
except:
    HASFIONA = False

USERNAME = None
PASSWORD = None

geoms = [
    Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}}),
    Geometry({
  "points" : [[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832]],
  "spatialReference" : {"wkid" : 4326}}),

    Geometry({
  "paths" : [[[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832]],
             [[-97.06326,32.759],[-97.06298,32.755]]],
  "spatialReference" : {"wkid" : 4326}
}),
    Geometry({
  "rings" : [[[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832],
              [-97.06138,32.837]],[[-97.06326,32.759],[-97.06298,32.755],[-97.06153,32.749],
              [-97.06326,32.759]]],
  "spatialReference" : {"wkid" : 4326}
})
]
import pytest
import pandas as pd
from arcgis.features.geo import GeoAccessor
##-------------------------------------------------------------------------
## Constructor Tests
##-------------------------------------------------------------------------
def test_dataframe_constructor():
    v = GeoArray(geoms)
    df = pd.DataFrame({"A": v})
    assert isinstance(df.dtypes['A'], GeoType)
    assert df.shape == (len(geoms), 1)
    str(df)
def test_series_constructor():
    v = GeoArray.from_geometry(geoms)
    result = pd.Series(v)
    assert result.dtype == v.dtype
    assert isinstance(result._data.blocks[0], ExtensionBlock)
def test_dataframe_head():
    v = GeoArray(geoms)
    df = pd.DataFrame({"A": v})
    df.spatial.set_geometry('A')
    print(df.head(1))

##-------------------------------------------------------------------------
## Begin GeoAccessor Tests
##
## These tests cover the functionality of the Accessor Extension
## and provide the coverage needed to ensure all functionality is
## properly working.
##
##-------------------------------------------------------------------------
## Set Geometry Tests
##-------------------------------------------------------------------------
def test_set_geometry_accessor_series():
    """set geometry from pd.Series"""
    data = [[1,2,3,4]] * len(geoms)
    columns = ['A', 'B', 'C', 'D']
    df = pd.DataFrame(data=data, columns=columns)
    df.spatial.set_geometry(pd.Series(geoms))
    assert df.spatial._name == 'SHAPE'
def test_set_geometry_accessor_list():
    """set geometry from a list"""
    data = [[1,2,3,4]] * len(geoms)
    columns = ['A', 'B', 'C', 'D']
    df = pd.DataFrame(data=data, columns=columns)
    df.spatial.set_geometry(geoms)
    assert df.spatial._name == 'SHAPE'
def test_set_geometry_accessor_tuple():
    """set geometry from a tuple"""
    data = [[1,2,3,4]] * len(geoms)
    columns = ['A', 'B', 'C', 'D']
    df = pd.DataFrame(data=data, columns=columns)
    df.spatial.set_geometry(tuple(geoms))
    assert df.spatial._name == 'SHAPE'
def test_set_geometry_accessor_geo_array():
    """set geometry from a GeoArray"""
    v = GeoArray(geoms)
    data = [[1,2,3,4]] * len(geoms)
    columns = ['A', 'B', 'C', 'D']
    df = pd.DataFrame(data=data, columns=columns)
    df.spatial.set_geometry(v)
    assert df.spatial._name == 'SHAPE'
def test_set_geometry_accessor_string():
    """set geometry from a string (column name)"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert df.spatial._name == "SHAPE"
def test_set_geometry_accessor_string_not_valid():
    """set geometry to a column that does not exist"""
    with pytest.raises(ValueError, message="Expecting ValueError"):
        data = [[1,2,3,4]] * len(geoms)
        columns = ['A', 'B', 'C', 'D']
        df = pd.DataFrame(data=data, columns=columns)
        df.spatial.set_geometry("FISH")
##-------------------------------------------------------------------------
## Plot Tests
##-------------------------------------------------------------------------
def test_plot_no_geom_set():
    """plots without setting geometry"""
    with pytest.raises(Exception, message="Expecting ValueError"):
        data = [[1,2,3,4]] * len(geoms)
        columns = ['A', 'B', 'C', 'D']
        df = pd.DataFrame(data=data, columns=columns)
        df.spatial.plot(map_widget=mw)

def test_plot():
    """tests plot with map widget"""
    from arcgis.gis import GIS
    mw = GIS().map()
    v = GeoArray(geoms)
    data = [[1,2,3,4]] * len(geoms)
    columns = ['A', 'B', 'C', 'D']
    df = pd.DataFrame(data=data, columns=columns)
    df.spatial.set_geometry(v)
    df.spatial.plot(map_widget=mw)
def test_plot_not_mapwidget_obj():
    """tests plot with invalid map widget"""
    mw = 1
    v = GeoArray(geoms)
    data = [[1,2,3,4]] * len(geoms)
    columns = ['A', 'B', 'C', 'D']
    df = pd.DataFrame(data=data, columns=columns)
    df.spatial.set_geometry(v)
    df.spatial.plot(map_widget=mw)
##-------------------------------------------------------------------------
## Geometry Property Call Tests
##-------------------------------------------------------------------------
def test_area():
    """tests area"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert df.spatial.area >= -5
#-------------------------------------------------------------------------
def test_centroid():
    """tests the centroid property"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.spatial.centroid, tuple)
#-------------------------------------------------------------------------
def test_true_centroid():
    """tests the centroid property"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.spatial.true_centroid, tuple)
##-------------------------------------------------------------------------
## I/O Tests Include:
#### to/from feature classses
####   - Using ArcPy  ## To Feature Class Done using Arcpy
####   - Using pyshp  ## Done
####   - Using fiona  ## Done
#### to/from services
#### to_feature_collection ## Done
#### __geo_interface__  ## Done
#### __feature_set__  ## Done
#### to/from featureset ## done
#### to/from geojson
#### from_xy
##-------------------------------------------------------------------------
def test_to_feature_collection():
    from arcgis.features import FeatureCollection
    g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    fc = df.spatial.to_feature_collection('name')
    assert isinstance(fc, FeatureCollection)


def test_to_featureclass_arcpy():
    """tests the export to feature class method"""
    import arcpy
    g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    fc = df.spatial.to_featureclass(os.path.join(arcpy.env.scratchGDB, "loasgadfg"))
    assert isinstance(fc, str)

#--------------------------------------------------------------------------
def test_to_featureclass_pyshp():
    """
       TODO: tests the export to feature class method using pyshp
    """
    import os, uuid
    shp = "a%s.shp" % uuid.uuid4().hex[:10]
    g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    fc = df.spatial.to_featureclass(r"d:\temp\%s" % shp)
    assert os.path.isfile(fc)

#--------------------------------------------------------------------------
def test_geo_interface():
    """tests the __geo_interface__ method"""
    g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    gjson = df.spatial.__geo_interface__
    assert isinstance(gjson, str)
#--------------------------------------------------------------------------
def test__feature_set__():
    """tests the __feature_set__ property"""
    g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    res = df.spatial.__feature_set__
    assert isinstance(res, dict)
    gg = []
    for k in list(res.keys()):
        if k in ['objectIdFieldName', 'displayFieldName',
                                'geometryType', 'spatialReference',
                                'fields', 'features']:
            gg.append(True)
        else:
            gg.append(False)

    assert all(gg)
#--------------------------------------------------------------------------
def test_full_extent():
    """test the full dataset extent property"""
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(geoms)
    assert df.spatial.full_extent == (-118.15, 32.832, -97.06124, 33.8)
#--------------------------------------------------------------------------
def test_sr_single():
    """tests getting the sr"""
    from arcgis.geometry import SpatialReference
    g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    assert df.spatial.sr == SpatialReference({'wkid' : 4326})
##--------------------------------------------------------------------------
##
##   Function Testing
##
##--------------------------------------------------------------------------
poly_geoms = [
       Geometry({
      "rings" : [[[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832],
                  [-97.06138,32.837]],[[-97.06326,32.759],[-97.06298,32.755],[-97.06153,32.749],
                  [-97.06326,32.759]]],
      "spatialReference" : {"wkid" : 4326}
    })
    ]
def test_project_as():
    g = geoms
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    s = df.spatial.project(3857)
    assert s == True
    assert df.spatial.sr == {'wkid': 102100}
def test_bbox():
    """returns the bounding box as a polygon"""
    g = geoms
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    bbox = df.spatial.bbox
    assert isinstance(bbox, Geometry)
def test_geometry_type():
    g = geoms
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    gt = df.spatial.geometry_type
    assert isinstance(gt, list)
#--------------------------------------------------------------------------
def test_from_fc_arcpy():
    """tests reading a FGDB from arcpy"""
    fc = r"./testdata.gdb/World30"

    sdf = from_featureclass(fc)
    assert sdf.spatial.geometry_type[0] == 'polygon'
#--------------------------------------------------------------------------
def test_from_fc_fiona():
    """tests reading a SHP/FGDB from fiona"""
    fc = r"./testdata.gdb/World30"
    if _io.fileops.HASFIONA == False:
        return
    oval_pyshp = copy.copy(_io.fileops.HASPYSHP)
    oval_arcpy = copy.copy(_io.fileops.HASARCPY)
    _io.fileops.HASPYSHP = False
    _io.fileops.HASARCPY = False
    sdf = from_featureclass(fc)
    assert sdf.spatial.geometry_type[0].lower() == 'polygon'
    _io.fileops.HASARCPY = oval_arcpy
    _io.fileops.HASPYSHP = oval_pyshp
#--------------------------------------------------------------------------
def test_from_fc_fiona_shp():
    """tests reading a SHP/FGDB from fiona"""
    fc = r"./World30.shp"

    if _io.fileops.HASFIONA == False:
        return
    oval_pyshp = copy.copy(_io.fileops.HASPYSHP)
    oval_arcpy = copy.copy(_io.fileops.HASARCPY)
    _io.fileops.HASPYSHP = False
    _io.fileops.HASARCPY = False
    sdf = from_featureclass(fc)
    assert sdf.spatial.geometry_type[0].lower() == 'polygon'
    _io.fileops.HASARCPY = oval_arcpy
    _io.fileops.HASPYSHP = oval_pyshp
#--------------------------------------------------------------------------
def test_from_fc_pyshp():
    """tests reading a SHP from arcpy"""
    fc = r"./World30.shp"
    if _io.fileops.HASPYSHP == False:
        return
    oval_fiona = copy.copy(_io.fileops.HASFIONA)
    oval_arcpy = copy.copy(_io.fileops.HASARCPY)
    sdf = from_featureclass(fc)
    assert sdf.spatial.geometry_type[0].lower() == 'polygon'
    _io.fileops.HASARCPY = oval_arcpy
    _io.fileops.HASFIONA = oval_fiona
#--------------------------------------------------------------------------
def test_from_fc_staticmethod():
    """tests reading a SHP from arcpy"""
    fc = r"./World30.shp"
    sdf = pd.DataFrame.spatial.from_featureclass(fc)
    assert sdf.spatial.geometry_type[0].lower() == 'polygon'
#--------------------------------------------------------------------------
def test_from_df():
    """tests geocoding from_df"""
    if USERNAME is None and PASSWORD is None:
        return
    from arcgis.gis import GIS
    gis = GIS(username=USERNAME, password=PASSWORD)
    locations = [[0,"12 York Street, Camden, NJ"], [1,"646 Kings Hwy, West Deptford, NJ 08096"]]
    df = pd.DataFrame(data=locations, columns=['OID', "ADDRESS"])
    df = pd.DataFrame.spatial.from_df(df, "ADDRESS")
    assert df.spatial.geometry_type[0].lower() == 'point'
    assert df.spatial.sr == {'wkid' : 4326}
#--------------------------------------------------------------------------
def test_from_xy():
    """tests the static method xy op"""
    locations = [[10,70, 'alpha'], [15, 75, "beta"]]
    df = pd.DataFrame(data=locations, columns=['X', "Y", "letter"])
    df = pd.DataFrame.spatial.from_xy(df, "X", "Y", 4326)
    assert df.spatial.geometry_type[0].lower() == 'point'
    assert df.spatial.sr == {'wkid' : 4326}
    assert df.spatial.full_extent == (10, 70, 15, 75)
#--------------------------------------------------------------------------
def test_print():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    print(df)
if __name__ == "__main__":
    print('#######################################################')
    print("visualize test")
    test_print()
    print('#######################################################')
    print('Testing Constructors')
    test_dataframe_constructor()
    test_series_constructor()
    test_dataframe_head()
    test_set_geometry_accessor_series()
    test_set_geometry_accessor_list()
    test_set_geometry_accessor_tuple()
    test_set_geometry_accessor_geo_array()
    test_set_geometry_accessor_string()
    test_set_geometry_accessor_string_not_valid()
    print('End of Testing Constructors')
    print('#######################################################')

    print('#######################################################')
    print('Testing Dataset Properties')
    test_area()
    test_bbox()
    test_centroid()
    test_sr_single()
    test_full_extent()
    test_geometry_type()
    test_true_centroid()
    print('End of Testing Dataset Properties')
    print('#######################################################')

    print('#######################################################')
    print("Testing IO/Data Converstion Operations")
    test_from_df()
    test_from_xy()
    test_geo_interface()
    test__feature_set__()
    test_to_feature_collection()
    print("End of Testing IO/Data Converstion Operations")
    print('#######################################################')

    print('#######################################################')
    print("Testing Package Specific Operations")
    if HASPYSHP and HASARCPY == False:
        test_to_featureclass_pyshp()
    if HASARCPY:
        test_to_featureclass_arcpy()
        test_project_as()
    print("End Testing Package Specific Operations")
    print('#######################################################')

    print('#######################################################')
    print("Begin Testing from_featureclass")
    if HASARCPY:
        print('++++ Testing ArcPy Import Feature Class')
        test_from_fc_arcpy()
        print('++++ End Testing ArcPy Import Feature Class')
    else:
        print('++++ Skipping ArcPy Test, ArcPy not found')
    if HASPYSHP:
        print('++++ Testing pyshp Import Feature Class')
        test_from_fc_pyshp()
        print('++++ End Testing pyshp Import Feature Class')
    else:
        print('++++ Skipping pyshp Test, pyshp not found')
    if HASFIONA:
        print('++++ Testing fiona Import Feature Class')
        test_from_fc_fiona()
        test_from_fc_fiona_shp()
        print('++++ End Testing fiona Import Feature Class')
    else:
        print('++++ Skipping fiona Test, fiona not found')

    print("End Testing from_featureclass")

    print('#######################################################')
    print("DataFrame Accessor Testing Finished")

