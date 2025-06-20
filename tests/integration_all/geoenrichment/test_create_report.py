import sys
import os
import logging
import tempfile
import unittest

from arcgis._impl.common._utils import is_pdf_file
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.geometry import Point
from arcgis.geoenrichment import Country, create_report, BufferStudyArea
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
class Test_GE_CreateReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_online_profile', verify_cert=False, proxy=PROXIES
        )

    def test_create_report_geom(self):
        """tests the create report logic"""
        pt = {
            'geometry': {
                "x": -118.15,
                "y": 33.80,
                "spatialReference": {"wkid": 4326},
            }
        }
        pt2 = Point(
            {
                "x": -118.15,
                "y": 33.80,
                "spatialReference": {"wkid": 4326},
            }
        )
        pt_report = create_report(
            study_areas=[pt, pt2],
            report="business_loc",
            export_format="PDF",
            out_folder=tempfile.gettempdir(),
            out_name="profile.pdf",
        )
        assert os.path.isfile(pt_report)
        assert is_pdf_file(pt_report)
        if os.path.isfile(pt_report):
            os.remove(pt_report)

    def test_create_report_address(self):
        """tests the create report logic"""
        address = "380 New York Street Redlands, California"

        pt_report = create_report(
            study_areas=[address],
            report="business_loc",
            export_format="PDF",
            out_folder=tempfile.gettempdir(),
            out_name="profile.pdf",
        )
        assert os.path.isfile(pt_report)
        assert is_pdf_file(pt_report)
        if os.path.isfile(pt_report):
            os.remove(pt_report)

    def test_create_report_empty_out_name(self):
        """tests the create report logic"""
        address = "380 New York Street Redlands, California"

        pt_report = create_report(
            study_areas=[address],
            report="business_loc",
            export_format="PDF",
            out_folder=tempfile.gettempdir(),
        )
        assert os.path.isfile(pt_report)
        assert is_pdf_file(pt_report)
        if os.path.isfile(pt_report):
            os.remove(pt_report)


if __name__ == "__main__":
    unittest.main()
