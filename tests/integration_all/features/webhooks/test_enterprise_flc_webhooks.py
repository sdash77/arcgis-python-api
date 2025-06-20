import unittest

from arcgis.features import FeatureLayerCollection
from arcgis.gis import User
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_enterprise
@integration_test
class Test_EnterpriseWebhooks(unittest.TestCase):

    test_service = None

    def setUp(self):
        user: User = self.gis.users.me
        self.item = self.gis.content.get("8e2f349ba5be4b5da8f44f5abccf85f8")
        servers = self.gis.admin.servers
        services = [
            service
            for service in servers.get("HOSTING_SERVER")[0].services.list("Hosted")
            if service._url.find("webhooks_tests_") > -1
        ]
        self.test_service = services[0]

    def tearDown(self):
        whm = self.test_service.webhook_manager
        if len(whm.list) > 0:
            all([hook.delete() for hook in whm.list])

    def test_webhook_mgr(self):
        flc = FeatureLayerCollection.fromitem(self.item)
        mgr = flc.manager
        whm = mgr.webhook_manager
        self.assertIsNotNone(whm, "Webhook Manager is None")

    def test_create_webhook(self):
        whm = self.test_service.webhook_manager
        hook = whm.create(
            name="simple_create",
            hook_url="https://kgalliher.esri.com/",
        )
        self.assertIsNotNone(hook, "Webhook is None")
        hook_service_name = hook.properties.get("serviceName")
        self.assertEqual(
            "webhooks_tests_DND", hook_service_name, "Incorrect service name found"
        )
        hook_name = hook.properties.get("name")
        self.assertEqual("simple_create", hook_name, "Incorrect webhook name found")
        hook_payload_format = hook.properties.get("payloadFormat")
        self.assertEqual("json", hook_payload_format, "Incorrect payload format.")

    def test_duplicate_webhooks_fails(self):
        whm = self.test_service.webhook_manager
        hook = whm.create(
            name="simple_create",
            hook_url="https://kgalliher.esri.com/",
        )
        self.assertIsNotNone(hook, "Webhook is None")
        with self.assertRaises(ValueError):
            whm.create(
                name="simple_create",
                hook_url="https://kgalliher.esri.com",
            )

    def test_enable_disable_webhooks(self):
        whm = self.test_service.webhook_manager
        assert whm.properties
        assert isinstance(whm.list, list)
        enable_hook = whm.enable_hooks()
        self.assertTrue(enable_hook, "Could not enable webhook")
        disable_hook = whm.disable_hooks()
        self.assertTrue(disable_hook, "Could not disable webhook")

    def test_rename_webhook(self):
        whm = self.test_service.webhook_manager
        assert len(whm.list) == 0
        hook = whm.create(
            name="simple_create",
            hook_url="https://kgalliher.esri.com",
        )
        hook.edit(name="new_name")
        self.assertEqual(
            "new_name", hook.properties["name"], "Webhook not renamed correctly."
        )


if __name__ == "__main__":
    unittest.main()
