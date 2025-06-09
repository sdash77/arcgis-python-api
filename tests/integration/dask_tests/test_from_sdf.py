import os
import random
import tempfile
import unittest  # pytest,
import dask
import dask.dataframe as dd
from uuid import uuid4
from arcgis.gis import ItemTypeEnum

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
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path
from utils.data_utils import publish_test_item, cleanup_published_items


dask.config.set({"dataframe.convert-string": False})

@profiles.agol
@integration_test
class TestSDF2Dask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resource_path = get_resource_path("staging_data/USA_Major_Cities.zip", unique_copy=True)
        cls.item = publish_test_item(gis=cls.gis, layer_name = f"dask_test_{str(uuid4())[:4]}", source_data_path=resource_path, item_type=ItemTypeEnum.SHAPEFILE)

    def test_consume_sdf(self):
        item = self.item
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name
        ddf = dd.from_pandas(sdf, npartitions=100)
        assert isinstance(ddf, dd.DataFrame)
        assert ddf.spatial.name
        assert ddf.spatial.geometry_type
        assert ddf.SHAPE.geom.area.sum().compute() >= 0

    def test_into_the_gp_tool(self):
        """tests passing a dask DF into a GP tool"""
        item = self.item
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        vs = create_viewshed(
            input_layer=ddf, maximum_distance=20, max_distance_units="Miles"
        )
        assert isinstance(vs, FeatureCollection)

    def test_dask_to_feature_collection(self):
        """tests passing a dask DF as FeatureCollection"""
        item = self.item
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        assert isinstance(
            ddf.spatial.to_feature_collection().compute(meta=pd.Series(dtype='object')), FeatureCollection
        )

    def test_dask_to_feature_set(self):
        """tests passing a dask DF as feature set (dict)"""
        item = self.item
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        assert isinstance(ddf.spatial.__feature_set__, dict)

    def test_dask_to_feature_class(self):
        """tests passing a dask DF as feature class"""
        item = self.item
        sdf = item.layers[0].query(as_df=True)
        sdf.spatial.name

        ddf = dd.from_pandas(sdf.iloc[[1, 2, 3]], npartitions=1)
        path = tempfile.gettempdir()
        out_fc = os.path.join(path, "data.shp")
        assert isinstance(ddf.spatial.to_featureclass(out_fc), str)
        assert os.path.isfile(out_fc)
        del ddf
        del sdf
        del item

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(items=[cls.item])


if __name__ == "__main__":
    unittest.main()
