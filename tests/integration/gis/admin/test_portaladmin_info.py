import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
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


profiles = ['your_ent_admin_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class Test_PortalAdmin(unittest.TestCase):
    def test_info_11_1(self):
        username = "PAPIadmin"
        password = "PAPIletmein01"
        gis = GIS(
            url="https://1110pubbi-1110pubbi.apps.openshift48release.esri.com/web",
            username=username,
            password=password,
            proxy=PROXIES,
            verify_cert=False,
            use_gen_token=True,
        )
        gis.users.me.update(security_question=1, security_answer="Redlands")
        gis = GIS(
            url="https://1110pubbi-1110pubbi.apps.openshift48release.esri.com/web",
            username=username,
            password=password,
            proxy=PROXIES,
            verify_cert=False,
        )
        assert gis.admin.info
        url = "https://rqawinbi01pt.ags.esri.com/gis"
        gis = GIS(
            url=url,
            username=username,
            password=password,
            proxy=PROXIES,
            verify_cert=False,
            use_gen_token=True,
        )
        gis.users.me.update(security_question=1, security_answer="Redlands")
        gis = GIS(
            url=url,
            username=username,
            password=password,
            proxy=PROXIES,
            verify_cert=False,
        )
        assert gis.admin.info

    def test_info_pre_11_1(self):

        gis = GIS(
            profile=profiles[0],
            proxy=PROXIES,
            verify_cert=False,
        )
        assert gis.admin.info is None


if __name__ == "__main__":
    unittest.main()
