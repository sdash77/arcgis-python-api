import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test
from config import QALAB_ROOT_PATH

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile']  # , 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestItemRelationships(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_objs = [
            GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            for profile in profiles
        ]
        cls.items = []
        cls.pitems = []
        fp: str = QALAB_ROOT_PATH + r"\esri_requests\issue_10433\issue_10433.zip"
        for gis in cls.gis_objs:
            item = gis.content.add(
                item_properties={
                    "type": "Shapefile",
                    "title": "issue_10433",
                },
                data=fp,
            )
            cls.items.append(item)
            cls.pitems.append(
                item.publish(
                    {
                        'name': "issue10433data",
                    }
                )
            )

    def test_relationships(self):
        """tests the relationships"""
        for pitem in self.pitems:
            related = pitem.related_items(
                rel_type="Service2Data", direction="forward"
            )
            assert len(related) > 0

    @classmethod
    def tearDownClass(cls):
        for i in cls.pitems:
            i.delete()
        for i in cls.items:
            i.delete()


if __name__ == "__main__":
    unittest.main()
