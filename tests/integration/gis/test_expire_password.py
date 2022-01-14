import sys

sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_7210\src")
import unittest
from arcgis.gis import GIS, User, UserManager

PROFILES = ['your_enterprise_profile', 'your_online_profile']


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
                firstname='testaccount',
                lastname='testaccount',
                email='test@esri.com',
            )
            assert isinstance(user, User)
            assert user.expire_password("!AmazingPassword1")
            assert user.delete()


if __name__ == "__main__":
    unittest.main()
