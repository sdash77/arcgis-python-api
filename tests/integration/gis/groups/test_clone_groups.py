import os
import uuid
import unittest

from arcgis.gis import GIS, Group, GroupManager
from arcgis.gis.clone import CloningJob
from utils.decorators import integration_test, from_to_profiles
from utils._logging import enable_verbose_logging
from utils.data_utils import cleanup_groups, create_group

#enable_verbose_logging()

import warnings
warnings.filterwarnings("ignore")

@from_to_profiles.all_except_k8s
#@from_to_profiles.all
@integration_test
class TestCloneGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grp_names = [f"group_clone_test_{uuid.uuid4().hex[:4]}" for i in range(0, 3)]
        
        cls.source_groups = [create_group(gis=cls.from_gis, group_name=gn) for gn in cls.grp_names]
        cls.target_groups = []
        
    def setUp(self):
        print(f"... running {self._testMethodName}\n{'-' * 40}")
        print(f"{' ' * 5} from_gis: {self.from_gis}")
        print(f"{' ' * 7}   to_gis: {self.to_gis}\n")

    def test_clone_groups(self):
        if self.from_gis.url == self.to_gis.url and self.from_gis.users.me == self.to_gis.users.me:
            self.skipTest("Clone groups empty when run in same GIS as same user.")
        cloned_groups = self.to_gis.groups.clone(self.source_groups)
        self.assertIsInstance(cloned_groups[0], CloningJob, "GroupManager clone did not return list of CloninJobs.")
        self.assertIsInstance(cloned_groups[0].result(), Group, "Clone job did not return a Group object.")
        self.assertEqual(
            cloned_groups[0].result().owner,
            self.to_gis.users.me.username,
            "Group owner is not the connected target GIS user."
        )
        self.assertEqual(
            len(cloned_groups),
            len(self.source_groups),
            "Number of cloned groups does not match number of groups in source gis list."
        )
        self.assertTrue(
            cloned_groups[0].result().title.startswith("group_clone_test_"),
            "Cloned group title value does not match source group title."
        )
        self.target_groups.extend(cjob.result() for cjob in cloned_groups)
        cleanup_groups(groups=self.target_groups)

    def test_clone_groups_offline(self):
        if self.from_gis.url == self.to_gis.url and self.from_gis.users.me == self.to_gis.users.me:
            self.skipTest("Clone groups empty when run in same GIS as same user.")        
        fp = self.to_gis.groups.clone(
            groups=self.source_groups,
            offline=True
        )
        assert len(fp) > 0
        assert fp[0]
        group_file = fp[0].result()
        assert os.path.isfile(group_file)
        os.remove(group_file)

    def test_clone_groups_load_offline(self):
        if self.from_gis.url == self.to_gis.url and self.from_gis.users.me == self.to_gis.users.me:
            self.skipTest("Clone groups empty when run in same GIS as same user.")        
        fp = self.from_gis.groups.clone(
            groups=self.source_groups,
            offline=True, 
            save_folder=r"/Users/john3092/Documents/group_cloning",
            file_name="ntgrtn_test_offline_clone"
        )[0]
        self.assertTrue(fp, "GroupManager clone did not return a list with one CloningJob.")
        group_file = fp.result()
        gmgr = self.to_gis.groups
        off_groups = gmgr.load_offline_configuration(group_file)
        os.remove(group_file)
        assert len(off_groups) == 3
        cleanup_groups(groups=[offg.result() for offg in off_groups])

    @classmethod
    def tearDownClass(cls):
        cleanup_groups(groups=cls.source_groups)


if __name__ == "__main__":
    unittest.main()
