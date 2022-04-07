import os
import unittest
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor


RUN = os.path.isdir("./testdata.gdb")


@unittest.skipIf(RUN == False, "missing data")
class TestFromFeatureClass(unittest.TestCase):
    def test_from_string_fc(self):
        """tests reading a SHP/FGDB from fiona"""
        fc = r"./testdata.gdb/world30"
        assert isinstance(pd.DataFrame.spatial.from_featureclass(fc), pd.DataFrame)

    def test_from_path_fc(self):
        """tests reading a SHP/FGDB from fiona"""
        from pathlib import Path

        fc = r"./testdata.gdb/world30"
        assert isinstance(
            pd.DataFrame.spatial.from_featureclass(Path(fc)), pd.DataFrame
        )

    def test_failure_path_fc(self):
        """tests that ValueError is raised"""
        with self.assertRaises(ValueError):
            pd.DataFrame.spatial.from_featureclass(12345)


if __name__ == "__main__":
    unittest.main()
