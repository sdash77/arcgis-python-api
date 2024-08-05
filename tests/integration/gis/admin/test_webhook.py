import sys
import unittest
import urllib.request
import uuid
import arcgis
from arcgis.gis import GIS
from arcgis.gis.admin._wh import WebhookManager
from utils.decorators import integration_test


PROFILES = ["your_ent_admin_profile"]
proxies = urllib.request.getproxies()
key = uuid.uuid4().hex[:5]


@integration_test
class TestWebhooks(unittest.TestCase):
    """Tests the webhook manager and associates functionality"""

    def test_get_whm(self):
        """tests the basic get web hook manager"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            admin = gis.admin
            webhook = admin.webhooks
            assert isinstance(webhook, WebhookManager)
            assert webhook

    def test_create_delete(self):
        """tests the basic get web hook manager"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            admin = gis.admin
            wh = admin.webhooks
            myHook = wh.create(
                f"ajc{key}WORK",
                "https://en1dx5cd33emv.x.pipedream.net",
                "ALL",
                secret="mysecretkey",
            )
            assert myHook
            assert myHook.delete()

    def test_create_delete(self):
        """tests the basic get web hook manager"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            admin = gis.admin
            wh = admin.webhooks
            myHook = wh.create(
                f"ajc{key}WORK", "https://en1dx5cd33emv.x.pipedream.net", "ALL"
            )
            assert myHook

            myHook.update(secret="mysecretkey")
            assert myHook.properties.secret
            myHook.update(secret="")
            assert not "secret" in myHook.properties
            assert myHook.delete()


if __name__ == "__main__":
    unittest.main()
