import sys
import uuid
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item, ItemProperties, ItemTypeEnum
from arcgis.features import FeatureLayerCollection, FeatureLayer
from utils.decorators import integration_test, profiles
from integration.config import QALAB_ROOT_PATH

from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestFeatureLayerCollectionSwap(unittest.TestCase):
    """Tests the swap view logic"""

    @classmethod
    def setUpClass(cls):
        uid: str = uuid.uuid4().hex[:3]
        cls.path1 = QALAB_ROOT_PATH + r"\swap_layer\swap_layer1.zip"
        cls.path2 = QALAB_ROOT_PATH + r"\swap_layer\swap_layer2.zip"

        content = cls.gis.content
        folder = content.folders.get()
        ip = ItemProperties(
            title=f"swap_{uid}_source", item_type=ItemTypeEnum.SHAPEFILE
        )

        cls.item_source = folder.add(item_properties=ip, file=cls.path1).result()
        cls.pitem_source = cls.item_source.publish(
            {
                "name": f"swap_{uid}_source",
                "maxRecordCount": 2000,
                "hasStaticData": True,
                "layerInfo": {"capabilities": "Query"},
            }
        )

        mgr = cls.pitem_source.layers[0].container.manager
        cls.view_item_source = mgr.create_view(name=f"swap_{uid}_view")
        ip = ItemProperties(
            title=f"swap_{uid}_replace", item_type=ItemTypeEnum.SHAPEFILE
        )

        cls.item_replace = folder.add(item_properties=ip, file=cls.path2).result()
        cls.pitem_replace = cls.item_replace.publish(
            {
                "name": f"swap_{uid}_replace",
                "maxRecordCount": 2000,
                "hasStaticData": True,
                "layerInfo": {"capabilities": "Query"},
            }
        )

        print("stop")

    def test_run_it(self):
        flc: FeatureLayerCollection = FeatureLayerCollection.fromitem(
            self.view_item_source
        )
        layer: FeatureLayer = FeatureLayer.fromitem(self.pitem_replace)
        index: int = 0
        mgr = flc.manager
        result = mgr.swap_view(index=index, new_source=layer)
        assert result

    @classmethod
    def tearDownClass(cls):
        cls.view_item_source.delete(permanent=True)
        cls.pitem_replace.delete(permanent=True)
        cls.item_replace.delete(permanent=True)
        cls.pitem_source.delete(permanent=True)
        cls.item_source.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
