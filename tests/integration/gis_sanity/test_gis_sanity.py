import sys
import os
import base64
import configparser
from functools import lru_cache
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis import ItemProperties, ItemTypeEnum
from arcgis.features import FeatureLayerCollection
from arcgis.gis import ContentManager
from integration.config import QALAB_ROOT_PATH
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


def decode_value(value: bytes) -> str:
    if isinstance(value, str):
        value = value.encode()
    return base64.b64decode(value).decode()


@lru_cache(maxsize=100)
def get_config_parser() -> dict:
    """
    loads the configuration settings

    :returns: Dict
    """
    configs = [
        os.path.join(
            QALAB_ROOT_PATH,
            "esri_requests",
            "config.ini",
        ),
        os.path.join(os.path.dirname(__file__), "config.ini.txt"),
        os.path.join(os.path.dirname(__file__), "config.ini"),
        os.path.join(
            QALAB_ROOT_PATH,
            "esri_requests",
            "config.ini",
        ),
        os.path.join(
            QALAB_ROOT_PATH,
            "esri_requests",
            "config.ini.txt",
        ),
    ]
    for config in configs:
        if os.path.isfile(config):
            cp = configparser.ConfigParser()
            config = cp.read(config)
            return dict(cp)
    return {}


@integration_test
class Test_GIS_Sanity_Operations(unittest.TestCase):
    """
    This is a collection of tests that performs the common operations
    to ensure the GIS object/Session is working correctly.

    It tests the following:

    - GET method
    - POST method
    - POST multiform post
    - POST multiform and by parts
    - Federated Servers Operations
    """

    @classmethod
    def setUpClass(cls):
        cls.gis_storage = []
        login_info = get_config_parser()
        for key in list(login_info.keys()):
            if key in [
                'iwa',
                'builtin',
                'ldap',
                'basic',
            ]:
                login_params = dict(login_info[key])
                login_params['verify_cert'] = False
                login_params['proxy'] = PROXIES
                gis = GIS(**login_params)
                cls.gis_storage.append(gis)
                assert gis.users.me
        for key in list(login_info.keys()):
            if key in [
                'api_key',
            ]:
                login_params = dict(login_info[key])
                login_params['verify_cert'] = False
                login_params['proxy'] = PROXIES
                assert (
                    GIS(**login_params).properties['appInfo']['appOwner']
                    == 'andrew57'
                )
        for key in list(login_info.keys()):
            if key in [
                'oauth',
            ]:
                login_params = dict(login_info[key])
                login_params['verify_cert'] = False
                login_params['proxy'] = PROXIES
                login_params['url'] = login_params.pop("base_url")
                gis = GIS(**login_params)
                assert (
                    gis.properties['appInfo']['appOwner'] == 'esri_requests'
                )

    # @unittest.skip("skipped")
    def test_login_profiles(self):
        """
        Tests the Login workflow for built-in. This covers GET/POST methods.
        """
        for profile in profiles:
            assert GIS(
                profile=profile, verify_cert=False, proxy=PROXIES
            ).users.me

    # @unittest.skip("skipped")
    def test_upload_small_file(self):
        """this tests the POST operation for a smaller file"""
        ip = ItemProperties(title="Tes", item_type=ItemTypeEnum.IMAGE)
        for gis in self.gis_storage:
            item = gis.content.add(
                item_properties=ip,
                data=QALAB_ROOT_PATH + r"\image\cows2.jpg",
            )
            assert item.delete()

    # @unittest.skip("skipped")
    def test_upload_large_file(self):
        """this tests the POST operation for a large file and covers the by parts method"""
        for gis in self.gis_storage:
            item = gis.content.add(
                {
                    "title": "2nZproduction",
                    "type": "Vector Tile Package",
                    "tags": "a,b,c",
                },
                data=QALAB_ROOT_PATH + r"\VTC\2nZproduction.vtpk",
            )
            assert item.delete()

    # @unittest.skip("skipped")
    def test_admin_sanity_ops(self):
        """tests working with a Federated server"""

        for gis in self.gis_storage:
            if gis._is_agol == False:
                cm: ContentManager = gis.content
                item = cm.create_service(name="AdminServiceTester")
                flc: FeatureLayerCollection = (
                    FeatureLayerCollection.fromitem(item)
                )
                assert flc.manager.properties
                assert flc.manager.refresh()
                assert item.delete()

    def test_apply_edits_agol(self):
        """
        Tests the Multiform POST operation using edit_features
        Tests the common publish operation
        """
        fc = QALAB_ROOT_PATH + r"\fgdb\FGDB_Test.zip"
        ip = ItemProperties(
            title="HFL_APPLY_EDITS", item_type=ItemTypeEnum.FILE_GEODATABASE
        )

        gis = GIS(profile=profiles[0], verify_cert=False, proxy=PROXIES)

        item = gis.content.add(
            item_properties=ip,
            data=fc,
        )
        pitem = item.publish()
        d = [
            {
                "geometry": {
                    "x": 8557728.34765625,
                    "y": 5614481.8983726725,
                    "spatialReference": {
                        "wkid": 102100,
                        "latestWkid": 3857,
                    },
                },
                "attributes": {"OBJECTID": 1},
            }
        ]
        assert pitem.layers[0].edit_features(adds=d)
        assert pitem.delete()
        assert item.delete()

    # @unittest.skip("skipped")
    def test_apply_edits(self):
        """
        Tests the Multiform POST operation using edit_features
        Tests the common publish operation
        """
        fc = QALAB_ROOT_PATH + r"\fgdb\FGDB_Test.zip"
        ip = ItemProperties(
            title="HFL_APPLY_EDITS", item_type=ItemTypeEnum.FILE_GEODATABASE
        )
        for gis in self.gis_storage:
            # gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)

            item = gis.content.add(
                item_properties=ip,
                data=fc,
            )
            pitem = item.publish()
            d = [
                {
                    "geometry": {
                        "x": 8557728.34765625,
                        "y": 5614481.8983726725,
                        "spatialReference": {
                            "wkid": 102100,
                            "latestWkid": 3857,
                        },
                    },
                    "attributes": {"OBJECTID": 1},
                }
            ]
            assert pitem.layers[0].edit_features(adds=d)
            assert pitem.delete()
            assert item.delete()


if __name__ == "__main__":
    unittest.main()
