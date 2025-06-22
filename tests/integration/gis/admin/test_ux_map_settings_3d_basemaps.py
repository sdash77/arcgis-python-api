import unittest
from arcgis.gis import GIS, Group
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from random import randrange

enable_verbose_logging()


@profiles.admin_agol
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

    def test_get_and_set_3d_basemaps_group(self):
        admin = self.gis.admin
        ux = admin.ux
        ms = ux.map_settings
        orig_group = ms.basemap_gallery_group_3d
        
        groups = self.gis.groups.search()
        if not groups:
            self.skipTest("No groups configured, cannot test")
        group = groups[randrange(len(groups))]

        ms.basemap_gallery_group_3d = group.id
        assert isinstance(ms.basemap_gallery_group_3d, Group)
        assert ms.basemap_gallery_group_3d.id == group.id
        
        # set back to original group
        ms.basemap_gallery_group_3d = orig_group.id if orig_group else None

if __name__ == "__main__":
    unittest.main()
