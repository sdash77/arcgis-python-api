import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item, ItemProperties, ItemTypeEnum
from arcgis.features import FeatureLayerCollection, FeatureLayer
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


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestFeatureLayerCollectionSwap(unittest.TestCase):
    """Tests the swap view logic"""

    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_online_profile', verify_cert=False, proxy=PROXIES
        )
        cls.path1 = QALAB_ROOT_PATH + r"\swap_layer\swap_layer1.zip"
        cls.path2 = QALAB_ROOT_PATH + r"\swap_layer\swap_layer2.zip"
        content = cls.gis.content
        folder = content.folders.get()
        ip = ItemProperties(
            title="swap_layers_source", item_type=ItemTypeEnum.SHAPEFILE
        )
        cls.item_source = folder.add(
            item_properties=ip, file=cls.path1
        ).result()
        cls.pitem_source = cls.item_source.publish(
            {
                "name": "swap_layer_source",
            }
        )
        mgr = cls.pitem_source.layers[0].container.manager
        cls.view_item_source = mgr.create_view(name="swap_layer_view")
        ip = ItemProperties(
            title="swap_layers_replace", item_type=ItemTypeEnum.SHAPEFILE
        )
        cls.item_replace = folder.add(
            item_properties=ip, file=cls.path2
        ).result()
        cls.pitem_replace = cls.item_replace.publish(
            {
                "name": "swap_layer_replace",
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
        cls.view_item_source.delete()
        cls.pitem_replace.delete()
        cls.item_replace.delete()
        cls.pitem_source.delete()
        cls.item_source.delete()


if __name__ == "__main__":
    unittest.main()
