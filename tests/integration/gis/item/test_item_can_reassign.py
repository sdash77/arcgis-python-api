import unittest
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import get_resource_path

enable_verbose_logging()


@profiles.admin_all
@integration_test
class TestCanReassignItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fp = get_resource_path("staging_data/USA_Major_Cities.zip", unique_copy=True)
        cls.folder = cls.gis.content.folders._get_or_create(
            "integration_test_gis_item_reassign"
        )
        cls.item = cls.folder.add(
            item_properties={
                "title": "reassign_item_test",
                "type": "Shapefile",
                "tags": "integration_testing,ntgrtn-tst",
            },
            file=fp,
        ).result()
        cls.pitem = cls.item.publish(
            {
                "name": "reassign_item_test_publish",
                "tags": "integration_testing,ntgrtn-tst",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.pitem.delete(permanent=True)
        cls.item.delete(permanent=True)
        cls.folder.delete(permanent=True)

    def test_can_reassign(self):
        """tests the new reassign operation"""
        items = [self.item, self.pitem]
        for item in items:
            for user in [
                u
                for u in self.gis.users.search("*")
                if not u.username.startswith("esri") and u.role == "org_admin"
            ][:3]:
                username_res = item.can_reassign(target_user=user.username)
                self.assertIsInstance(username_res, tuple, "Result must be a tuple.")
                self.assertEqual(
                    username_res[0],
                    True,
                    f"Reassignment of {item.type} item to {user.username} failed.",
                )
                self.assertTrue(
                    username_res[1].get("success"),
                    f"Reassignment of {item.type} item to {user.username} failed.",
                )
                self.assertIn(
                    "itemId",
                    list(username_res[1].keys()),
                    "itemId not a key in tuple response second index.",
                )
                self.assertEqual(
                    item.id, username_res[1]["itemId"], "Item id values do not match."
                )
                user_res = item.can_reassign(target_user=user)
                self.assertIsInstance(user_res, tuple, "Result must be a tuple.")
                self.assertEqual(
                    user_res[0], True, f"Reassignment to {user.username} failed."
                )
                self.assertTrue(
                    user_res[1].get("success"),
                    f"Reassignment to {user.username} failed.",
                )
                self.assertIn(
                    "itemId",
                    list(user_res[1].keys()),
                    "ietmId not a key in tuple response second index.",
                )
                self.assertEqual(
                    item.id, user_res[1]["itemId"], "Item id values do not match."
                )


if __name__ == "__main__":
    unittest.main()
