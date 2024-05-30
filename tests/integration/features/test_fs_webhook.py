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
from utils.decorators import integration_test

hook_end_point_url = "https://en1dx5cd33emv.x.pipedream.net/"
SKIPIF = False
msg = ""
try:
    PROFILE = "your_online_profile"
    gis = GIS(profile=PROFILE, verify_cert=False)
    SKIPIF = gis.version < [8, 2]
    if SKIPIF:
        msg = f"Incorrect Version {gis.version}"
except Exception as e:
    SKIPIF = True
    msg = f"An Error Occured {str(e)}"

try:
    ENT_PROFILE = "your_enterprise_profile"
    gis = GIS(profile=ENT_PROFILE, verify_cert=False)
    SKIPIF = gis.version < [10, 3]
    if SKIPIF:
        msg = f"Incorrect Version {gis.version}"
except Exception as e:
    SKIPIF = True
    msg = f"An Error Occured {str(e)}"

try:
    from utils import INTEGRATION_TESTS_DIR

    fp = os.path.join(INTEGRATION_TESTS_DIR, "features", "webhook_data.zip")
    if os.path.isfile(fp) == False:
        SKIPIF = True
        msg = "Missing file"
except:
    fp = r"./webhook_data.zip"
    if os.path.isfile(fp) == False:
        SKIPIF = True
        msg = "Missing file"


@unittest.skipIf(SKIPIF, msg)
@integration_test
class TestFeatureServiceWebHook(unittest.TestCase):
    """
    Tests the AGOL Webhook Service Framework
    """

    def test_web_hook(self):
        """
        Tests the Web Hook Class' Methods and properties
        """
        gis = GIS(
            profile=PROFILE,
            verify_cert=False,
            trust_env=True,
        )
        for item in gis.content.search("ABCD1234EFGH"):
            item.delete()
        item = gis.content.add(
            {
                "type": "File Geodatabase",
                "tags": "erase me",
                "title": "ABCD1234EFGH",
            },
            data=fp,
        )
        pitem = item.publish()
        flc = pitem.layers[0].container
        isinstance(flc, FeatureLayerCollection)
        import json

        update_dict2 = {
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
        flc.manager.update_definition(update_dict2)
        whm = flc.manager.webhook_manager
        dah = whm.delete_all_hooks()

        assert isinstance(whm, WebHookServiceManager)
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
        pitem.delete()
        item.delete()

    def test_web_hook_manager(self):
        """
        Tests the Web Hook Manager Class' Methods and properties
        """
        gis = GIS(
            profile=PROFILE,
            verify_cert=False,
            trust_env=True,
        )
        for item in gis.content.search("ABCD1234EFGH"):
            item.delete()
        item = gis.content.add(
            {
                "type": "File Geodatabase",
                "tags": "erase me",
                "title": "ABCD1234EFGH",
            },
            data=fp,
        )
        pitem = item.publish()
        flc = pitem.layers[0].container
        isinstance(flc, FeatureLayerCollection)
        import json

        update_dict2 = {
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
        flc.manager.update_definition(update_dict2)
        whm = flc.manager.webhook_manager
        assert isinstance(whm, WebHookServiceManager)

        wh = whm.create(
            f"hook{uuid.uuid4().hex[:5]}test",
            "https://en1dx5cd33emv.x.pipedream.net",
            active=True,
        )
        assert wh.properties
        hooks = whm.list
        for hook in hooks:
            assert isinstance(hook, WebHook)
            del hook
        eh = whm.enable_hooks()

        assert eh
        dh = whm.disable_hooks()

        assert dh
        dah = whm.delete_all_hooks()
        assert dah

        pitem.delete()
        item.delete()


@unittest.skipIf(SKIPIF, msg)
class TestFeatureServiceWebHookEnt(unittest.TestCase):
    """
    Tests the AGOL Webhook Service Framework
    """

    def test_web_hook(self):
        """
        Tests the Web Hook Class' Methods and properties
        """
        gis = GIS(
            profile=ENT_PROFILE,
            verify_cert=False,
            trust_env=True,
        )
        for item in gis.content.search("ABCD1234EFGH"):
            item.delete()
        item = gis.content.add(
            {
                "type": "File Geodatabase",
                "tags": "erase me",
                "title": "ABCD1234EFGH",
            },
            data=fp,
        )
        pitem = item.publish()
        flc = pitem.layers[0].container
        isinstance(flc, FeatureLayerCollection)
        import json

        update_dict2 = {
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
        flc.manager.update_definition(update_dict2)
        whm = flc.manager.webhook_manager
        dah = whm.delete_all_hooks()
        from arcgis.gis.server.admin._services import (
            ServiceWebHookManager,
            ServiceWebHook,
        )

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
        pitem.delete()
        item.delete()

    def test_web_hook_manager(self):
        """
        Tests the Web Hook Manager Class' Methods and properties
        """
        gis = GIS(
            profile=ENT_PROFILE,
            verify_cert=False,
            trust_env=True,
        )
        for item in gis.content.search("ABCD1234EFGH"):
            item.delete()
        item = gis.content.add(
            {
                "type": "File Geodatabase",
                "tags": "erase me",
                "title": "ABCD1234EFGH",
            },
            data=fp,
        )
        pitem = item.publish()
        flc = pitem.layers[0].container
        isinstance(flc, FeatureLayerCollection)
        import json

        update_dict2 = {
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
        flc.manager.update_definition(update_dict2)
        whm = flc.manager.webhook_manager
        from arcgis.gis.server.admin._services import (
            ServiceWebHookManager,
            ServiceWebHook,
        )

        assert isinstance(whm, ServiceWebHookManager)

        wh = whm.create(
            f"hook{uuid.uuid4().hex[:5]}test",
            "https://en1dx5cd33emv.x.pipedream.net",
            active=True,
        )
        assert wh.properties
        hooks = whm.list
        for hook in hooks:
            assert isinstance(hook, ServiceWebHook)
            del hook
        eh = whm.enable_hooks()

        assert eh
        dh = whm.disable_hooks()

        assert dh
        dah = whm.delete_all_hooks()
        assert dah

        pitem.delete()
        item.delete()


if __name__ == "__main__":
    unittest.main()
