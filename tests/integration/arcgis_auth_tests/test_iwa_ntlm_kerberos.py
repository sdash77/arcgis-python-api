import sys

sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import platform
import unittest
from arcgis.gis import GIS

try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser


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
        gis = GIS(url=iwa_url, password=iwa_pw, username=iwa_user)
        assert gis.users.me

    def test_win_auth_no_user(self):
        gis = GIS(url=iwa_url)
        assert gis.users.me


@unittest.skipIf(
    WINDOWS == False or SKIP_KERBEROS == True, "Operating System is not Windows"
)
class TestKerberos(unittest.TestCase):
    def test_kerberos(self):
        """Tests the Kerberos"""
        gis = GIS(url=ker_url)
        assert gis.users.me  # not working


@unittest.skipIf(
    WINDOWS == False or SKIP_LDAP == True, "Operating System is not Windows"
)
class TestLDAPAuth(unittest.TestCase):
    """LDAP Test"""

    def test_ldap(self):
        ldap_url = "https://rpubrh77017.ags.esri.com/portal"
        username = ldap_user
        password = ldap_pw
        gis = GIS(url=ldap_url, username=username, password=password)
        assert gis.users.me


if __name__ == "__main__":
    unittest.main()
