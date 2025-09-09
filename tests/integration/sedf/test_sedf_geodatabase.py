import unittest
import os
import pandas as pd
import shutil
from config import get_resource_path
from arcgis.gis import GIS  # Do not remove

try:
    import arcpy

    arcpy.env.overwriteOutput = True
    HAS_ARCPY = True
except:
    HAS_ARCPY = False


@unittest.skipIf(not HAS_ARCPY, "ArcPy is not installed")
class TestSedfGeodatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fgdb_path = get_resource_path(
            "staging_data/geodatabase/TestFileGDB.gdb.zip", unique_copy=True, unzip=True
        )
        fgdb_path = os.path.join(fgdb_path, "TestFileGDB.gdb")
        assert os.path.exists(fgdb_path), "Did not properly extract the fgdb zip"

        cls.file_gdb_fc = os.path.join(fgdb_path, "HCADSubset2k")

        mobile_gdb_path = get_resource_path(
            "staging_data/geodatabase/TestMobileGDB.geodatabase", unique_copy=True
        )
        cls.mobile_gdb_fc = os.path.join(mobile_gdb_path, "HCADSubset2k")

    def test_fgdb_to_df(self):
        sdf = pd.DataFrame.spatial.from_featureclass(
            self.file_gdb_fc,
            sr=2278,
        )
        self.assertIsInstance(
            sdf, pd.DataFrame, msg=f"Got type: {type(sdf)} instead of pd.DataFrame"
        )

    def test_mobile_to_df(self):
        sdf = pd.DataFrame.spatial.from_featureclass(
            self.mobile_gdb_fc,
            sr=2278,
        )
        self.assertIsInstance(
            sdf, pd.DataFrame, msg=f"Got type: {type(sdf)} instead of pd.DataFrame"
        )
