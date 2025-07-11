import sys
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging
from arcgis.gis import GIS

enable_verbose_logging()

@integration_test
@profiles.admin_enterprise
class TestMisMatchEnterprise(unittest.TestCase):

    
    def test_mismatch(self):
        if self.gis.version < [2025, 1]:
            self.skipTest("enterprise does not support `mismatch`")
        val = self.gis.admin.system.indexer.mismatch
        assert isinstance(val, dict)
        assert "status" in val


if __name__ == "__main__":
    unittest.main()