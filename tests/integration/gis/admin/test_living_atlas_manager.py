import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_enterprise
@integration_test
class TestLivingAtlasManager(unittest.TestCase):
    def test_living_atlas(self):
        admin = self.gis.admin
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
