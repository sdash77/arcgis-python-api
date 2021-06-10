import unittest
import unittest.mock
from unittest.mock import MagicMock
from arcgis.gis import GIS, Item
from arcgis.gis._impl._apikeys import APIKeyManager, APIKey

gis = GIS("https://devext.arcgis.com", "andrew_token", "#2020EsriConference", verify_cert=False, trust_env=True)
USERNAME = gis.users.me.username is None


###########################################################################
@unittest.skipIf(USERNAME, "Cannot Access Developer Account")
class TestLoginWithAPIKey(unittest.TestCase):
    def test_login_api_key(self):
        for k in  gis.api_keys.keys:
            if k._item.title.find('delete') > -1 or k._item.title.find("econd") > -1:
                k.delete()
        for k in gis.api_keys.keys:
            if k._item.title.lower().find('first') > -1:
                break
        api_key_gis = GIS(url="https://devext.arcgis.com", api_key=k.properties.apikey, verify_cert=False, set_active=False)
        assert api_key_gis.properties.appInfo.appOwner == 'andrew_token'
    def test_login_api_key_environment_variable(self):
        """tests logging in with API Key in environmental os variable"""

        for k in gis.api_keys.keys:
            if k._item.title.lower().find('first') > -1:
                break
        import os
        with unittest.mock.patch.dict('os.environ', {'ESRI_API_KEY': k.properties.apikey}, clear=True):

            with unittest.mock.patch.object(os, "getenv", return_value=k.properties.apikey):
                api_key_gis = GIS(url="https://devext.arcgis.com", api_key=k.properties.apikey, verify_cert=False, set_active=False)
                assert api_key_gis.properties.appInfo.appOwner == 'andrew_token'
###########################################################################
@unittest.skipIf(USERNAME, "Cannot Access Developer Account")
class TestAPIKeyManager(unittest.TestCase):
    """Tests the Manager Operations"""
    def test_access(self):
        assert isinstance(gis.api_keys, APIKeyManager)
    def test_keys(self):
        """Tests listing all the keys"""
        assert isinstance(gis.api_keys.keys, tuple)
    def test_get(self):
        """tests the retrieve function in the API"""
        akm = gis.api_keys
        api_item = akm.create(title="delete_me", tags="geocoding fun, the other stuff", description="description")
        apikey = api_item.properties.apikey
        assert akm.get(apikey).properties.apikey == apikey
        api_item.delete()
    def test_validate(self):
        akm = gis.api_keys
        api_item = akm.create(title="delete_me", tags="geocoding fun, the other stuff", description="description")
        assert akm.validate(api_item)
        api_item.delete()
###########################################################################
@unittest.skipIf(USERNAME, "Cannot Access Developer Account")
class TestAPIKey(unittest.TestCase):
    """Tests the API Key Operations"""
    def test_properties(self):
        """tests the properties property"""
        akm = gis.api_keys
        api_item = akm.create(title="delete_me", tags="geocoding fun, the other stuff", description="description")
        assert api_item.properties
        api_item.delete()
    def test_reset(self):
        """tests the reset function in the API"""
        akm = gis.api_keys
        api_item = akm.create(title="delete_me", tags="geocoding fun, the other stuff", description="description")
        old_api_key = api_item.properties.apikey
        api_item.reset()
        assert api_item.properties.apikey != old_api_key
        api_item.delete()
    def test_update(self):
        """tests the update function in the API"""
        akm = gis.api_keys
        api_item = akm.create(title="delete_me", tags="geocoding fun, the other stuff", description="description")
        orig_ref = api_item.properties.httpReferrers
        assert api_item.update(http_referers=['https://arcgis.com'])
        assert orig_ref != api_item.properties.httpReferrers
        api_item.delete()
if __name__ == "__main__":
    unittest.main()

