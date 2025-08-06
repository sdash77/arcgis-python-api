import uuid
import unittest
import tempfile
from pathlib import Path

from arcgis.gis import GIS, Group
from arcgis.gis.clone import CloningJob
from utils.decorators import integration_test, from_to_profiles
from utils._logging import enable_verbose_logging
from utils.data_utils import cleanup_groups, create_group

enable_verbose_logging()

@from_to_profiles.all
@integration_test
class TestCloneGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grp_names = [
            f"group_clone_test_{uuid.uuid4().hex[:4]}" for i in range(0, 3)
        ]
        
        cls.source_groups = [
            create_group(gis=cls.from_gis, group_name=gn) for gn in cls.grp_names
        ]
              
    def setUp(self):
        """
        Create an empty list to store groups created in to_gis from cloning.
        and delete them afterwards to avoid groups already exist errors.
        """
        self.target_groups = []
        
    def tearDown(self):
        """
        Delete the groups created in the to_gis deployment after each test.
        """
        cleanup_groups(self.target_groups)

    def test_clone_groups(self):
        if self.from_gis.url == self.to_gis.url and self.from_gis.users.me == self.to_gis.users.me:
            self.skipTest("Clone groups empty when run in same GIS as same user.")
        cloned_groups = self.to_gis.groups.clone(self.source_groups)
        self.assertIsInstance(
            cloned_groups[0],
            CloningJob,
            "GroupManager clone did not return list of CloninJobs."
        )
        self.assertIsInstance(
            cloned_groups[0].result(),
            Group,
            "Clone job did not return a Group object."
        )
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
        
        # Add new groups to list so can be cleaned up properly.
        self.target_groups.extend(cjob.result() for cjob in cloned_groups)

    def test_clone_groups_offline_file_config_defaults(self):
        if self.from_gis.url == self.to_gis.url and self.from_gis.users.me == self.to_gis.users.me:
            self.skipTest("Cloning groups in same GIS as same user is not valid.")         
        fp = self.from_gis.groups.clone(
            groups=self.source_groups,
            offline=True
        )
        self.assertGreater(len(fp), 0, "Group clone did not create a list of jobs.")
        self.assertTrue(fp[0], "No CloningJob objects created from clone method.")
        group_file = fp[0].result()
        self.assertTrue(
            Path(group_file).is_file(),
            "Offline argument did not create a file for loading."
        )
        self.assertEqual(
            Path(group_file).suffix,
            ".GROUP_CLONER",
            "Default file extension not created with expected suffix."
        )
        Path(group_file).unlink()
        
    def test_clone_groups_load_offline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fp = self.from_gis.groups.clone(
                groups=self.source_groups,
                offline=True, 
                save_folder=tmpdir,
                file_name="ntgrtn_test_offline_cloner"
            )[0]
            self.assertTrue(fp, "GroupManager clone did not return a list with one CloningJob.")
            group_file = fp.result()
            self.assertTrue(
                Path(group_file).exists(),
                "File path for offline configuration does not exist."
            )            
            self.assertTrue(
                Path(group_file).is_file(),
                "Offline argument did not create a file for loading."
            )
            self.assertEqual(
                Path(group_file).stem,
                "ntgrtn_test_offline_cloner",
                "File name not created with correct name."
            )
            self.assertEqual(
                Path(group_file).suffix,
                ".GROUP_CLONER",
                "Group configuration file not created with correct default extension."
            )
            
            # Use a separate GIS profile to load config when from_to profiles are same GIS
            # to avoid already exist errors
            if self.from_gis.url == self.to_gis.url and self.from_gis.users.me == self.to_gis.users.me:
                dev_gis = GIS(profile="your_dev_online_admin_profile")
                gmgr = dev_gis.groups
            else:
                gmgr = self.to_gis.groups
                
            off_groups = gmgr.load_offline_configuration(group_file)
            self.assertEqual(
                len(off_groups),
                3,
                "Loading of group config file did not create 3 jobs."
            )
            self.assertIsInstance(
                off_groups[0].result(),
                Group,
                "Result of cloning job is not a group as expected."
            )
            
            # Add new groups to list so can be cleaned up properly.
            self.target_groups.extend(offg.result() for offg in off_groups)

    @classmethod
    def tearDownClass(cls):
        cleanup_groups(groups=cls.source_groups)


if __name__ == "__main__":
    unittest.main()
