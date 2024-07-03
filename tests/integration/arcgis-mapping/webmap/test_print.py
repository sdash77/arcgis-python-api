import unittest
from arcgis.map import Map
from arcgis.gis import GIS
from utils.decorators import integration_test

PROFILES = ["your_online_profile"]

@integration_test
class TestPrintMap(unittest.TestCase):
    def test_print_png8(self):
        """Test print to PNG8"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            rprint = wm.print(
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
