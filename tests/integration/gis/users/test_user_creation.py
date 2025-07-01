import unittest
import uuid
import os
from arcgis.gis import User
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path


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
            self.skipTest("use_defaults param is only available in ArcGIS Enterprise 11.5+.")
        self.created_user = self.gis.users.create(
            self.username,
            self.password,
            self.firstname,
            self.lastname,
            self.email,
            use_defaults=True,
        )
        self.assertIsInstance(self.created_user, User)

    def test_create_user_with_thumbnail(self):
        """
        Test create user with thumbnail
        """
        thumbnail_path = get_resource_path("staging_data/users/Basemaps.png")
        self.created_user = self.gis.users.create(
            self.username,
            self.password,
            self.firstname,
            self.lastname,
            self.email,
            self.role,
            self.user_type,
            thumbnail=thumbnail_path,
        )
        self.assertIsInstance(self.created_user, User)
        self.assertIsNotNone(self.created_user.get_thumbnail(), "Thumbnail object was not found for the new user")

    def test_create_user_user_defaults_false(self):
        """
        Test create user with defaults false
        """
        if self.gis.version < [2025, 1]:
            self.skipTest("use_defaults param is only available in ArcGIS Enterprise 11.5+.")
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
        )
        self.assertIsInstance(self.created_user, User)
        self.assertEqual(self.created_user.role, "org_user", "Thumbnail object was not found for the new user")


if __name__ == "__main__":
    unittest.main()
