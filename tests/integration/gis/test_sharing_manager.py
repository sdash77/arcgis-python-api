import sys
import time
import logging, uuid
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestSharingManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = []

    def test_shared_with(self):
        for item in self.gis.content.search(
            f"owner:{self.gis.users.me.username} type:'File Geodatabase'"
        ):
            sharing = item.sharing
            assert isinstance(sharing.shared_with, dict)

    def test_list_groups(self):
        for item in self.gis.content.search(
            f"owner:{self.gis.users.me.username} type:'File Geodatabase'"
        ):
            gm = self.gis.groups
            group = gm.create(
                f"test group {uuid.uuid4().hex[:4]}", tags='tags'
            )

            sharing = item.sharing
            gm = sharing.groups
            assert gm.add(group)
            time.sleep(2)
            assert len(gm.list()) > 0
            group.delete()

    def test_sharing_manager(self):
        for item in self.gis.content.search(
            f"owner:{self.gis.users.me.username} type:'File Geodatabase'"
        ):
            gm = self.gis.groups
            group = gm.create(
                f"test group {uuid.uuid4().hex[:4]}", tags='tags'
            )

            sharing = item.sharing
            original_sharing_count = len(sharing.groups.list())
            gm = sharing.groups
            assert gm.add(group)
            import time

            time.sleep(2)
            assert len(gm.list()) == original_sharing_count + 1

            gm.remove(group)
            assert len(sharing.groups.list()) == original_sharing_count
            self.groups.append(group)
            break

    @classmethod
    def tearDownClass(cls):
        for grp in cls.groups:
            assert grp.delete()


if __name__ == "__main__":
    unittest.main()
