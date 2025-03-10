import os, uuid
import time
import unittest
from utils._logging import enable_verbose_logging
from arcgis.gis._impl import ItemTypeEnum

from arcgis.features import FeatureLayerCollection
from arcgis.features.managers import (
    WebHook,
    WebHookServiceManager,
    WebHookEvents,
    WebHookScheduleInfo,
)
from arcgis.gis.server.admin._services import (
    ServiceWebHookManager,
    ServiceWebHook,
)
from utils.data_utils import publish_test_item, cleanup_published_items
from utils.decorators import integration_test, profiles
from integration.config import QALAB_ROOT_PATH

fp = os.path.join(
    QALAB_ROOT_PATH, "features_mod_WebhookService_cls", "webhook_data.zip"
)


enable_verbose_logging()


@profiles.admin_enterprise_and_agol
@integration_test
class TestFeatureServiceWebHook(unittest.TestCase):
    """
    Tests the Webhook Service Framework
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up feature service for test
        """
        # Publish new item for testing
        uid = int(time.time())
        cls.layer_name = f"webhook_data_fgdb_{uid}"
        item_type = ItemTypeEnum.FILE_GEODATABASE
        cls.published_item = publish_test_item(
            gis=cls.gis,
            layer_name=cls.layer_name,
            source_data_path=fp,
            item_type=item_type,
            prep_for_editing=False,
        )
        cls.flc = cls.published_item.layers[0].container
        isinstance(cls.flc, FeatureLayerCollection)

        # update item definition to enable ChangeTracking
        update_dict = {
            "hasStaticData": False,
            "capabilities": "Query,Editing,Create,Update,Delete,ChangeTracking",
            "editorTrackingInfo": {
                "allowAnonymousToDelete": True,
                "allowAnonymousToUpdate": True,
                "allowOthersToDelete": True,
                "allowOthersToQuery": True,
                "allowOthersToUpdate": True,
                "enableEditorTracking": False,
                "enableOwnershipAccessControl": False,
            },
        }
        cls.flc.manager.update_definition(update_dict)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            whm = cls.flc.manager.webhook_manager
            if len(whm.list) > 0:
                all([hook.delete() for hook in whm.list])
        finally:
            cleanup_published_items([cls.published_item])

    def test_webhook(self):
        """
        Tests the WebHook Class' Methods and properties
        """
        whm = self.flc.manager.webhook_manager
        if self.gis._is_agol:
            assert isinstance(whm, WebHookServiceManager)
        else:
            assert isinstance(whm, ServiceWebHookManager)

        wh_name = f"hook{uuid.uuid4().hex[:5]}test"
        hook = whm.create(
            wh_name,
            "https://kgalliher.esri.com/FabricPyAPI",
        )
        self.assertIsNotNone(hook, "Webhook is None")

        hook_service_name = hook.properties.get("serviceName")
        if hook_service_name and not self.gis._is_agol:
            self.assertEqual(
                self.layer_name, hook_service_name, "Incorrect service name found"
            )

        hook_name = hook.properties.get("name")
        self.assertEqual(wh_name, hook_name, "Incorrect webhook name found")

    def test_edit_webhook(self):
        whm = self.flc.manager.webhook_manager
        wh_name = f"hook{uuid.uuid4().hex[:5]}test"
        wh = whm.create(
            wh_name,
            "https://kgalliher.esri.com/FabricPyAPI",
        )
        res = wh.edit(
            name=None,
            change_types="FeaturesCreated",
            hook_url=None,
            signature_key=None,
            active=None,
            schedule_info=None,
            payload_format=None,
        )
        self.assertEqual(
            ["FeaturesCreated"], res.get("changeTypes"), "Incorrect changeTypes value"
        )
        self.assertEqual(
            "", res.get("scheduleInfo").get("name"), "Incorrect scheduleInfo value"
        )
        res2 = wh.edit(
            name=None,
            change_types=None,
            hook_url=None,
            signature_key=None,
            active=True,
            schedule_info=None,
            payload_format=None,
        )
        self.assertEqual(
            ["FeaturesCreated"], res2.get("changeTypes"), "Incorrect changeTypes value"
        )
        self.assertEqual(
            "", res.get("scheduleInfo").get("name"), "Incorrect scheduleInfo value"
        )
        import datetime as _dt

        res3 = wh.edit(
            schedule_info=WebHookScheduleInfo(
                name="whm test", start_at=_dt.datetime.now()
            ),
        )
        self.assertEqual(
            ["FeaturesCreated"], res3.get("changeTypes"), "Incorrect changeTypes value"
        )
        self.assertEqual(
            "whm test",
            res3.get("scheduleInfo").get("name"),
            "Incorrect scheduleInfo value",
        )

    def test_web_hook_manager(self):
        """
        Tests the WebHook Manager Class' Methods and properties
        """
        whm = self.flc.manager.webhook_manager
        if self.gis._is_agol:
            assert isinstance(whm, WebHookServiceManager)
        else:
            assert isinstance(whm, ServiceWebHookManager)

        wh = whm.create(
            f"hook{uuid.uuid4().hex[:5]}test",
            "https://kgalliher.esri.com/",
        )
        assert wh.properties
        hooks = whm.list
        for hook in hooks:
            if self.gis._is_agol:
                assert isinstance(hook, WebHook)
            else:
                assert isinstance(hook, ServiceWebHook)
            del hook
        eh = whm.enable_hooks()
        self.assertTrue(eh, "Webooks not enabled")
        dh = whm.disable_hooks()
        self.assertTrue(dh, "Webooks not disabled")


if __name__ == "__main__":
    unittest.main()
