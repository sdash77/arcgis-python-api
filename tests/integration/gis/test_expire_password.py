import unittest
from arcgis.gis import GIS, User, UserManager
from integration.dino_utils.manage_test_profiles import create_test_profiles
from utils.decorators import integration_test

PROFILES = ["your_ent_admin_profile", "your_online_admin_profile"]


@integration_test
class TestUserExpirePassword(unittest.TestCase):
    """
    Tests the expire password logic
    """

    def test_expire_password(self):
        """tests the expire password logic"""
        for profile in PROFILES:

            gis = GIS(profile=profile, verify_cert=False)

            um = gis.users
            for u in um.search("testexpirepass"):
                u.delete()
            isinstance(um, UserManager)
            user = um.create(
                username="testexpirepass",
                password="!Am4zingp0iNt",
                firstname="testaccount",
                lastname="testaccount",
                email="test@esri.com",
                role="org_user"
            )
            assert isinstance(user, User)
            assert user.expire_password("!AmazingPassword1")
            assert user.delete()


if __name__ == "__main__":
    unittest.main()
