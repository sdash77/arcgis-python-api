import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_agol
@integration_test
class TestCreateNotebookServiceAGOL(unittest.TestCase):
    def setUp(self):
        self.notebook_item = self.gis.content.get(
            "2078a889b01e40eda0d29fd157c0c325"
        )
        if self.notebook_item:
            self.skip = False
        else:
            self.skip = True

    def test_publish_service(self):
        if self.skip == False:
            gis = self.gis
            notebooks = gis.notebook_server
            services = notebooks[0].services
            assert services.properties
            import uuid

            u: str = uuid.uuid4().hex[:4]
            service = services.create(
                item=self.notebook_item, title=f"Simple{u}GP"
            )
            assert service
            assert service.delete()


if __name__ == "__main__":
    unittest.main()
