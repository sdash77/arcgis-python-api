import unittest
from arcgis.network import ODCostMatrixLayer, NAJob
from arcgis._impl.common._isd import InsensitiveDict
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestODCostMatricLayer(unittest.TestCase):
    """tests the OD Cost Matric Layer and it's functionality"""

    @classmethod
    def setUpClass(cls):
        if not "odCostMatrix" in cls.gis.properties.helperServices:
            cls.skipTest("Test site does not support origin destination cost matrix.")

    def test_get_layer(self):
        """Tests the Creation of the Cost Matrix Layer and Properties"""
        url = self.gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, self.gis)
        assert isinstance(cml, ODCostMatrixLayer)
        assert cml.properties

    def test_get_travel_modes(self):
        """Tests the retrieve travel modes call"""
        url = self.gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, self.gis)
        assert cml.retrieve_travel_modes()
        assert isinstance(cml.retrieve_travel_modes(), InsensitiveDict)

    def test_solve_od_matrix(self):
        """Tests the retrieve travel modes call"""
        url = self.gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, self.gis)
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
        url = self.gis.properties.helperServices.odCostMatrix.url
        cml = ODCostMatrixLayer(url, self.gis)
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
