# Uncomment this and update the paths to be the `src` folder and `tests` folder path
# to run it locally.
# import sys

# sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
# sys.path.insert(1, r"C:\SVN\geosaurus_master\tests")

#######################################################################
import unittest
import os
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

try:
    from integration.config import QALAB_ROOT_PATH
except:
    from .integration.config import QALAB_ROOT_PATH


_QALABS_DATSET: str = rf"{QALAB_ROOT_PATH}\EntepriseSOE_SOI\linux"

enable_verbose_logging()


@unittest.skipIf(
    os.path.isdir(_QALABS_DATSET) == False, "Cannot find test dataset."
)
@profiles.admin_enterprise  #  must be administrator
@integration_test
class TestTypesSOISOE(unittest.TestCase):
    """tests the SOI/SOE"""

    def test_extensions(self):
        gis = self.gis
        servers = gis.admin.servers.get("HOSTING_SERVER")
        server = servers[0]
        types = server.services.types
        ext_name: str = "Javadownloadfilerestsoe.soe"
        fp = os.path.join(_QALABS_DATSET, "Javadownloadfilerestsoe.soe")
        ext = types.extension
        assert ext
        print(ext)
        for e in ext.extensions:
            e.delete()
        ext.register(fp)

        for e in ext.extensions:
            assert e
            assert e.update(fp)
            assert e.properties
            assert e.extension_name
            assert e.delete()

    def test_providers(self):
        gis = self.gis
        servers = gis.admin.servers.get("HOSTING_SERVER")
        server = servers[0]
        types = server.services.types

        provider = types.provider
        assert provider
        assert provider.properties
        assert provider.get(provider.properties['providers'][0])


if __name__ == "__main__":
    unittest.main()
