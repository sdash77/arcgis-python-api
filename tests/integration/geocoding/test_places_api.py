import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.geocoding._places import PlacesAPI
from arcgis.geocoding._places import PlaceIdEnums, get_places_api
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestPlacesAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis: GIS = GIS(
            api_key="AAPKed706a70151045f3a51b1917d84757610pwOA7fIeA6M3kLOR0_kBLPRMfwnympI0ql7knab8d6sTEJyRRKAzQBGqgP6XSDj",
            verify_cert=False,
            proxy=PROXIES,
        )
        cls.places_api = PlacesAPI(gis=cls.gis)

    def test_check_privileges(self):
        assert self.places_api._check_privileges(gis=self.gis)
        assert (
            self.places_api._check_privileges(
                gis=GIS(
                    profile='your_online_profile',
                    verify_cert=False,
                    proxy=PROXIES,
                    set_active=False,
                )
            )
            == True
        )
        assert (
            self.places_api._check_privileges(
                gis=GIS(
                    verify_cert=False,
                    proxy=PROXIES,
                    set_active=False,
                )
            )
            == False
        )

    def test_categories(self):
        result = self.places_api.find_category(query="dog")
        assert result

    def test_category_lookup(self):
        result = self.places_api.examine_category("16032")
        assert result

    def test_bbox_search(self):
        for result in self.places_api.search_by_extent(
            bbox=[-74.006910, 40.741713, -73.966076, 40.758895],
            categories=["17117", "16032"],
        ):
            assert result
            break

    def test_radius_pt(self):
        for result in self.places_api.search_by_radius(
            point=[-74.004142, 40.743892],
            radius=250,
            categories=["17117", "16032"],
        ):
            assert result

    def test_get_place(self):
        placeid = "c4e33d618a328873f554a46c87ca9ea9"
        result = self.places_api.get_place_by_id(placeid)
        assert result

    def test_get_place_enum(self):
        placeid = "c4e33d618a328873f554a46c87ca9ea9"
        enums = [
            PlaceIdEnums.ADDRESS_COUNTRY,
            PlaceIdEnums.ADDRESS,
            None,
            'fish',
            12,
        ]
        result = self.places_api.get_place_by_id(placeid, enums)
        assert result


@integration_test
class TestPlacesAPIFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis: GIS = GIS(
            api_key="AAPKed706a70151045f3a51b1917d84757610pwOA7fIeA6M3kLOR0_kBLPRMfwnympI0ql7knab8d6sTEJyRRKAzQBGqgP6XSDj",
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_get_places_api(self):
        assert isinstance(get_places_api(self.gis), PlacesAPI)


if __name__ == "__main__":
    unittest.main()
