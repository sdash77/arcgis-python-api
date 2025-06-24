import importlib
import unittest
import pandas as pd
from unittest import mock
from arcgis.auth.tools._lazy import LazyLoader
from arcgis.features import GeoAccessor, GeoSeriesAccessor  # noqa: F401

_geometry = LazyLoader("arcgis.geometry")

polygon_data = [
    """MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)), ((15 5, 40 10, 10 20, 5 10, 15 5)))""",  # WKT
    {  # GeoJSON
        "type": "Polygon",
        "coordinates": [
            [
                [100.0, 0.0],
                [101.0, 0.0],
                [101.0, 1.0],
                [100.0, 1.0],
                [100.0, 0.0],
            ]
        ],
    },
    {
        "rings": [
            [
                [-97.06138, 32.837],
                [-97.06133, 32.836],
                [-97.06124, 32.834],
                [-97.06127, 32.832],
                [-97.06138, 32.837],
            ],
            [
                [-97.06326, 32.759],
                [-97.06298, 32.755],
                [-97.06153, 32.749],
                [-97.06326, 32.759],
            ],
        ],
        "spatialReference": {"wkid": 4326},
    },
]


class _SRBase(unittest.TestCase):
    """Shared helpers for the ArcPy / no-ArcPy test variants."""

    def setUp(self):
        base_df = pd.DataFrame({"geom": polygon_data, "oid": [1, 2, 3]})
        self._tpl = pd.DataFrame.spatial.from_df(base_df, geometry_column="geom")

    # utility – clone the template so every test works on fresh data
    def _fresh(self):
        return self._tpl.copy()

    # ----------------------------------------------------------------------
    # core checker (all tests run through this)
    def _assign_and_check(self, sdf, ref):
        """Assign *ref* to sdf.spatial.sr and verify the result."""
        sdf.spatial.sr = ref
        wkid_expected = ({ref} if isinstance(ref, int) else {ref["wkid"]}) | {
            102100
        }  # ArcGIS’s alias for Web-Mercator
        self.assertIn(sdf.spatial.sr["wkid"], wkid_expected)

    # ----------------------------------------------------------------------
    # concrete tests
    def test_set_int(self):
        sdf = self._fresh()
        self._assign_and_check(sdf, 3857)

    def test_set_dict(self):
        sdf = self._fresh()
        self._assign_and_check(sdf, {"wkid": 3857})

    def test_set_str(self):
        sdf = self._fresh()
        wkt = """PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]"""
        sdf.spatial.sr = wkt
        if "wkid" in sdf.spatial.sr:
            self.assertIn(sdf.spatial.sr["wkid"], (3857, 102100))
        else:
            self.assertEqual(sdf.spatial.sr["wkt"], wkt)

    def test_no_op_on_same_sr(self):
        sdf = self._fresh()
        geom_before = sdf["geom"].copy(deep=True)
        sdf.spatial.sr = 4326  # identical ⇒ should be no reprojection
        pd.testing.assert_series_equal(geom_before, sdf["geom"])


# ------------------------------------------------------------------------------
# Two subclasses toggle the private flag ---------------------------------------
# ------------------------------------------------------------------------------


class TestSRSetter_HasArcPy(_SRBase):
    """Exercises the branch where self._HASARCPY is True."""

    def setUp(self):

        try:
            from arcgis._impl._geometry_engine import HAS_ARCPY
        except ImportError:
            HAS_ARCPY = False

        if not HAS_ARCPY:
            raise unittest.SkipTest("Skipping tests because arcpy is not available.")

        super().setUp()

    def test_set_spatialreference(self):
        sdf = self._fresh()
        ref = _geometry.SpatialReference(3857)
        sdf.spatial.sr = ref
        wkid_expected = (
            {ref} if isinstance(ref, int) else {_geometry.SpatialReference(ref).wkid}
        ) | {
            102100
        }  # ArcGIS’s alias for Web-Mercator
        self.assertIn(sdf.spatial.sr["wkid"], wkid_expected)

    def test_arcpy_available(self):
        """arcpy should be visible to the GeoAccessor if it is installed"""
        sdf = self._fresh()
        sdf.spatial._check_geometry_engine()
        self.assertTrue(sdf.spatial._HASARCPY)


class TestSRSetter_NoArcPy(_SRBase):
    """Same goal as variant 1, using a decorator."""

    def setUp(self):
        super().setUp()

        geom_engine_mod = importlib.import_module("arcgis._impl._geometry_engine")
        self._has_arcpy_patch = mock.patch.object(
            geom_engine_mod, "HAS_ARCPY", False, create=True
        )
        self._has_arcpy_patch.start()

        self._module_patch = mock.patch.dict("sys.modules", {"arcpy": None})
        self._module_patch.start()

        self._flag_patch = mock.patch.object(
            type(self._tpl.spatial), "_HASARCPY", False, create=True
        )
        self._flag_patch.start()

    def tearDown(self):
        self._flag_patch.stop()
        self._module_patch.stop()
        self._has_arcpy_patch.stop()

    def test_arcpy_not_available(self):
        """arcpy should not be visible to the GeoAccessor"""
        sdf = self._fresh()
        sdf.spatial._check_geometry_engine()
        self.assertFalse(sdf.spatial._HASARCPY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
