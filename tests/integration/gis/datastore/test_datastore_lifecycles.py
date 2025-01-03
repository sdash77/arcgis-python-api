import unittest
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@integration_test
@profiles.admin_enterprise
class TestDataStoreLifeCycles(unittest.TestCase):
    def test_datastore_mgr(self):
        server = self.gis.admin.servers.get("HOSTING_SERVER")[0]
        ds = server.datastores
        datastores = ds.list()
        if len(datastores) > 0:
            datastore = datastores[0]
            assert datastore.lifecycleinfos
            assert isinstance(datastore.lifecycleinfos, dict)


if __name__ == "__main__":
    unittest.main()
