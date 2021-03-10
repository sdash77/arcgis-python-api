import unittest
from arcgis.geometry import Geometry

geoms = [
    {"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}},
    {
      "points" : [[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832]],
      "spatialReference" : {"wkid" : 4326}
    },
    {
      "paths" : [[[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832]],
                 [[-97.06326,32.759],[-97.06298,32.755]]],
      "spatialReference" : {"wkid" : 4326}
    },
    {
      "rings" : [[[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832],
                  [-97.06138,32.837]],[[-97.06326,32.759],[-97.06298,32.755],[-97.06153,32.749],
                  [-97.06326,32.759]]],
      "spatialReference" : {"wkid" : 4326}
    }
]

class TestGeometryHash(unittest.TestCase):
    def test_hash(self):
        """tests the hash and __hash__ methods"""
        for g in geoms:
            g = Geometry(g)
            assert g.__hash__() == hash(g)



if __name__ == '__main__':
    unittest.main()