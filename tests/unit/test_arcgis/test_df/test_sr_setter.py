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

dataset2 = [
    {
        "Unnamed: 0": 0,
        "Unnamed: 0.1": 0,
        "OBJECTID": 1,
        "iOEEncounteredID": 1,
        "ftNorthing": 1501166.5480627269,
        "ftEasting": 566546.4904219806,
    },
    {
        "Unnamed: 0": 1,
        "Unnamed: 0.1": 1,
        "OBJECTID": 2,
        "iOEEncounteredID": 2,
        "ftNorthing": 1501210.1001409742,
        "ftEasting": 567718.5333534777,
    },
    {
        "Unnamed: 0": 2,
        "Unnamed: 0.1": 2,
        "OBJECTID": 3,
        "iOEEncounteredID": 3,
        "ftNorthing": 1501548.460028559,
        "ftEasting": 568784.0131779015,
    },
    {
        "Unnamed: 0": 3,
        "Unnamed: 0.1": 3,
        "OBJECTID": 4,
        "iOEEncounteredID": 4,
        "ftNorthing": 1502049.1299589726,
        "ftEasting": 568425.8432905674,
    },
    {
        "Unnamed: 0": 4,
        "Unnamed: 0.1": 4,
        "OBJECTID": 5,
        "iOEEncounteredID": 5,
        "ftNorthing": 1501499.460126549,
        "ftEasting": 568779.0131879002,
    },
    {
        "Unnamed: 0": 5,
        "Unnamed: 0.1": 5,
        "OBJECTID": 6,
        "iOEEncounteredID": 6,
        "ftNorthing": 1499585.798927635,
        "ftEasting": 570088.1404908895,
    },
    {
        "Unnamed: 0": 6,
        "Unnamed: 0.1": 6,
        "OBJECTID": 7,
        "iOEEncounteredID": 7,
        "ftNorthing": 1500230.9800519643,
        "ftEasting": 577231.3834222257,
    },
    {
        "Unnamed: 0": 7,
        "Unnamed: 0.1": 7,
        "OBJECTID": 8,
        "iOEEncounteredID": 8,
        "ftNorthing": 1480716.5801044703,
        "ftEasting": 586698.8034637272,
    },
    {
        "Unnamed: 0": 8,
        "Unnamed: 0.1": 8,
        "OBJECTID": 9,
        "iOEEncounteredID": 9,
        "ftNorthing": 1496939.527973473,
        "ftEasting": 580633.4002402276,
    },
    {
        "Unnamed: 0": 9,
        "Unnamed: 0.1": 9,
        "OBJECTID": 10,
        "iOEEncounteredID": 10,
        "ftNorthing": 1496976.7939750552,
        "ftEasting": 580634.1702518165,
    },
    {
        "Unnamed: 0": 10,
        "Unnamed: 0.1": 10,
        "OBJECTID": 11,
        "iOEEncounteredID": 11,
        "ftNorthing": 1496969.403897971,
        "ftEasting": 580634.3992539793,
    },
    {
        "Unnamed: 0": 11,
        "Unnamed: 0.1": 11,
        "OBJECTID": 12,
        "iOEEncounteredID": 12,
        "ftNorthing": 1496949.6460634768,
        "ftEasting": 580633.6722213179,
    },
    {
        "Unnamed: 0": 12,
        "Unnamed: 0.1": 12,
        "OBJECTID": 13,
        "iOEEncounteredID": 13,
        "ftNorthing": 1496947.230057806,
        "ftEasting": 580633.5603448898,
    },
    {
        "Unnamed: 0": 13,
        "Unnamed: 0.1": 13,
        "OBJECTID": 14,
        "iOEEncounteredID": 14,
        "ftNorthing": 1496945.0781592282,
        "ftEasting": 580634.2102779746,
    },
    {
        "Unnamed: 0": 14,
        "Unnamed: 0.1": 14,
        "OBJECTID": 15,
        "iOEEncounteredID": 15,
        "ftNorthing": 1496954.600121811,
        "ftEasting": 580633.748336643,
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
        from arcgis._impl._geometry_engine import HAS_ARCPY

        if not HAS_ARCPY:
            raise ModuleNotFoundError("ArcPy Not Installed")

        super().setUp()
        self._patcher = mock.patch.object(
            type(self._tpl.spatial), "_HASARCPY", True, create=True
        )
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()

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


@mock.patch.dict("sys.modules", {"arcpy": None})
class TestSRSetter_NoArcPy(_SRBase):
    """Same goal as variant 1, using a decorator."""

    def setUp(self):
        super().setUp()
        self._flag_patch = mock.patch.object(
            type(self._tpl.spatial), "_HASARCPY", False, create=True
        )
        self._flag_patch.start()

        geom_engine_mod = importlib.import_module("arcgis._impl._geometry_engine")
        self._has_arcpy_patch = mock.patch.object(
            geom_engine_mod, "HAS_ARCPY", False, create=True
        )
        self._has_arcpy_patch.start()

    def tearDown(self):
        self._flag_patch.stop()
        self._has_arcpy_patch.stop()


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
