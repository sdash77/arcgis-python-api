import unittest
from arcgis.gis import Item
from arcgis.geoprocessing._job import GPJob
from integration.config import QALAB_ROOT_PATH, get_resource_path

from arcgis.gis.server import Service
from utils.data_utils import cleanup_published_items
from utils.decorators import integration_test, profiles

from utils._logging import enable_verbose_logging


enable_verbose_logging()


@profiles.enterprise
@integration_test
class TestServerPublishSDFile(unittest.TestCase):
    """
    Tests publishing SD file to ArcGIS Server
    """

    def test_publish_sd_file_sync(self):
        fp = get_resource_path("staging_data/SDs/JLD_Preserve.sd", unique_copy=True)
        servers = self.gis.admin.servers
        server = servers.get(role="HOSTING_SERVER")[0]
        service = None

        try:
            result = server.publish_sd(fp, future=False)
            self.assertTrue(result, "Publishing (sync) result is not True")
            service = [
                s
                for s in server.services.list()
                if s.properties.serviceName.lower() == "jld_preserve"
            ][0]
            self.assertIsNotNone(service, "Publishing result is None")
            self.assertIsInstance(
                service,
                Service,
                f"The result is not of type <arcgis.gis.server.Service>: {type(service)}",
            )
        finally:
            if service:
                service.delete()

    def test_publish_sd_file_async(self):
        fp = get_resource_path("staging_data/SDs/JLD_Preserve.sd", unique_copy=True)
        servers = self.gis.admin.servers
        server = servers.get(role="HOSTING_SERVER")[0]

        service = None
        try:
            res = server.publish_sd(fp, future=True)
            assert isinstance(res, GPJob)
            assert not res.done() is None
            assert isinstance(res.messages, list)
            assert res.running() in [True, False]
            assert isinstance(res.status, str)
            assert isinstance(res.task, str)
            result = res.result()
            self.assertTrue(result, "Incorrect result (async)")
            service = [
                s
                for s in server.services.list()
                if s.properties.serviceName.lower() == "jld_preserve"
            ][0]
            self.assertIsNotNone(service, "Published item (async) is None")
        finally:
            if service:
                service.delete()


if __name__ == "__main__":
    unittest.main()
