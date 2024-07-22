import unittest
from unittest import mock
import arcgis


class TestNetworkAccessFailsGIS(unittest.TestCase):

    @unittest.SkipTest
    def test_network_access_fails(self):
        """All unit tests should NOT connect to the network. Assert that trying
        to connect to a GIS raises the `test_blockage` plugin's exception
        """
        requests_mock_inst = mock.patch(
            'arcgis.gis',
            mock.Mock(side_effect=RuntimeError(
                'No connection here.'
            ))
        )
        with requests_mock_inst:
            gis1 = arcgis.gis.GIS()
            gis2 = arcgis.gis.GIS("https://pythonapi.playground.esri.com")


if __name__ == '__main__':
    unittest.main()
