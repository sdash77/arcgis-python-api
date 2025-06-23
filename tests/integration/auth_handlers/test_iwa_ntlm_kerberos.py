import os
import unittest
from arcgis.gis import GIS
from arcgis.auth import EsriKerberosAuth, EsriSession, EsriWindowsAuth
from arcgis.auth._auth._basic import EsriBasicAuth
from utils.decorators import integration_test, credentials
from utils._common import environ_key_to_bool, parse_username

# skip multi_iwa on automation runs
iwa_credentials = credentials.enterprise_iwa if environ_key_to_bool("CI") else credentials.enterprise_all_iwa

WINDOWS = os.name != "posix"
AVWORLD = os.environ.get("USERDOMAIN", "").lower() == "AVWORLD".lower()

@unittest.skipIf(
    not WINDOWS, "Windows Authentication only supported on Windows"
)
@iwa_credentials
@integration_test
class TestWinAuth(unittest.TestCase):
    def test_get_portal_config(self):
        auth = EsriWindowsAuth(username=self.username, password=self.password)
        with EsriSession(auth=auth, verify_cert=False) as session:
            resp = session.get(
                url=self.portal_url + "/sharing/rest/portals/self",
                params={"f": "json"},
            )
            data = resp.json()
            assert data
            assert parse_username(self.username) in data.get("user", {}).get("username")

    @unittest.skipIf(not AVWORLD, "Must be on AVWORLD to test implicit credentials")
    def test_get_portal_config_implicit_user(self):
        url = self.portal_url
        auth = EsriWindowsAuth()
        with EsriSession(auth=auth, verify_cert=False) as session:
            resp = session.get(url=url + "/sharing/rest/portals/self?f=json")
            data = resp.json()
            assert data
            assert "@avworld" in data.get("user", {}).get("username", "").lower()

    @unittest.skipIf(not AVWORLD, "Must be on AVWORLD to test implicit credentials")
    def test_get_server_system_services_implicit_user(self):
        url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"

        auth = EsriWindowsAuth()
        with EsriSession(auth=auth, verify_cert=False) as session:
            resp = session.get(url=url)
            server_url = get_primary_hosting_server(resp.json()["servers"]) + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data

    def test_get_server_system_services_forced_sspi(self):
        if self.connection_name != "enterprise_multi_iwa":
            self.skipTest("Test only valid for multi-iwa")
        url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriWindowsAuth()
        with EsriSession(auth=auth, verify_cert=False) as session:
            resp = session.get(url=url)
            server_url = get_primary_hosting_server(resp.json()["servers"]) + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            # TODO @achapkowski do we need to assert the SSPI somewhere?
            data = resp2.json()
            assert data
    
    def test_list_servers_gis(self):
        gis = GIS(url=self.portal_url, username=self.username, password=self.password, verify_cert=False)
        servers = gis.admin.servers.list()
        if len(servers) > 0:
            assert servers[0].properties
        assert gis.users.me
        assert parse_username(self.username).lower() in gis.users.me.username.lower()

    @unittest.skipIf(not AVWORLD, "Must be on AVWORLD to test implicit credentials")
    def test_list_servers_implicit_user_gis(self):
        gis = GIS(url=self.portal_url)
        servers = gis.admin.servers.list()
        if len(servers) > 0:
            assert servers[1].properties
        assert gis.users.me

@credentials.enterprise_kerberos
@integration_test
class TestKerberos(unittest.TestCase):
    def test_get_server_list_system_services(self):
        url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriKerberosAuth(username=self.username, password=self.password)
        with EsriSession(auth=auth, verify_cert=False) as session:
            resp = session.get(url=url)
            data = resp.json()
            assert data
            server_url = get_primary_hosting_server(resp.json()["servers"]) + "/rest/services/System"
            resp2 = session.get(server_url + "?f=json")
            data = resp2.json()
            assert data
    
    @unittest.skipIf(not AVWORLD, "Must be on AVWORLD to test implicit credentials")
    def test_list_servers_implicit_user_gis(self):
        gis = GIS(url=self.portal_url)
        servers = gis.admin.servers.list()
        if len(servers) > 0:
            assert servers[1].properties
        assert gis.users.me


@credentials.enterprise_ldap
@integration_test
class TestLDAPAuth(unittest.TestCase):
    """LDAP Test"""
    def test_get_server_list_system_services(self):
        url = f"{self.portal_url}/sharing/rest/portals/self?f=json"
        server_url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
        auth = EsriBasicAuth(session=EsriSession(), username=self.username, password=self.password, verify_cert=False)
        with EsriSession(auth=auth, verify_cert=False) as session:
            resp = session.get(url)
            data = resp.json()
            assert data["user"]
            resp = session.get(url=server_url)
            data = resp.json()
            server_url = get_primary_hosting_server(resp.json()["servers"]) + "/rest/services/System"
            resp = session.get(server_url + "?f=json")
            data = resp.json()
            assert data["services"]
    
    def test_get_user_gis(self):
        gis = GIS(url=self.portal_url, username=self.username, password=self.password, verify_cert=False)
        assert gis.users.me

def get_primary_hosting_server(servers):
    hosting_servers = [s["url"] for s in servers if s["isHosted"]]
    return hosting_servers[0] if hosting_servers else None

if __name__ == "__main__":
    unittest.main()
