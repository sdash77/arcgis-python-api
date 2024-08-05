import unittest
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.agol_admin
@integration_test
class TestUxMapSettings3DBasemaps(unittest.TestCase):
    def test_get_3d_basemaps(self):
        admin = self.gis.admin
        ux = admin.ux
        assert ux.map_settings.use_3D_basemaps in [True, False]

    def test_set_3d_basemaps(self):
        admin = self.gis.admin
        ux = admin.ux
        original_value = ux.map_settings.use_3D_basemaps
        not_orignal_value = not original_value
        ux.map_settings.use_3D_basemaps = not_orignal_value
        assert ux.map_settings.use_3D_basemaps == not_orignal_value
        ux.map_settings.use_3D_basemaps = original_value
        assert ux.map_settings.use_3D_basemaps == original_value


if __name__ == "__main__":
    unittest.main()
