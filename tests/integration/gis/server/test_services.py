import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_enterprise
@integration_test
class TestArcGISServerServices(unittest.TestCase):
    def test_edit_services_sync(self):
        """tests the edit service feature synchronously"""
        server = self.gis.admin.servers.get("HOSTING_SERVER")[0]
        service = server.services.list()[0]
        props = dict(service.properties)
        props["minInstancesPerNode"] = 0
        status, message = service.edit(props)
        assert status
        assert message

    def test_edit_services_async(self):
        """tests the edit service feature asynchronously"""
        server = self.gis.admin.servers.get("HOSTING_SERVER")[0]
        service = server.services.list()[0]
        props = dict(service.properties)
        props["minInstancesPerNode"] = 0
        status, job = service.edit(props, future=True)
        assert status
        assert job
        assert job.properties
        assert job.result()


if __name__ == "__main__":
    unittest.main()
