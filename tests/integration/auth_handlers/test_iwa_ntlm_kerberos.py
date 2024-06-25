import platform
import unittest
from arcgis.auth import EsriKerberosAuth, EsriSession, EsriWindowsAuth
from arcgis.auth._auth._basic import EsriBasicAuth
from utils.decorators import integration_test, credentials


WINDOWS = platform.platform().lower().find("windows") > -1


@unittest.skipIf(
    WINDOWS == False, "Operating System is not Windows"
)
@credentials.enterprise_all_iwa
@integration_test
class TestWinAuth(unittest.TestCase):
    def test_win_auth(self):
        auth = EsriWindowsAuth(username=self.username, password=self.password)
        with EsriSession(auth=auth) as session:
            resp = session.get(
                url=self.portal_url + "/sharing/rest/portals/self",
                params={"f": "json"},
            )
            data = resp.json()
            assert 'creator2' in data["user"]["username"]

    def test_win_auth_no_user(self):
        url = self.portal_url
        auth = EsriWindowsAuth()
        with EsriSession(auth=auth) as session:
            resp = session.get(url=url + "/sharing/rest/portals/self?f=json")
            data = resp.json()
            assert data["user"]["username"]

    def test_win_auth_no_user_server(self):
        url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"

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
        if self.connection_name == "enterprise_multi_iwa":
            url = self.portal_url  # multiiwa_url
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

@unittest.skipIf(
    WINDOWS == False,
    "Operating System is not Windows",
)
@credentials.enterprise_kerberos
@integration_test
class TestKerberos(unittest.TestCase):
    def test_kerberos(self):
        portal_url = self.portal_url

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
        portal_url = self.portal_url

        url = f"{portal_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriKerberosAuth(username=self.username, password=self.password)
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
    WINDOWS == False, "Operating System is not Windows"
)
@credentials.enterprise_ldap
@integration_test
class TestLDAPAuth(unittest.TestCase):
    """LDAP Test"""

    def test_ldap(self):
        url = f"{self.portal_url}/sharing/rest/portals/self?f=json"
        server_url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriBasicAuth(self.username, self.password)
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
