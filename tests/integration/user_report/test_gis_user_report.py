import unittest
import datetime as _dt
from utils.decorators import integration_test, profiles


@profiles.admin_enterprise_and_agol
@integration_test
class TestReportApi(unittest.TestCase):
    """Tests the <username>/report API for Online"""

    def setUp(self):
        """setup user and start_time"""
        self.user = self.gis.users.me

        self.today = _dt.datetime.utcnow()
        # first day of this month
        self.start_time_monthly = self.today.replace(day=1)
        # past monday
        self.start_time_weekly = self.today - _dt.timedelta(days=self.today.weekday())
        # first day of current quarter
        self.current_quarter = (self.today.month - 1) // 3 + 1
        self.start_time_quarterly = self.today.replace(month=self.current_quarter * 3 - 2, day=1)

    def test_missing_argument_error(self):
        """test missing argument raises error"""
        with self.assertRaises(Exception) as e:
            self.user.report("users", None, "weekly")

    def test_daily_report_error(self):
        """test daily reports raise ValueError (daily activity report does not)"""
        with self.assertRaises(Exception) as e:
            self.user.report("users", self.start_time_monthly, "daily")
            assert "Daily only applies to activity report" in e.exception

    def test_start_time_error_weekly(self):
        """test start_time raising error for weekly report not started from Sunday or Monday"""
        invalid_start_time = self.today - _dt.timedelta(days=self.today.weekday() + 2)
        with self.assertRaises(Exception) as e:
            self.user.report("users", "weekly", start_time=invalid_start_time)
            assert "Invalid start_time" in e.exception

    def test_start_time_error_monthly(self):
        """test start_time raising error for monthly report not started from the first day of the month"""
        invalid_start_time = self.today.replace(day=2)
        with self.assertRaises(Exception) as e:
            self.user.report("users", "monthly", start_time=invalid_start_time)
            assert "Invalid start_time" in e.exception

    def test_content_report(self):
        """test weekly content report without start_time"""
        content_item = self.user.report(
            report_type="content", duration="weekly"
        )
        assert content_item
        assert content_item.delete()

    def test_users_report(self):
        """test monthly users report without start_time"""
        users_item = self.user.report(
            report_type="users", duration="monthly"
        )
        assert users_item
        assert users_item.delete()

    def test_credit_report(self):
        """test weekly users report"""
        if not self.gis._is_agol:
            self.skipTest("Implemented only on ArcGIS Online")
        credit_item = self.user.report(
            report_type="credits", duration="weekly", start_time=self.start_time_weekly
        )
        assert credit_item
        assert credit_item.delete()

    def test_activity_daily_report(self):
        """test daily activity report"""
        if not self.gis._is_agol:
            self.skipTest("Implemented only on ArcGIS Online")
        activity_item = self.user.report(
            report_type="activity", duration="daily", start_time=self.today
        )
        assert activity_item
        assert activity_item.delete()

    def test_itemUsages_report_aggregate(self):
        """test quarterly item usage report with weekly aggregation"""
        if not self.gis._is_agol:
            self.skipTest("Implemented only on ArcGIS Online")
        itemUsage_item = self.user.report(
            report_type="itemUsages",
            duration="quarterly",
            start_time=self.start_time_quarterly,
            time_aggregate="week",
        )
        assert itemUsage_item
        assert itemUsage_item.delete()

    def test_serviceUsages_report(self):
        """test weekly service usage report"""
        if not self.gis._is_agol:
            self.skipTest("Implemented only on ArcGIS Online")
        serviceUsage_item = self.user.report(
            report_type="serviceUsages",
            duration="weekly",
            start_time=self.start_time_weekly,
        )
        assert serviceUsage_item
        assert serviceUsage_item.delete()


if __name__ == "__main__":
    unittest.main()
