import os
import random
import tempfile
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
from utils.decorators import integration_test

import arcgis

try:
    import arcpy
    HASARCPY = True
except:
    HASARCPY = False
geoms = [
    Geometry({'x': 1, 'y': 1, 'spatialReference': {'wkid': 4326}}),
    Geometry({'x': 2, 'y': 2, 'spatialReference': {'wkid': 4326}}),
]


@integration_test
class TestDaskSeriesAccessor(unittest.TestCase):
    def test_properties(self):
        """tests creating a feature set dictionary"""
        data_size = 100
        x = [
            random.randrange(start=1, stop=10) + random.random()
            for i in range(data_size)
        ]
        y = [
            random.randrange(*sorted([1, 10])) - random.random()
            for i in range(data_size)
        ]
        a = [random.randrange(*sorted([1, 10000])) for i in range(data_size)]
        coords = list(zip(x, y))
        geoms = [
            Geometry(
                {'x': i[0], 'y': i[1], 'spatialReference': {'wkid': 4326}}
            )
            for i in coords
        ]

        ga = GeoArray(geoms)
        s = pd.Series(_from_geometry(geoms))
        df = pd.DataFrame({"SHAPE": s, 'a': a})
        ddf = dd.from_pandas(df, 5)
        assert isinstance(ddf.SHAPE.geom, GeoDaskSeriesAccessor)
        series = ddf.SHAPE.geom
        isinstance(series, GeoDaskSeriesAccessor)
        assert series.area.compute().sum() == 0
        assert isinstance(series.as_arcpy.compute(), pd.Series)
        assert isinstance(series.centroid.compute(), pd.Series)
        assert isinstance(series.extent.compute(), pd.Series)
        assert isinstance(series.first_point.compute(), pd.Series)
        assert isinstance(series.geoextent.compute(), pd.Series)
        assert isinstance(series.geometry_type.compute(), pd.Series)
        assert isinstance(series.hull_rectangle.compute(), pd.Series)
        assert isinstance(series.has_z.compute(), pd.Series)
        assert isinstance(series.has_m.compute(), pd.Series)
        assert isinstance(series.is_empty.compute(), pd.Series)
        assert isinstance(series.is_multipart.compute(), pd.Series)
        assert isinstance(series.is_valid.compute(), pd.Series)
        assert isinstance(series.JSON.compute(), pd.Series)
        assert isinstance(series.WKT.compute(), pd.Series)
        assert isinstance(series.WKB.compute(), pd.Series)
        assert isinstance(series.label_point.compute(), pd.Series)
        assert isinstance(series.last_point.compute(), pd.Series)
        assert isinstance(series.length.compute(), pd.Series)
        assert isinstance(series.length3D.compute(), pd.Series)
        assert isinstance(series.part_count.compute(), pd.Series)
        assert isinstance(series.point_count.compute(), pd.Series)
        assert isinstance(series.true_centroid.compute(), pd.Series)
        assert isinstance(series.spatial_reference.compute(), pd.Series)

    # ----------------------------------------------------------------------
    def test_angleDistTo(self):
        """tests angle distance to"""
        try:
            data_size = 10
            x = [
                random.randrange(start=1, stop=10) + random.random()
                for i in range(data_size)
            ]
            y = [
                random.randrange(*sorted([1, 10])) - random.random()
                for i in range(data_size)
            ]
            a = [
                random.randrange(*sorted([1, 10000]))
                for i in range(data_size)
            ]
            coords = list(zip(x, y))
            geoms = [
                Geometry(
                    {
                        'x': i[0],
                        'y': i[1],
                        'spatialReference': {'wkid': 4326},
                    }
                )
                for i in coords
            ]

            ga = GeoArray(geoms)
            s = pd.Series(_from_geometry(geoms))
            df = pd.DataFrame({"SHAPE": s, 'a': a})
            ddf = dd.from_pandas(df, 5)
            r = ddf.SHAPE.geom.angle_distance_to(geoms[0]).compute()
            assert isinstance(r, pd.Series)
            assert isinstance(r[0], tuple)
        except:  # Handles ARCPY not being signed in
            pass

    ##--------------------------------------------------------------------------
    @unittest.skipIf(not HASARCPY, "arcpy is not installed")
    def test_boundary(self):
        geoms = [
            Geometry(
                {
                    "rings": [
                        [
                            [-97.06138, 32.837],
                            [-97.06133, 32.836],
                            [-97.06124, 32.834],
                            [-97.06127, 32.832],
                        ]
                    ],
                    "spatialReference": {"wkid": 4326},
                }
            )
        ]
        s = pd.Series(_from_geometry(geoms))
        df = pd.DataFrame({"SHAPE": s, 'a': [1]})
        ddf = dd.from_pandas(df, 5)

        b = ddf.SHAPE.geom.boundary().compute()
        assert isinstance(b, pd.Series)
        assert b.geom.geometry_type.unique()[0] == 'polyline'


###########################################################################
@integration_test
class TestDaskTestCase(unittest.TestCase):
    """Unit Tests for Dask Spatial Accessor"""

    def test_from_pandas(self):
        s = pd.Series(_from_geometry(geoms))
        ds = dd.from_pandas(s, 2)

        assert ds.dtype == s.dtype
        dd.utils.assert_eq(s, ds)

        df = pd.DataFrame({"A": s})
        ddf = dd.from_pandas(df, 2)
        assert ddf.dtypes["A"] == s.dtype
        dd.utils.assert_eq(df, ddf)

    def test_accessor_test(self):
        """test the accessor test"""
        s = pd.Series(_from_geometry(geoms))
        ds = dd.from_pandas(s, 2)

        assert ds.dtype == s.dtype
        dd.utils.assert_eq(s, ds)

        df = pd.DataFrame({"SHAPE": s})
        ddf = dd.from_pandas(df, 2)
        assert ddf.SHAPE.geom
        assert ddf.spatial

    def test_to_from_featureclass(self):
        """tests the read/write feature classes"""
        path = tempfile.gettempdir()
        ga = GeoArray(geoms)
        s = pd.Series(ga)
        a = pd.Series(data=[-1, 2])
        df = pd.DataFrame({"SHAPE": s, 'a': a})
        ddf = dd.from_pandas(df, 2)
        fp = os.path.join(path, "dataset.shp")
        ddf.spatial.to_featureclass(fp)
        assert fp == ddf.spatial.to_featureclass(fp)
        ddf2 = dd.DataFrame.spatial.from_featureclass(fp, 2)
        assert isinstance(ddf2, dd.DataFrame)

    def test_df_spatial(self):
        """tests the dataframe spatial props"""
        ga = GeoArray(geoms)
        s = pd.Series(_from_geometry(geoms))
        df = pd.DataFrame({"SHAPE": s, 'a': [-10, 20]})
        ddf = dd.from_pandas(df, 2)
        spatial = ddf.spatial
        assert isinstance(spatial, GeoDaskSpatialAccessor)

        assert spatial.full_extent
        assert spatial.area.compute() == 0
        assert spatial.length.compute() == 0
        assert spatial.sr.compute() is not None
        assert isinstance(spatial.bbox, Geometry)
        assert isinstance(spatial.centroid, tuple)
        assert isinstance(spatial.geometry_type, list)
        assert spatial.has_z.compute() == False
        assert spatial.has_m.compute() == False
        a, b, c = spatial._check_geometry_engine()
        assert a is not None
        assert b is not None
        assert c is not None
        assert spatial.renderer
        spatial.renderer['symbol']['color'] = [0, 255, 0, 128]
        assert spatial.renderer['symbol']['color'] == [0, 255, 0, 128]

    def test_df_project(self):
        """tests projecting to a new coordinate reference system"""

        s = pd.Series(_from_geometry(geoms))
        df = pd.DataFrame({"SHAPE": s, 'a': [-10, 20]})
        ddf = dd.from_pandas(df, 2)
        spatial = ddf.spatial
        assert isinstance(spatial, GeoDaskSpatialAccessor)
        assert spatial.project(3857)

    def test_df_sindex(self):
        """tests the sindex creation"""
        s = pd.Series(_from_geometry(geoms))
        df = pd.DataFrame({"SHAPE": s, 'a': [-10, 20]})
        ddf = dd.from_pandas(df, 2)
        spatial = ddf.spatial
        assert isinstance(spatial, GeoDaskSpatialAccessor)
        assert spatial.sindex()

    def test_feature_set(self):
        """tests creating a feature set dictionary"""
        data_size = 100
        x = [
            random.randrange(start=1, stop=10) + random.random()
            for i in range(data_size)
        ]
        y = [
            random.randrange(*sorted([1, 10])) - random.random()
            for i in range(data_size)
        ]
        a = [random.randrange(*sorted([1, 10000])) for i in range(data_size)]
        coords = list(zip(x, y))
        geoms = [
            Geometry(
                {'x': i[0], 'y': i[1], 'spatialReference': {'wkid': 4326}}
            )
            for i in coords
        ]

        ga = GeoArray(geoms)
        s = pd.Series(_from_geometry(geoms))
        df = pd.DataFrame({"SHAPE": s, 'a': a})
        ddf = dd.from_pandas(df, 5)
        fs = ddf.spatial.__feature_set__
        assert isinstance(fs, dict)
        assert len(fs['features']) == data_size

    def test_feature_collection(self):
        """tests creating a feature collection"""
        data_size = 100
        x = [
            random.randrange(start=1, stop=10) + random.random()
            for i in range(data_size)
        ]
        y = [
            random.randrange(*sorted([1, 10])) - random.random()
            for i in range(data_size)
        ]
        a = [random.randrange(*sorted([1, 10000])) for i in range(data_size)]
        coords = list(zip(x, y))
        geoms = [
            Geometry(
                {'x': i[0], 'y': i[1], 'spatialReference': {'wkid': 4326}}
            )
            for i in coords
        ]

        ga = GeoArray(geoms)
        s = pd.Series(_from_geometry(geoms))
        df = pd.DataFrame({"SHAPE": s, 'a': a})
        ddf = dd.from_pandas(df, 5)
        fc = ddf.spatial.to_feature_collection().compute()
        assert isinstance(fc, FeatureCollection)


if __name__ == '__main__':
    unittest.main()
