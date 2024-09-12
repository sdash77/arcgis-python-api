import unittest
from unittest.mock import patch

import arcgis.gis._impl._con._connection
import arcgis.auth._auth._token
from arcgis.auth.tools._lazy import LazyLoader

def get_mock_arcpy():
    mock_arcpy = unittest.mock.MagicMock()
    mock_arcpy.GetActivePortalURL.return_value = "https://geosaurus.maps.arcgis.com"
    mock_arcpy.GetSigninToken.return_value = {"referer": "https://www.arcgis.com"}
    return mock_arcpy

def lazy_loader_arcpy_patch(module_name: str, submod_name=None, strict=False):
    if module_name == "arcpy":
        return get_mock_arcpy()
    return LazyLoader(module_name, submod_name, strict)

class TestConnection(unittest.TestCase):
    @patch.object(arcgis.gis._impl._con._connection, 'arcpy', get_mock_arcpy(), create=True)
    @patch.object(arcgis.auth._auth._token, 'LazyLoader')
    def test_auth_pro(self, mock_lazy_loader):
        mock_lazy_loader.side_effect = lazy_loader_arcpy_patch
        connection = arcgis.gis._impl._con._connection.Connection("pro")
        assert connection._auth == "PRO"

    def test_auth_anon(self):
        connection = arcgis.gis._impl._con._connection.Connection()
        assert connection._auth == "ANON"
    
    def test_auth_home(self):
        connection = arcgis.gis._impl._con._connection.Connection(is_hosted_nb_home=True)
        assert connection._auth == "HOME"
    
    @patch.object(arcgis.gis._impl._con._connection, 'arcpy', get_mock_arcpy(), create=True)
    @patch.object(arcgis.auth._auth._token, 'LazyLoader')
    def test_auth_ags_file(self, mock_lazy_loader):
        mock_lazy_loader.side_effect = lazy_loader_arcpy_patch
        connection = arcgis.gis._impl._con._connection.Connection(ags_file="./test.ags")
        assert connection._auth == "AGS_AUTH"
    
    def test_auth_token(self):
        connection = arcgis.gis._impl._con._connection.Connection(token="token")
        assert connection._auth == "USER_TOKEN"
    
    def test_auth_api_key(self):
        connection = arcgis.gis._impl._con._connection.Connection(api_key="api_key")
        assert connection._auth == "API_KEY"

    def test_auth_oauth_client_id_client_secret(self):
        connection = arcgis.gis._impl._con._connection.Connection(client_id="client_id", client_secret="client_secret")
        assert connection._auth == "OAUTH"
    
    def test_auth_oauth_client_id(self):
        connection = arcgis.gis._impl._con._connection.Connection(client_id="client_id")
        assert connection._auth == "OAUTH"
    
    def test_auth_iwa(self):
        connection = arcgis.gis._impl._con._connection.Connection(username=r"avworld\geosaurusaccnt", password="notarealpassword")
        assert connection._auth == "IWA"
    
    def test_auth_built_in(self):
        connection = arcgis.gis._impl._con._connection.Connection(username="username", password="notarealpassword")
        assert connection._auth == "BUILTIN"
    
    @unittest.skip("TODO mock or create cert")
    def test_auth_pki_cert_file(self):
        connection = arcgis.gis._impl._con._connection.Connection(cert_file="./cert_file")
        assert connection._auth == "PKI"
    
    @unittest.skip("TODO mock or create cert/key")
    def test_auth_pki_cert_file_key_file(self):
        connection = arcgis.gis._impl._con._connection.Connection(cert_file="./cert_file", key_file="./key_file")
        assert connection._auth == "PKI"