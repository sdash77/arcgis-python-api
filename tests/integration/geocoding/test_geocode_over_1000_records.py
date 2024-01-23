import sys

#
#  Update the Path to set the test area
#  sys.path.insert(0, r"C:\SVN\geosaurus_issue_10456\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

from arcgis.features import GeoAccessor
from arcgis.geocoding import Geocoder
import pandas as pd
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


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestGeoAccessorFromDFGeocoding(unittest.TestCase):
    def test_geocoding_over_1000_records(self):
        # OR geocoder has a max batch size of 1000
        geocoder = Geocoder(
            'https://navigator.state.or.us/arcgis/rest/services/Locators/OregonAddress/GeocodeServer'
        )

        adds = pd.read_csv(
            "https://github.com/Esri/arcgis-python-api/files/12480454/or_addresses.csv"
        )

        or_sdf = pd.DataFrame.spatial.from_df(
            adds, address_column='Address', geocoder=geocoder
        )
        assert len(adds) == len(or_sdf)


if __name__ == "__main__":
    unittest.main()
