from arcgis.gis import GIS
from arcgis.map import Map
from arcgis.geocoding import geocode
import unittest
from utils.decorators import integration_test

PROFILES = ["your_online_profile"]

@integration_test
class TestExtent(unittest.TestCase):
    def test_extent_4326_sr(self):
        """Test setting extent with spatial reference 4326"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            m = Map(gis=gis)
            assert m

            ext = geocode("Bangalore", out_sr=4326)[0]["extent"]
            ext["spatialReference"] = {"wkid": 4326}
            m.extent = ext
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 4326

            new_map = m.save(
                {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
            )
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 102100

            assert new_map.delete()

    def test_extent_102100_sr(self):
        """Test setting extent with spatial reference 102100"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            m = Map(gis=gis)
            assert m

            ext = geocode("Bangalore", out_sr=102100)[0]["extent"]
            ext["spatialReference"] = {"wkid": 102100}
            m.extent = ext
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 102100

            new_map = m.save(
                {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
            )
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 102100

            assert new_map.delete()

    def test_extent_3857_sr(self):
        """Test setting extent with spatial reference 3857"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            m = Map(gis=gis)
            assert m

            ext = geocode("Bangalore", out_sr=3857)[0]["extent"]
            ext["spatialReference"] = {"wkid": 3857}
            m.extent = ext
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 3857

            new_map = m.save(
                {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
            )
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 102100

            assert new_map.delete()

    def test_extent_4326_update(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            m = Map(gis=gis)
            assert m

            ext = geocode("Bangalore", out_sr=4326)[0]["extent"]
            ext["spatialReference"] = {"wkid": 4326}
            m.extent = ext
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 4326

            new_map = m.save(
                {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
            )
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 102100

            ext2 = geocode("Lausanne")[0]["extent"]
            ext2["spatialReference"] = {"wkid": 4326}
            m.extent = ext2
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 4326

            m.update()
            assert m.extent
            assert m.extent["spatialReference"]["wkid"] == 102100

            assert new_map.delete()


if __name__ == "__main__":
    unittest.main()
