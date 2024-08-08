import unittest
import unittest.mock
from arcgis.gis import GIS, Item
from arcgis.gis._impl._apikeys import APIKeyManager, APIKey
from arcgis.auth.tools._util import detect_proxy
from utils.decorators import integration_test

PROXIES = detect_proxy(True)
gis = GIS(
    profile='your_online_profile',
    verify_cert=False,
    proxy=PROXIES,
)
USERNAME = gis.users.me.username is None


###########################################################################
@unittest.skipIf(USERNAME, "Cannot Access Developer Account")
@integration_test
class TestLoginWithAPIKey(unittest.TestCase):
    def test_login_api_key(self):
        apk: APIKeyManager = gis.api_keys
        k = apk.create(
            title="testkey2",
            tags="tags",
            http_referers=[],
            redirect_uris=[],
            privileges=[
                "premium:user:geocode:temporary",
                "portal:apikey:basemaps",
            ],
        )

        api_key_gis = GIS(
            url="https://www.arcgis.com",
            api_key=k.properties.apikey,
            verify_cert=False,
            proxy=PROXIES,
            set_active=False,
        )
        assert (
            api_key_gis.properties.appInfo.appOwner == gis.users.me.username
        )
        assert k.delete()

    def test_login_api_key_environment_variable(self):
        """tests logging in with API Key in environmental os variable"""

        apk: APIKeyManager = gis.api_keys
        k = apk.create(
            title="testkey2",
            tags="tags",
            http_referers=[],
            redirect_uris=[],
            privileges=[
                "premium:user:geocode:temporary",
                "portal:apikey:basemaps",
            ],
        )
        import os

        with unittest.mock.patch.dict(
            "os.environ", {"ESRI_API_KEY": k.properties.apikey}, clear=True
        ):

            with unittest.mock.patch.object(
                os, "getenv", return_value=k.properties.apikey
            ):
                api_key_gis = GIS(
                    url="https://www.arcgis.com",
                    api_key=k.properties.apikey,
                    verify_cert=False,
                    proxy=PROXIES,
                    set_active=False,
                )
                assert (
                    api_key_gis.properties.appInfo.appOwner
                    == gis.users.me.username
                )

        assert k.delete()


###########################################################################
@unittest.skipIf(USERNAME, "Cannot Access Developer Account")
@integration_test
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
        api_item = akm.create(
            title="delete_me",
            tags="geocoding fun, the other stuff",
            description="description",
        )
        apikey = api_item.properties.apikey
        assert akm.get(apikey).properties.apikey == apikey
        api_item.delete()

    def test_validate(self):
        akm = gis.api_keys
        api_item = akm.create(
            title="delete_me",
            tags="geocoding fun, the other stuff",
            description="description",
        )
        assert akm.validate(api_item)
        api_item.delete()


###########################################################################
@unittest.skipIf(USERNAME, "Cannot Access Developer Account")
@integration_test
class TestAPIKey(unittest.TestCase):
    """Tests the API Key Operations"""

    def test_properties(self):
        """tests the properties property"""
        akm = gis.api_keys
        api_item = akm.create(
            title="delete_me",
            tags="geocoding fun, the other stuff",
            description="description",
        )
        assert api_item.properties
        api_item.delete()

    def test_reset(self):
        """tests the reset function in the API"""
        akm = gis.api_keys
        api_item = akm.create(
            title="delete_me",
            tags="geocoding fun, the other stuff",
            description="description",
        )
        old_api_key = api_item.properties.apikey
        api_item.reset()
        assert api_item.properties.apikey != old_api_key
        api_item.delete()

    def test_update(self):
        """tests the update function in the API"""
        akm = gis.api_keys
        api_item = akm.create(
            title="delete_me",
            tags="geocoding fun, the other stuff",
            description="description",
        )
        orig_ref = api_item.properties.httpReferrers
        assert api_item.update(http_referers=["https://arcgis.com"])
        assert orig_ref != api_item.properties.httpReferrers
        api_item.delete()


if __name__ == "__main__":
    unittest.main()
