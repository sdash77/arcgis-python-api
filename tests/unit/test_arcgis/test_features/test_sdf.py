import unittest

import pandas as pd

from arcgis.features import FeatureSet

class TestFeatureSetGeoJSON(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json, pathlib
        data_path = pathlib.Path(__file__).parent / "data.json"
        with open(data_path) as f:
            cls.data = json.load(f)

    def test_sdf(self):
        data = self.data
        fs = FeatureSet.from_geojson(data)
        df = fs.sdf  # triggers from_featureset()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("SHAPE", df.columns)
        self.assertEqual(df.spatial.sr["wkid"], 4326)
        self.assertEqual(len(df), len(data["features"]))
        self.assertFalse(df["SHAPE"].isna().any())


if __name__ == "__main__":
    unittest.main()
