import unittest
from utils.mocks import *


class TestLivingAtlas(unittest.TestCase):

    def test_groups_empty_list(self):
        from arcgis.gis.admin import LivingAtlas

        mock_livingatlas = MockLivingAtlas()
        mock_livingatlas._groups = []
        LivingAtlas.groups.__get__(mock_livingatlas)
        mock_livingatlas._init.assert_called()

    def test_groups_hydrated_list(self):
        from arcgis.gis.admin import LivingAtlas

        mock_livingatlas = MockLivingAtlas()
        mock_livingatlas._groups = ["x"]
        LivingAtlas.groups.__get__(mock_livingatlas)
        mock_livingatlas.init.assert_not_called()


if __name__ == "__main__":

    unittest.main()
