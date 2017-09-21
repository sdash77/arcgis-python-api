"""
Tests Related to Spatial Data Frame
"""
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

from arcgis.geometry import _types
from arcgis import SpatialDataFrame
from arcgis._impl._server import Service
from arcgis.features._data.geodataset.io import from_layer, to_featureclass, to_sqlite, from_featureclass
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
        def setUp(self):
            self._fs_urls = ["https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/HSEC/FeatureServer/0",# Point
                             "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Hurricanes/MapServer/1", # Polyline
                             "https://sampleserver6.arcgisonline.com/arcgis/rest/services/MontgomeryQuarters/MapServer/0"] #polygon
            self._table_url =  "https://sampleserver6.arcgisonline.com/arcgis/rest/services/ServiceRequest/MapServer/1" # table
        #----------------------------------------------------------------------
        def test_with_geometry(self):
            """test with geometries"""
            for url in self._fs_urls:
                fl = Service(url=url)
                res = fl.query().df
                self.assertIsInstance(res, SpatialDataFrame, msg=\
                                      "Got type: %s instead of SpatialDataFrame" % type(res))
        #----------------------------------------------------------------------
        def test_without_geometry(self):
            """table test"""
            fl = Service(url=self._table_url)
            res = fl.query().df
            self.assertIsInstance(res, pd.DataFrame, msg=\
                                  "Got type: %s instead of pandas.DataFrame" % type(res))
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
            url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/USA/MapServer/0"
            sdf = from_layer(layer=Service(url=url))
            geoms = sdf.geometry
            self.assertIsInstance(sdf, SpatialDataFrame)
        #----------------------------------------------------------------------
        def test_to_featureclass_shp(self):
            url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/HSEC/FeatureServer/0"
            sdf = from_layer(layer=Service(url=url))
            fc = to_featureclass(df=sdf,
                                 out_location=self._dir,
                                 out_name=self._shp)
            self.assertTrue(arcpy.Exists(fc))
        #----------------------------------------------------------------------
        def test_to_featureclass_fgdb(self):
            url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/HSEC/FeatureServer/0"
            sdf = from_layer(layer=Service(url=url))
            fc = to_featureclass(df=sdf,
                                 out_location=self._gdb,
                                 out_name="fgdb_test")
            self.assertTrue(arcpy.Exists(fc))
        #----------------------------------------------------------------------
        def test_to_sqlite(self):
            url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/HSEC/FeatureServer/0"
            sdf = from_layer(layer=Service(url=url))
            fc = to_sqlite(df=sdf,
                           out_folder=self._dir,
                           db_name="mydata.sqlite",
                           table_name="mysqlitetest")
            self.assertTrue(arcpy.Exists(fc))
        #----------------------------------------------------------------------
        def test_from_featureclass(self):
            from arcgis.features._data.geodataset.io import from_featureclass
            fc = self._construct_featureclass()
            spdf = from_featureclass(filename=fc)
            geom = spdf.geometry
            print(geom)
            self.assertIsInstance(spdf, SpatialDataFrame)

        def test_to_pickle(self):
            out_file = r"c:\temp\test.pkl"
            if os.path.isfile(out_file):
                os.remove(out_file)
            from arcgis.features._data.geodataset.io import from_featureclass
            fc = self._construct_featureclass()
            spdf = from_featureclass(filename=fc)
            spdf.to_pickle(out_file)
        #----------------------------------------------------------------------
        @unittest.skip
        def test_to_hdf(self):
            from uuid import uuid4
            out_file = r"c:\temp\%s.hf5" % uuid4().hex
            if os.path.isfile(out_file):
                os.remove(out_file)
            from arcgis.features._data.geodataset.io import from_featureclass
            fc = self._construct_featureclass()
            spdf = from_featureclass(filename=fc)
            spdf.to_hdf(out_file, uuid4().hex)
            self.assertTrue(out_file, os.path.isfile(out_file))
            os.remove(out_file)
            arcpy.Delete_management(fc)
        #----------------------------------------------------------------------
        @unittest.SkipTest
        def test_from_hdf(self):
            from uuid import uuid4
            key = uuid4().hex
            out_file = r"c:\temp\%s.hf5" % uuid4().hex
            if os.path.isfile(out_file):
                os.remove(out_file)
            from arcgis.features._data.geodataset.io import from_featureclass
            fc = self._construct_featureclass()
            spdf = from_featureclass(filename=fc)
            spdf.to_hdf(path_or_buf=out_file, key=key)
            spdf = SpatialDataFrame.from_hdf(out_file, key=key)
            self.assertIsInstance(spdf, SpatialDataFrame)
            os.remove(out_file)
            arcpy.Delete_management(fc)
        #----------------------------------------------------------------------
    ########################################################################
    #@unittest.SkipTest
    class SpatailDataFrameTest1(unittest.TestCase):
        """
        Tests the spatial dataframe using dummy data
        """
        def setUp(self):
            sr = arcpy.SpatialReference(4326)
            self._coords = [[0,1], [1,1], [2,3]]

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
            df = pd.DataFrame.from_records(data=self._attributes, columns=self._col)
            sdf = SpatialDataFrame(df,
                                   geometry=[arcpy.PointGeometry(arcpy.Point(X=r[0], Y=r[1])) \
                                             for r in self._coords])
            self.assertTrue(isinstance(sdf.geometry.all(), (arcpy.Geometry, _types.Geometry)), True)
        #####PROPERTY TESTS####################################################################

        def test_geoextent(self):
            res = []
            #,
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.geoextent, tuple))
            self.assertTrue(all(res))
        def test_JSON(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.JSON, pd.Series))
            self.assertTrue(all(res))
        def test_WKT(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.WKT, pd.Series))
            self.assertTrue(all(res))
        def test_WKB(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.WKB, pd.Series))
            self.assertTrue(all(res))
        def test_area(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.area, pd.Series))
            self.assertTrue(all(res))
        def test_centroid(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.centroid, GeoSeries))
            self.assertTrue(all(res))
        def test_extent(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.extent, pd.Series))
            self.assertTrue(all(res))
        def test_firstPoint(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.first_point, GeoSeries))
            self.assertTrue(all(res))
        def test_hullRectangle(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.hull_rectangle, pd.Series))
            self.assertTrue(all(res))
        def test_isMultipart(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.is_multipart, pd.Series))
            self.assertTrue(all(res))
        def test_labelPoint(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.label_point, GeoSeries))
            self.assertTrue(all(res))
        def test_lastPoint(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.last_point, GeoSeries))
            self.assertTrue(all(res))
        def test_length(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.length, pd.Series))
            self.assertTrue(all(res))
        def test_length3D(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.length3D, pd.Series))
            self.assertTrue(all(res))
        def test_partCount(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.part_count, pd.Series))
            self.assertTrue(all(res))
        def test_pointCount(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.point_count, pd.Series))
            self.assertTrue(all(res))
        def test_spatialReference(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.spatial_reference, pd.Series))
            self.assertTrue(all(res))
        def test_trueCentroid(self):
            res = []
            #,
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.true_centroid, pd.Series))
            self.assertTrue(all(res))
        def test_type(self):
            res = []
            #,
            from six import string_types
            from arcgis.features._data.geodataset import GeoSeries
            import pandas as pd
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                         self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                   geometry=[geom])
                res.append(isinstance(sdf.geometry_type, string_types))
                res.append(isinstance(sdf.geometry.geometry_type, string_types))
            self.assertTrue(all(res))
        ### Geometry Index Tests ###################################################################
        def test_create_spatial_index(self):
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                             self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                index = sdf.sindex
                res.append(isinstance(index, (quadtree.Index, rtree.RTree)))
            self.assertTrue(all(res))
        def test_searching_index(self):
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                             self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                index = sdf.sindex
                bbox = list(sdf.geoextent)
                res.append(len(index.intersect(bbox))>0)
            self.assertTrue(all(res))
        def test_searching_index_no_items(self):
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in [self.geom_ptgeoms[0],self.geom_pts[0],
                             self.geom_lines[0], self.geom_polygon[0]]:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                index = sdf.sindex
                bbox = [99,99,99,99]
                res.append(len(index.intersect(bbox))==0)
            self.assertTrue(all(res))
        ### Geometry Function Tests ################################################################
        def test_angleAndDistanceTo(self):
            """angleAndDistanceTo (other, {method})"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_ptgeoms:

                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.angle_distance_to(second_geometry=self.geom_ptgeoms[0]),
                                       pd.Series))
        def test_boundary(self):
            """boundary"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            count = 0
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                count += 1
                res.append( isinstance(sdf.boundary(),
                                       GeoSeries))
            self.assertTrue(all(res))
        def test_buffer(self):
            """buffer"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.buffer(1),
                                       GeoSeries))
            self.assertTrue(all(res))
        def test_clip(self):
            """clip"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.clip(geom.extent),
                                       GeoSeries))

            self.assertTrue(all(res))
        def test_contains(self):
            """contains"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.contains(geom),
                                       GeoSeries))

            self.assertTrue(all(res) == False)
        def test_convexhull(self):
            """convex hull"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.convex_hull(),
                                       GeoSeries))

            self.assertTrue(all(res))
        def test_crosses(self):
            """crosses"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.crosses(second_geometry=geom),
                                       pd.Series))

            self.assertTrue(all(res))
        def test_crosses(self):
            """crosses"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.crosses(second_geometry=geom),
                                       pd.Series))

            self.assertTrue(all(res))
        @unittest.skip("testing skipping")
        def test_densify(self):
            """densify"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.densify(method="GEODESIC", distance=10, deviation=1),
                                       GeoSeries))

            self.assertTrue(all(res))
        def test_difference(self):
            """difference"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.difference(second_geometry=geom),
                                       GeoSeries))

            self.assertTrue(all(res))
        def test_disjoint(self):
            """disjoint"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.disjoint(second_geometry=geom),
                                       GeoSeries))

            self.assertTrue(all(res) == False)
        def test_distanceTo(self):
            """distanceTo"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_pts:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.distance_to(second_geometry=geom),
                                       pd.Series))

            self.assertTrue(all(res))
        def test_equals(self):
            """equals"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_pts:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.equals(second_geometry=geom),
                                       pd.Series))
            self.assertTrue(all(res))
        def test_getArea(self):
            """getArea"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.get_area(method="PLANAR", units="SQUAREFEET"),
                                       pd.Series))
            self.assertTrue(all(res))
        def test_getLength(self):
            """getArea"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.get_length(method="PLANAR", units="FEET"),
                                       pd.Series))
            self.assertTrue(all(res))
        def test_getPart(self):
            """getPart"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.get_part(index=0),
                                       pd.Series))
            self.assertTrue(all(res))
        def test_intersect(self):
            """intersect"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.intersect(second_geometry=geom, dimension=4),
                                       pd.Series))
            self.assertTrue(all(res))
        def test_overlaps(self):
            """overlaps"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.overlaps(second_geometry=geom),
                                       pd.Series))
            self.assertTrue(all(res))
        def test_projectAs(self):
            """projectAs"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.project_as(spatial_reference=arcpy.SpatialReference(4326)),
                                       GeoSeries))
            self.assertTrue(all(res))
        def test_symetricalDifference(self):
            """symetricalDifference"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.symmetric_difference(second_geometry=geom),
                                       GeoSeries))
            self.assertTrue(all(res))
        def test_touches(self):
            """touches"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.touches(second_geometry=geom),
                                       GeoSeries))
            self.assertTrue(all(res) == False)
        def test_within(self):
            """union"""
            from arcgis.features._data.geodataset import GeoSeries
            from arcgis.features._data.geodataset.index import quadtree, rtree
            import pandas as pd
            res = []
            for geom in self.geom_polygon:
                df = pd.DataFrame.from_records(data=[self._attributes[0]], columns=self._col)
                sdf = SpatialDataFrame(df,
                                       geometry=[geom])
                res.append( isinstance(sdf.within(second_geometry=geom),
                                       GeoSeries))
            self.assertTrue(all(res) == False)
if __name__ == "__main__":
    unittest.main()