import sys
import os

#
#  Update the Path to set the test area
#  sys.path.insert(0, r"C:\SVN\geosaurus_issue_9564\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item, ContentManager, User, UserManager
from arcgis.features import FeatureLayer, FeatureLayerCollection

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

FILE_PATH = r"\\qalab_server\pydata\v109\geosaurus\ContingentValues\SDs\CV_SimpleSubtypesFromSD.sd"


@unittest.skipIf(os.path.isfile(FILE_PATH) == False, "Missing Test Data")
class TestContingentValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """sets up the class"""

        url: str = "https://rqawinbi01pt.ags.esri.com/gis"
        username: str = "PAPIadmin"
        password: str = "PAPIletmein01"

        gis = GIS(
            url=url,
            username=username,
            password=password,
            verify_cert=False,
            use_gen_token=True,
        )
        user: User = gis.users.me
        user.update(security_question=1, security_answer="Redlands")
        cls.gis = GIS(
            url=url, username=username, password=password, verify_cert=False
        )
        items: list[Item] = gis.content.search("CV_SimpleSubtypesFromSD")
        [item.delete() for item in items]
        if len(items) == 0:
            cm: ContentManager = gis.content
            cls.sditem_ent = cm.add(item_properties={}, data=FILE_PATH)
            cls.pitem_ent = cls.sditem_ent.publish()

    def test_continegent_values_field_group_enterprise(self):
        gis: GIS = self.gis

        fl: FeatureLayer = self.pitem_ent.layers[0]
        assert isinstance(fl.contingent_values, dict)
        assert isinstance(fl.field_groups, dict)

    @classmethod
    def tearDownClass(cls):
        cls.pitem_ent.delete()
        cls.sditem_ent.delete()


if __name__ == "__main__":
    unittest.main()
