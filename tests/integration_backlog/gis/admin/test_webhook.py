import unittest
import uuid
from arcgis.gis.admin._wh import WebhookManager
from utils.decorators import integration_test, profiles

key = uuid.uuid4().hex[:5]


@profiles.admin_enterprise
@integration_test
class TestWebhooks(unittest.TestCase):
    """Tests the webhook manager and associates functionality"""

    def test_get_whm(self):
        """tests the basic get web hook manager"""
        admin = self.gis.admin
        webhook = admin.webhooks
        assert isinstance(webhook, WebhookManager)
        assert webhook

    def test_create_delete(self):
        """tests the basic get web hook manager"""
        admin = self.gis.admin
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
        admin = self.gis.admin
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
