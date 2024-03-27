import sys

import json
import uuid
import logging
import concurrent.futures
import unittest
from arcgis.features import FeatureLayer
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test
from integration.config import QALAB_ROOT_PATH

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']  #
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


def search_and_remove(gis):
    for i in gis.content.search("test_new_edit_features.zip"):
        [ii.delete() for ii in i.related_items("Service2Data", 'reverse')]

        i.delete()


@integration_test
class TestEditFeaturesUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fp = QALAB_ROOT_PATH + r"\edits_features_tests\test_new_edit_features.zip"
        cls.gis_objs = [
            GIS(profile=p, verify_cert=False, proxy=PROXIES)
            for p in profiles
        ]
        [search_and_remove(gis) for gis in cls.gis_objs]
        cls.items = []
        cls.pitems = []
        cls.deletes = [2]
        cls.adds = [
            {
                "geometry": {
                    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                    "rings": [
                        [
                            [-13454319.533799998, 4426881.11234218],
                            [-13405346.871, 4480458.836900003],
                            [-13343138.367800001, 4417531.982509322],
                            [-13387257.8852, 4383731.248593805],
                            [-13454319.533799998, 4426881.11234218],
                        ]
                    ],
                },
                "attributes": {"OBJECTID": 34},
            }
        ]
        cls.updates = [
            {
                "geometry": {
                    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                    "rings": [
                        [
                            [-13454319.533799998, 4426881.11234218],
                            [-13405346.871, 4480458.836900003],
                            [-13343138.367800001, 4417531.982509322],
                            [-13387257.8852, 4383731.248593805],
                            [-13454319.533799998, 4426881.11234218],
                        ]
                    ],
                },
                "attributes": {"OBJECTID": 1},
            }
        ]

        for gis in cls.gis_objs:
            item = gis.content.add(
                {
                    "type": "File Geodatabase",
                    "name": uuid.uuid4().hex[:6],
                },
                data=fp,
            )
            cls.items.append(item)
            cls.pitems.append(item.publish())
        for item in cls.pitems:
            lyr: FeatureLayer = item.layers[0]
            container = lyr.container
            container.manager.update_definition(
                json_dict=json.loads(
                    """{"hasStaticData":false,"capabilities":"Query,Uploads,Editing,Create,Update,Delete","layerOverridesEnabled":true,"editorTrackingInfo":{"enableEditorTracking":false,"enableOwnershipAccessControl":false,"allowOthersToUpdate":true,"allowOthersToDelete":true,"allowOthersToQuery":true,"allowAnonymousToQuery":true,"allowAnonymousToUpdate":true,"allowAnonymousToDelete":true}}"""
                )
                # {"capabilities": "Query,Uploads"}
            )
            container.manager.refresh()

    def test_add_feature(self):
        for item in self.pitems:
            lyr = item.layers[0]
            result = lyr.edit_features(
                adds=self.adds,
                future=True,
                rollback_on_failure=True,
            )
            if isinstance(result, concurrent.futures.Future):
                assert isinstance(result, concurrent.futures.Future)
                assert isinstance(result.result(), (list, dict))
                assert result.result()

    def test_adds_update_feature(self):
        for item in self.pitems:
            lyr = item.layers[0]
            result = lyr.edit_features(
                adds=self.adds,
                updates=self.updates,
                future=True,
                rollback_on_failure=True,
            )
            if isinstance(result, concurrent.futures.Future):
                assert isinstance(result, concurrent.futures.Future)
                assert isinstance(result.result(), (list, dict))
                assert result.result()

    def test_adds_update_deletes_feature(self):
        for item in self.pitems:
            lyr = item.layers[0]
            result = lyr.edit_features(
                adds=self.adds,
                updates=self.updates,
                deletes=self.deletes,
                future=True,
                rollback_on_failure=True,
            )
            if isinstance(result, concurrent.futures.Future):
                assert isinstance(result, concurrent.futures.Future)
                assert isinstance(result.result(), (list, dict))
                assert result.result()

    @classmethod
    def tearDownClass(cls):
        for pitem in cls.pitems:
            pitem.delete()
        for item in cls.items:
            item.delete()


if __name__ == "__main__":
    unittest.main()
