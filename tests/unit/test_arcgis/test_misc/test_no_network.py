import unittest
import urllib.request
from unittest import mock


class TestNetworkAccessFails(unittest.TestCase):
    """demonstrates that patching urllib.request will cause a MockHttpCall"""

    def test_network_access_fails(self):
        """All unit tests should NOT connect to the network. Assert that trying
        to ping https://arcgis.com throws a MockHttpCall
        """
        requests_mock_inst = mock.patch(
            'urllib.request',
            mock.Mock(side_effect=RuntimeError(
                'No internet here.'
            ))
        )
        with requests_mock_inst:
            response = urllib.request.urlopen("https://arcgis.com/")
            html = response.read()
            print(html)


if __name__ == '__main__':
    unittest.main()
