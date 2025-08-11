import unittest

from arcgis.features import FeatureSet

class TestFeatureSetGeoJSON(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json, pathlib
        data_path = pathlib.Path(__file__).parent / "data.json"
        with open(data_path) as f:
            cls.data = json.load(f)

    def test_fs_from_geojson(self):
        data = self.data
        fs = FeatureSet.from_geojson(self.data)
        assert all([f.geometry.is_valid() for f in fs])


if __name__ == "__main__":
    unittest.main()
