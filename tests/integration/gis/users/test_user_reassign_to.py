import sys
import logging
import unittest
import uuid
from collections import Counter
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import (
    GIS,
    UserManager,
    ContentManager,
    ItemTypeEnum,
    Item,
    ItemProperties,
)
from integration.config import get_resource_path
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


PROXIES = detect_proxy(True)  # Handles Fiddler when True
# enable_verbose_logging(__logger__)


@profiles.admin_enterprise_and_agol
@integration_test
class TestContentManagerReassignTo(unittest.TestCase):
    """tests the reassigning of items to a new user"""

    def test_reassign_to_nonexistent_user(self):
        test_user_name = "arcgis_python"

        user_mgr = self.gis.users
        test_user = user_mgr.search(test_user_name)[0]
        reassign_to_nobody = test_user.reassign_to("non_existent_username")

        self.assertFalse(reassign_to_nobody, "Assigning to non-existent user was True")

    def test_reassign_to(self):
        """tests the re-assign logic in enterprise"""
        uid = uuid.uuid4().hex[:5]
        um: UserManager = self.gis.users
        pw = f"A1{uid}!z"
        user1 = um.create(
            username=f"a{uuid.uuid4().hex[:5]}z",
            password=pw,
            firstname=f"a{uuid.uuid4().hex[:3]}z",
            lastname=f"a{uuid.uuid4().hex[:3]}z",
            email="testaccount@esri.com",
            role="org_user",
        )
        fp = get_resource_path(
            "staging_data/esri_requests/Clip_090160.tif", unique_copy=True
        )
        item = None
        try:
            ip: ItemProperties = ItemProperties(
                title=f"Clip_090160_{uid}",
                item_type=ItemTypeEnum.IMAGE,
                extension="tif",
                tags="ntgrtn-tst",
            )
            item: Item = self.gis.content.add(
                item_properties=ip,
                data=fp,
            )
        except Exception as ex:
            user1.delete()
            user1 = None
            raise ex
        finally:
            if user1:
                item.reassign_to(target_owner=user1)
                assert len(Counter(user1.items())) > 0
                [i.delete() for i in user1.items()]
                user1.delete()


if __name__ == "__main__":
    unittest.main()
