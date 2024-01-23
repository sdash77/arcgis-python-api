import sys
import time

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_sharing_manager_redo\src")
import logging, uuid
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
class TestSharingManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_objects = []
        cls.gis_objects = [
            GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            for profile in profiles
        ]
        cls.groups = []

    def test_shared_with(self):
        for gis in self.gis_objects:
            for item in gis.content.search(
                f"owner:{gis.users.me.username} type:'File Geodatabase'"
            ):
                sharing = item.sharing
                assert isinstance(sharing.shared_with, dict)

    def test_list_groups(self):
        for gis in self.gis_objects:
            for item in gis.content.search(
                f"owner:{gis.users.me.username} type:'File Geodatabase'"
            ):
                gm = gis.groups
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
        for gis in self.gis_objects:
            for item in gis.content.search(
                f"owner:{gis.users.me.username} type:'File Geodatabase'"
            ):
                gm = gis.groups
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
