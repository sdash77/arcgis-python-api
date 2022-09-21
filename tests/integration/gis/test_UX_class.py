import sys

#  Update the Path to set the test area
sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis.admin import UX, HomePageSettings, MapSettings


#### MUST TEST WITH ADMIN PRIVILEGES ####

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


PROFILES = ["your_online_profile", "your_enterprise_profile"]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class Test_UXClass(unittest.TestCase):
    """Tests UX Class"""

    def test_class_calls(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ux = gis.admin.ux
            assert isinstance(ux, UX)

    def test_properties(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ux = gis.admin.ux

            # name property
            name = ux.name
            assert name
            ux.name = "Python API Test"
            assert ux.name == "Python API Test"
            ux.name = name

            # summary property
            summary = ux.summary
            try:
                assert summary
            except:
                continue
            ux.summary = "Python API Test"
            assert ux.summary == "Python API Test"
            ux.summary = summary

            # contact link property
            contact_link = ux.contact_link
            try:
                assert contact_link
            except:
                continue
            ux.contact_link = "www.test_it.com"
            assert ux.contact_link == "www.test_it.com"
            ux.contact_link = contact_link

            # admin contacts property
            contact = ux.admin_contacts
            assert contact
            ux.admin_contacts = [gis.users.me.username]
            assert ux.admin_contacts == [gis.users.me.username]
            ux.admin_contacts = contact

            # enable comments property
            comments = ux.enable_comments
            assert comments
            ux.enable_comments = True
            assert ux.enable_comments is True
            ux.enable_comments = comments

            # description visibility property
            visibility = ux.description_visibility
            assert visibility
            ux.description_visibility = False
            assert ux.description_visibility is False
            ux.description_visibility = visibility

            # description property
            desc = ux.description
            assert desc
            ux.description = "Python API Test"
            assert ux.description == "Python API Test"
            ux.description = desc


class Test_HomePageSettingsClass(unittest.TestCase):
    """Tests Home Page Editor Class"""


class Test_MapSettingsClass(unittest.TestCase):
    """Tests Org Map Settings Class"""


if __name__ == "__main__":
    unittest.main()
