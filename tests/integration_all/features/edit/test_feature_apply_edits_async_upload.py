import json
import uuid
import concurrent.futures
import unittest
from arcgis.features import FeatureLayer
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import QALAB_ROOT_PATH


# enable_verbose_logging()


def search_and_remove(gis):
    for i in gis.content.search("test_new_edit_features.zip"):
        [ii.delete() for ii in i.related_items("Service2Data", "reverse")]
        i.delete()


@profiles.enterprise_and_agol
@integration_test
class TestEditFeaturesUpload(unittest.TestCase):
    """test async edit_feature() with add, update and delete"""

    @classmethod
    def setUpClass(cls):
        fp = QALAB_ROOT_PATH + r"\edits_features_tests\test_new_edit_features.zip"

        search_and_remove(cls.gis)

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
        item_name = f"apply_edits_async_{uuid.uuid4().hex[:6]}"
        item = cls.gis.content.add(
            {
                "type": "File Geodatabase",
                "name": item_name,
            },
            data=fp,
        )
        cls.items.append(item)
        cls.pitems.append(
            item.publish({"name": item_name, "tags": "intergration-test"})
        )

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

        print(cls.pitems)

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
            pitem.delete(permanent=True)
        for item in cls.items:
            item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
