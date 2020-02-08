"""
Tests the Spatial Index logic

By default the
"""
import os
import sys
#sys.path.append(r"D:\SVN\git_hub\ArcGIS\geo_public")
import pytest
import pandas as pd
import datetime
from arcgis.geometry import Geometry
from arcgis.features.geo._accessor import GeoAccessor
from arcgis.features.geo._index._impl import SpatialIndex
from arcgis.features.geo._index.quadtree import Index as QIndex
RTREE_FILENAME = "small.index"


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

#--------------------------------------------------------------------------
def test_build_sindex_rtree():
    """builds r-tree spatial index in-memory"""
    try:
        import datetime
        from rtree.index import Index as RIndex
        g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
        data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
        df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
        df.spatial.set_geometry(g)
        si = df.spatial.sindex('rtree')
        assert isinstance(si, SpatialIndex)
        assert si._filename is None
        assert si._stype == 'rtree'
        assert isinstance(si._index, RIndex)
    except:
        pass
#--------------------------------------------------------------------------
def test_build_sindex_quadtree():
    """builds quad-tree spatial index in-memory"""
    import datetime
    g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
    data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
    df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
    df.spatial.set_geometry(g)
    si = df.spatial.sindex('quadtree', bbox=df.spatial.full_extent)
    assert isinstance(si, SpatialIndex)
    assert si._filename is None
    assert si._stype == 'quadtree'
    assert isinstance(si._index, QIndex)
#--------------------------------------------------------------------------
def test_build_sindex_rt_filename():
    """builds r-tree spatial index to a file"""
    try:
        import datetime
        from rtree.index import Index as RIndex
        for f in [RTREE_FILENAME + '.dat', RTREE_FILENAME + '.idx']:
            if os.path.isfile(f):
                os.remove(f)
        g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
        data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
        df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
        df.spatial.set_geometry(g)
        si = df.spatial.sindex('rtree', filename=RTREE_FILENAME)
        assert isinstance(si, SpatialIndex)
        assert os.path.isfile(RTREE_FILENAME + ".idx")
        assert os.path.isfile(RTREE_FILENAME + ".dat")
        assert si._stype == 'rtree'
        assert isinstance(si._index, RIndex)
        del si._index
        os.remove(RTREE_FILENAME + ".idx")
        os.remove(RTREE_FILENAME + ".dat")
    except ImportError:
        pass    
#--------------------------------------------------------------------------
def test_build_sindex_rt_load_fn():
    """tests loading an existing R-Tree index from file"""
    try:
        import datetime
        EXISTING_FILENAME = 'sindex.index'
        g = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * len(geoms)
        data = [[1,datetime.datetime.now(),True,"BLAHBLAH"]] * len(geoms)
        df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', "Gamma", "Delta"])
        df.spatial.set_geometry(g)
        si = df.spatial.sindex('rtree', filename=EXISTING_FILENAME)
    except Exception as e:
        print("no rtree installed.") 
#--------------------------------------------------------------------------
def test_intersect_rtree():
    """"""
    try:
        
        import datetime
        from arcgis.features.geo._index._impl import SpatialIndex
        si = SpatialIndex('rtree')
        si.insert(0, [-179, -89, 179, 89])
        r = si.intersect([-180, -90, 180, 90])
        assert r == [0]
    except:
        print("no rtree installed.")
#--------------------------------------------------------------------------
def test_intersect_quadtree():
    """"""
    try:
        from arcgis.features.geo._index._impl import SpatialIndex
        si = SpatialIndex('quadtree', [-179, -89, 179, 89])
        si.insert(0, [-179, -89, 179, 89])
        r = si.intersect([-180, -90, 180, 90])
        assert  r == [0]
    except Exception as e:
        print("no rtree installed.") 
if __name__ == "__main__":
    print("####  Begin  ##################################################################")
    print("Running Spatial Index Tests")
    test_build_sindex_rtree()
    print("######################################################################")
    test_build_sindex_quadtree()
    print("######################################################################")
    test_build_sindex_rt_filename()
    print("######################################################################")
    test_build_sindex_rt_load_fn()
    print("######################################################################")
    test_intersect_quadtree()
    print("######################################################################")
    test_intersect_rtree()
    print("####  Finished ##################################################################")