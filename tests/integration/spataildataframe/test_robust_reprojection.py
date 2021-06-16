import unittest
import pandas as pd
import os, shutil
from arcgis.geometry import _types
from arcgis.features import SpatialDataFrame
from arcgis.features._data.geodataset import GeoSeries

try:
    import arcpy

    HAS_ARCPY = True
except:
    HAS_ARCPY = False
if HAS_ARCPY:

    class RobustReProjectionTest(unittest.TestCase):
        def setUp(self):
            import random

            self._sr = arcpy.SpatialReference(4326)
            geojson_polygon = {
                "type": "Polygon",
                "coordinates": [
                    [[0.0, 0.0], [10.0, 0.0], [10.0, 5.0], [5.0, 5.0], [0.0, 0.0]]
                ],
            }
            geojson_polygon2 = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [0.0, random.randint(0, 10)],
                        [random.randint(1, 10), 0.0],
                        [10, random.randint(0, 5)],
                        [5.0, 5.0],
                        [0.0, random.randint(0, 10)],
                    ]
                ],
            }
            geojson_polygon3 = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [0.0, random.randint(0, 10)],
                        [random.randint(1, 10), 0.0],
                        [10, random.randint(0, 5)],
                        [5.0, 5.0],
                        [0.0, random.randint(0, 10)],
                    ]
                ],
            }
            self._wkt = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision"
            self._geoms = [
                arcpy.AsShape(geojson_polygon).projectAs(self._sr),
                arcpy.AsShape(geojson_polygon2).projectAs(self._sr),
                arcpy.AsShape(geojson_polygon3).projectAs(self._sr),
            ]  # * 3
            self._attributes = [
                ["A", 1, 2],
                ["B", 13, -2.99],
                ["C", 1 - (4 ** 3), 2 ** 9],
            ]
            self._col = ["APPLE", "BLUE", "ROGERWILCO"]
            self._df = pd.DataFrame.from_records(
                data=self._attributes, columns=self._col
            )

        def test_create_from_arcpy(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            self.assertIsInstance(sdf1.sr.as_arcpy, arcpy.SpatialReference)

        def test_create_from_wkid_arcgis(self):
            sdf2 = SpatialDataFrame(
                self._df,
                geometry=self._geoms,
                sr=_types.SpatialReference({"wkid": 4326}),
            )
            self.assertIsInstance(sdf2.sr.as_arcpy, arcpy.SpatialReference)

        def test_create_sdf_from_wkt_arcgis(self):
            sdf3 = SpatialDataFrame(
                self._df,
                geometry=self._geoms,
                sr=_types.SpatialReference({"wkt": self._wkt}),
            )
            self.assertIsInstance(sdf3.sr.as_arcpy, arcpy.SpatialReference)

        def test_create_sdf_from_int(self):
            sdf4 = SpatialDataFrame(self._df, geometry=self._geoms, sr=4326)
            self.assertIsInstance(sdf4.sr.as_arcpy, arcpy.SpatialReference)

        def test_create_sdf_from_wkt(self):
            sdf5 = SpatialDataFrame(self._df, geometry=self._geoms, sr=self._wkt)
            self.assertIsInstance(sdf5.sr.as_arcpy, arcpy.SpatialReference)

        #######################################################################
        ##  TEST RE-PROJECTING WHOLE DF                                       #
        #######################################################################
        def test_reproject_arcpy(self):
            sr_new = arcpy.SpatialReference(3857)
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            self.assertIsInstance(
                sdf1.reproject(spatial_reference=sr_new), SpatialDataFrame
            )

        def test_reproject_arcgis_wkid(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            a_sr_wkid = _types.SpatialReference({"wkid": 3857})
            self.assertIsInstance(
                sdf1.reproject(spatial_reference=a_sr_wkid), SpatialDataFrame
            )

        def test_reproject_arcgis_wkt(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            wkt = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
            a_sr_wkt = _types.SpatialReference({"wkt": wkt})
            self.assertIsInstance(
                sdf1.reproject(spatial_reference=a_sr_wkt), SpatialDataFrame
            )

        def test_reproject_wkid(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            wkid = 3857
            self.assertIsInstance(
                sdf1.reproject(spatial_reference=wkid), SpatialDataFrame
            )

        def test_project_wkt(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            wkt = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
            self.assertIsInstance(
                sdf1.reproject(spatial_reference=wkt), SpatialDataFrame
            )

        #######################################################################
        ##  TEST RE-PROJECTING GeoSeries                                      #
        #######################################################################
        def test_project_as_arcpy(self):
            sr_new = arcpy.SpatialReference(3857)
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            self.assertIsInstance(sdf1.geometry.project_as(sr_new), GeoSeries)

        def test_reproject_arcgis_wkid(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            a_sr_wkid = _types.SpatialReference({"wkid": 3857})
            self.assertIsInstance(sdf1.geometry.project_as(a_sr_wkid), GeoSeries)

        def test_reproject_arcgis_wkt(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            wkt = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
            a_sr_wkt = _types.SpatialReference({"wkt": wkt})
            self.assertIsInstance(sdf1.geometry.project_as(a_sr_wkt), GeoSeries)

        def test_reproject_wkid(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            wkid = 3857
            self.assertIsInstance(sdf1.geometry.project_as(wkid), GeoSeries)

        def test_project_wkt(self):
            sdf1 = SpatialDataFrame(
                self._df, geometry=self._geoms, sr=arcpy.SpatialReference(4326)
            )
            wkt = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]];-20037700 -30241100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
            self.assertIsInstance(sdf1.geometry.project_as(wkt), GeoSeries)


if __name__ == "__main__":
    unittest.main()
