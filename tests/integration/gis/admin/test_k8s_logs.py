import unittest
import datetime
from utils.decorators import integration_test, profiles


@unittest.skip("Skip until get back to our own k8s environment")
@profiles.admin_k8s
@integration_test
class TestLogsAdminTemplate(unittest.TestCase):
    """
    Tests the Kubernetes Admin Logs Functions
    """

    def test_admin_logs(self):
        """runs the admin.logs tests for Kubernetes"""
        admin = self.gis.admin
        assert admin.logs
        logs = admin.logs
        assert logs
        res = logs.query(
            start_time=datetime.datetime.now()
            - datetime.datetime.now()
            - datetime.timedelta(days=1)
        )
        assert res
        assert logs.edit("DEBUG")
        assert logs.settings
        assert admin.logs.clean()


if __name__ == "__main__":
    unittest.main()
