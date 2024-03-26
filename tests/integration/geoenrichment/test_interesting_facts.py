import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.geoenrichment import BufferStudyArea, Country
from arcgis.geoenrichment.enrichment import NamedArea
from arcgis.geometry import Point, Polygon, Polyline, Geometry
from arcgis.geoenrichment import interesting_facts
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
class Test_InterestingFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile=profiles[0],
            verify_cert=False,
            proxies=PROXIES,
            proxy=PROXIES,
        )

    def test_string_address(self):
        """tests with a string address"""
        a = "380 New York Street, Redlands, CA"
        facts = interesting_facts(study_areas=[a])
        assert 'results' in facts
        assert 'messages' in facts

    def test_input_admin_areas(self):
        usa = Country.get("USA")
        redlands = usa.subgeographies.states['California'].zip5['92373']
        facts = interesting_facts(study_areas=[redlands])
        assert 'results' in facts
        assert 'messages' in facts

    def test_buffered_study_area(self):
        buffered = BufferStudyArea(
            area='380 New York St Redlands CA 92373',
            radii=[1, 3, 5],
            units='Miles',
            overlap=False,
        )
        facts = interesting_facts(study_areas=[buffered])
        assert 'results' in facts
        assert 'messages' in facts

    def test_drive_time_areas(self):
        drive_times = BufferStudyArea(
            **{
                "area": Geometry(
                    {
                        "x": -122.435,
                        "y": 37.785,
                        'spatialReference': {'wkid': 4326},
                    }
                ),
                "units": "Minutes",
                "radii": [10],
                "travel_mode": "Driving",
            }
        )
        facts = interesting_facts(study_areas=[drive_times])
        assert 'results' in facts
        assert 'messages' in facts

    def test_geometries(self):
        polygon = Polygon(
            {
                "rings": [
                    [
                        [-117.156258, 34.077351],
                        [-117.138835, 34.077386],
                        [-117.13892, 34.062811],
                        [-117.156344, 34.062882],
                        [-117.156258, 34.077351],
                    ]
                ],
                "spatialReference": {"wkid": 4326},
            }
        )
        point = Point(
            {
                "x": -122.435,
                "y": 37.785,
                "spatialReference": {"wkid": 4326},
            }
        )
        polyline = Geometry(
            {
                "paths": [[[-13048580, 4036370], [-13046151, 4036366]]],
                "spatialReference": {"wkid": 102100},
            }
        )
        facts = interesting_facts(study_areas=[polygon])
        assert 'results' in facts
        assert 'messages' in facts

        facts = interesting_facts(study_areas=[point])
        assert 'results' in facts
        assert 'messages' in facts
        facts = interesting_facts(study_areas=[polyline])
        assert 'results' in facts
        assert 'messages' in facts
        facts = interesting_facts(study_areas=[point, polygon])
        assert 'results' in facts
        assert 'messages' in facts

    def test_dict_input(self):
        study_areas = [
            {"sourceCountry": "US", "layer": "Admin2", "ids": ["06"]}
        ]
        facts = interesting_facts(study_areas=study_areas)
        assert 'results' in facts
        assert 'messages' in facts

    def test_sedf(self):
        gis = GIS(set_active=False)
        item = gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        sdf = item.layers[0].query(as_df=True)
        facts = interesting_facts(study_areas=[sdf.head()], gis=self.gis)
        assert 'results' in facts
        assert 'messages' in facts

    def test_mix_of_inputs(self):
        gis = GIS(set_active=False)
        item = gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        sdf = item.layers[0].query(as_df=True)
        polyline = Geometry(
            {
                "paths": [[[-13048580, 4036370], [-13046151, 4036366]]],
                "spatialReference": {"wkid": 102100},
            }
        )
        facts = interesting_facts(
            study_areas=[
                sdf.head(),
                {"sourceCountry": "US", "layer": "Admin2", "ids": ["06"]},
                polyline,
            ],
            gis=self.gis,
        )
        assert 'results' in facts
        assert 'messages' in facts


if __name__ == "__main__":
    unittest.main()
