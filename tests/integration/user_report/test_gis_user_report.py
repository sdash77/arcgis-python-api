import sys

# sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_8518\src")
import unittest
import datetime as _dt
from arcgis.gis import GIS


class TestReportApi(unittest.TestCase):
    """Tests the <username>/report API"""

    def test_error_on_eneterprise(self):
        gis = GIS(profile="your_enterprise_profile", verify_cert=False, trust_env=True)
        user = gis.users.me
        date_time_str = "16/01/22"
        then = _dt.datetime.strptime(date_time_str, "%d/%m/%y")
        val = int(then.timestamp() * 1000)
        with self.assertRaises(Exception):
            user.report("users", "weekly")

    def test_assert_error(self):
        gis = GIS(profile="your_online_profile", verify_cert=False, trust_env=True)
        user = gis.users.me
        date_time_str = "16/01/22"
        then = _dt.datetime.strptime(date_time_str, "%d/%m/%y")
        val = int(then.timestamp() * 1000)

        with self.assertRaises(Exception):
            user.report("user", None, "weekly")

    def test_content_report(self):
        gis = GIS(profile="your_online_admin_profile", verify_cert=False, trust_env=True)
        user = gis.users.me
        date_time_str = "16/01/22"
        then = _dt.datetime.strptime(date_time_str, "%d/%m/%y")
        val = int(then.timestamp() * 1000)
        # user.report("user", "weekly")

        items = gis.content.advanced_search(
            f"accountid:{gis.properties.id} type:'Administrative Report'"
        )
        [item.delete() for item in items.get("results", [])]
        # final_item = user.report("content", "weekly", val)
        user = gis.users.me
        date_time_str = "16/01/22"
        then = _dt.datetime.strptime(date_time_str, "%d/%m/%y")
        val = int(then.timestamp() * 1000)

        final_item = user.report(
            report_type="content", duration="weekly", start_time=val
        )

        assert final_item
        assert final_item.delete()

    def test_users_report(self):
        gis = GIS(profile="your_online_admin_profile", verify_cert=False, trust_env=True)
        user = gis.users.me
        date_time_str = "16/01/22"
        then = _dt.datetime.strptime(date_time_str, "%d/%m/%y")
        val = int(then.timestamp() * 1000)
        users_item = user.report(
            report_type="users", duration="monthly", start_time=val
        )
        assert users_item
        assert users_item.delete()


if __name__ == "__main__":
    unittest.main()
