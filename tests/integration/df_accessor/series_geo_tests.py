import os
import sys
#sys.path.append(r"D:\SVN\git_hub\ArcGIS\geo_public")

import tempfile
import shutil, datetime
from arcgis.features.geo._array import GeoArray, GeoType
from arcgis.features.geo import from_featureclass
from arcgis.geometry import Geometry
import copy
from arcgis.features.geo import _io
import pandas as pd
from pandas.core.internals import ExtensionBlock
from arcgis.geometry import Geometry
import numpy as np
import pandas as pd
import pandas.util.testing as tm


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
simple_polygon = Geometry({
  "rings" : [[[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832]]],
  "spatialReference" : {"wkid" : 4326}
}).buffer(1)

pt_single_geoms = [
    Geometry({"x" : -118.15, "y" : 29.80, "spatialReference" : {"wkid" : 4326}}),
    Geometry({"x" : -120.95, "y" : 30.80, "spatialReference" : {"wkid" : 4326}}),
    Geometry({"x" : -110.75, "y" : 31.80, "spatialReference" : {"wkid" : 4326}}),
    Geometry({"x" : -100.0, "y" : 32.80, "spatialReference" : {"wkid" : 4326}})
]
import pytest
import pandas as pd

MIXED_GEOMS = GeoArray(geoms)
##--------------------------------------------------------------------------
## Creation Tests
##--------------------------------------------------------------------------
def test_series_gen():
    """tests series creates from GeoArray"""
    series = pd.Series(data=GeoArray(geoms))
    assert isinstance(series, pd.Series)
    assert series.dtype.name == 'geometry'
    assert isinstance(series.dtype, GeoType)
#--------------------------------------------------------------------------
def test_has_geom_namespace():
    """tests 'geom' namespace exists"""
    series = pd.Series(data=GeoArray(geoms))
    assert hasattr(series, 'geom')
#--------------------------------------------------------------------------
def test_create_df_from_series():
    """tests df creation from series"""
    series = pd.Series(GeoArray)
    df = pd.DataFrame(data=series, columns=['SHAPE'])
    df.spatial.set_geometry('SHAPE')
    assert hasattr(series, 'geom')
    assert isinstance(df, pd.DataFrame)
##--------------------------------------------------------------------------
## Tests Properties
##--------------------------------------------------------------------------
#--------------------------------------------------------------------------
def test_area():
    """tests area"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert sum(df.SHAPE.geom.area) >= -5
#--------------------------------------------------------------------------
def test_as_arcpy():
    """tests the arcpy property"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert df.SHAPE.geom.as_arcpy is not None
#--------------------------------------------------------------------------
def test_as_shapely():
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    geom = df.SHAPE.geom
    assert isinstance(geom.as_shapely, pd.Series)
    assert geom.as_shapely.dtype.name.lower() == 'object'
    assert geom.as_shapely.name == 'as_shapely'
#--------------------------------------------------------------------------
def test_centroid():
    """tests the centroid property"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.SHAPE.geom.centroid, pd.Series)
#--------------------------------------------------------------------------
def test_extent():
    """tests the extent property"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.extent
    assert isinstance(ext[0], tuple)
    assert isinstance(ext, pd.Series)
#--------------------------------------------------------------------------
def test_first_point():
    """tests the first point property"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    fp = df.SHAPE.geom.first_point
    assert isinstance(fp[0], Geometry)
    assert isinstance(fp, pd.Series)
#--------------------------------------------------------------------------
def test_geo_extent():
    """tests the geoextent property"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.geoextent
    assert isinstance(ext[0], tuple)
    assert isinstance(ext, pd.Series)
#--------------------------------------------------------------------------
def test_geo_type():
    """performs the geometry_type tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    gt = df.SHAPE.geom.geometry_type
    assert isinstance(gt[0], str)
    assert isinstance(gt, pd.Series)
#--------------------------------------------------------------------------
def test_hull_rect():
    """performs the hull_rectangle tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.hull_rectangle
    assert isinstance(ext[0], str)
    assert isinstance(ext, pd.Series)
#--------------------------------------------------------------------------
def test_is_empty():
    """performs the is_empty tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.is_empty
    assert ext[0] == 0
    assert ext[0] == False
    assert isinstance(ext, pd.Series)
#--------------------------------------------------------------------------
def test_is_multipart():
    """performs the is_multipart tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.is_multipart
    assert ext[0] == 0
    assert ext[0] == False
    assert isinstance(ext, pd.Series)
#--------------------------------------------------------------------------
def test_is_valid():
    """performs the is_valid tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.is_valid
    assert bool == type(bool(ext[0]))
    assert ext[0] == True
    assert isinstance(ext, pd.Series)
#--------------------------------------------------------------------------
def test_JSON():
    """performs the JSON tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.JSON
    assert isinstance(ext[0], str)
    assert isinstance(ext, pd.Series)
#--------------------------------------------------------------------------
def test_label_point():
    """performs the label_point tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.label_point
    assert ext.dtype.name == 'geometry'
    assert isinstance(ext, pd.Series)
    assert isinstance(ext[0], Geometry)
#--------------------------------------------------------------------------
def test_last_point():
    """performs the last_point tests"""
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.last_point
    assert ext.dtype.name == 'geometry'
    assert isinstance(ext, pd.Series)
    assert isinstance(ext[0], Geometry)
#--------------------------------------------------------------------------
def test_part_cnt():
    """performs the part_count tests"""
    import numpy as np
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    ext = df.SHAPE.geom.part_count
    assert isinstance(ext, pd.Series)
    assert isinstance(ext[0], (int, np.int64))#isinstance(ext[0], int)
#--------------------------------------------------------------------------
def test_point_count():
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.SHAPE.geom.point_count, pd.Series)
    assert isinstance(df.SHAPE.geom.point_count[0], (int, np.int64))
#--------------------------------------------------------------------------
def test_sr():
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.SHAPE.geom.spatial_reference, pd.Series)
#--------------------------------------------------------------------------
def test_WKB():
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.SHAPE.geom.WKB, pd.Series)
#--------------------------------------------------------------------------
def test_WKT():
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.SHAPE.geom.WKT, pd.Series)
def test_length():
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.SHAPE.geom.length, pd.Series)
def test_length3D():
    v = GeoArray(geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    assert isinstance(df.SHAPE.geom.length3D, pd.Series)
##--------------------------------------------------------------------------
## Tests Geometry Methods
##--------------------------------------------------------------------------
geojson_point = {
    "type": "Point",
    "coordinates": [0.0, 1.0]}
pt = Geometry(geojson_point)
geojson_point = {
    "type": "Point",
    "coordinates": [1.0, 1.0]}
pt1 = Geometry(geojson_point)
geojson_point = {
    "type": "Point",
    "coordinates": [2.0, 3.0]}
pt2 = Geometry(geojson_point)
gj_geoms = [pt, pt1, pt2]
geojson_polygon = {
    "type": "Polygon",
    "coordinates": [
        [[10.0, 0.0], [20.0, 0.0], [20.0, 10.0], [10.0, 10.0],
         [10.0, 0.0]]]}
polygon = Geometry(geojson_polygon)
geojson_polygon = {
    "type": "Polygon",
    "coordinates": [
        [[0.0, 0.0],
         [10.0, 0.0],
         [10.0, 5.0],
         [5.0, 5.0],
         [0.0, 0.0]]]}
polygon2 = Geometry(geojson_polygon)
poly_geoms = [polygon, polygon2]
#--------------------------------------------------------------------------
def test_angleDistTo():
    """tests angle distance to"""

    df = pd.DataFrame(data=[['a', 1, 2.1, gj_geoms[0]]], columns=['a', 'b', 'c', 'SHAPE'])
    df.spatial.set_geometry("SHAPE")
    r = df.SHAPE.geom.angle_distance_to(gj_geoms[1])
    assert isinstance(r, pd.Series)
    assert isinstance(r[0], tuple)
##--------------------------------------------------------------------------
def test_boundary():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    b =  df.SHAPE.geom.boundary()
    assert isinstance(b, pd.Series)
    assert b.geom.geometry_type.unique()[0]== 'polyline'
##--------------------------------------------------------------------------
def test_buffer():
    v = GeoArray(gj_geoms)
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    g = df.SHAPE.geom.buffer(100)
    assert df.SHAPE.geom.buffer(100).dtype.name == 'geometry'
    df.spatial.set_geometry(g)
    assert all([df.spatial.geometry_type[0] == 'polygon'])
    assert df.spatial.geometry_type[0] == 'polygon'
#--------------------------------------------------------------------------
#def test_clip():
#    v = GeoArray(poly_geoms)
#    df = pd.DataFrame({"SHAPE": v})
#    df.spatial.set_geometry("SHAPE")
#    extent = df.spatial.full_extent
#    s = df.spatial.clip(extent)
#    print(s)
#--------------------------------------------------------------------------
def test_contains():
    """tests the contain logic"""
    v = GeoArray([g.label_point for g in [geoms[3]]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    g = df.SHAPE.geom.buffer(2000)
    assert all(df.SHAPE.geom.contains(g[0])) == False
#--------------------------------------------------------------------------
def test_convex_hull():
    """ tests the convex_hull method"""
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    g = df.SHAPE.geom.convex_hull()
    assert g.dtype.name == 'geometry'
#--------------------------------------------------------------------------
def test_clip():
    """test the clip operation"""
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    g = df.SHAPE.geom.clip(v[0].extent)
    assert g.dtype.name.lower() == "geometry"
    assert g.geom.geometry_type.unique()[0] == 'polygon'
#--------------------------------------------------------------------------
def test_crosses():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.crosses(geoms[3])
    assert r.dtype.name == 'bool'
#--------------------------------------------------------------------------
def test_cut():
    v = GeoArray([geoms[3]])
    line = geoms[2]
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    #df.SHAPE.geom.
    r = df.SHAPE.geom.cut(line)
    assert r.dtype.name.lower() == 'geometry'

#--------------------------------------------------------------------------
def test_densify():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.densify(method="GEODESIC", distance=10, deviation=1)
    assert r.dtype.name.lower() == "geometry"
    assert r.geom.geometry_type.unique()[0] == 'polygon'
#--------------------------------------------------------------------------
def test_difference():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry('SHAPE')
    r = df.SHAPE.geom.difference(geoms[3].buffer(-.5))
    assert r.dtype.name.lower() == "geometry"
    assert r.geom.geometry_type.unique()[0] == 'polygon'
#--------------------------------------------------------------------------
def test_disjoint():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.disjoint(geoms[3].buffer(-.5))
    assert r.dtype.name.lower() == "bool"
#--------------------------------------------------------------------------
def test_dist_to():
    pass
#--------------------------------------------------------------------------
def test_equals():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.equals(geoms[3])
    assert r.dtype.name.lower() == "bool"
#--------------------------------------------------------------------------
def test_generalize():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.generalize(1)
    assert r.dtype.name.lower() == "geometry"
#--------------------------------------------------------------------------
def test_get_area():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.get_area(method="PLANAR", units="SQUAREFEET")
    assert r.dtype.name.lower() == "float64"
#--------------------------------------------------------------------------
def test_get_length():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.get_length(method="PLANAR", units="FEET")
    assert r.dtype.name.lower() == "float64"

#--------------------------------------------------------------------------
def test_get_part():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.get_part(index=0)
    assert r.dtype.name.lower() == 'object'
#--------------------------------------------------------------------------
def test_intersect():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.intersect(geoms[3], 4)
    assert r.dtype.name.lower() == "geometry"
#--------------------------------------------------------------------------
def test_touches():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.touches(geoms[3])
    assert r.dtype.name.lower() == "bool"
#--------------------------------------------------------------------------
def test_meas_on_ln():
    v = GeoArray([geoms[2]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.measure_on_line(geoms[0],True)
    assert r.dtype.name.lower() == "float64"
#--------------------------------------------------------------------------
def test_overlaps():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.overlaps(geoms[3])
    assert r.dtype.name.lower() == "bool"
#--------------------------------------------------------------------------
def test_pt_ang_dist():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.point_from_angle_and_distance(angle=90, distance=1.1, method='PLANAR')
    assert r.dtype.name.lower() == 'geometry'
    assert isinstance(r[0], Geometry)
#--------------------------------------------------------------------------
def test_posit_alg_ln():
    v = GeoArray([geoms[2]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.position_along_line(.3,True)
    assert r.dtype.name.lower() == "geometry"
#--------------------------------------------------------------------------
def test_prj_as():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    r = df.SHAPE.geom.project_as(spatial_reference=3875)
    assert r.dtype.name.lower() == "geometry"
#--------------------------------------------------------------------------
def test_query_pt_dist():
    v = GeoArray([geoms[2]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    pt = Geometry({'x' : -97.06133, 'y' : 32.8379, 'spatialReference' : {'wkid' : 4326}})
    r = df.SHAPE.geom.query_point_and_distance(pt, True)
    assert r.dtype.name.lower() == 'object'
    assert isinstance(r[0], tuple)
#--------------------------------------------------------------------------
def test_seg_alg_ln():
    v = GeoArray([geoms[2]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    r = df.SHAPE.geom.segment_along_line(.1,.30, True)
    assert r.dtype.name.lower() == "geometry"
#--------------------------------------------------------------------------
def test_union():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    #r = df.SHAPE.geom.union(geoms[3].buffer(4)
    #assert r.dtype.name.lower() == 'geometry'
#--------------------------------------------------------------------------
def test_snap_to_line():
    pt = Geometry({'x' : -97.06133, 'y' : 32.8379, 'spatialReference' : {'wkid' : 4326}})
    v = GeoArray([geoms[2]])
    df = pd.DataFrame({"SHAPE": v})
    df.spatial.set_geometry("SHAPE")
    r = df.SHAPE.geom.snap_to_line(pt)
    assert r.dtype.name.lower() == "geometry"
    assert isinstance(r[0], Geometry)

#--------------------------------------------------------------------------
def test_within():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.within(geoms[3])
    assert r.dtype.name.lower() == "bool"
#--------------------------------------------------------------------------
def test_sym_diff():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    r = df.SHAPE.geom.symmetric_difference(geoms[3].buffer(1.1))
    assert r.dtype.name.lower() == "geometry"
def test_print():
    v = GeoArray([geoms[3]])
    df = pd.DataFrame({"SHAPE": v})
    print(df.SHAPE)
###########################################################################
if __name__ == '__main__':
    test_print()
    test_series_gen()
    test_has_geom_namespace()
    print('property tests')
    test_area()
    test_as_arcpy()
    test_as_shapely()
    test_centroid()
    test_extent()
    test_first_point()
    test_geo_extent()
    test_geo_type()
    test_hull_rect()
    test_is_empty()
    test_is_multipart()
    test_is_valid()
    test_JSON()
    test_label_point()
    test_last_point()
    test_part_cnt()
    test_point_count()
    test_sr()
    test_WKB()
    test_WKT()
    test_length()
    test_length3D()
    print('method tests')
    test_angleDistTo()
    test_boundary()
    test_buffer()
    test_contains()
    test_convex_hull()
    test_clip()
    test_crosses()
    test_densify()
    test_difference()
    test_disjoint()
    test_equals()
    test_generalize()
    test_touches()
    test_within()
    test_intersect()
    test_overlaps()
    test_prj_as()
    test_sym_diff()
    test_get_area()
    test_get_length()
    test_get_part()
    test_seg_alg_ln()
    test_query_pt_dist()
    test_meas_on_ln()
    test_posit_alg_ln()
    test_pt_ang_dist()
    test_snap_to_line()

    #test_cut()
    #test_union()

    print('series tests finished')


