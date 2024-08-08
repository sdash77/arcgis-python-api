import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
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
class Test_Geocoder_Outfields(unittest.TestCase):
    def test_no_out_fields(self):
        """tests without the out_fields parameters"""

        from arcgis.geocoding import batch_geocode

        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            batched = batch_geocode(
                addresses=[
                    "380 New York St, Redlands, CA",
                    "1 World Way, Los Angeles, CA",
                    "1200 Getty Center Drive, Los Angeles, CA",
                    "5905 Wilshire Boulevard, Los Angeles, CA",
                    "100 Universal City Plaza, Universal City, CA 91608",
                    "4800 Oak Grove Dr, Pasadena, CA 91109",
                ],
                as_featureset=True,
                match_out_of_range=True,
            )
            assert len(batched.sdf.columns) > 5  # The amount varies

    def test_out_fields(self):
        """tests without the out_fields parameters"""
        from arcgis.geocoding import batch_geocode

        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            batched = batch_geocode(
                addresses=[
                    "380 New York St, Redlands, CA",
                    "1 World Way, Los Angeles, CA",
                    "1200 Getty Center Drive, Los Angeles, CA",
                    "5905 Wilshire Boulevard, Los Angeles, CA",
                    "100 Universal City Plaza, Universal City, CA 91608",
                    "4800 Oak Grove Dr, Pasadena, CA 91109",
                ],
                as_featureset=True,
                match_out_of_range=True,
                out_fields="LongLabel,ShortLabel",
            )
            assert len(batched.sdf.columns) == 5


if __name__ == "__main__":
    unittest.main()
