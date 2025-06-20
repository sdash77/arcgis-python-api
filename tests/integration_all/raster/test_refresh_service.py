import sys
import logging
import unittest
import uuid
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.raster import Raster, ImageryLayer
import arcgis
from utils.decorators import integration_test

from arcgis.raster.analytics import copy_raster
from integration.config import QALAB_ROOT_PATH

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_ent_admin_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestImageRasterService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile=profiles[0], verify_cert=False, proxy=PROXIES)
        uuid.uuid4().hex[:5]
        cls.item = copy_raster(
            input_raster=QALAB_ROOT_PATH + r"\esri_requests\raster_data\Clip_090160.tif",
            output_name=f"output_{uuid.uuid4().hex[:5]}_layer",
            gis=cls.gis,
        )

    @classmethod
    def tearDownClass(cls):
        cls.item.delete()

    def test_refresh_image_service(self):
        lyr = self.item.layers[0]

        result = lyr.refresh_service(future=True)
        assert isinstance(result.result(), str)
        result = lyr.refresh_service(future=False)
        assert isinstance(result, str)

    def test_refresh_raster(self):
        raster = Raster(path=self.item.url, gis=self.gis)
        result = raster.refresh_service(future=True)
        assert isinstance(result.result(), str)
        result = raster.refresh_service(future=False)
        assert isinstance(result, str)


if __name__ == "__main__":
    unittest.main()
