import sys
import logging
import unittest
import uuid
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import (
    GIS,
    UserManager,
    ContentManager,
    ItemTypeEnum,
    Item,
    ItemProperties,
)
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


profiles = ['your_online_admin_profile', 'your_ent_admin_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestContentManagerReassignTo(unittest.TestCase):
    """tests the reassigning of items to a new user"""

    def test_reassign_to_enterprise(self):
        """tests the re-assign logic in enterprise"""

        gis = GIS(profile=profiles[1], verify_cert=False, proxy=PROXIES)
        um: UserManager = gis.users
        pw = f"A1{uuid.uuid4().hex[:5]}!z"
        user1 = um.create(
            username=f"a{uuid.uuid4().hex[:5]}z",
            password=pw,
            firstname=f"a{uuid.uuid4().hex[:3]}z",
            lastname=f"a{uuid.uuid4().hex[:3]}z",
            email="testaccount@esri.com",
            role="org_user"
        )
        fp = QALAB_ROOT_PATH + r"\esri_requests\raster_data\Clip_090160.tif"
        try:
            ip: ItemProperties = ItemProperties(
                **{
                    "title": "Clip_090160",
                    "item_type": ItemTypeEnum.IMAGE,
                    "extension": "tif",
                }
            )
            item: Item = gis.content.add(
                item_properties=ip,
                data=fp,
            )
        except Exception as ex:
            user1.delete()
            user1 = None
            raise ex
        if user1:
            item.reassign_to(target_owner=user1)
            assert len(user1.items()) > 0
            [i.delete() for i in user1.items()]
            user1.delete()

    def test_reassign_to_agol(self):
        """tests the re-assign logic in AGOL"""

        gis = GIS(profile=profiles[0], verify_cert=False, proxy=PROXIES)
        um: UserManager = gis.users
        pw = f"A1{uuid.uuid4().hex[:5]}!z"
        user1 = um.create(
            username=f"a{uuid.uuid4().hex[:5]}z",
            password=pw,
            firstname=f"a{uuid.uuid4().hex[:3]}z",
            lastname=f"a{uuid.uuid4().hex[:3]}z",
            email="testaccount@esri.com",
            role="org_user"
        )
        fp = QALAB_ROOT_PATH + r"\esri_requests\raster_data\Clip_090160.tif"
        try:
            ip: ItemProperties = ItemProperties(
                **{
                    "title": "Clip_090160",
                    "item_type": ItemTypeEnum.IMAGE,
                    "extension": "tif",
                }
            )
            item: Item = gis.content.add(
                item_properties=ip,
                data=fp,
            )
        except Exception as ex:
            user1.delete()
            user1 = None
            raise ex
        if user1:
            item.reassign_to(target_owner=user1)
            assert len(user1.items()) > 0
            [i.delete() for i in user1.items()]
            user1.delete()


if __name__ == "__main__":
    unittest.main()
