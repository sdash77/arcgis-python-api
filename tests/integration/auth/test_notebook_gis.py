import os
from arcgis.auth.tools._util import detect_proxy

# import imp
import json
import tempfile
import unittest
import unittest.mock
from unittest.mock import MagicMock


import unittest
from arcgis.auth import EsriNotebookAuth, EsriSession, EsriKerberosAuth
from arcgis.gis import GIS, ProfileManager

try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser
if "notebook" in get_config_parser():
    SKIPME = False
    SITE_URL = get_config_parser()["notebook"]["url"]
    API_KEY = get_config_parser()["notebook"]["token"]
else:
    SKIPME = True

print(SITE_URL, API_KEY)


###########################################################################
from utils.decorators import integration_test


@integration_test
class TestHomeNBAUTHLogic(unittest.TestCase):
    """Test the 'home' logic for NBAUTH file"""

    def test_home_nbauth_login(self):
        """tests the login method using the NBAUTH logic (pre-10.8.1 style of NB_AUTH_FILE"""
        gis_source = GIS(
            profile="your_enterprise_profile", verify_cert=False
        )
        private_url = gis_source._url
        public_url = gis_source._url
        referer = ""
        token_resp = gis_source._con.post(
            gis_source._con._token_url,
            {
                "username": gis_source.users.me.username,
                "password": ProfileManager()._securely_get_password(
                    "your_enterprise_profile"
                ),
                "referer": json.dumps(referer),
                "expiration": 1440,
                "f": "json",
            },
            add_token=False,
        ).get("token", None)
        if token_resp is None:
            raise Exception(
                "Could not authenticate, please verify `your_enterprise_profile` exists on the system."
            )
        del gis_source

        with tempfile.TemporaryDirectory() as d:
            token = json.dumps(
                {
                    "token": f"{token_resp}",
                    "referer": "",
                    "privatePortalUrl": public_url,
                    "publicPortalUrl": public_url,
                }
            )
            f = open(os.path.join(d, ".nbauth.json"), "w")
            f.write(token)
            f.close()
            del f
            os.getenv
            with unittest.mock.patch.dict(
                "os.environ",
                {"NB_AUTH_FILE": os.path.join(d, ".nbauth.json")},
                clear=True,
            ):
                with unittest.mock.patch.object(
                    os,
                    "getenv",
                    return_value=os.path.join(d, ".nbauth.json"),
                ):
                    self.assertEqual(
                        os.environ.get("NB_AUTH_FILE"),
                        os.path.join(d, ".nbauth.json"),
                    )
                    self.assertEqual(len(os.environ), 1)
                    gis = GIS(url="home", verify_cert=False)
                    assert gis._con._expiration == 10080
                    assert gis.users.me
                    del gis

    # ----------------------------------------------------------------------
    def test_home_nbauth_login_expiration_stated(self):
        """
        tests the login method using the NBAUTH logic with expiration key
        present (new style 10.8.1+)
        """
        gis_source = GIS(
            profile="your_enterprise_profile", verify_cert=False
        )
        private_url = gis_source._url
        public_url = gis_source._url
        referer = ""
        token_resp = gis_source._con.post(
            gis_source._con._token_url,
            {
                "username": gis_source.users.me.username,
                "password": ProfileManager()._securely_get_password(
                    "your_enterprise_profile"
                ),
                "referer": json.dumps(referer),
                "expiration": 1440,
                "f": "json",
            },
            add_token=False,
        ).get("token", None)
        if token_resp is None:
            raise Exception(
                "Could not authenticate, please verify `your_enterprise_profile` exists on the system."
            )
        del gis_source

        with tempfile.TemporaryDirectory() as d:
            token = json.dumps(
                {
                    "token": f"{token_resp}",
                    "referer": "",
                    "privatePortalUrl": public_url,
                    "publicPortalUrl": public_url,
                    "expiration": 20160,
                }
            )
            f = open(os.path.join(d, ".nbauth.json"), "w")
            f.write(token)
            f.close()
            del f
            os.getenv
            with unittest.mock.patch.dict(
                "os.environ",
                {"NB_AUTH_FILE": os.path.join(d, ".nbauth.json")},
                clear=True,
            ):
                with unittest.mock.patch.object(
                    os,
                    "getenv",
                    return_value=os.path.join(d, ".nbauth.json"),
                ):
                    self.assertEqual(
                        os.environ.get("NB_AUTH_FILE"),
                        os.path.join(d, ".nbauth.json"),
                    )
                    self.assertEqual(len(os.environ), 1)
                    gis = GIS(url="home", verify_cert=False)
                    assert gis._con._expiration > 0
                    assert gis.users.me
                    del gis


if __name__ == "__main__":
    unittest.main()
