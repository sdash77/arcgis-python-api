import os
import uuid
import unittest
from arcgis.gis import GIS
from utils.decorators import integration_test, from_to_profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()

@from_to_profiles.all
@integration_test
class TestCloneGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gmgr = cls.from_gis.groups
        cls.source_groups = [
            gmgr.create(title=f"group_{uuid.uuid4().hex[:4]}", tags="tags"),
            gmgr.create(title=f"group_{uuid.uuid4().hex[:4]}", tags="tags"),
            gmgr.create(title=f"group_{uuid.uuid4().hex[:4]}", tags="tags"),
        ]

    def test_clone_groups(self):
        if self.from_gis.url == self.to_gis.url and self.from_gis.users.me == self.to_gis.users.me:
            self.skipTest("Clone groups empty if same GIS as same user.")
        groups = self.to_gis.groups.clone(self.source_groups)
        assert len(groups) == len(self.source_groups)
        [g.result().delete() for g in groups]

    def test_clone_groups_offline(self):
        fp = self.to_gis.groups.clone(self.source_groups, offline=True)
        assert len(fp) > 0
        assert fp[0]
        group_file = fp[0].result()
        assert os.path.isfile(group_file)
        os.remove(group_file)

    def test_clone_groups_load_offline(self):
        fp = self.to_gis.groups.clone(self.source_groups, offline=True)
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
