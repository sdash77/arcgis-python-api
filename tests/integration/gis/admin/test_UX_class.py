import unittest
from arcgis.gis import GIS, Group
from arcgis.gis.admin import (
    UX,
    HomePageSettings,
    MapSettings,
    ItemSettings,
    SecuritySettings,
    StockImage,
    UtilityServicesSettings,
)
import tempfile
import requests
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from random import randrange

# Download Image to Temp File to be used for logo, background, etc.
image_url = "https://previews.123rf.com/images/stephane106/stephane1060705/stephane106070500053/927250-isolated-earth-globe-on-white-background-the-map-is-public-domain-from-nasa-visibleearth-nasa-gov-.jpg"
response = requests.get(image_url)
with open(tempfile.gettempdir() + "\\Image.jpg", "wb") as image_file:
    image_file.write(response.content)


enable_verbose_logging()


@profiles.admin_enterprise_and_agol
@integration_test
class TestUxClass(unittest.TestCase):
    """Tests UX Class"""

    def test_class_calls(self):
        gis = self.gis
        ux = gis.admin.ux
        assert isinstance(ux, UX)

    def test_enable_ai_assistance(self):
        if self.gis._is_arcgisonline:
            original_value =  self.gis.admin.ux.ai_assistants_enabled
            assert self.gis.admin.ux.ai_assistants_enabled in [True, False]
            self.gis.admin.ux.ai_assistants_enabled = True
            assert gis.admin.ux.ai_assistants_enabled == True
            self.gis.admin.ux.ai_assistants_enabled = False
            assert self.gis.admin.ux.ai_assistants_enabled == False
            self.gis.admin.ux.ai_assistants_enabled = original_value

    def test_properties(self):
        gis = self.gis
        ux = gis.admin.ux

        # name property
        name = ux.name
        assert name
        ux.name = "Python API Test"
        assert ux.name == "Python API Test"
        ux.name = name

        # summary property
        summary = ux.summary
        if summary:
            assert summary
        else:
            self.skipTest("gis.admin.ux.summary not available, cannot test")
        ux.summary = "Python API Test"
        assert ux.summary == "Python API Test"
        ux.summary = summary

        # contact link property
        contact_link = ux.contact_link
        if contact_link:
            assert contact_link
        else:
            assert contact_link is None
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

        # featured content
        # get the groups
        featured_groups = ux.featured_content
        orig_len = len(featured_groups)
        # add a group
        featured_groups.append(gis.groups.search()[1])
        ux.featured_content = featured_groups
        assert len(ux.featured_content) == orig_len + 1
        # remove the group we added
        del featured_groups[-1]
        ux.featured_content = featured_groups
        assert len(ux.featured_content) == orig_len

    def test_logo(self):
        gis = self.gis
        ux = gis.admin.ux

        # get orig logo, if none then None is returned
        logo = ux.get_logo(tempfile.gettempdir())
        if logo:
            assert logo
        else:
            self.skipTest("No logo configured, cannot test")
        # set logo
        assert ux.set_logo(image_file.name, show_logo=True)
        assert ux.get_logo(tempfile.gettempdir())
        # set orig logo
        assert ux.set_logo(logo)

    def test_shared_theme(self):
        ux = self.gis.admin.ux

        # get orig shared theme, might be None
        shared_theme = ux.shared_theme()
        assert shared_theme
        # set new theme props
        new_theme = ux.shared_theme(
            button={"background": "#0d7bba", "text": "#000000"}
        )
        assert new_theme["button"] == {
            "background": "#0d7bba",
            "text": "#000000",
        }
        # reset original
        assert ux.shared_theme(button=shared_theme["button"])

    def test_navigation_bar(self):
        ux = self.gis.admin.ux

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
        ux = self.gis.admin.ux

        # store original setting
        original_gallery_group = ux.gallery_group
        # set new group
        groups = self.gis.groups.search()
        if not groups:
            self.skipTest("No groups configured, cannot test")
        # get a random group
        group = groups[randrange(len(groups))]
        # set group by id
        ux.gallery_group = group.id
        # gallery_group should return the group object
        assert isinstance(ux.gallery_group, Group)
        # verify gallery_group now has the same id that was set
        assert ux.gallery_group.id == group.id
        # reset to original setting
        ux.gallery_group = original_gallery_group.id if original_gallery_group else original_gallery_group


@profiles.admin_enterprise_and_agol
@integration_test
class TestHomePageSettingsClass(unittest.TestCase):
    """Tests Home Page Editor Class"""

    def test_class_calls(self):
        hps = self.gis.admin.ux.homepage_settings
        assert isinstance(hps, HomePageSettings)

    def test_background(self):
        hps = self.gis.admin.ux.homepage_settings

        # get background, if default then None will be returned
        bck = hps.get_background(tempfile.gettempdir())

        if bck:
            assert bck
        else:
            assert bck == None
        # set background to new image
        assert hps.set_background(image_file.name)
        # get background, this time there will be a file
        assert hps.get_background(tempfile.gettempdir())

        # determine if stock image before reset
        names = [member.name for member in StockImage]
        if bck in names:
            bck = StockImage[bck]
        # reset original background
        assert hps.set_background(bck)

    def test_title(self):
        hps = self.gis.admin.ux.homepage_settings

        # get title
        orig_title = hps.get_title()
        if orig_title:
            assert orig_title["title"]
        else:
            self.skipTest("No title configured, cannot test")
        # set title
        assert hps.set_title(
            "Python API Test", show_title=True, color="#000000"
        )
        assert hps.get_title()["title"] == "Python API Test"
        # reset original title
        if orig_title:
            assert hps.set_title(orig_title["title"])
        else:
            assert hps.set_title(orig_title)

    def test_contact_email(self):
        hps = self.gis.admin.ux.homepage_settings

        # get contact email, if using legacy homepage then None is returned
        contact_email = hps.get_contact_email()
        if contact_email is None:
            self.skipTest("Portal is configured with legacy homepage, contact email not implemented")
        assert 'email' in contact_email
        assert 'show_email' in contact_email

        # set contact email
        assert hps.set_contact_email("test@esri.com", show_email=True)
        assert hps.get_contact_email()["email"] == "test@esri.com"
        assert hps.get_contact_email()["show_email"] == True

        # reset email to original value
        reset_contact_email = hps.set_contact_email(email=contact_email["email"], show_email=contact_email["show_email"])
        assert reset_contact_email
        reset_contact_email = hps.get_contact_email()
        assert reset_contact_email["email"] == contact_email["email"]
        assert reset_contact_email["show_email"] == contact_email["show_email"]


@profiles.admin_enterprise_and_agol
@integration_test
class TestMapSettingsClass(unittest.TestCase):
    """Tests Org Map Settings Class"""

    def test_class_calls(self):
        ms = self.gis.admin.ux.map_settings
        assert isinstance(ms, MapSettings)

    def test_default_extent(self):
        """test the default_extent property of MapSettings class"""
        ms = self.gis.admin.ux.map_settings
        extent = ms.default_extent
        assert extent['spatialReference']["wkid"] == 102100

        new_extent = {
            "xmin": -13458971.714869041,
            "ymin": 3612376.446092521,
            "xmax": -12305256.512287628,
            "ymax": 4354833.185272345,
            "spatialReference": {"wkid": 3857},
        }
        ms.default_extent = new_extent
        assert ms.default_extent["spatialReference"]["wkid"] == 3857
        ms.default_extent = extent

    def test_default_basemap(self):
        """test the default_basemap property of MapSettings class"""
        ms = self.gis.admin.ux.map_settings
        basemap = ms.default_basemap
        assert basemap

    def test_vector_basemap(self):
        """test the vector basemap properties of MapSettings class"""
        ms = self.gis.admin.ux.map_settings
        use_vector_basemap = ms.use_vector_basemap
        assert use_vector_basemap in [True, False]

        vector_basemap = ms.vector_basemap
        assert vector_basemap["title"] == "Topographic"

    def test_basemap_gallery(self):
        """
        test the basemap_gallery_group property of MapSettings class

        note:
        basemap_gallery_group will return a string "title:"ArcGIS Online Vector Basemaps" AND owner:esri_en" when group
        was set as default;
        basemap_gallery_group will return a Group object when group was set as a specific group in org.
        """
        ms = self.gis.admin.ux.map_settings
        bsmap_gall_group = ms.basemap_gallery_group
        assert isinstance(bsmap_gall_group, (Group, str))

        # test set basemap gallery group
        groups = self.gis.groups.search()
        if not groups:
            self.skipTest("No groups configured, cannot test")
        group = groups[randrange(len(groups))]

        ms.basemap_gallery_group = group.id
        assert isinstance(ms.basemap_gallery_group, Group)
        assert ms.basemap_gallery_group.id == group.id

        # set back basemap gallery group
        ms.basemap_gallery_group = None if isinstance(bsmap_gall_group, str) else bsmap_gall_group

    def test_map_viewer(self):
        """test the map viewer property of MapSettings class"""
        ms = self.gis.admin.ux.map_settings
        mv = ms.default_mapviewer
        assert mv in ['modern', 'classic']

    def test_units(self):
        """test the units property of MapSettings class"""
        ms = self.gis.admin.ux.map_settings
        units = ms.units
        assert units in ['english', 'metric']

    def test_config_apps_group(self):
        """test the config apps group property of MapSettings class"""
        groups = self.gis.groups.search()
        if not groups:
            self.skipTest("No groups configured, cannot test")
        group = groups[randrange(len(groups))]

        # get config apps group
        ms = self.gis.admin.ux.map_settings
        config_apps_group = ms.config_apps_group
        assert isinstance(config_apps_group, (Group, str))

        # set config apps group
        ms.config_apps_group = group.id
        assert isinstance(ms.config_apps_group, Group)
        assert ms.config_apps_group.id == group.id
        ms.config_apps_group = None if isinstance(config_apps_group, str) else config_apps_group

    def test_analysis_group_layer(self):
        """test the analysis group layer property of MapSettings class"""
        groups = self.gis.groups.search()
        if not groups:
            self.skipTest("No groups configured, cannot test")
        group = groups[randrange(len(groups))]

        ms = self.gis.admin.ux.map_settings
        analysis_layer_group = ms.analysis_layer_group
        assert isinstance(analysis_layer_group, (Group, str))

        ms.analysis_layer_group = group.id
        assert isinstance(ms.analysis_layer_group, Group)
        assert ms.analysis_layer_group.id == group.id
        if len(analysis_layer_group) > 0:
            ms.analysis_layer_group = self.gis.groups.search(
                analysis_layer_group.id
            )[0]
        else:
            ms.analysis_layer_group = analysis_layer_group

    def test_bing_map(self):
        ms = self.gis.admin.ux.map_settings

        bing_config = ms.bing_map()
        assert bing_config
        assert 'key' in bing_config
        assert 'public' in bing_config
        assert ms.bing_map(bing_key="abcde")
        assert ms.bing_map()["key"] == "abcde"
        # revert to original config
        ms.bing_map(bing_key=bing_config["key"], share_public=bing_config["public"])


@profiles.admin_enterprise_and_agol
@integration_test
class TestItemSettingsClass(unittest.TestCase):
    """Tests Org Item Settings Class"""

    def test_class_calls(self):
        it_set = self.gis.admin.ux.item_settings
        assert isinstance(it_set, ItemSettings)

    def test_propeties(self):
        it_set = self.gis.admin.ux.item_settings
        # enable comments property
        comments = it_set.enable_comments
        assert comments in [True, False]
        it_set.enable_comments = True
        assert it_set.enable_comments is True
        it_set.enable_comments = comments

        # enable metadata edit
        edit = it_set.enable_metadata_edit
        assert edit in [True, False]
        it_set.enable_metadata_edit = False
        assert it_set.enable_metadata_edit is False
        it_set.enable_metadata_edit = edit

        # metadata format
        frmt = it_set.metadata_format
        assert frmt
        it_set.metadata_format = "inspire"
        assert it_set.metadata_format == "inspire"
        it_set.metadata_format = frmt


@profiles.admin_enterprise_and_agol
@integration_test
class TestSecuritySettingsClass(unittest.TestCase):
    """Tests Org Security Settings Class"""

    def test_class_calls(self):
        ss = self.gis.admin.ux.security_settings
        assert isinstance(ss, SecuritySettings)

    def test_properties(self):
        ss = self.gis.admin.ux.security_settings

        assert ss.enable_https in [True, False]
        assert isinstance(ss.anonymous_access, str)
        assert isinstance(ss.allowed_origins, list)
        assert isinstance(ss.allowed_redirect_uris, list)
        assert ss.enable_update_user_profile in [True, False]
        assert ss.share_public in [True, False]
        assert ss.show_social_media in [True, False]

    def test_informational_banner(self):
        ss = self.gis.admin.ux.security_settings

        # get current banner, or None
        ib = ss.get_informational_banner()
        if ib:
            assert ib
        else:
            assert ib == None
        # set informational banner
        assert ss.set_informational_banner(
            text="Test For Python API",
            bg_color="white",
            font_color="black",
            enabled=True,
        )
        assert ss.get_informational_banner()["text"] == "Test For Python API"
        # reset original banner
        if ib:
            assert ss.set_informational_banner(
                text=ib["text"],
                bg_color=ib["bgColor"],
                font_color=ib["fontColor"],
                enabled=ib["enabled"],
            )
        else:
            assert ss.set_informational_banner(text=None, enabled=False)

    def test_password_policy(self):
        ss = self.gis.admin.ux.security_settings

        # get password policy
        assert ss.get_password_policy()

        # change some settings
        assert ss.update_password_policy(min_length=10, include_uppercase=True)
        assert ss.get_password_policy()["minLength"] == 10
        assert ss.get_password_policy()["minUpper"] == 1
        # reset
        assert ss.update_password_policy(min_length=8, include_uppercase=False)

    def test_org_access_notice(self):
        ss = self.gis.admin.ux.security_settings

        orig = ss.get_org_access_notice()
        if orig:
            assert orig
        else:
            assert orig == None

        # Set a test notice
        assert ss.set_org_access_notice(
            "TEST FOR UX MODULE", "TEST FOR UX MODULE", "okOnly"
        )
        if orig:
            assert ss.set_org_access_notice(
                orig["title"], orig["text"], orig["buttons"]
            )
        else:
            assert ss.set_org_access_notice()

    def test_anonymous_access_notice(self):
        ss = self.gis.admin.ux.security_settings

        orig = ss.get_anonymous_access_notice()
        if orig:
            assert orig
        else:
            assert orig == None

        # Set a test notice
        assert ss.set_anonymous_access_notice(
            "TEST FOR UX MODULE", "TEST FOR UX MODULE", "okOnly"
        )
        if orig:
            assert ss.set_anonymous_access_notice(
                orig["title"], orig["text"], orig["buttons"]
            )
        else:
            assert ss.set_anonymous_access_notice()

    def test_mfa(self):
        ss = self.gis.admin.ux.security_settings

        orig = ss.get_multifactor_authentication()
        assert isinstance(orig, dict)

        # set to true and add admins
        admins = []
        users = self.gis.users.search()
        for user in users:
            if user.role == "org_admin":
                admins.append(user.username)
            if len(admins) == 2:
                break

        assert ss.set_multifactor_authentication(admins, enabled=True)
        assert ss.get_multifactor_authentication()["admins"]
        # reset
        if "admins" in orig and orig["admins"]:
            assert ss.set_multifactor_authentication(
                orig["admins"], orig["enabled"]
            )
        else:
            assert ss.set_multifactor_authentication(enabled=False)

    def test_email_settings(self):
        if self.gis._is_agol is True:
            self.skipTest("Email settings not available for AGOL")
        ss = self.gis.admin.ux.security_settings
        # get
        assert ss.get_email_settings

        assert isinstance(
            ss.set_email_settings(
                smtp_host="smtp.gmail.com",
                smtp_port=25,
                from_address="test@gmail.com",
                from_address_label="test_admin",
            ),
            dict,
        )
        try:
            assert ss.delete_email_settings()
        except:
            # Mulitfactor authentication turned on so cannot delete org email settings
            assert 1 == 1

    def test_signin_settings(self):
        ss = self.gis.admin.ux.security_settings

        assert isinstance(ss.signin_settings, dict)

    def test_apps(self):
        if not self.gis._is_agol:
            self.skipTest("Set approved/blocked apps is only available for AGOL")
        ss = self.gis.admin.ux.security_settings
        assert ss.set_approved_apps(True)
        assert ss.set_approved_apps(False)

        assert ss.set_blocked_apps(True)
        assert ss.set_blocked_apps(False)

    def test_social_media_login(self):
        if not self.gis._is_agol:
            self.skipTest("Social Media Login not available for Enterprise")
        ss = self.gis.admin.ux.security_settings
        assert ss.set_social_media_login(False)
        assert (
            "arcgis" in ss.signin_settings["signinOptionsOrder"]["logins"]
        )
        assert ss.set_social_media_login(
            True, ["facebook"], ["facebook", "github", "google", "apple"]
        )
        assert ss.signin_settings["signinOptionsOrder"]["social"] == [
            "facebook",
            "github",
            "google",
            "apple",
        ]
        assert ss.set_social_media_login(
            True, ["facebook"], ["facebook", "google", "github", "apple"]
        )

    def test_idp(self):
        if not self.gis._is_agol:
            self.skipTest("IDP not available for Enterprise")
        ss = self.gis.admin.ux.security_settings
        assert isinstance(ss.get_idp(), dict)


@profiles.admin_enterprise
@integration_test
class TestUtilityServicesSettingsClass(unittest.TestCase):
    """Tests Org Utility Services Settings Class"""

    def test_class_calls(self):
        uss = self.gis.admin.ux.utility_services_settings
        assert isinstance(uss, UtilityServicesSettings)
    
    def test_add_reset(self):
        enterprise_gis = self.gis
        online_gis = GIS(profile="your_online_admin_profile", verify_cert=False, proxy=self.proxies)

        if enterprise_gis.version < [2024, 2]:
            self.skipTest("The add_from_online() method will be available in ArcGIS Enterprise 11.4")

        uss = enterprise_gis.admin.ux.utility_services_settings
        settings = uss.add_from_online(
            ["Elevation", "Geocode", "GeoEnrichment", "Hydrology", "Network", "Orthomapping Elevation"],
            online_gis,
            "RoutingService"
        )
        assert settings

        for service in ['analysis', 'asyncClosestFacility', 'asyncGeocode', 'asyncLocationAllocation', 'asyncODCostMatrix', 'asyncRoute', 'asyncServiceArea', 'asyncVRP', 'closestFacility', 'defaultElevationLayers', 'elevation', 'elevationSync', 'geoanalytics', 'geocode', 'geoenrichment', 'geometry', 'hydrology', 'odCostMatrix', 'orthoMapping', 'packaging', 'printTask', 'rasterAnalytics', 'rasterUtilities', 'route', 'routingServicesSource', 'routingUtilities', 'serviceArea', 'symbols', 'syncVRP', 'traffic', 'trafficData', 'workflowManager', 'asyncFleetRouting', 'snapToRoads']:
            if service == 'snapToRoads' and enterprise_gis.version <= [2024,1]:
                continue
            assert service in enterprise_gis.properties["helperServices"]
        
        uss.reset_services(["Elevation", "Geocode", "GeoEnrichment", "Hydrology", "Network", "Orthomapping Elevation"])


if __name__ == "__main__":
    unittest.main()
