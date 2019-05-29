
from unittest.mock import MagicMock

def test_url_property():
    from arcgis.gis import GIS

    mock_gis_inst = MagicMock()
    mock_gis_inst._is_hosted_nb_home = False
    mock_gis_inst._url = "https://defaulturl/"
    assert GIS.url.__get__(mock_gis_inst) == "https://defaulturl/"

    mock_gis_inst._is_hosted_nb_home = True
    mock_gis_inst._public_portal_url = "https://hostednburl/"
    assert GIS.url.__get__(mock_gis_inst) == "https://hostednburl/"
