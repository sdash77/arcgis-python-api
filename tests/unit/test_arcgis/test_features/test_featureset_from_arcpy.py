import unittest
from arcgis.features import FeatureSet

try:
    import arcpy

    HAS_ARCPY = True
except:
    HAS_ARCPY = False


geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [10.0, 5.0]},
                "properties": {"route": "341A7", "class": "local"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [10.0, 7.0]},
                "properties": {"route": "341A7", "class": "local"},
            },
        ],
    }
fs = FeatureSet.from_geojson(geojson)


@unittest.skipIf(not HAS_ARCPY, "Environment does not have arcpy")
class TestFeatureSetFromArcpy(unittest.TestCase):
    def test_from_arcpy(self):
        """tests the featureset from arcpy"""
        fs_arcpy = arcpy.FeatureSet(fs.to_json)
        fs_from_arcpy = FeatureSet.from_arcpy(fs_arcpy)
        assert isinstance(fs_from_arcpy, FeatureSet)
        assert len(fs_from_arcpy.features) == len(geojson["features"])


if __name__ == "__main__":
    unittest.main()
