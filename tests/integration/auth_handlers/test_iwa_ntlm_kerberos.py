import sys

# sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import platform
import unittest
from arcgis.auth import EsriWindowsAuth, EsriKerberosAuth, EsriSession
from arcgis.auth._auth._basic import EsriBasicAuth

try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser


if 'iwa' in get_config_parser():
    SKIP_IWA = False
    iwa_url = get_config_parser()['iwa']['url']
    iwa_user = get_config_parser()['iwa']['username']
    iwa_pw = get_config_parser()['iwa']['password']
else:
    SKIP_IWA = True

if 'kerberos' in get_config_parser():
    SKIP_KERBEROS = False
    ker_url = get_config_parser()['kerberos']['url']
else:
    SKIP_KERBEROS = True

if 'ldap' in get_config_parser():
    SKIP_LDAP = False
    ldap_url = get_config_parser()['ldap']['url']
    ldap_user = get_config_parser()['ldap']['username']
    ldap_pw = get_config_parser()['ldap']['password']
else:
    SKIP_LDAP = True

url_iwa = "https://nap1.esri.com/portal"
username = "networkanalyst"
password = "geocodingscrum"
verify_cert = False
trust_env = True

WINDOWS = platform.platform().lower().find("windows") > -1
try:
    import requests

    resp = requests.get(url_iwa)
except:
    WINDOWS = False


@unittest.skipIf(
    WINDOWS == False or SKIP_IWA == True, "Operating System is not Windows"
)
class TestWinAuth(unittest.TestCase):
    def test_win_auth(self):
        auth = EsriWindowsAuth(username=iwa_user, password=iwa_pw)
        with EsriSession(auth=auth) as session:
            resp = session.get(url=iwa_url + "/sharing/rest/portals/self?f=json")
            data = resp.json()
            assert data["user"]["username"].find(iwa_user.split('\\')[-1]) > -1

    def test_win_auth_no_user(self):
        url = iwa_url
        auth = EsriWindowsAuth()
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url + "/sharing/rest/portals/self?f=json")
            data = resp.json()
            assert data["user"]["username"]

    def test_win_auth_no_user_server(self):
        url = f"{iwa_url}/sharing/rest/portals/self/servers?f=json"

        auth = EsriWindowsAuth()
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url)
            server_url = [s["url"] for s in resp.json()["servers"] if s["isHosted"]][
                0
            ] + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data


@unittest.skipIf(
    WINDOWS == False or SKIP_KERBEROS == True, "Operating System is not Windows"
)
class TestKerberos(unittest.TestCase):
    def test_kerberos(self):
        """Tests the Kerberos"""
        portal_url = ker_url

        url = f"{portal_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriKerberosAuth()
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url)
            data = resp.json()
            assert data
            server_url = [s["url"] for s in resp.json()["servers"] if s["isHosted"]][
                0
            ] + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data


@unittest.skipIf(
    WINDOWS == False or SKIP_LDAP == True, "Operating System is not Windows"
)
class TestLDAPAuth(unittest.TestCase):
    """LDAP Test"""

    def test_ldap(self):
        ldap_url = "https://rpubrh77017.ags.esri.com/portal"
        url = f"{ldap_url}/sharing/rest/portals/self?f=json"
        server_url = f"{ldap_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriBasicAuth(ldap_user, ldap_pw, legacy=True)
        with EsriSession(auth=auth) as session:
            resp = session.get(url)
            data = resp.json()
            assert data["user"]
            resp = session.get(url=server_url)
            data = resp.json()
            server_url = [s["url"] for s in resp.json()["servers"] if s["isHosted"]][
                0
            ] + "/rest/services/System"
            resp = session.get(server_url + "?f=json")
            data = resp.json()
            assert data["services"]


if __name__ == "__main__":
    unittest.main()
