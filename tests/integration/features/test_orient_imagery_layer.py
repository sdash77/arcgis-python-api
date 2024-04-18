import sys
import logging
import unittest, os, uuid
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.features.layer import OrientedImageryLayer
from arcgis.gis._impl._dataclasses._contentds import (
    ItemTypeEnum,
    ItemProperties,
)
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


profiles = ['your_online_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

QA_LABS = QALAB_ROOT_PATH + r"\oriented_image_layer"
DATASET = "OI_sample.gdb.zip"


@integration_test
class TestOrientedImageryLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_objs = [
            GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            for profile in profiles
        ]
        PDATA = os.path.join(QA_LABS, DATASET)
        ip = ItemProperties(
            **{
                "item_type": ItemTypeEnum.FILE_GEODATABASE,
                "title": f"FGDB{uuid.uuid4().hex[: 4]}",
                "tags": "tags",
            }
        )
        cls.items = []
        cls.pitems = []
        for gis in cls.gis_objs:
            item = gis.content.add(item_properties=ip, data=PDATA)
            cls.items.append(item)
            cls.pitems.append(item.publish())

    def test_fromitem(self):
        """tests the from"""
        for item in self.pitems:
            lyr = OrientedImageryLayer.fromitem(item)
            assert isinstance(lyr, OrientedImageryLayer)

    def test_create_OIL(self):
        """create OI Layer"""
        for item in self.pitems:
            lyr = OrientedImageryLayer(url=f"{item.url}/0", gis=item._gis)
            assert isinstance(lyr, OrientedImageryLayer)

    @classmethod
    def tearDownClass(cls):
        for item in cls.pitems:
            item.delete()
        for item in cls.items:
            item.delete()


if __name__ == "__main__":
    unittest.main()
