import os, uuid
import unittest
from arcgis.gis import GIS
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
from utils.decorators import integration_test, profiles
from integration.config import QALAB_ROOT_PATH


hook_end_point_url = "https://en1dx5cd33emv.x.pipedream.net/"
fp = os.path.join(
    QALAB_ROOT_PATH, "features_mod_WebhookService_cls", "webhook_data.zip"
)


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
        print(cls.gis)

        # delete previous test outputs if exists
        outputs = cls.gis.content.search("ABCD1234EFGH")
        if outputs:
            for item in outputs:
                print(item)
                item.delete()

        # add test item
        item = cls.gis.content.add(
            {
                "type": "File Geodatabase",
                "tags": "erase me",
                "title": "ABCD1234EFGH",
            },
            data=fp,
        )
        cls.pitem = item.publish()
        cls.flc = cls.pitem.layers[0].container
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
        cls.pitem.delete()

    def test_webhook(self):
        """
        Tests the WebHook Class' Methods and properties
        """
        whm = self.flc.manager.webhook_manager
        dah = whm.delete_all_hooks()
        if self.gis._is_agol:
            assert isinstance(whm, WebHookServiceManager)
        else:
            assert isinstance(whm, ServiceWebHookManager)

        wh = whm.create(
            f"hook{uuid.uuid4().hex[:5]}test",
            "https://en1dx5cd33emv.x.pipedream.net",
            active=True,
        )
        assert wh.properties
        res = wh.edit(
            name=None,
            change_types="FeaturesCreated",
            hook_url=None,
            signature_key=None,
            active=None,
            schedule_info=None,
            payload_format=None,
        )
        assert res
        res2 = wh.edit(
            name=None,
            change_types=[
                WebHookEvents.FEATURESEDITED,
                WebHookEvents.FEATURESUPDATED,
            ],
            hook_url=None,
            signature_key=None,
            active=None,
            schedule_info=None,
            payload_format=None,
        )
        assert res2
        import datetime as _dt

        res3 = wh.edit(
            schedule_info=WebHookScheduleInfo(
                name="whm test", start_at=_dt.datetime.now()
            ),
        )
        assert res3
        assert wh.properties
        assert wh.delete()
        assert len(whm.list) == 0

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
            "https://en1dx5cd33emv.x.pipedream.net",
            active=True,
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

        assert eh
        dh = whm.disable_hooks()

        assert dh
        dah = whm.delete_all_hooks()
        assert dah


if __name__ == "__main__":
    unittest.main()
