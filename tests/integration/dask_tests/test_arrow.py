import sys, os

sys.path.insert(0, r"C:\SVN\geosaurus_master_dask_integration\src")
sys.path.insert(0, r"C:\SVN\geosaurus_master_dask_integration\tests")
import unittest
import tempfile
import pandas as pd

from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser

from arcgis.geometry import SpatialReference, Geometry

skip_me = False
try:
    from arcgis.features.geo._io._arrow import _read_parquet, _to_parquet, _to_feather, _read_feather
except ImportError:
    skip_me = True




geoms = [
    Geometry({'x' : -10, 'y' : 13, 'spatialReference' : {'wkid' : 4326}}),
    Geometry({'x' : 2, 'y' : 2, 'spatialReference' : {'wkid' : 4326}}),
    Geometry({'x' : 20, 'y' : -22, 'spatialReference' : {'wkid' : 4326}})
] * 1



class TestArrowFeatureSupport(unittest.TestCase):
    """tests the arrow/feature support for SeDF"""

    def test_arrow_to_from(self):
        df = pd.DataFrame(
            data={'SHAPE' : geoms, 'a' : range(len(geoms))}
        )
        df.spatial.name
        df.spatial.project({'wkid' : 4326})
        with tempfile.TemporaryDirectory() as path:
            fp =_to_parquet(df=df, path=os.path.join(path, "test.parquet"))
            assert os.path.isfile(fp)
            df2 = _read_parquet(fp)
            pd.testing.assert_frame_equal(df, df2)

    def test_feather_to_from(self):
        df = pd.DataFrame(
            data={'SHAPE' : geoms, 'a' : range(len(geoms))}
        )
        df.spatial.name
        df.spatial.project({'wkid' : 4326})
        with tempfile.TemporaryDirectory(suffix="_feather") as path:
            fp =_to_feather(df=df, path=os.path.join(path, "test.feather"))
            assert os.path.isfile(fp)
            df2 = _read_feather(fp)
            pd.testing.assert_frame_equal(df, df2)


if __name__ == "__main__":
    unittest.main()