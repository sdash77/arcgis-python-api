import sys, os
import random
import tempfile

#sys.path.insert(0, r"C:\SVN\geosaurus_master_dask_integration\src")
import pandas as pd
import unittest  # pytest,
import dask.dataframe as dd

from arcgis.geometry import Geometry
from arcgis.features import FeatureCollection
from arcgis.features.geo._array import GeoArray
from arcgis.features.geo._dask import (
    _from_geometry,
    GeoDaskSeriesAccessor,
    GeoDaskSpatialAccessor,
)
import pandas as pd
from arcgis.gis import GIS
from arcgis.features.analysis import create_viewshed

gis = GIS(profile='your_online_profile', verify_cert=False, trust_env=True)


class TestSDF2Dask(unittest.TestCase):
    def test_consume_sdf(self):
        item = gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name
        ddf = dd.from_pandas(sdf, npartitions=100)
        assert isinstance(ddf, dd.DataFrame)
        assert ddf.spatial.name
        assert ddf.spatial.geometry_type
        assert ddf.SHAPE.geom.area.sum().compute() >= 0

    def test_into_the_gp_tool(self):
        """tests passing a dask DF into a GP tool"""
        item = gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        vs = create_viewshed(
            input_layer=ddf, maximum_distance=20, max_distance_units="Miles"
        )
        assert isinstance(vs, FeatureCollection)

    def test_dask_to_feature_collection(self):
        """tests passing a dask DF as FeatureCollection"""
        item = gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        assert isinstance(
            ddf.spatial.to_feature_collection().compute(), FeatureCollection
        )

    def test_dask_to_feature_set(self):
        """tests passing a dask DF as feature set (dict)"""
        item = gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        assert isinstance(ddf.spatial.__feature_set__, dict)

    def test_dask_to_feature_class(self):
        """tests passing a dask DF as feature class"""
        item = gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        with tempfile.TemporaryDirectory("_sss") as path:
            out_fc = os.path.join(path, "data.shp")
            assert isinstance(ddf.spatial.to_featureclass(out_fc), str)
            assert os.path.isfile(out_fc)
        del ddf
        del sdf
        del item


if __name__ == "__main__":
    unittest.main()
