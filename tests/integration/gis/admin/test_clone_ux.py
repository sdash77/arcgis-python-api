import unittest
import concurrent.futures
from utils.decorators import integration_test, from_to_profiles, profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()


@profiles.admin_enterprise_and_agol
@integration_test
class TestOfflineCloneUX(unittest.TestCase):
    """tests offline UX cloning with same org"""

    @classmethod
    def setUpClass(cls):
        cls.result_files = []
        cls.ux = cls.gis.admin.ux
        cls.default_ux = cls.ux.clone()

    @classmethod
    def tearDownClass(cls):
        cls.restore_default_ux = cls.ux.load_offline_configuration(cls.default_ux[0].result())

    def test_offline_defaults(self):
        """tests local UX file returned if target is None"""

        if not self.gis._is_agol:
            self.gis.update_properties(
                {
                    "allowedOrigins": "http://localhost:8888,http://localhost:8889,http://*.esri.com,http://*,https://*"
                }
            )
        ux = self.gis.admin.ux
        fp = ux.clone()
        assert len(fp) >= 0
        assert fp[0].result()
        self.result_files.append(fp[0].result())

    def test_offline_package_loading(self):
        self.gis.update_properties(
            {
                "allowedOrigins": "http://localhost:8888,http://localhost:8889,http://*.esri.com,http://*,https://*"
            }
        )
        ux = self.gis.admin.ux
        fp = ux.clone()
        assert len(fp) >= 0
        fp = fp[0].result()
        ux_dest = self.gis.admin.ux
        assert ux_dest.load_offline_configuration(fp)


@from_to_profiles.all_except_k8s
@integration_test
class TestCloneUX(unittest.TestCase):
    """tests the clone ux workflows"""

    def setUp(self):
        self.ux_from = self.from_gis.admin.ux
        self.default_ux_from = self.ux_from.clone()
        self.ux_to = self.to_gis.admin.ux
        self.default_ux_to = self.ux_to.clone()

    def test_clone_ux(self):
        self.from_gis.update_properties(
            {
                "allowedOrigins": "http://localhost:8888,http://localhost:8889,http://*.esri.com,http://*,https://*"
            }
        )
        ux = self.from_gis.admin.ux
        result = ux.clone(targets=[self.to_gis])
        assert len(result) == 1
        assert isinstance(result[0], concurrent.futures.Future)
        assert result[0].result()

    def tearDown(self):
        self.restore_ux_from = self.ux_from.load_offline_configuration(self.default_ux_from[0].result())
        self.restore_ux_to = self.ux_to.load_offline_configuration(self.default_ux_to[0].result())


if __name__ == "__main__":
    unittest.main()
