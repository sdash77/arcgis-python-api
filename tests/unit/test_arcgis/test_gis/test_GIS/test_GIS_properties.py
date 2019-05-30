import pytest
from pytest_blockage import MockHttpCall

from utils.mocks import *

def test_url_property():
    """Tests that the `GIS.url` property returns the correct property
    depending on if it's GIS("home") or standard GIS object
    """
    from arcgis.gis import GIS

    mock_gis_inst = MockGIS()
    mock_gis_inst._is_hosted_nb_home = False
    mock_gis_inst._url = "https://defaulturl/"
    assert GIS.url.__get__(mock_gis_inst) == "https://defaulturl/"

    mock_gis_inst._is_hosted_nb_home = True
    mock_gis_inst._public_portal_url = "https://hostednburl/"
    assert GIS.url.__get__(mock_gis_inst) == "https://hostednburl/"
