import unittest
import uuid
import os
from arcgis.gis import User
from utils.decorators import integration_test, profiles
from config import get_resource_path


@integration_test
@profiles.admin_all
class TestUserManagerCreate(unittest.TestCase):
    """
    Test UserManager create() method
    """

    def setUp(self):
        self.username = f"test_create_user_{uuid.uuid4().hex[:4]}"
        self.password = "IL0veMyGI$_4Ever"
        self.firstname = "user"
        self.lastname = "geosaurus"
        self.role = "org_publisher"
        self.user_type = "creator"
        self.email = "amani@esri.com"

        self.created_user = None

    def tearDown(self):
        """
        Delete test user
        """
        if self.created_user:
            try:
                self.created_user.delete()
            except Exception as e:
                print(f"Failed to delete user {self.username}: {e}")

    def test_create_user_use_defaults(self):
        """
        Test create user with user defaults; use_defaults is True by default
        """
        if self.gis.version < [2025, 1]:
            self.skipTest(
                "use_defaults param is only available in ArcGIS Enterprise 11.5+."
            )
        if not self.gis.users.user_settings:
            self.skipTest(
                "New Member Defaults not set. user_type and role are required."
            )
        self.created_user = self.gis.users.create(
            self.username,
            self.password,
            self.firstname,
            self.lastname,
            self.email,
            use_defaults=True,
        )
        self.assertIsInstance(self.created_user, User)
        self.assertIn(
            self.gis.users.user_settings["role"],
            [self.created_user.role, self.created_user.roleId],
            "Role not set correctly.",
        )
        self.assertEqual(
            self.created_user.userLicenseTypeId,
            self.gis.users.user_settings["userLicenseType"],
            "User license type ID not set correctly for user_type argument.",
        )
        if self.gis.users.user_settings.get("groups"):
            for group_id in self.gis.users.user_settings["groups"]:
                self.assertIn(
                    group_id,
                    [g.id for g in self.created_user.groups],
                    "Group not found in user groups",
                )

    def test_create_user_with_thumbnail(self):
        """
        Test create user with thumbnail
        """
        thumbnail_path = get_resource_path("staging_data/users/Basemaps.png")
        self.created_user = self.gis.users.create(
            username=self.username,
            password=self.password,
            firstname=self.firstname,
            lastname=self.lastname,
            email=self.email,
            user_type=self.user_type,
            role=self.role,
            thumbnail=thumbnail_path,
        )
        self.assertIsInstance(self.created_user, User)
        self.assertIsNotNone(
            self.created_user.get_thumbnail(),
            "Thumbnail object was not found for the new user",
        )
        self.assertEqual(
            self.created_user.role,
            "org_publisher",
            "Role value does not match role argument.",
        )
        self.assertEqual(
            self.created_user.userLicenseTypeId,
            "creatorUT",
            "User license type ID does not match user_type.",
        )

    def test_create_user_user_defaults_false(self):
        """
        Test create user with defaults false
        """
        if self.gis.version < [2025, 1]:
            self.skipTest(
                "use_defaults param is only available in ArcGIS Enterprise 11.5+."
            )
        thumbnail_path = get_resource_path("staging_data/users/Basemaps.png")
        self.created_user = self.gis.users.create(
            self.username,
            self.password,
            self.firstname,
            self.lastname,
            self.email,
            role="org_user",
            user_type="GISProfessionalStdUT",
            use_defaults=False,
            thumbnail=thumbnail_path,
        )
        self.assertIsInstance(self.created_user, User)
        self.assertEqual(
            self.created_user.role,
            "org_user",
            "Role value does not match role argument",
        )
        self.assertEqual(self.created_user.userLicenseTypeId, "GISProfessionalStdUT")
        self.assertIsNotNone(
            self.created_user.get_thumbnail(),
            "Thumbnail object was not found for the new user",
        )


if __name__ == "__main__":
    unittest.main()
