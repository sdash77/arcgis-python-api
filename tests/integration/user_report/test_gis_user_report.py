import unittest
import datetime as _dt
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles


@profiles.admin_agol
@integration_test
class TestReportApiOnline(unittest.TestCase):
    """Tests the <username>/report API for Online"""

    def setUp(self) -> None:
        self.user = self.gis.users.me
        self.start_time_val = _dt.datetime(2024, 4, 1, 16)

    def test_missing_argument_error(self):
        """test missing argument raises error"""
        with self.assertRaises(Exception) as e:
            self.user.report("users", None, "weekly")

    def test_daily_report_error(self):
        """test daily reports raise ValueError (daily activity report does not)"""
        with self.assertRaises(Exception) as e:
            self.user.report("users", self.start_time_val, "daily")
            assert "Daily only applies to activity report" in e.exception

    def test_start_time_error(self):
        """test start_time raising error for weekly report not started from Sunday or Monday"""
        start_time = _dt.datetime(2024, 4, 2, 16)
        with self.assertRaises(Exception) as e:
            self.user.report("users", "weekly", start_time=start_time)
            assert "Invalid start_time" in e.exception

    def test_content_report(self):
        """test weekly content report"""
        content_item = self.user.report(
            report_type="content", duration="weekly", start_time=self.start_time_val
        )
        assert content_item
        assert content_item.delete()

    def test_users_report(self):
        """test monthly users report"""
        users_item = self.user.report(
            report_type="users", duration="monthly", start_time=self.start_time_val
        )
        assert users_item
        assert users_item.delete()

    def test_activity_daily_report(self):
        """test daily activity report"""
        activity_item = self.user.report(
            report_type="activity", duration="daily", start_time=self.start_time_val
        )
        assert activity_item
        assert activity_item.delete()

    def test_itemUsages_report_aggregate(self):
        """test quarterly item usage report"""
        itemUsage_item = self.user.report(
            report_type="itemUsages",
            duration="quarterly",
            start_time=self.start_time_val,
            time_aggregate="month",
        )
        assert itemUsage_item
        assert itemUsage_item.delete()

    def test_serviceUsages_report(self):
        """test weekly service usage report"""
        serviceUsage_item = self.user.report(
            report_type="serviceUsages",
            duration="weekly",
            start_time=self.start_time_val,
        )
        assert serviceUsage_item
        assert serviceUsage_item.delete()


@profiles.admin_enterprise
@integration_test
class TestReportApiEnterprise(unittest.TestCase):
    """Tests the <username>/report API for portal"""

    def setUp(self) -> None:
        self.user = self.gis.users.me
        self.start_time_val = _dt.datetime(2024, 4, 1, 16)

    def test_missing_argument_error(self):
        """test missing argument raises error"""
        with self.assertRaises(Exception) as e:
            self.user.report("user", None, "weekly")

    def test_start_time_error(self):
        """test start_time raising error for monthly report not started from the first day of the month"""
        start_time = _dt.datetime(2024, 4, 2, 16)
        with self.assertRaises(Exception) as e:
            self.user.report("users", "monthly", start_time=start_time)
            assert "Invalid start_time" in e.exception

    def test_content_report(self):
        """test weekly content report without start_time"""
        content_item = self.user.report(report_type="content", duration="weekly")
        assert content_item
        assert content_item.delete()

    def test_users_report(self):
        """test monthly users report without start_time"""
        users_item = self.user.report(report_type="users", duration="monthly")
        assert users_item
        assert users_item.delete()


if __name__ == "__main__":
    unittest.main()
