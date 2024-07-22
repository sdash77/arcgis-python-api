import unittest
import uuid
from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy

from utils.decorators import integration_test


@unittest.skipIf(detect_proxy() is None, "no proxy")
@integration_test
class TestOauth2WithProxy(unittest.TestCase):
    """
    When a Proxy is Enabled this UnitTest tests the login method of the EsriOAuth2Auth class
    """

    @classmethod
    def setUpClass(cls):
        gis = GIS(
            profile='your_enterprise_profile',
            verify_cert=False,
            proxy=detect_proxy(),
        )
        item = gis.content.add(
            item_properties={
                'title': uuid.uuid4().hex,
                'type': 'Application',
                'allowedStoreAuth': True,
                "typeKeywords": ['Application'],
                "applicationType": "otherApplication",
            }
        )
        item.register(
            app_type='multiple', redirect_uris=["urn:ietf:wg:oauth:2.0:oob"]
        )
        cls._url = gis.url
        cls._client_id = item.app_info['client_id']
        cls._client_secret = item.app_info['client_secret']
        cls._proxy = detect_proxy()
        cls._itemid = item.itemid

    def tearDown(self):
        gis = GIS(
            profile='your_enterprise_profile',
            verify_cert=False,
            proxy=detect_proxy(),
        )
        gis.content.get(self._itemid).delete()

    def test_login(self):
        """"""
        gis = GIS(
            url=self._url,
            client_id=self._client_id,
            client_secret=self._client_secret,
            proxy=self._proxy,
            verify_cert=False,
        )
        assert gis.properties.appInfo


if __name__ == "__main__":
    unittest.main()
