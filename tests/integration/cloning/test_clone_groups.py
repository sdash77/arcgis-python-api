import sys
import os
import logging
import uuid
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

    def test_clone_groups_offline(self):
        fp = self.gis_source.groups.clone(self.source_groups, offline=True)
        assert len(fp) > 0
        assert fp[0]
        group_file = fp[0].result()
        assert os.path.isfile(group_file)
        os.remove(group_file)

    def test_clone_groups_load_offline(self):
        fp = self.gis_source.groups.clone(self.source_groups, offline=True)
        group_file = fp[0].result()
        gis = GIS(profile='your_enterprise_profile')
        gmgr = gis.groups
        groups = gmgr.load_offline_configuration(group_file)
        os.remove(group_file)
        assert len(groups) == 3
        [grp.result().delete() for grp in groups]

    @classmethod
    def tearDownClass(cls):
        [g.delete() for g in cls.source_groups]


if __name__ == "__main__":
    unittest.main()
