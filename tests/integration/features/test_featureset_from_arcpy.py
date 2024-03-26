import unittest
from arcgis.features import FeatureSet
from utils.decorators import integration_test

try:
    import arcpy

    SKIPNOARCPY = False
except:
    SKIPNOARCPY = True
import json


fs = FeatureSet.from_geojson(
    {
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
)


@unittest.skipIf(SKIPNOARCPY, "ArcPY cannot be imported!")
@integration_test
class TestArcPyFeatureSet(unittest.TestCase):
    def test_from_arcpy(self):
        """tests the featureset from arcpy"""
        fs_arcpy = arcpy.FeatureSet(fs.to_json)
        fs_from_arcpy = FeatureSet.from_arcpy(fs_arcpy)
        assert isinstance(fs_from_arcpy, FeatureSet)
        assert len(fs_from_arcpy.features) == 2


if __name__ == "__main__":
    unittest.main()
