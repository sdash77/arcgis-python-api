import sys

import unittest

from arcgis.gis import GIS
from arcgis.network import ODCostMatrixLayer, NAJob
from arcgis._impl.common._isd import InsensitiveDict
from utils.decorators import integration_test

PROFILE = "your_online_profile"
gis = GIS(profile=PROFILE, verify_cert=False)
if "odCostMatrix" in gis.properties.helperServices:
    SKIP_TEST = False
else:
    SKIP_TEST = True


@unittest.skipIf(SKIP_TEST == True, "Test site does not support this operation.")
@integration_test
class Test_ODCostMatricLayer(unittest.TestCase):
    """tests the OD Cost Matric Layer and it's functionality"""

    def test_get_layer(self):
        """Tests the Creation of the Cost Matrix Layer and Properties"""
        gis = GIS(profile=PROFILE, verify_cert=False)
        url = gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, gis)
        assert isinstance(cml, ODCostMatrixLayer)
        assert cml.properties

    def test_get_travel_modes(self):
        """Tests the retrieve travel modes call"""
        gis = GIS(profile=PROFILE, verify_cert=False)
        url = gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, gis)
        assert cml.retrieve_travel_modes()
        assert isinstance(cml.retrieve_travel_modes(), InsensitiveDict)

    def test_solve_od_matrix(self):
        """Tests the retrieve travel modes call"""
        gis = GIS(profile=PROFILE, verify_cert=False)
        url = gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, gis)
        assert isinstance(cml, ODCostMatrixLayer)
        assert cml.solve_od_cost_matrix(
            origins={
                "spatialReference": {"wkid": 102100},
                "features": [
                    {
                        "geometry": {"x": -13042381.897669187, "y": 3857625.761983883},
                        "attributes": {"ObjectID": 1, "Name": "San Diego"},
                    },
                    {
                        "geometry": {"x": -13163008.811087687, "y": 4035986.6896486743},
                        "attributes": {"ObjectID": 2, "Name": "Los Angeles"},
                    },
                ],
            },
            destinations={
                "spatialReference": {"wkid": 102100},
                "features": [
                    {
                        "geometry": {"x": -13042381.897669187, "y": 3857625.761983883},
                        "attributes": {"ObjectID": 1, "Name": "San Diego"},
                    },
                    {
                        "geometry": {"x": -13163008.811087687, "y": 4035986.6896486743},
                        "attributes": {"ObjectID": 2, "Name": "Los Angeles"},
                    },
                ],
            },
            future=False,
        )

    def test_solve_od_matrix_future(self):
        """Tests the retrieve travel modes call"""
        gis = GIS(profile=PROFILE, verify_cert=False)
        url = gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, gis)
        assert isinstance(cml, ODCostMatrixLayer)
        f = cml.solve_od_cost_matrix(
            origins={
                "spatialReference": {"wkid": 102100},
                "features": [
                    {
                        "geometry": {"x": -13042381.897669187, "y": 3857625.761983883},
                        "attributes": {"ObjectID": 1, "Name": "San Diego"},
                    },
                    {
                        "geometry": {"x": -13163008.811087687, "y": 4035986.6896486743},
                        "attributes": {"ObjectID": 2, "Name": "Los Angeles"},
                    },
                ],
            },
            destinations={
                "spatialReference": {"wkid": 102100},
                "features": [
                    {
                        "geometry": {"x": -13042381.897669187, "y": 3857625.761983883},
                        "attributes": {"ObjectID": 1, "Name": "San Diego"},
                    },
                    {
                        "geometry": {"x": -13163008.811087687, "y": 4035986.6896486743},
                        "attributes": {"ObjectID": 2, "Name": "Los Angeles"},
                    },
                ],
            },
            future=True,
        )
        assert isinstance(f, NAJob)
        assert f.result()


if __name__ == "__main__":
    unittest.main()
