import os, sys

# sys.path.append(r"D:\SVN\git_hub\ArcGIS\geo_public")
import shutil
import tempfile
import unittest

from arcgis.features.geo import GeoAccessor, GeoSeriesAccessor
from arcgis.geometry import Geometry
import pandas as pd

from arcgis.gis import GIS
from arcgis.geometry import Geometry
from utils.decorators import integration_test

gis = GIS()
wm = gis.map()

geoms = [
    Geometry(
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
        }
    )
] * 5
attr = [["a", 1.2, 1]] * 5


@integration_test
class TestPlotting(unittest.TestCase):

    def test_plot(self):
        df = pd.DataFrame(data=attr, columns=["A", "B", "C"])
        df.spatial.set_geometry(geoms)
        assert df.spatial.plot(map_widget=wm)


if __name__ == "__main__":

    unittest.main()
