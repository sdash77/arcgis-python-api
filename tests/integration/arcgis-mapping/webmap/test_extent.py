from arcgis.map import Map
from arcgis.geocoding import geocode
import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestExtent(unittest.TestCase):

    def setUp(self):
        # create webmap
        self.wm = Map(gis=self.gis)
        assert self.wm

    def test_extent_4326_sr(self):
        """Test setting extent with spatial reference 4326"""

        ext = geocode("Bangalore", out_sr=4326)[0]["extent"]
        ext["spatialReference"] = {"wkid": 4326}
        self.wm.extent = ext
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 4326

        new_map = self.wm.save(
            {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
        )
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 102100

        assert new_map.delete()

    def test_extent_102100_sr(self):
        """Test setting extent with spatial reference 102100"""

        ext = geocode("Bangalore", out_sr=102100)[0]["extent"]
        ext["spatialReference"] = {"wkid": 102100}
        self.wm.extent = ext
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 102100

        new_map = self.wm.save(
            {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
        )
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 102100

        assert new_map.delete()

    def test_extent_3857_sr(self):
        """Test setting extent with spatial reference 3857"""

        ext = geocode("Bangalore", out_sr=3857)[0]["extent"]
        ext["spatialReference"] = {"wkid": 3857}
        self.wm.extent = ext
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 3857

        new_map = self.wm.save(
            {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
        )
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 102100

        assert new_map.delete()

    def test_extent_4326_update(self):
        ext = geocode("Bangalore", out_sr=4326)[0]["extent"]
        ext["spatialReference"] = {"wkid": 4326}
        self.wm.extent = ext
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 4326

        new_map = self.wm.save(
            {"title": "test_map_ext", "tags": "test_map", "snippet": "test_map"}
        )
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 102100

        ext2 = geocode("Lausanne")[0]["extent"]
        ext2["spatialReference"] = {"wkid": 4326}
        self.wm.extent = ext2
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 4326

        self.wm.update()
        assert self.wm.extent
        assert self.wm.extent["spatialReference"]["wkid"] == 102100

        assert new_map.delete()


if __name__ == "__main__":
    unittest.main()
