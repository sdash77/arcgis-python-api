import sys
import os
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.geoprocessing._job import GPJob
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


profiles = ['your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

data_location = QALAB_ROOT_PATH + r"\data_prep\SDs"


@integration_test
class TestServerPublishSDFile(unittest.TestCase):
    """
    Tests the synchronous and asynchronous workflows for publish SD files to ArcGIS Server
    """

    def test_publish_sd_file_sync(self):
        fp = os.path.join(data_location, "test002.sd")
        gis = GIS(profile=profiles[0], verify_cert=False, proxy=detect_proxy(True))
        server = gis.admin.servers.list()[0]
        service_list = [
            service
            for service in server.services.list()
            if service.properties.serviceName.lower() == "test002"
        ]
        if service_list:
            [s.delete() for s in service_list]
        res = server.publish_sd(fp, future=False)
        if res:
            service_list = [
                service
                for service in server.services.list()
                if service.properties.serviceName.lower() == "test002"
            ]
            if service_list:
                [s.delete() for s in service_list]
        assert res

    def test_publish_sd_file_async(self):
        fp = os.path.join(data_location, "test002.sd")
        gis = GIS(profile=profiles[0], verify_cert=False, proxy=detect_proxy(True))
        server = gis.admin.servers.list()[0]
        service_list = [
            service
            for service in server.services.list()
            if service.properties.serviceName.lower() == "test002"
        ]

        [s.delete() for s in service_list]
        res = server.publish_sd(fp, future=True)
        assert isinstance(res, GPJob)
        assert not res.done() is None
        assert isinstance(res.messages, list)
        assert res.running() in [True, False]
        assert isinstance(res.status, str)
        assert isinstance(res.task, str)
        assert res.result()
        service_list = [
            service
            for service in server.services.list()
            if service.properties.serviceName.lower() == "test002"
        ]

        [s.delete() for s in service_list]


if __name__ == "__main__":
    unittest.main()
