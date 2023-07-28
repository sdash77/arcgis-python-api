import unittest
import os
from arcgis.gis import GIS
from arcgis.gis.admin import AGOLAdminManager
from arcgis.gis.admin._ux import UX
from arcgis.gis.admin._collaboration import CollaborationManager
from arcgis.gis.admin._catagoryschema import CategoryManager
from arcgis.gis.admin._idp import IdentityProviderManager
from arcgis.gis.admin import AGOLAdminManager
from arcgis.apps.tracker import LocationTrackingManager
from arcgis.gis.admin._socialproviders import SocialProviders
from arcgis.gis.admin._creditmanagement import CreditManager
from arcgis.gis.admin._metadata import MetadataManager
from arcgis.gis.admin._security import PasswordPolicy
from arcgis.gis.admin._usage import AGOLUsageReports
from arcgis.gis.admin._license import LicenseManager
from datetime import datetime


online_admin = GIS(profile="your_online_admin_profile", verify_cert=False)
# create an admin
admin = AGOLAdminManager(gis=online_admin)


class TestPortalAdminManager(unittest.TestCase):
    def test_properties(self):
        ux_manager = admin.ux
        assert isinstance(ux_manager, UX)

        collaboration = admin.collaborations
        assert isinstance(collaboration, CollaborationManager)

        cat_schema = admin.category_schema
        assert isinstance(cat_schema, CategoryManager)

        id_provider = admin.idp
        assert isinstance(id_provider, IdentityProviderManager)

        location = admin.location_tracking
        assert isinstance(location, LocationTrackingManager)

        social_providers = admin.social_providers
        assert isinstance(social_providers, SocialProviders)

        credits = admin.credits
        assert isinstance(credits, CreditManager)

        metadata = admin.metadata
        assert isinstance(metadata, MetadataManager)

        pass_policy = admin.password_policy
        assert isinstance(pass_policy, PasswordPolicy)

        usage_reports = admin.usage_reports
        assert isinstance(usage_reports, AGOLUsageReports)

        license = admin.license
        assert isinstance(license, LicenseManager)

        urls = admin.urls
        assert isinstance(urls, dict)

    def test_set_ux_program(self):
        """
        tests setting user experience program to True/False
        Begin by checking what the original value is: True or False
        Set new value to be the opposite of original value
        Change value
        Check the changed value is different than the original
        Go back to original value
        """
        ux_program = admin._user_experience_program
        # test changing to other value then what it already is
        new_value = False if ux_program else True
        assert ux_program != new_value
        # change value then change back
        admin._user_experience_program = new_value
        admin._user_experience_program = ux_program
        # make sure value is back to original setting
        final_value = admin._user_experience_program
        assert ux_program == final_value

    def test_schedule_tasks(self):
        """
        tests if receive scheduled tasks, if any
        """
        tasks = admin.scheduled_tasks()
        assert isinstance(tasks, list)

    def test_get_history(self):
        """
        tests if receive login history
        """
        today = datetime.now()
        history = admin.history(start_date=today)
        assert isinstance(history, str)
        assert history
        os.remove(history)

    def test_agol_usage_report(self):
        usage_reports = admin.usage_reports
        reports = [
            "content",
            "users",
            "credits",
        ]
        for report in reports:
            with self.subTest(report):
                generated = usage_reports.generate_report(focus="org", report_type=report, duration="monthly")
                assert generated

if __name__ == "__main__":
    unittest.main()
