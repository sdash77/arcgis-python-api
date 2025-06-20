import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis import ItemTypeEnum, ItemProperties

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class TestPublishNetworkDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            url="https://nap2.esri.com/portal",
            username="networkanalyst",
            password="geocodingscrum",
            verify_cert=False,
            proxy=PROXIES,
        )
        cls.item = cls.gis.content.get("2d54b5c94825415793a4ff74078df8df")
        cls.path = r"/NorthAmerica.gdb/Routing/Routing_ND"
        cls.server_id = cls.gis.servers['servers'][0]['id']

    def test_import(self):
        from arcgis.network import publish_routing_services

    def test_create_service_server_id(self):
        from arcgis.network import publish_routing_services

        from arcgis.network._utils import SolverType

        item = self.item
        path = self.path
        import uuid

        result = publish_routing_services(
            datastore=item,
            path=path,
            solver_types=SolverType.ROUTE,
            server_id=self.server_id,
            folder=f"ROUTING{uuid.uuid4().hex[:4]}",
        )
        assert result
        assert result.result()

    def test_create_service_no_server_id(self):
        from arcgis.network import publish_routing_services

        from arcgis.network._utils import SolverType

        item = self.item
        path = self.path
        import uuid

        result = publish_routing_services(
            datastore=item,
            path=path,
            solver_types=SolverType.ROUTE,
            server_id=self.server_id,
            folder=f"ROUTING{uuid.uuid4().hex[:4]}",
        )
        assert result
        assert result.result()

    @classmethod
    def tearDownClass(cls):
        print('fin')


if __name__ == "__main__":
    unittest.main()
