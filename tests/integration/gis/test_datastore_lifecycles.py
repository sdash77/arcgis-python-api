import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, User
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


@integration_test
class TestDataStoreLifeCycles(unittest.TestCase):
    def test_datastore_mgr(self):
        url = "https://rqalnxbi01pt.esri.com/gis"
        username = "PAPIadmin"
        password = "PAPIletmein01"
        gis = GIS(
            url, username, password, verify_cert=False, use_gen_token=True
        )
        user: User = gis.users.me
        user.update(security_answer="Redlands", security_question=1)
        gis = GIS(
            url,
            username,
            password,
            verify_cert=False,
        )
        server = gis.admin.servers.get("HOSTING_SERVER")[0]
        ds = server.datastores
        datastores = ds.list()
        if len(datastores) > 0:
            datastore = datastores[0]
            assert datastore.lifecycleinfos
            assert isinstance(datastore.lifecycleinfos, dict)


if __name__ == "__main__":
    unittest.main()
