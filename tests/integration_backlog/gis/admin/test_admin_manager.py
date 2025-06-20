import os
import pandas as pd
import unittest
from arcgis.apps.tracker import LocationTrackingManager
from arcgis.gis.admin import AGOLAdminManager, PortalAdminManager
from arcgis.gis.admin._catagoryschema import CategoryManager
from arcgis.gis.admin._collaboration import CollaborationManager
from arcgis.gis.admin._creditmanagement import CreditManager
from arcgis.gis.admin._federation import Federation
from arcgis.gis.admin._idp import IdentityProviderManager
from arcgis.gis.admin._license import LicenseManager
from arcgis.gis.admin._livingatlas import LivingAtlas
from arcgis.gis.admin._logs import Logs
from arcgis.gis.admin._machines import Machines
from arcgis.gis.admin._metadata import MetadataManager
from arcgis.gis.admin._security import PasswordPolicy, Security
from arcgis.gis.admin._site import Site
from arcgis.gis.admin._socialproviders import SocialProviders
from arcgis.gis.admin._system import System
from arcgis.gis.admin._usage import AGOLUsageReports
from arcgis.gis.admin._ux import UX
from arcgis.gis.admin._wh import WebhookManager
from arcgis.gis.server.sm import ServerManager
from arcgis._impl.common._isd import InsensitiveDict
from datetime import datetime
from utils.decorators import profiles, integration_test


@profiles.admin_enterprise_and_agol
@integration_test
class TestAdminManager(unittest.TestCase):
    def setUp(self):
        if self.gis._is_agol:
            self.admin = AGOLAdminManager(gis=self.gis)
        else:
            self.admin = PortalAdminManager(
                url=f"{self.gis.url}/sharing/rest/", gis=self.gis
            )

    def test_properties_are_instances_of_expected_type(self):
        dict_or_insensitive = (dict, InsensitiveDict)
        assert isinstance(self.admin.category_schema, CategoryManager)
        assert isinstance(self.admin.collaborations, CollaborationManager)
        assert isinstance(self.admin.idp, IdentityProviderManager)
        assert isinstance(self.admin.license, LicenseManager)
        assert isinstance(
            self.admin.location_tracking, LocationTrackingManager
        )
        assert isinstance(self.admin.metadata, MetadataManager)
        assert isinstance(self.admin.password_policy, PasswordPolicy)
        assert isinstance(self.admin.social_providers, SocialProviders)
        assert isinstance(self.admin.ux, UX)
        if self.gis._is_agol:
            assert isinstance(self.admin.credits, CreditManager)
            assert isinstance(self.admin.urls, dict_or_insensitive)
            assert self.admin.urls
            assert isinstance(self.admin.usage_reports, AGOLUsageReports)
        else:
            assert isinstance(self.admin.federation, Federation)
            assert isinstance(self.admin.living_atlas, LivingAtlas)
            assert isinstance(self.admin.logs, Logs)
            assert isinstance(self.admin.machines, Machines)
            assert isinstance(self.admin.mode, dict_or_insensitive)
            assert self.admin.mode
            assert isinstance(self.admin.security, Security)
            assert isinstance(self.admin.servers, ServerManager)
            assert isinstance(
                self.admin.servers.properties, dict_or_insensitive
            )
            assert self.admin.servers.properties
            assert isinstance(self.admin.site, Site)
            assert isinstance(self.admin.system, System)
            assert isinstance(self.admin.webhooks, WebhookManager)
            assert isinstance(self.admin.info, dict_or_insensitive)

    def test_set_ux_program(self):
        """
        tests setting user experience program to True/False
        Begin by checking what the original value is: True or False
        Set new value to be the opposite of original value
        Change value
        Check the changed value is different than the original
        Go back to original value
        """
        if not self.gis._is_agol:
            self.skipTest("Only available for ArcGIS Online")
        ux_program = self.admin._user_experience_program
        # test changing to other value then what it already is
        new_value = False if ux_program else True
        assert ux_program != new_value
        # change value then change back
        self.admin._user_experience_program = new_value
        assert self.admin._user_experience_program == new_value
        self.admin._user_experience_program = ux_program
        # make sure value is back to original setting
        final_value = self.admin._user_experience_program
        assert ux_program == final_value

    def test_schedule_tasks(self):
        """
        tests if receive scheduled tasks, if any
        """
        tasks = list(self.admin.scheduled_tasks())
        assert isinstance(tasks, list)

    def test_get_history_csv(self):
        """
        tests if receive login history as csv file saved to disk
        """
        if not self.gis._is_agol:
            self.skipTest("Only available for ArcGIS Online")
        today = datetime.now()
        history = self.admin.history(start_date=today)
        assert isinstance(history, str)
        assert history
        assert os.path.isfile(history)
        os.remove(history)

    def test_get_history_df(self):
        """
        tests if receive login history as DataFrame
        """
        if not self.gis._is_agol:
            self.skipTest("Only available for ArcGIS Online")
        today = datetime.now()
        history = self.admin.history(start_date=today, data_format='df')
        assert isinstance(history, pd.DataFrame)

    def test_get_history_json(self):
        """
        tests if receive login history as list
        """
        if not self.gis._is_agol:
            self.skipTest("Only available for ArcGIS Online")
        today = datetime.today()
        history = self.admin.history(start_date=today, data_format='json')
        assert isinstance(history, list)

    def test_agol_usage_report(self):
        if not self.gis._is_agol:
            self.skipTest("Only available for ArcGIS Online")
        usage_reports = self.admin.usage_reports
        reports = [
            "content",
            "users",
            "credits",
        ]
        date_str = '2023-02-01'
        date_format = '%Y-%m-%d'
        date_obj = datetime.strptime(date_str, date_format)
        from arcgis.gis import ItemTypeEnum

        [
            item.delete()
            for item in self.gis.admin.content(
                ItemTypeEnum.ADMINISTRATIVE_REPORT
            )
        ]
        for report in reports:
            with self.subTest(report):
                try:
                    generated = usage_reports.generate_report(
                        focus="org",
                        report_type=report,
                        duration="monthly",
                        start_time=date_obj,
                    )
                except Exception as e:
                    assert "already generated" in str(e)
                    continue
                assert generated
                assert generated.result().delete()


if __name__ == "__main__":
    unittest.main()
