import unittest
import platform

WINDOWS = platform.platform().lower().find("windows") > -1
from arcgis.auth import EsriSession, EsriGenTokenAuth

try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser

if "builtin_server" in get_config_parser():
    parsed = get_config_parser()["builtin_server"]
    url = parsed["url"]
    username = parsed["username"]
    password = parsed["password"]
    print([url, username, password])
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

from utils.decorators import integration_test

# @unittest.skipIf(SKIPME == True, reason=msg)
@unittest.skipIf(
    WINDOWS == False or SKIPME == True, "Operating System is not Windows"
)
@integration_test
class TestStandAloneServer(unittest.TestCase):
    def test_server_login_generateToken(self):
        """tests a basic login of server"""
        token_auth = EsriGenTokenAuth(
            token_url=f"{url}/tokens/generateToken",
            referer="http",
            username=username,
            password=password,
            verify_cert=False,
        )
        assert token_auth.token()

    def test_server_login_just_token(self):
        """tests a basic login of server"""
        token_auth = EsriGenTokenAuth(
            token_url=f"{url}/tokens",
            referer="http",
            username=username,
            password=password,
            verify_cert=False,
        )
        assert token_auth.token()

    def test_simple_connection(self):
        token_url = f"{url}/tokens/generateToken"
        builtin = EsriGenTokenAuth(
            token_url=token_url,
            referer="http",
            username=username,
            password=password,
            verify_cert=False,
            legacy=True,
        )
        with EsriSession(
            auth=builtin, verify_cert=False, trust_env=True
        ) as session:
            resp1 = session.get(
                f"{url}/rest/services",
                params={"f": "json"},
            )
            resp2 = session.get(
                f"{url}/rest/services/System",
                params={"f": "json"},
            )
            data = resp1.json()
            assert "System" in data["folders"]
            assert resp2.status_code == 200
            assert len(resp2.json()["services"]) > 0


if __name__ == "__main__":
    unittest.main()
