import sys

#  Update the Path to set the test area
sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import logging
import shutil
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis.admin import UX, HomePageSettings, MapSettings, ItemSettings
import tempfile
import requests

# Download Image to Temp File to be used for logo, background, etc.
image_url = "https://previews.123rf.com/images/stephane106/stephane1060705/stephane106070500053/927250-isolated-earth-globe-on-white-background-the-map-is-public-domain-from-nasa-visibleearth-nasa-gov-.jpg"
response = requests.get(image_url)
with open(tempfile.gettempdir() + "\\Image.jpg", "wb") as image_file:
    image_file.write(response.content)

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

    def test_informational_banner(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ux = gis.admin.ux

            # get current banner, or None
            ib = ux.get_informational_banner()
            try:
                assert ib
            except:
                continue
            # set informational banner
            assert ux.set_informational_banner(
                text="Test For Python API",
                bg_color="white",
                font_color="black",
                enabled=True,
            )
            assert ux.get_informational_banner()["text"] == "Test For Python API"
            # reset original banner
            if ib:
                assert ux.set_informational_banner(
                    text=ib["text"],
                    bg_color=ib["bgColor"],
                    font_color=ib["fontColor"],
                    enabled=ib["enabled"],
                )
            else:
                assert ux.set_informational_banner(text=None, enabled=False)

    def test_logo(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ux = gis.admin.ux

            # get orig logo, if none then None is returned
            logo = ux.get_logo(tempfile.gettempdir())
            try:
                assert logo
            except:
                continue
            # set logo
            assert ux.set_logo(image_file.name, show_logo=True)
            assert ux.get_logo(tempfile.gettempdir())
            # set orig logo
            assert ux.set_logo(logo)

    def test_shared_theme(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ux = gis.admin.ux

            # get orig shared theme, might be None
            shared_theme = ux.shared_theme()
            assert shared_theme
            # set new theme props
            new_theme = ux.shared_theme(
                button={"background": "#0d7bba", "text": "#000000"}
            )
            assert new_theme["button"] == {"background": "#0d7bba", "text": "#000000"}
            # reset original
            assert ux.shared_theme(button=shared_theme["button"])

    def test_navigation_bar(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ux = gis.admin.ux

            # get nav bar
            nav_bar = ux.navigation_bar()
            # set nav bar
            new_bar = ux.navigation_bar(gallery="members", groups="members")
            assert new_bar
            # reset original
            assert ux.navigation_bar(
                gallery=nav_bar["gallery"], groups=nav_bar["groups"]
            )

    def test_gallery_group(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ux = gis.admin.ux

            # get gallery group
            gall_grp = ux.gallery_group
            try:
                assert gall_grp
            except:
                assert gall_grp == ""
            # set new group
            group_id = gis.groups.search()[0].id
            ux.gallery_group = group_id
            assert ux.gallery_group == "id:" + group_id
            # reset
            if gall_grp:
                ux.gallery_group = gall_grp[3::]
            else:
                ux.gallery_group = gall_grp


class Test_HomePageSettingsClass(unittest.TestCase):
    """Tests Home Page Editor Class"""

    def test_class_calls(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            hps = gis.admin.ux.homepage_settings
            assert isinstance(hps, HomePageSettings)

    def test_background(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            hps = gis.admin.ux.homepage_settings

            # get background, if default then None will be returned
            bck = hps.get_background(tempfile.gettempdir())
            try:
                assert bck
            except:
                continue
            # set background to new image
            assert hps.set_background(image_file.name)
            # get background, this time there will be a file
            assert hps.get_background(tempfile.gettempdir())
            # reset original background
            assert hps.set_background(bck)

    def test_title(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            hps = gis.admin.ux.homepage_settings

            # get title
            orig_title = hps.get_title()
            try:
                assert orig_title["title"]
            except:
                continue
            # set title
            assert hps.set_title("Python API Test", show_title=True, color="#000000")
            assert hps.get_title()["title"] == "Python API Test"
            # reset original title
            if orig_title:
                assert hps.set_title(orig_title["title"])
            else:
                assert hps.set_title(orig_title)

    def test_contact_email(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            hps = gis.admin.ux.homepage_settings

            # get contact email, if none then None is returned
            cnt_email = hps.get_contact_email()
            try:
                assert cnt_email["email"]
            except:
                continue
            # set contact email
            assert hps.set_contact_email("test@esri.com", show_email=True)
            assert hps.get_contact_email()["email"] == "test@esri.com"
            # reset email
            if cnt_email:
                assert hps.set_contact_email(cnt_email["email"])
            else:
                assert hps.set_contact_email(cnt_email)


class Test_MapSettingsClass(unittest.TestCase):
    """Tests Org Map Settings Class"""

    def test_class_calls(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ms = gis.admin.ux.map_settings
            assert isinstance(ms, MapSettings)

    def test_propeties(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ms = gis.admin.ux.map_settings

            # default extent
            extent = ms.default_extent
            assert extent
            new_extent = {
                "xmin": -13458971.714869041,
                "ymin": 3612376.446092521,
                "xmax": -12305256.512287628,
                "ymax": 4354833.185272345,
                "spatialReference": {"wkid": 102100},
            }
            ms.default_extent = new_extent
            assert ms.default_extent == {
                "xmin": -13458971.714869041,
                "ymin": 3612376.446092521,
                "xmax": -12305256.512287628,
                "ymax": 4354833.185272345,
                "spatialReference": {"wkid": 102100},
            }
            ms.default_extent = extent

            # default basemap
            df_bsmap = ms.default_basemap
            assert df_bsmap

            # vector basemap
            set_vb = ms.use_vector_basemap
            assert set_vb in [True, False]
            vbmap = ms.vector_basemap
            assert vbmap

            # basemap gallery group
            bsmap_gall_group = ms.basemap_gallery_group
            assert bsmap_gall_group
            group_id = gis.groups.search()[0].id
            ms.basemap_gallery_group = group_id
            assert ms.basemap_gallery_group == "id:" + group_id
            if bsmap_gall_group:
                ms.basemap_gallery_group = bsmap_gall_group[3::]
            else:
                ms.basemap_gallery_group = bsmap_gall_group

            # map viewer
            mv = ms.default_mapviewer
            assert mv

            # units
            units = ms.units
            assert units

            # config apps group
            config_apps_group = ms.config_apps_group
            assert config_apps_group
            group_id = gis.groups.search()[0].id
            ms.config_apps_group = group_id
            assert ms.config_apps_group == "id:" + group_id
            if config_apps_group:
                ms.config_apps_group = gis.groups.search(config_apps_group[3::])[0]
            else:
                ms.config_apps_group = config_apps_group

            # analysis group layer
            analysis_layer_group = ms.analysis_layer_group
            try:
                assert analysis_layer_group
            except:
                assert analysis_layer_group == ""
            group_id = gis.groups.search()[0].id
            ms.analysis_layer_group = group_id
            assert ms.analysis_layer_group == "id:" + group_id
            if len(analysis_layer_group) > 0:
                ms.analysis_layer_group = gis.groups.search(analysis_layer_group[3::])[
                    0
                ]
            else:
                ms.analysis_layer_group = analysis_layer_group

    def test_bing_map(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            ms = gis.admin.ux.map_settings

            key = ms.bing_map()
            assert key
            assert ms.bing_map(bing_key="abcde")
            assert ms.bing_map()["key"] == "abcde"
            ms.bing_map(bing_key=key["key"], share_public=key["public"])


class Test_ItemSettingsClass(unittest.TestCase):
    """Tests Org Item Settings Class"""

    def test_class_calls(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            it_set = gis.admin.ux.item_settings
            assert isinstance(it_set, ItemSettings)

    def test_propeties(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            it_set = gis.admin.ux.item_settings
            # enable comments property
            comments = it_set.enable_comments
            assert comments in [True, False]
            it_set.enable_comments = True
            assert it_set.enable_comments is True
            it_set.enable_comments = comments


if __name__ == "__main__":
    unittest.main()
