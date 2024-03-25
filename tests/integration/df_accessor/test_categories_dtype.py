import sys
import logging
import unittest
from arcgis.auth.tools import LazyLoader
from arcgis.auth.tools._util import detect_proxy
import pandas as pd
import numpy as np
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from integration.config import QALAB_ROOT_PATH


__logger__ = logging.getLogger()

try:
    arcpy = LazyLoader("arcpy", strict=True)
    SKIP_NO_ARCPY = False
except:
    SKIP_NO_ARCPY = True


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

import os
from utils.decorators import integration_test


@unittest.skipIf(SKIP_NO_ARCPY, "ArcPy not present, skipping this test.")
@integration_test
class TestCategoriesSeDF(unittest.TestCase):
    def test_categories_to_featureclass(self):
        fc = QALAB_ROOT_PATH + r"\df_accessor_test\world30.shp"
        if arcpy.Exists(fc):
            sdf = pd.DataFrame.spatial.from_featureclass(fc)

            sdf["cats_str"] = [
                "a" if i % 2 == 0 else "b" for i in range(len(sdf))
            ]
            sdf["cats_ints"] = [
                1 if i % 2 == 0 else 2 for i in range(len(sdf))
            ]
            sdf["cats_ints"] = sdf["cats_ints"].astype("category")
            sdf["cats_str"] = sdf["cats_str"].astype("category")
            out_fc = os.path.join(arcpy.env.scratchGDB, "outputfccats")
            sdf.spatial.to_featureclass(out_fc)
            assert arcpy.Exists(out_fc)

    def test_categories_to_featureset_featureclass(self):
        fc = QALAB_ROOT_PATH + r"\df_accessor_test\world30.shp"
        if arcpy.Exists(fc):
            sdf = pd.DataFrame.spatial.from_featureclass(fc)

            sdf["cats_str"] = [
                "a" if i % 2 == 0 else "b" for i in range(len(sdf))
            ]
            sdf["cats_ints"] = [
                1 if i % 2 == 0 else 2 for i in range(len(sdf))
            ]
            sdf["cats_ints"] = sdf["cats_ints"].astype("category")
            sdf["cats_str"] = sdf["cats_str"].astype("category")

            fs = sdf.spatial.to_featureset()
            assert fs
            assert fs.features[0]
            assert fs.features[0].attributes['cats_str']

    def test_categories_to_featurecollection(self):
        fc = QALAB_ROOT_PATH + r"\df_accessor_test\world30.shp"
        if arcpy.Exists(fc):
            sdf = pd.DataFrame.spatial.from_featureclass(fc)

            sdf["cats_str"] = [
                "a" if i % 2 == 0 else "b" for i in range(len(sdf))
            ]
            sdf["cats_ints"] = [
                1 if i % 2 == 0 else 2 for i in range(len(sdf))
            ]
            sdf["cats_ints"] = sdf["cats_ints"].astype("category")
            sdf["cats_str"] = sdf["cats_str"].astype("category")

            fc = sdf.spatial.to_feature_collection()
            assert fc

    def test_categories_to_table(self):
        df = pd.DataFrame({"value": np.random.randint(0, 100, 20)})
        labels = ["{0} - {1}".format(i, i + 9) for i in range(0, 100, 10)]
        df["group"] = pd.cut(
            df.value, range(0, 105, 10), right=False, labels=labels
        )
        df["cats_ints"] = [
            1 if i % 2 == 0 else 2 for i in range(len(df['group']))
        ]
        df["cats_ints"] = df["cats_ints"].astype("category")
        df = df.convert_dtypes()
        table = os.path.join(arcpy.env.scratchGDB, "mycategoriestbl")
        df.spatial.to_table(table)

        assert arcpy.Exists(table)

    def test_categories_to_featureset_table(self):
        df = pd.DataFrame({"value": np.random.randint(0, 100, 20)})
        labels = ["{0} - {1}".format(i, i + 9) for i in range(0, 100, 10)]
        df["group"] = pd.cut(
            df.value, range(0, 105, 10), right=False, labels=labels
        )
        df["cats_ints"] = [
            1 if i % 2 == 0 else 2 for i in range(len(df['group']))
        ]
        df["cats_ints"] = df["cats_ints"].astype("category")
        fs = df.spatial.to_featureset()
        assert fs
        assert fs.features[0]


if __name__ == "__main__":
    unittest.main()
