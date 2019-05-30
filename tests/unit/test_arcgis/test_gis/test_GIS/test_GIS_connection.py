import pytest
from pytest_blockage import MockHttpCall

def test_network_access_fails():
    """All unit tests should NOT connect to the network. Assert that trying
    to connect to a GIS raises the `test_blockage` plugin's exception
    """
    from arcgis.gis import GIS
    with pytest.raises(MockHttpCall):
        gis = GIS()
    with pytest.raises(MockHttpCall):
        from arcgis.gis import GIS
        gis = GIS("https://pythonapi.playground.esri.com")

