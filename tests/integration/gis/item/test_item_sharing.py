# -----------------------------------------------------------------------------
# Name:        Test for sharing of a public item to a new group.
# Purpose:     Integration tests for sharing items using ArcGIS Python API.
# -----------------------------------------------------------------------------

import unittest
import time

from utils.decorators import integration_test, profiles
from utils.data_utils import create_group, cleanup_groups


@profiles.admin_all
@integration_test
class Test_Item_share_public_item(unittest.TestCase):
    """Testig the sharing of a public item using a new group."""

    @classmethod
    def setUpClass(cls):
        cls.new_grp = create_group(
            gis=cls.gis,
            group_name="aa_group_for_sharing_test",
        )

    @classmethod
    def tearDownClass(cls):
        cleanup_groups(groups=[cls.new_grp])

    def setUp(self):
        print(f"\n{'-' * 40}\nTest: starting {self._testMethodName}...")
        print(f"{' ' * 2}ID: {self.id()}")
        self._start_time = time.time()

    def tearDown(self):
        elapsed_time = time.time() - self._start_time
        print(f"{' ' * 4}...test took {elapsed_time / 60:.2f} minutes.\n")

    def test_nonorg_public_Item_share_unshare_orggroup(self):
        """
        In AGOL, users can search for public items outside the org and share
        them to their group. This is a popular way to accumulate content in
        their GIS.
        """
        public_data_item = self.gis.content.search(
            "title: Hurricane * AND access:public", outside_org=True
        )[0]
        self.assertIsNotNone(
            public_data_item, "Cannot create an Item Obj using a non org public item id"
        )
        self.assertEqual(
            len(public_data_item.sharing.groups.list()),
            0,
            "Public item should not be shared to any group by default.",
        )

        self.assertEqual(
            len(self.new_grp.content()),
            0,
            "New group should not have any content by default.",
        )

        public_data_item.sharing.groups.add(self.new_grp)

        import time

        time.sleep(50)

        self.assertIsNotNone(
            self.new_grp.content(),
            "New group should have content after adding public item to it.",
        )
        new_grp_content = self.new_grp.content()

        time.sleep(50)

        interested_item = [i for i in new_grp_content if i.id == public_data_item.id]
        self.assertEqual(
            len(interested_item), 1, "Shared item not found in group's contents"
        )
        self.assertTrue(
            public_data_item.sharing.groups.remove(self.new_grp),
            "Unable to unshare public item with group",
        )


if __name__ == "__main__":
    unittest.main()
