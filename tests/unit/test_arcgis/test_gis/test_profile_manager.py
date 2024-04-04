import uuid
import unittest
from arcgis.gis._impl._profile import ProfileManager
from arcgis.gis import login_profiles
import pandas as pd


def get_fake_profile_name():
    return f"FAKE{uuid.uuid4().hex[:5]}"


class TestProfileManager(unittest.TestCase):
    """tests the profile manager"""

    def test_login_profiles(self):
        assert isinstance(login_profiles, ProfileManager)

    def test_list(self):
        """tests list method"""
        pm = ProfileManager()
        assert isinstance(pm.list(), list)

    def test_list_dataframe(self):
        """tests list method with as_df=True"""
        pm = ProfileManager()
        assert isinstance(pm.list(as_df=True), pd.DataFrame)

    def test_create_built_in(self):
        """tests creating/deleting a profile with built-in auth"""
        profile_name = get_fake_profile_name()
        pm = ProfileManager()
        created = pm.create(
            profile=profile_name,
            url=f"https://{profile_name}.maps.arcgis.com",
            username="fakeuser",
            password=f"{profile_name}_fakepassword",
        )
        assert created
        assert profile_name in pm.list()
        profile = pm.get(profile_name)
        assert profile
        self.assertIsInstance(profile, dict)
        assert profile.get("url") == f"https://{profile_name}.maps.arcgis.com"
        assert profile.get("username") == "fakeuser"
        assert not profile.get("key_file")
        assert not profile.get("cert_file")
        assert not profile.get("client_id")
        assert pm._securely_get_password(profile_name) == f"{profile_name}_fakepassword"
        assert pm.delete(profile_name)
        assert profile_name not in pm.list()
        assert not pm._securely_get_password(profile_name)

    def test_create_key_file(self):
        """tests creating/deleting a profile with key file"""
        profile_name = get_fake_profile_name()
        pm = ProfileManager()
        created = pm.create(
            profile=profile_name,
            url=f"https://{profile_name}.maps.arcgis.com",
            key_file="fakekey.pem",
        )
        assert created
        assert profile_name in pm.list()
        profile = pm.get(profile_name)
        assert profile
        self.assertIsInstance(profile, dict)
        assert profile.get("url") == f"https://{profile_name}.maps.arcgis.com"
        assert not profile.get("username")
        assert profile.get("key_file") == "fakekey.pem"
        assert not profile.get("cert_file")
        assert not profile.get("client_id")
        assert pm.delete(profile_name)
        assert profile_name not in pm.list()
        assert not pm._securely_get_password(profile_name)

    def test_create_cert_file(self):
        """tests creating/deleting a profile with cert file"""
        profile_name = get_fake_profile_name()
        pm = ProfileManager()
        created = pm.create(
            profile=profile_name,
            url=f"https://{profile_name}.maps.arcgis.com",
            cert_file="fakecert.pem",
            password=f"{profile_name}_fakepassword",
        )
        assert created
        assert profile_name in pm.list()
        profile = pm.get(profile_name)
        assert profile
        self.assertIsInstance(profile, dict)
        assert profile.get("url") == f"https://{profile_name}.maps.arcgis.com"
        assert not profile.get("username")
        assert not profile.get("key_file")
        assert profile.get("cert_file") == "fakecert.pem"
        assert not profile.get("client_id")
        retrieved_password = pm._securely_get_password(profile_name)
        assert retrieved_password == f"{profile_name}_fakepassword"
        assert pm.delete(profile_name)
        assert profile_name not in pm.list()

    def test_create_oauth_profile(self):
        """tests creating/deleting a profile with oauth"""
        profile_name = get_fake_profile_name()
        pm = ProfileManager()
        created = pm.create(
            profile=profile_name,
            url=f"https://{profile_name}.maps.arcgis.com",
            client_id="fakeclientid",
        )
        assert created
        assert profile_name in pm.list()
        profile = pm.get(profile_name)
        assert profile
        self.assertIsInstance(profile, dict)
        assert profile.get("url") == f"https://{profile_name}.maps.arcgis.com"
        assert not profile.get("username")
        assert not profile.get("key_file")
        assert not profile.get("cert_file")
        assert profile.get("client_id") == "fakeclientid"
        assert not pm._securely_get_password(profile_name)
        assert pm.delete(profile_name)
        assert profile_name not in pm.list()

    def test_update(self):
        """tests update"""
        profile_name = get_fake_profile_name()
        pm = ProfileManager()
        created = pm.create(
            profile=profile_name,
            url=f"https://{profile_name}.maps.arcgis.com",
            username="fakeuser",
            password=f"{profile_name}_fakepassword",
        )
        assert created
        assert profile_name in pm.list()
        updated = pm.update(profile=profile_name, url="https://faked.maps.arcgis.com")
        assert updated
        profile = pm.get(profile_name)
        assert profile
        self.assertIsInstance(profile, dict)
        assert profile.get("url") == "https://faked.maps.arcgis.com"
        assert pm.delete(profile_name)

    def test_delete(self):
        """tests delete"""
        profile_name = get_fake_profile_name()
        pm = ProfileManager()
        created = pm.create(
            profile=profile_name,
            url=f"https://{profile_name}.maps.arcgis.com",
            username="fakeuser",
            password=f"{profile_name}_fakepassword",
        )
        assert created
        assert profile_name in pm.list()
        assert pm.delete(profile_name)
        assert profile_name not in pm.list()
        assert not pm._securely_get_password(profile_name)


if __name__ == "__main__":
    unittest.main()
