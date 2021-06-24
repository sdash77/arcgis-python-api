import arcgis

try:
    import arcpy

    HASARCPY = True
except:
    HASARCPY = False
from arcgis.features import SpatialDataFrame
import pandas as pd
import json
import unittest

if HASARCPY:
    geom_pts = [arcpy.Point(X=1, Y=2), arcpy.Point(X=2, Y=3), arcpy.Point(X=3, Y=4)]
    geom_geom_pt = [
        arcpy.PointGeometry(arcpy.Point(X=1, Y=2), 4326),
        arcpy.PointGeometry(arcpy.Point(X=11, Y=21), 4326),
        arcpy.PointGeometry(arcpy.Point(X=2, Y=23), 4326),
    ]
    geom_geom_pt_str = [
        arcpy.PointGeometry(arcpy.Point(X=1, Y=2), 4326).JSON,
        arcpy.PointGeometry(arcpy.Point(X=11, Y=21), 4326).JSON,
        arcpy.PointGeometry(arcpy.Point(X=2, Y=23), 4326).JSON,
    ]
    geom_geom_dict = [
        json.loads(arcpy.PointGeometry(arcpy.Point(X=1, Y=2), 4326).JSON),
        json.loads(arcpy.PointGeometry(arcpy.Point(X=11, Y=21), 4326).JSON),
        json.loads(arcpy.PointGeometry(arcpy.Point(X=2, Y=23), 4326).JSON),
    ]
    geom_geom_arcgis_objs = [
        arcgis.geometry.Geometry(
            json.loads(arcpy.PointGeometry(arcpy.Point(X=1, Y=2), 4326).JSON)
        ),
        arcgis.geometry.Geometry(
            json.loads(arcpy.PointGeometry(arcpy.Point(X=2, Y=3), 4326).JSON)
        ),
        arcgis.geometry.Geometry(
            json.loads(arcpy.PointGeometry(arcpy.Point(X=4, Y=5), 4326).JSON)
        ),
    ]

    ALL_GEOMS = [geom_geom_arcgis_objs, geom_geom_pt, geom_pts]
    DF = pd.DataFrame([[1, 2, 3], [2, 3, 4], [3, 4, 5]], columns=["A", "B", "C"])
    DF_GEOMS = pd.DataFrame(
        [
            [1, 2, 3, geom_geom_arcgis_objs[0]],
            [2, 3, 4, geom_geom_arcgis_objs[1]],
            [3, 4, 5, geom_geom_arcgis_objs[2]],
        ],
        columns=["A", "B", "C", "LOCATION"],
    )

    class Test_SR_SDF(unittest.TestCase):
        # @unittest.SkipTest
        def test_init_geoms(self):
            """tests the"""
            test = []
            for geom in ALL_GEOMS:
                sdf = SpatialDataFrame(DF, geometry=geom)
                test.append(isinstance(sdf, SpatialDataFrame))
            self.assertTrue(all(test))

        # @unittest.SkipTest
        def test_set_geoms(self):
            """tests the"""
            test = []
            for i in [True, False]:
                for geom in ALL_GEOMS:
                    sdf = SpatialDataFrame(DF)
                    sdf.set_geometry(col=geom, inplace=i)
                    test.append(isinstance(sdf, SpatialDataFrame))
            self.assertTrue(all(test))

        # @unittest.SkipTest
        def test_set_geoms_wkid(self):
            """tests the"""
            test = []
            for i in [True, False]:
                for geom in ALL_GEOMS:
                    sdf = SpatialDataFrame(DF)
                    sdf.set_geometry(col=geom, inplace=i, sr=4326)
                    test.append(isinstance(sdf, SpatialDataFrame))
            self.assertTrue(all(test))

        # @unittest.SkipTest
        def test_init_sdf_wkid(self):
            """tests the"""
            test = []
            for geom in ALL_GEOMS:
                sdf = SpatialDataFrame(DF, geometry=geom, sr=4326)
                test.append(isinstance(sdf, SpatialDataFrame))
            self.assertTrue(all(test))

        def test_set_geom_columns(self):
            """tests the"""
            test = []
            for i in [True, False]:  # True,
                sdf = SpatialDataFrame(DF_GEOMS)
                sdf.set_geometry("LOCATION", inplace=i, sr=4326)
                test.append(isinstance(sdf, SpatialDataFrame))
            self.assertTrue(all(test))


if __name__ == "__main__":
    unittest.main()
