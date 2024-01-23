import sys

#
#  Update the Path to set the test area
# sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test

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
class TestCanReassignItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile='your_online_profile')
        fp = r"\\qalab_server\pydata\v109\geosaurus\gis_mod_Item_cls\issue_10434.zip"
        cls.item = cls.gis.content.add(
            item_properties={
                "title": "reassign_item_test",
                "type": "Shapefile",
            },
            data=fp,
        )
        cls.pitem = cls.item.publish(
            {
                "name": "reassign_item_test",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.pitem.delete()
        cls.item.delete()

    def test_can_reassign(self):
        """tests the new reassign operation"""
        items = [self.item, self.pitem]
        for item in items:
            for user in self.gis.users.search("*")[:3]:
                assert isinstance(
                    item.can_reassign(target_user=user.username), tuple
                )
                assert isinstance(item.can_reassign(target_user=user), tuple)


if __name__ == "__main__":
    unittest.main()
