import sys

sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
from arcgis.gis import GIS
import unittest

PROFILES = ["your_online_profile"]
ALLOWED_LANDING_PAGES = [
    "home",
    "gallery",
    "map",
    "scene",
    "groups",
    "content",
    "organization",
]
landing_pages_lu = {
    "home": "index.html",
    "gallery": "gallery.html",
    "map": "webmap/viewer.html",
    "scene": "webscene/viewer.html",
    "groups": "groups.html",
    "content": "content.html",
    "organization": "organization.html",
}


class TestUserSettings(unittest.TestCase):
    def test_landing_page_get(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            user = gis.users.me
            assert user.landing_page in ALLOWED_LANDING_PAGES

    def test_landing_page_post(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            user = gis.users.me
            for lp in ALLOWED_LANDING_PAGES:
                user.landing_page = lp
                assert user.landing_page in ALLOWED_LANDING_PAGES

    def test_user_settings_get(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            user = gis.users.me
            assert user.user_settings

    def test_user_settings_post(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            user = gis.users.me
            user.landing_page = "organization"
            us = user.user_settings
            us["landingPage"]["url"] = "index.html"
            user.user_settings = us
            assert user.landing_page == "home"


if __name__ == "__main__":
    unittest.main()
