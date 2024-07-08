import unittest
from arcgis.map import Map
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestPrintMap(unittest.TestCase):

    def setUp(self):
        # create webmap
        self.wm = Map(gis=self.gis)
        assert self.wm

    def test_print_png8(self):
        """Test print to PNG8"""

        rprint = self.wm.print(
            "PNG8",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint

    def test_print_png32(self):
        """Test print to PNG32"""
        rprint = self.wm.print(
            "PNG32",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint

    def test_print_jpg(self):
        """Test print to JPG"""
        rprint = self.wm.print(
            "JPG",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint

    def test_print_gif(self):
        """Test print to GIF"""
        rprint = self.wm.print(
            "GIF",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint

    def test_print_pdf(self):
        """Test print to PDF"""
        rprint = self.wm.print(
            "PDF",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint

    def test_print_eps(self):
        """Test print to EPS"""
        rprint = self.wm.print(
            "EPS",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint

    def test_print_svg(self):
        """Test print to SVG"""
        rprint = self.wm.print(
            "SVG",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint

    def test_print_svgz(self):
        """Test print to SVGZ"""
        rprint = self.wm.print(
            "SVGZ",
            {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -8491340.458070718,
                "ymin": 4652530.856239656,
                "xmax": -8146456.586448021,
                "ymax": 5118490.980666067,
            },
        )
        assert rprint


if __name__ == "__main__":
    unittest.main()
