import sys
import os
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item, ContentManager, User, UserManager
from arcgis.features import FeatureLayer, FeatureLayerCollection
from integration.config import QALAB_ROOT_PATH
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


profiles = ['your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

FILE_PATH = (
    QALAB_ROOT_PATH + r"\ContingentValues\CV_Gas.zip"
)


@unittest.skipIf(os.path.isfile(FILE_PATH) == False, "Missing Test Data")
@integration_test
class TestContingentValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """sets up the class"""
        gis = GIS(
            profile='your_online_profile',
            verify_cert=False,
            # use_gen_token=True,
        )
        # user: User = gis.users.me
        # user.update(security_question=1, security_answer="Redlands")
        cls.gis = (
            gis  # GIS(profile='your_online_profile', verify_cert=False)
        )
        items: list[Item] = gis.content.search("CV_Gas")
        [item.delete() for item in items]
        items: list[Item] = gis.content.search("CV_Gas")
        if len(items) == 0:
            cm: ContentManager = gis.content
            cls.sditem_ent = cm.add(
                item_properties={
                    "title": "CV_Gas",
                    "type": "File Geodatabase",
                    "tags": "gas",
                },
                data=FILE_PATH,
            )
            cls.pitem_ent = cls.sditem_ent.publish(
                publish_parameters={
                    "name": "CV_Gas",
                    'capabilities': "Create,Delete,Query,Update,Editing,Extract",
                }
            )

    def test_continegent_values_public(self):
        gis: GIS = self.gis

        fl: FeatureLayer = self.pitem_ent.layers[0]
        assert isinstance(fl.contingent_values, dict)
        assert isinstance(fl.field_groups, dict)

    def test_continegent_values_manager(self):
        gis: GIS = self.gis

        fl: FeatureLayer = self.pitem_ent.layers[0]
        mgr = fl.manager
        assert mgr.contingent_values
        assert mgr.field_groups

    @classmethod
    def tearDownClass(cls):
        cls.pitem_ent.delete()
        cls.sditem_ent.delete()


if __name__ == "__main__":
    unittest.main()
