import unittest
from arcgis.auth import EsriNotebookAuth, EsriSession, EsriKerberosAuth

try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser
if "api_key" in get_config_parser():
    SKIPME = False
    SITE_URL = get_config_parser()["notebook"]["url"]
    API_KEY = get_config_parser()["notebook"]["token"]
else:
    SKIPME = True

from utils.decorators import integration_test


@unittest.skipIf(SKIPME == True, "could not read the configuration file.")
@integration_test
class TestAPIKey(unittest.TestCase):
    """Tests working with the API Key"""

    def test_notebook_login(self):
        auth = EsriNotebookAuth(token=API_KEY, referer="")
        assert auth.token == API_KEY
        assert auth.referer == ""
        assert auth.verify_cert in (True, False)
        assert auth._token == API_KEY

    def test_notebook_get_set(self):
        auth = EsriNotebookAuth(token=API_KEY, referer="")
        assert auth.token == API_KEY
        auth.token = "THIS IS NOT RIGHT"
        assert auth.token != API_KEY

    def test_notebook_referer(self):
        auth = EsriNotebookAuth(token=API_KEY, referer="AmazingEsri")
        assert auth.referer == "AmazingEsri"

    def test_notebook_auth(self):
        auth = EsriNotebookAuth(
            token=API_KEY, referer=None, auth=EsriKerberosAuth(referer="")
        )
        assert auth.auth

    def test_notebook_op(self):
        """Tests a web call using a API Key"""
        auth = EsriNotebookAuth(
            token=API_KEY, auth=EsriKerberosAuth(referer="")
        )
        with EsriSession(auth=auth) as session:
            resp = session.get(
                url=f"{SITE_URL}/sharing/rest/portals/self?f=json"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "user" in data or "appInfo" in data
            resp = session.get(
                url=f"https://www.arcgis.com/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert not "user" in data
            resp = session.get(
                url=f"https://www.arcgis.com/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert not "user" in data


if __name__ == "__main__":
    unittest.main()
