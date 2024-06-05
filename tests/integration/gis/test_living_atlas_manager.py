#######################################################################
import sys
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()

from arcgis.gis import GIS


# @profiles.enterprise
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
class TestLivingAtlasManager(unittest.TestCase):
    def test_living_atlas(self):
        username = "PAPIadmin"
        password = "PAPIletmein01"

        gis = GIS(
            url="https://rextapilnx02eb.esri.com/portal",
            username=username,
            password=password,
            trust_env=True,
        )
        admin = gis.admin
        assert admin.living_atlas
        la = admin.living_atlas
        mgr = la.update_manager
        assert mgr

        checked: dict = mgr.check()
        assert checked
        assert mgr.package_directory
        assert mgr.properties
        if len(checked['availablePackages']) > 0:

            update_id = checked['availablePackages'][0]['packageId']
            job = mgr.update(package_id=update_id)
            job.result()


if __name__ == "__main__":
    unittest.main()
