import sys

#
#  Update the Path to set the test area
# sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
import logging
import uuid
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

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


class Test_CloneGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_source = GIS(profile='your_online_profile', set_active=False)
        gmgr = cls.gis_source.groups
        cls.source_groups = [
            gmgr.create(title=f"group_{uuid.uuid4().hex[:4]}", tags="tags"),
            gmgr.create(title=f"group_{uuid.uuid4().hex[:4]}", tags="tags"),
            gmgr.create(title=f"group_{uuid.uuid4().hex[:4]}", tags="tags"),
        ]

    def test_clone_groups(self):
        gis = GIS(profile='your_enterprise_profile')
        groups = gis.groups.clone(self.source_groups)
        assert len(groups) == len(self.source_groups)
        [g.result().delete() for g in groups]

    @classmethod
    def tearDownClass(cls):
        [g.delete() for g in cls.source_groups]


if __name__ == "__main__":
    unittest.main()
