import platform
import unittest
from arcgis.auth import EsriKerberosAuth, EsriSession, EsriWindowsAuth


from arcgis.auth._auth._basic import EsriBasicAuth

try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser


if "iwa" in get_config_parser():
    SKIP_IWA = False
    iwa_url = get_config_parser()["iwa"]["url"]
    iwa_user = get_config_parser()["iwa"]["username"]
    iwa_pw = get_config_parser()["iwa"]["password"]
else:
    SKIP_IWA = True

if "kerberos" in get_config_parser():
    SKIP_KERBEROS = False
    ker_url = get_config_parser()["kerberos"]["url"]
else:
    SKIP_KERBEROS = True

if "ldap" in get_config_parser():
    SKIP_LDAP = False
    ldap_url = get_config_parser()["ldap"]["url"]
    ldap_user = get_config_parser()["ldap"]["username"]
    ldap_pw = get_config_parser()["ldap"]["password"]
else:
    SKIP_LDAP = True

if "multiiwa" in get_config_parser():
    SKIP_MULTIIWA = False
    multiiwa_url = get_config_parser()["multiiwa"]["url"]
    multiiwa_user = get_config_parser()["multiiwa"]["username"]
    multiiwa_pw = get_config_parser()["multiiwa"]["password"]
else:
    SKIP_MULTIIWA = True


# url_iwa = "https://nap1.esri.com/portal"
# username = "networkanalyst"
# password = "geocodingscrum"
verify_cert = False
trust_env = True

WINDOWS = platform.platform().lower().find("windows") > -1
try:
    import requests
    import requests_kerberos

    resp = requests.get(iwa_url, auth=requests_kerberos.HTTPKerberosAuth())
except:
    WINDOWS = False


from utils.decorators import integration_test


@unittest.skipIf(
    WINDOWS == False or SKIP_IWA == True, "Operating System is not Windows"
)
@integration_test
class TestWinAuth(unittest.TestCase):
    def test_win_auth(self):
        auth = EsriWindowsAuth(username=iwa_user, password=iwa_pw)
        with EsriSession(auth=auth) as session:
            resp = session.get(
                url=iwa_url + "/sharing/rest/portals/self",
                params={"f": "json"},
            )
            data = resp.json()
            assert 'creator2' in data["user"]["username"]

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
            server_url = [
                s["url"] for s in resp.json()["servers"] if s["isHosted"]
            ][0] + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data

    def test_multi_win_auth(self):
        auth = EsriWindowsAuth(username=iwa_user, password=iwa_pw)
        with EsriSession(auth=auth) as session:
            resp = session.get(
                url=multiiwa_url + "/sharing/rest/portals/self",
                params={"f": "json"},
            )
            data = resp.json()
            assert 'creator2' in data["user"]["username"]

    def test_multi_win_auth_no_user(self):
        url = "https://rqawintest99pt.ags.esri.com/gis"  # multiiwa_url
        auth = EsriWindowsAuth()
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url + "/sharing/rest/portals/self?f=json")
            data = resp.json()
            assert data["user"]["username"]

    def test_multiiwa_no_user_server(self):
        url = "https://rqawintest99pt.ags.esri.com/gis"  # multiiwa_url
        url = f"{url}/sharing/rest/portals/self/servers?f=json"

        auth = EsriWindowsAuth()
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url)
            server_url = [
                s["url"] for s in resp.json()["servers"] if s["isHosted"]
            ][0] + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data

    def test_iwa_no_user_forced_sspi(self):
        url = "https://rqawintest99pt.ags.esri.com/gis"  # multiiwa_url
        url = f"{url}/sharing/rest/portals/self/servers?f=json"
        import copy

        auth = EsriWindowsAuth()
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url)
            server_url = [
                s["url"] for s in resp.json()["servers"] if s["isHosted"]
            ][0] + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data


@unittest.skipIf(
    WINDOWS == False or SKIP_KERBEROS == True,
    "Operating System is not Windows",
)
@integration_test
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
            server_url = [
                s["url"] for s in resp.json()["servers"] if s["isHosted"]
            ][0] + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data

    def test_kerberos_credentials(self):
        """Tests the Kerberos"""
        portal_url = ker_url

        url = f"{portal_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriKerberosAuth(username=iwa_user, password=iwa_pw)
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url)
            data = resp.json()
            assert data
            server_url = [
                s["url"] for s in resp.json()["servers"] if s["isHosted"]
            ][0] + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data


@unittest.skipIf(
    WINDOWS == False or SKIP_LDAP == True, "Operating System is not Windows"
)
@integration_test
class TestLDAPAuth(unittest.TestCase):
    """LDAP Test"""

    def test_ldap(self):
        url = f"{ldap_url}/sharing/rest/portals/self?f=json"
        server_url = f"{ldap_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriBasicAuth(ldap_user, ldap_pw)
        with EsriSession(auth=auth) as session:
            resp = session.get(url)
            data = resp.json()
            assert data["user"]
            resp = session.get(url=server_url)
            data = resp.json()
            server_url = [
                s["url"] for s in resp.json()["servers"] if s["isHosted"]
            ][0] + "/rest/services/System"
            resp = session.get(server_url + "?f=json")
            data = resp.json()
            assert data["services"]


if __name__ == "__main__":
    unittest.main()
