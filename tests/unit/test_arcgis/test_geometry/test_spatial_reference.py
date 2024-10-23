import unittest
from arcgis.geometry import SpatialReference, Geometry


class TestSpatialReferenceCreation(unittest.TestCase):

    def test_wkid_initialization(self):
        """Test initialization with a WKID."""
        sr = SpatialReference(4326)  # Using WKID for WGS84
        self.assertEqual(sr["wkid"], 4326)

    def test_wkt_initialization(self):
        """Test initialization with a WKT string."""
        wkt = 'PROJCS["WGS_1984_UTM_Zone_33N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",15.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
        sr = SpatialReference(wkt)
        self.assertEqual(sr["wkt"], wkt)

    def test_json_initialization(self):
        """Test initialization with a JSON object."""
        json_sr = {"wkid": 3857, "latestWkid": 102100}  # Web Mercator
        sr = SpatialReference(json_sr)
        self.assertEqual(sr["wkid"], 3857)
        self.assertEqual(sr["latestWkid"], 102100)

    def test_geometry_with_wkt(self):
        """Test that Geometry(txt) with WKT input returns a SpatialReference."""
        wkt = 'PROJCS["WGS_1984_UTM_Zone_33N",...]'
        geom = Geometry(wkt)  # This should return a SpatialReference
        self.assertEqual(geom["wkt"], wkt)

    def test_geometry_with_json(self):
        """Test that Geometry(json) with JSON wkid input returns a SpatialReference object."""
        json_geom = {"wkid": 4326}
        geom = Geometry(json_geom)
        self.assertEqual(geom["wkid"], 4326)

    def test_geometry_with_wkid(self):
        """Test that Geometry(wkid) with WKID input returns a SpatialReference object."""
        geom = Geometry(3857)
        self.assertEqual(geom["wkid"], 3857)


if __name__ == "__main__":
    unittest.main()
