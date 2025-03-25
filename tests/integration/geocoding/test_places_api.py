import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.geocoding._places import PlacesAPI, PlaceIdEnums, get_places_api
from utils.decorators import integration_test, credentials
from utils._logging import enable_verbose_logging


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()


@integration_test
@credentials.agol_api_key
class TestPlacesAPI(unittest.TestCase):
    @property
    def gis(self):
        self._gis = self._gis if hasattr(self, "_gis") else GIS(
            api_key=self.password,
            verify_cert=False,
            proxy=PROXIES,
        )
        return self._gis
    
    @property
    def places_api(self):
        self._places_api = self._places_api if hasattr(self, "_places_api") else get_places_api(self.gis)
        return self._places_api
    
    def get_valid_place_id(self):
        results = self.places_api.search_by_radius(
            point=[-74.004142, 40.743892],
            radius=250,
        )
        assert results.__class__.__name__ == "generator"
        result = next(results)
        assert type(result) == dict
        assert "placeId" in result
        return result["placeId"]

    def test_get_places_api(self):
        assert self.gis
        assert isinstance(self.places_api, PlacesAPI)

    def test_check_privileges(self):
        assert self.places_api._check_privileges(gis=self.gis)

    def test_check_privileges_anonymous(self):
        assert not self.places_api._check_privileges(
            gis = GIS(
                verify_cert=False,
                proxy=PROXIES,
                set_active=False,
            )
        )

    def test_categories(self):
        result = self.places_api.find_category(query="dog")
        assert result

    def test_category_lookup(self):
        result = self.places_api.examine_category("16032")
        assert result

    def test_bbox_search(self):
        results = self.places_api.search_by_extent(
            bbox=[-74.006910, 40.741713, -73.966076, 40.758895],
        )
        assert results.__class__.__name__ == "generator"
        result = next(results)
        assert result

    def test_radius_pt(self):
        results = self.places_api.search_by_radius(
            point=[-74.004142, 40.743892],
            radius=250,
        )
        assert results.__class__.__name__ == "generator"
        result = next(results)
        assert result

    def test_get_place_by_id(self):
        placeid = self.get_valid_place_id()
        result = self.places_api.get_place_by_id(placeid)
        assert result
        assert type(result) == dict
        assert 'placeDetails' in result
        assert type(result['placeDetails']) == dict
        assert 'placeId' in result['placeDetails']
        assert result['placeDetails']['placeId'] == placeid

    def test_get_place_by_id_filtered_by_enum(self):
        placeid = self.get_valid_place_id()
        enums = [
            PlaceIdEnums.ADDRESS_COUNTRY,
            PlaceIdEnums.ADDRESS,
            None,
            'fish',
            12,
        ]
        result = self.places_api.get_place_by_id(placeid, enums)
        assert result


if __name__ == "__main__":
    unittest.main()
