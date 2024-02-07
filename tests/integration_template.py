import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.enterprise_and_agol
# ^^^ runs tests for each profile
# sets `self.profile` to the profile name
# sets `self.gis` to the GIS for the profile, if connection is successful
# sets `self.proxies` to the detected proxies, if any
#
# see tests/utils/decorators.py for available credential and profile decorators
@integration_test
# ^^^ marks the test as an integration test
# sets the default timeout for the test
# may be enhanced with additional functionality in the future
class TestFeature(unittest.TestCase):
    def test_feature(self):
        pass


if __name__ == "__main__":
    unittest.main()
