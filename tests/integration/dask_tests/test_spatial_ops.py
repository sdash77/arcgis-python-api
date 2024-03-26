import os
import random
import tempfile
import pandas as pd
import unittest #pytest,
import dask.dataframe as dd

from arcgis.geometry import Geometry
from arcgis.features import FeatureCollection
from arcgis.features.geo._array import GeoArray
from arcgis.features.geo._dask import (_from_geometry,
                                       GeoDaskSeriesAccessor,
                                       GeoDaskSpatialAccessor)
from arcgis.features.geo import _is_geoenabled
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test

@integration_test
class TestDaskSpatialOps(unittest.TestCase):
    """tests the spatial operations select, join, overlay"""

    def test_select(self):
        """tests the spatial select method"""
        data_size = 10
        y = [random.randrange(start=-90,stop=90) + random.random() for i in range(data_size)]
        x = [random.randrange(*sorted([-90,90])) - random.random() for i in range(data_size)]
        a = [random.randrange(*sorted([1,10000])) for i in range(data_size)]
        coords = list(zip(x,y))
        geoms = [ Geometry({'x' : i[0], 'y' : i[1], 'spatialReference' : {'wkid' : 4326}}) for i in coords]
        s = pd.Series(_from_geometry(geoms))
        ds = dd.from_pandas(s, 5)
        df = pd.DataFrame({"SHAPE": s, "a" : a})
        geom = df.SHAPE.geom.buffer(2)[0]
        ddf_point = dd.from_pandas(df, 16)
        ddf_point['b'] = 2
        s = ddf_point.SHAPE.geom.buffer(5).compute()
        geom = s[0]
        assert len(ddf_point.spatial.select(other=geom).compute()) >= 1

    def test_join(self):
        """tests the spatial join"""

        fp_dir = QALAB_ROOT_PATH + r"\dask_test\spatial"
        sdf1 = pd.DataFrame.spatial.from_featureclass(fr"{fp_dir}/area_of_int.shp")
        sdf2 = pd.DataFrame.spatial.from_featureclass(fr"{fp_dir}/training.shp")
        ddf1 = dd.from_pandas(sdf1, 5)

        final_right = ddf1.spatial.join(sdf2, 'right').compute()
        assert isinstance(final_right, pd.DataFrame)
        assert _is_geoenabled(final_right)
        final_left = ddf1.spatial.join(sdf2, 'left').compute()
        assert len(final_left) == 34
        assert len(ddf1.spatial.join(sdf2, 'inner').compute()) == 34

    def test_overlay(self):
        """test the spatial overlay"""

        geom1 = Geometry({
            'rings' : [[[0,0], [1, 0], [1,1], [0,1], [0,0]]],
            'spatialReference' : {'wkid' : 4326}
        }).buffer(1)
        geom2 = Geometry({
            'rings' : [[[0.5,0], [2, 0], [2,1], [0.5,1], [0.5,0]]],
            'spatialReference' : {'wkid' : 4326}
        }).buffer(1)

        data_size = 1

        a = [random.randrange(*sorted([1,10000])) for i in range(data_size)]

        geoms1 = [geom1]
        geoms2 = [geom2]
        s1 = pd.Series(_from_geometry(geoms1))
        s2 = pd.Series(_from_geometry(geoms2))

        df1 = pd.DataFrame({"SHAPE": s1, "fielda" : a})
        df2 = pd.DataFrame({"SHAPE": s2, "a" : a})


        ddf1 = dd.from_pandas(df1, 5)
        ddf2 = dd.from_pandas(df2, 5)

        ddf1['b'] = 2
        ddf2['c'] = 3

        allowed_hows = [
            'intersection',
            'union',
            'identity',
            'symmetric_difference',
            'difference',
            'erase'
        ]
        res = {}
        for how in allowed_hows:
            res[how] = ddf1.spatial.overlay(df2, how).compute()





if __name__ == "__main__":
    unittest.main()
