"""
Tests Related to Spatially Enabled Data Frame
"""
import sys
import shutil
import unittest
import pytest
import pandas as pd
from arcgis.features import GeoSeriesAccessor, GeoAccessor
from arcgis.features.geo import _is_geoenabled

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import unittest
import pandas as pd
import os, shutil
try:
    import arcpy
    arcpy.env.overwriteOutput = True
    HAS_ARCPY = True
except:
    HAS_ARCPY = False
from arcgis.geometry import _types, Geometry
from arcgis.features.geo import GeoAccessor, GeoSeriesAccessor
from arcgis.features.geo._array import GeoArray
from arcgis.gis.server._service import Service
from arcgis.features import FeatureLayer
import tempfile, uuid
import pytest

fs_urls = ["https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/World_Cities/FeatureServer/0",# Point
           "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Railroads/FeatureServer/0", # Polyline
           "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/World_Countries_(Generalized)/FeatureServer/0"] #polygon
table_url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/ServiceRequest/MapServer/1" # table

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

if HAS_ARCPY:
    #############################################################################
    #@unittest.SkipTest
    class FeatureSetConversionTest(unittest.TestCase):
        """
        tests the spatial dataframe operations related
        to the Spatial DataFrame where a featureset returns a
        spatial dataframe or a dataframe.
        """
        #----------------------------------------------------------------------
        def test_with_geometry(self):
            """test with geometries"""
            for url in fs_urls:
                fl = Service(url=url)
                res = fl.query(where="%s < 10" % fl.properties.objectIdField)
                res = res.sdf
                self.assertIsInstance(res, pd.DataFrame, msg=\
                                      "Got type: %s instead of pd.DataFrame" % type(res))
                res = fl.query(where="%s < 10" % fl.properties.objectIdField, as_df=True)
                self.assertIsInstance(res, pd.DataFrame, msg=\
                                      "Got type: %s instead of pd.DataFrame" % type(res))
        #----------------------------------------------------------------------
        def test_without_geometry(self):
            """table test"""
            fl = Service(url=table_url)
            oidname = [fld.name for fld in fl.properties.fields if fld.type.lower() =='esrifieldtypeoid'][0]
            res = fl.query().sdf
            self.assertIsInstance(res, pd.DataFrame, msg=\
                                  "Got type: %s instead of pd.DataFrame" % type(res))
    ###########################################################################
    #@unittest.SkipTest
    class IOTest(unittest.TestCase):
        """tests the spatial dataframe io functions"""
        def _construct_featureclass(self):
            import uuid, os
            import arcpy
            fc = os.path.basename(arcpy.CreateUniqueName(base_name="a" + uuid.uuid4().hex[:6] + "a",
                                                         workspace=arcpy.env.scratchGDB))#

            return arcpy.CreateRandomPoints_management(out_path=arcpy.env.scratchGDB,
                                                       out_name=fc)[0]
        #----------------------------------------------------------------------
        def setUp(self):
            self._dir = arcpy.env.scratchFolder#r"c:\temp\testing"
            self._shp = "myshptest.shp"
            self._gdb = arcpy.env.scratchGDB

            if os.path.isdir(self._dir):
                shutil.rmtree(self._dir, ignore_errors=True)
            os.makedirs(self._dir)
        #----------------------------------------------------------------------
        def test_from_layer(self):
            """test io.from_layer"""

            url = fs_urls[0]
            sdf = pd.DataFrame.spatial.from_layer(layer=Service(url=url))
            self.assertIsInstance(sdf, pd.DataFrame)
            self.assertTrue(_is_geoenabled(sdf))
        #----------------------------------------------------------------------
        def test_to_featureclass_shp(self):
            url = fs_urls[0]
            fl = FeatureLayer(url=url)
            sdf = fl.query(where="OBJECTID < 10", as_df=True)
            wrksp = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex[:4])
            if os.path.isdir(wrksp) == False:
                os.makedirs(wrksp)
            else:
                shutil.rmtree(wrksp, ignore_errors=True)
                os.makedirs(wrksp)

            fc = sdf.spatial.to_featureclass(os.path.join(wrksp, "mydataset.shp"))
            self.assertTrue(os.path.isfile(fc))
            shutil.rmtree(wrksp, ignore_errors=True)
        #----------------------------------------------------------------------
        @unittest.skipIf(HAS_ARCPY == False, "ArcPy Not Installed, Skipping")
        def test_to_featureclass_fgdb(self):
            url = fs_urls[0]
            from arcgis.features import FeatureLayer
            fl = FeatureLayer(url=url)
            sdf = fl.query(where="OBJECTID < 10", as_df=True)

            wrksp = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex[:4])
            if os.path.isdir(wrksp) == False:
                os.makedirs(wrksp)
            else:
                shutil.rmtree(wrksp, ignore_errors=True)
                os.makedirs(wrksp)
            fgdb = arcpy.management.CreateFileGDB(wrksp, "scratch.gdb")[0]

            fc = sdf.spatial.to_featureclass(os.path.join(fgdb, "data12a"))
            self.assertTrue(arcpy.Exists(fc))
            arcpy.Delete_management(fgdb)
            shutil.rmtree(wrksp, ignore_errors=True)
        #----------------------------------------------------------------------
        def test_from_featureclass(self):
            """tests reading from spatial data"""
            sdf = pd.DataFrame.spatial.from_featureclass(r"./spatial/aoi.shp")
            self.assertIsInstance(sdf, pd.DataFrame)
            self.assertTrue(_is_geoenabled(sdf))
        #----------------------------------------------------------------------
        def test_to_pickle(self):
            """tests exporting at a frame to pickle"""
            pklout = os.path.join(tempfile.gettempdir(), "export.pkl")
            if os.path.isfile(pklout):
                os.remove(pklout)
            sdf = pd.DataFrame.spatial.from_featureclass(r"./spatial/aoi.shp")
            sdf.to_pickle(pklout)
            self.assertTrue(os.path.isfile(pklout))
            os.remove(pklout)
        #----------------------------------------------------------------------
        def test_from_pickle(self):
            """tests loading from pickle"""
            pklin = r"./spatial/sample.pkl"
            sdf = pd.read_pickle(pklin)
            self.assertTrue(_is_geoenabled(sdf))

    ########################################################################
    #@unittest.SkipTest
    class TestCaseGeoAccessor(unittest.TestCase):
        """
        Tests the GeoAccessor Methods and Properties
        """
        def setUp(self):
            sr = arcpy.SpatialReference(4326)
            self._coords = [[0, 1], [1, 1], [2, 3]]

            geojson_point = {
                "type": "Point",
                "coordinates": [0.0, 1.0]}
            pt = arcpy.AsShape(geojson_point).projectAs(sr)
            geojson_point = {
                "type": "Point",
                "coordinates": [1.0, 1.0]}
            pt1 = arcpy.AsShape(geojson_point).projectAs(sr)
            geojson_point = {
                "type": "Point",
                "coordinates": [2.0, 3.0]}
            pt2 = arcpy.AsShape(geojson_point).projectAs(sr)
            geojson_linestring = {
                "type": "LineString",
                "coordinates": [[5.0, 4.0], [8.0, 7.0]]}
            polyline = arcpy.AsShape(geojson_linestring).projectAs(sr)
            geojson_linestring = {
                "type": "LineString",
                "coordinates": [[1.0, 1.0], [10.0, 100.0]]}
            polyline2 = arcpy.AsShape(geojson_linestring).projectAs(sr)
            geojson_polygon = {
                "type": "Polygon",
                "coordinates": [
                    [[10.0, 0.0], [20.0, 0.0], [20.0, 10.0], [10.0, 10.0],
                     [10.0, 0.0]]]}
            polygon = arcpy.AsShape(geojson_polygon).projectAs(sr)
            geojson_polygon = {
                "type": "Polygon",
                "coordinates": [
                    [[0.0, 0.0],
                     [10.0, 0.0],
                     [10.0, 5.0],
                     [5.0, 5.0],
                     [0.0, 0.0]]]}
            polygon2 = arcpy.AsShape(geojson_polygon).projectAs(sr)

            self._attributes = [['A', 1, 2],
                                ['B', 13, -2.99],
                                ['C', 1-(4**3), 2**9]]
            self._col = ['APPLE', "BLUE", "ROGERWILCO"]
            self.geom_pts = [pt, pt1, pt2]
            self.geom_ptgeoms = [pt, pt1, pt2]
            self.geom_lines = [polyline, polyline2]
            self.geom_polygon = [polygon, polygon2]
        def test_df_geom_to_sdf(self):
            """test the initialization where a dataframe and geometry list is given"""
            from arcgis.geometry import Geometry, Polygon
            df = pd.DataFrame(data=self._attributes, columns=self._col)
            geoms = [Geometry(g) for g in self.geom_ptgeoms]
            df['SHAPE'] = geoms
            df.spatial.set_geometry("SHAPE")
            self.assertTrue(_is_geoenabled(df))
        #----------------------------------------------------------------------
        def test_df_geom_to_sdf_inplace(self):
            """test initialization and returning dataframe from set_geometry method"""
            from arcgis.geometry import Geometry, Polygon
            df = pd.DataFrame(data=self._attributes, columns=self._col)
            geoms = [Geometry(g) for g in self.geom_ptgeoms]
            df['SHAPE'] = geoms
            new_df = df.spatial.set_geometry("SHAPE", inplace=False)
            self.assertTrue(_is_geoenabled(new_df))
        #----------------------------------------------------------------------
        def test_spatial_propeties(self):
            """tests the properties off of the 'spatial' namespace"""
            from arcgis.geometry import Geometry, Polygon
            from scipy.spatial import cKDTree, KDTree
            from arcgis.geometry._types import SpatialReference
            df = pd.DataFrame(data=self._attributes, columns=self._col)
            geoms = [Geometry(g) for g in self.geom_ptgeoms]
            df['SHAPE'] = geoms
            sp = df.spatial
            sp.set_geometry("SHAPE")
            assert isinstance(sp, GeoAccessor)
            assert sp.area == 0
            assert isinstance(sp.bbox, (tuple, list, Polygon))
            assert isinstance(sp.centroid, (dict, list, tuple))
            assert isinstance(sp.distance_matrix(), (cKDTree, KDTree))
            assert isinstance(sp.full_extent, (tuple, list))
            assert isinstance(sp.geometry_type, (str, list))
            assert sp.length >= 0
            assert isinstance(sp.name, str)
            assert isinstance(sp.sr, (dict, SpatialReference))
            assert sp.validate()
            assert sp.validate(True)
            assert isinstance(sp.voronoi(), pd.Series)
        #----------------------------------------------------------------------
        def test_spatial_join(self):
            """tests the spatial join"""
            from arcgis.geometry import Geometry, Polygon
            from scipy.spatial import cKDTree, KDTree
            from arcgis.geometry._types import SpatialReference
            sdf1 = pd.DataFrame.spatial.from_featureclass(r"./spatial/area_of_int.shp")
            sdf2 = pd.DataFrame.spatial.from_featureclass(r"./spatial/training.shp")
            final_right = sdf1.spatial.join(sdf2, 'right')
            assert isinstance(final_right, pd.DataFrame)
            assert _is_geoenabled(final_right)
            final_left = sdf1.spatial.join(sdf2, 'left')
            assert len(final_left) == 34
            assert len(sdf1.spatial.join(sdf2, 'inner')) == 34
        #----------------------------------------------------------------------
        def test_ga_project(self):
            """tests the geoaccessor"""
            sdf = pd.DataFrame.spatial.from_featureclass(r"./spatial/area_of_int.shp")
            ga = sdf.spatial
            isinstance(ga, GeoAccessor)
            assert ga.project(spatial_reference=4326)
            assert ga.sr['wkid'] == 4326
            ga.sr = 3857
            assert ga.sr['wkid'] in [3857, 102100]
        #----------------------------------------------------------------------
        def test_overlay_ops(self):
            """tests the various overlay operations."""
            sdf = pd.DataFrame.spatial.from_featureclass(r"./spatial/area_of_int.shp")
            sdf2 = pd.DataFrame.spatial.from_featureclass(r"./spatial/training.shp")
            ga = sdf.spatial
            isinstance(ga, GeoAccessor)
            union = ga.overlay(sdf=sdf2)
            erase = ga.overlay(sdf2, 'erase')
            identity = ga.overlay(sdf2, 'identity')
            intersection = ga.overlay(sdf2, 'intersection')
        #----------------------------------------------------------------------
        def test_ga_relationship(self):
            """GA Relationship Method"""
            sdf = pd.DataFrame.spatial.from_featureclass(r"./spatial/area_of_int.shp")
            sdf2 = pd.DataFrame.spatial.from_featureclass(r"./spatial/training.shp")
            ga = sdf.spatial
            isinstance(ga, GeoAccessor)
            df1 = ga.relationship(other=sdf2, op='contains')
            assert isinstance(df1, pd.DataFrame)
            df2 = ga.relationship(other=sdf2, op='crosses')
            assert isinstance(df2, pd.DataFrame)
            df3 = ga.relationship(other=sdf2, op='disjoint')
            assert isinstance(df3, pd.DataFrame)
            df4 = ga.relationship(other=sdf, op='equals')
            assert isinstance(df4, pd.DataFrame)
            df5 = ga.relationship(other=sdf2, op='equals')
            assert isinstance(df5, pd.DataFrame)
            df6 = ga.relationship(other=sdf2, op='overlaps')
            assert isinstance(df6, pd.DataFrame)
            df7 = ga.relationship(other=sdf2, op='touches')
            assert isinstance(df7, pd.DataFrame)
            df8 = ga.relationship(other=sdf2, op='within')
            assert isinstance(df8, pd.DataFrame)

        #----------------------------------------------------------------------
        def test_ga_select(self):
            """tests the select operation"""
            sdf = pd.DataFrame.spatial.from_featureclass(r"./spatial/area_of_int.shp")
            sdf2 = pd.DataFrame.spatial.from_featureclass(r"./spatial/training.shp")
            ga = sdf.spatial
            select = ga.select(other=sdf2)
        #----------------------------------------------------------------------
        def test_to_methods(self):
            """test the GeoAccessor to methods"""
            sdf = pd.DataFrame.spatial.from_featureclass(r"./spatial/area_of_int.shp")
            ga = sdf.spatial
            isinstance(ga, GeoAccessor)
            fs = ga.to_featureset()
            fc = ga.to_feature_collection(name='amazing feature collection')
            assert fs
            assert fc
    ########################################################################
    #@unittest.SkipTest
    class TestCaseGeoSeriesAccessor(unittest.TestCase):
        """Tests the `geom` namespace on the pd.Series object"""
        #####pd.Series.geom PROPERTY TESTS####################################################################

        def setUp(self):
            self._HAS_SHAPELY = False
            try:
                import shapely
                self._HAS_SHAPELY = True
            except:
                pass
            from arcgis.geometry import Geometry
            self._sdf = pd.read_pickle(r"./spatial/sample.pkl")
            self._pt = Geometry({"x" : 1, "y" : 1, "spatialReference" : {"wkid" : 4326}})
            self._pt2 = Geometry({"x" : 2.22, "y" : -1.5, "spatialReference" : {"wkid" : 4326}})
            self._pt_inside = Geometry({"x" : 1.167, "y" : 0.833, "spatialReference" : {"wkid" : 4326}})
            self._line = Geometry({
                "paths" : [[.5,.5], [1, 1]],
                "spatialReference" : {"wkid" : 4326}
            })
            self._polygon = Geometry({
                "rings" : [[[.5,.5],[1,1],[1.5,1.5], [1.5, .5], [.5,.5]]],
                "spatialReference" : {"wkid" : 4326}
            })
        #@unittest.SkipTest
        def test_namespace(self):
            """tests that the namespace exists"""
            assert self._sdf.spatial.name
            assert hasattr(self._sdf[self._sdf.spatial.name], 'geom')
            assert isinstance(self._sdf[self._sdf.spatial.name].geom, GeoSeriesAccessor)
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_properties(self):
            """tests the properties off of the geom namespace"""
            geom = self._sdf[self._sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            assert geom.area.sum() >= 0
            if HAS_ARCPY:
                assert geom.as_arcpy.isnull().all() == False
                assert geom.as_arcpy.name == 'as_arcpy'
            if self._HAS_SHAPELY:
                assert geom.as_shapely.isnull().all() == False
                assert geom.as_shapely.name == 'as_shapely'
            assert geom.centroid.isnull().all() == False
            assert geom.centroid.dtype == 'object'
            assert geom.extent.isnull().all() == False
            assert geom.first_point.isnull().all() == False
            assert geom.first_point.dtype.name == 'geometry'
            assert geom.geometry_type.isnull().all() == False
            assert geom.geoextent.isnull().all() == False
            assert geom.hull_rectangle.isnull().all() == False
            assert geom.is_empty.isnull().all() == False
            assert geom.is_multipart.isnull().all() == False
            assert geom.is_valid.isnull().all() == False
            assert geom.JSON.isnull().all() == False
            assert geom.label_point.isnull().all() == False
            assert geom.label_point.dtype.name == 'geometry'
            assert geom.last_point.isnull().all() == False
            assert geom.last_point.dtype.name == 'geometry'
            assert geom.length.isnull().all() == False
            assert geom.length3D.isnull().all() == False
            assert geom.part_count.isnull().all() == False
            assert geom.point_count.isnull().all() == False
            assert geom.spatial_reference.isnull().all() == False
            assert geom.true_centroid.isnull().all() == False
            assert geom.true_centroid.dtype.name == 'geometry'
            assert geom.WKB.isnull().all() == False
            assert geom.WKT.isnull().all() == False
        ## GeoSeriesAccessor Method Tests #################################
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_method_angle_distance_to(self):
            """tests the angle distance to method off of the geom namespace"""
            geom = self._sdf[self._sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.angle_distance_to(second_geometry=self._pt2, method="PLANAR")
            r2 = geom.angle_distance_to(second_geometry=self._pt2, method="GEODESIC")
            r3 = geom.angle_distance_to(second_geometry=self._pt2, method="GREAT_ELLIPTIC")
            r4 = geom.angle_distance_to(second_geometry=self._pt2, method="PRESERVE_SHAPE")
            r5 = geom.angle_distance_to(second_geometry=self._pt2, method="LOXODROME")
            assert r1.isnull().all() == False
            assert r2.isnull().all() == False
            assert r3.isnull().all() == False
            assert r4.isnull().all() == False
            assert r5.isnull().all() == False
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_method_buffer(self):
            """tests the buffer method off of the geom namespace"""
            geom = self._sdf[self._sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.buffer(10)
            assert r1.isnull().all() == False
            assert r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_method_contains(self):
            """tests the contains method off of the geom namespace"""
            geom = self._sdf[self._sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.contains(second_geometry=self._pt_inside)
            assert r1.isnull().all() == False
            #assert r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_method_clip(self):
            """tests the clip method off of the geom namespace"""
            geom = self._sdf[self._sdf.spatial.name].geom
            ext = self._sdf.SHAPE.geom.extent[0]
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.clip(envelope=ext)
            assert r1.isnull().all() == False
            assert r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_convex_hull(self):
            """tests the convex hull method off of the geom namespace"""
            geom = self._sdf[self._sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.convex_hull()
            assert r1.isnull().all() == False
            assert r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_crosses(self):
            """tests the crosses method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            sdf.loc[0, 'SHAPE'] = self._polygon.JSON
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            cross_line = Geometry({
                "paths" : [[[.51, .51], [3, .49]]],
                "spatialReference" : {"wkid" : 4326}
            })
            no_cross_line = Geometry({
                "paths" : [[[51, 51], [3, 49]]],
                "spatialReference" : {"wkid" : 4326}
            })
            sdf.spatial.name

            r1 = geom.crosses(second_geometry=cross_line) # SHOULD be ALL True
            r2 = geom.crosses(second_geometry=no_cross_line) # SHOULD be ALL False
            assert isinstance(r1, pd.Series)
            assert isinstance(r2, pd.Series)
        #------------------------------------------------------------------
        @unittest.SkipTest
        def test_cut(self):
            """tests the cut method off of the geom namespace"""
            l = Geometry({"paths":[[[-97.061379999787107,32.837000000449734],
                                    [-97.061270000110369,32.832000000099981]],
                                   ],"spatialReference":{"wkid":4326,"latestWkid":4326}})

            v = GeoArray([geoms[3]])
            line = geoms[2]
            df = pd.DataFrame({"SHAPE": v})
            df.spatial.set_geometry("SHAPE")
            #df.SHAPE.geom.
            r = df.SHAPE.geom.cut(l)
            assert r.dtype.name.lower() == 'geometry'
        #------------------------------------------------------------------
        def test_desnify(self):
            """tests the densify method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.densify(method="DISTANCE", distance=.001, deviation=0.000001)
            assert r1.isnull().all() == False
            assert r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        def test_difference(self):
            """tests the difference method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.difference(second_geometry=self._polygon)
            assert r1.isnull().all() == False
            assert r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        def test_disjoint(self):
            """tests the disjoint method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.disjoint(second_geometry=sdf.SHAPE[0])
            r2 = geom.disjoint(second_geometry=self._polygon)
            assert isinstance(r1, pd.Series)
            assert isinstance(r2, pd.Series)
        #------------------------------------------------------------------
        def test_distance_to(self):
            """tests the distance to method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.distance_to(second_geometry=self._pt)
            assert r1.sum() >= 0
            assert isinstance(r1, pd.Series)
        #------------------------------------------------------------------
        def test_equals(self):
            """tests the equals method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.equals(sdf.SHAPE[0])
            r2 = geom.equals(self._pt)
            assert isinstance(r1, pd.Series)
            assert isinstance(r2, pd.Series)
        #------------------------------------------------------------------
        def test_generalize(self):
            """tests the generalize method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.generalize(max_offset=0.001)
            assert isinstance(r1, pd.Series)
            assert r1.dtype.name == 'geometry'
            assert r1.isnull().all() == False
        #------------------------------------------------------------------
        def test_get_area(self):
            """tests the get_area method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom

            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.get_area(method="PLANAR", units="ACRES")
            assert isinstance(r1, pd.Series)
            #assert r1.dtype.name == 'geometry'
            assert r1.isnull().all() == False
            assert r1.sum() >= 0
        #------------------------------------------------------------------
        def test_get_length(self):
            """tests the get_length method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom

            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.get_length(method="PLANAR", units="FEET")
            assert isinstance(r1, pd.Series)
            #assert r1.dtype.name == 'geometry'
            assert r1.isnull().all() == False
            assert r1.sum() >= 0
        #------------------------------------------------------------------
        def test_get_area(self):
            """tests the get_area method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.get_area(method="PLANAR", units="ACRES")
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
            assert r1.sum() >= 0
        #------------------------------------------------------------------
        def test_get_part(self):
            """tests the get_part method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.get_part(0)
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
        #------------------------------------------------------------------
        def test_intersect(self):
            """tests the intersect method off of the geom namespace"""
            from arcgis.geometry import Geometry
            cross_line = Geometry({'paths': [[[0.51, 0.51], [3, 0.49]]], 'spatialReference': {'wkid': 4326, 'latestWkid': 4326}})
            sdf = self._sdf.copy()
            sdf.loc[0, 'SHAPE'] = self._polygon.JSON
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.intersect(second_geometry=cross_line)
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
            assert r1.dtype.name == 'bool'
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_measure_on_line(self):
            """tests the measure_on_line method off of the geom namespace"""
            v = GeoArray([geoms[2]])
            df = pd.DataFrame({"SHAPE": v})
            r = df.SHAPE.geom.measure_on_line(geoms[0],True)
            assert isinstance(r, pd.Series)
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_overlaps(self):
            """tests the overlaps method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.overlaps(second_geometry=sdf.SHAPE[0])
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_point_from_angle_and_distance(self):
            """tests the point_from_angle_and_distance method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.point_from_angle_and_distance(angle=.10, distance=1, method="PRESERVE_SHAPE")
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_position_along_line(self):
            """tests the position_along_line method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.position_along_line(25, True)
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False #
            r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_project_as(self):
            """tests the project_as method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.project_as(3857)
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
            assert r1.dtype.name == 'geometry'
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_query_point_and_distance(self):
            """tests the query_point_and_distance method off of the geom namespace"""
            v = GeoArray([geoms[2]])
            df = pd.DataFrame({"SHAPE": v})
            df.spatial.set_geometry("SHAPE")
            pt = Geometry({'x' : -97.06133, 'y' : 32.8379, 'spatialReference' : {'wkid' : 4326}})
            r = df.SHAPE.geom.query_point_and_distance(pt, True)
            assert r.dtype.name.lower() == 'object'
            assert isinstance(r[0], tuple)
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_segment_along_line(self):
            """tests the segment_along_line method off of the geom namespace"""
            v = GeoArray([geoms[2]])
            df = pd.DataFrame({"SHAPE": v})
            df.spatial.set_geometry("SHAPE")
            r = df.SHAPE.geom.segment_along_line(.1,.30, True)
            assert r.dtype.name.lower() == "geometry"
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_snap_to_line(self):
            """tests the snap_to_line method off of the geom namespace"""
            pt = Geometry({'x' : -97.06133, 'y' : 32.8379, 'spatialReference' : {'wkid' : 4326}})
            v = GeoArray([geoms[2]])
            df = pd.DataFrame({"SHAPE": v})
            df.spatial.set_geometry("SHAPE")
            r = df.SHAPE.geom.snap_to_line(pt)
            assert r.dtype.name.lower() == "geometry"
            assert isinstance(r[0], Geometry)
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_symmetric_difference(self):
            """tests the symmetric_difference method off of the geom namespace"""
            self.setUp()
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.symmetric_difference(second_geometry=sdf.SHAPE[0].buffer(.25))
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_touches(self):
            """tests the touches method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.touches(second_geometry=sdf.SHAPE[0])
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_union(self):
            """tests the union method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.touches(second_geometry=sdf.SHAPE[0])
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False
        #------------------------------------------------------------------
        #@unittest.SkipTest
        def test_within(self):
            """tests the within method off of the geom namespace"""
            from arcgis.geometry import Geometry
            sdf = self._sdf.copy()
            geom = sdf[sdf.spatial.name].geom
            isinstance(geom, GeoSeriesAccessor)
            r1 = geom.within(second_geometry=sdf.SHAPE[0])
            assert isinstance(r1, pd.Series)
            assert r1.isnull().all() == False


if __name__ == "__main__":
    unittest.main()
