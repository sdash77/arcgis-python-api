import pytest
import urllib.request
from pytest_blockage import MockHttpCall

def test_network_access_fails():
    """All unit tests should NOT connect to the network. Assert that trying
    to ping https://arcgis.com throws a MockHttpCall
    """
    with pytest.raises(MockHttpCall):
        with urllib.request.urlopen('https://arcgis.com/') as response:
           html = response.read()
