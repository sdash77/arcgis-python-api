import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

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


class TestAcceptPartneredCollab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_source = GIS(
            profile='your_online_profile', verify_cert=False, proxy=PROXIES
        )
        cls.gis_dest = GIS(
            username='python_collaboration',
            password='FrankTheTank1!',
            verify_cert=False,
            proxy=PROXIES,
        )
        cls.admin_source = cls.gis_source.admin
        pc_source = cls.admin_source.partnered_collaboration

        cls.admin_dest = cls.gis_dest.admin
        pc_dest = cls.admin_dest.partnered_collaboration

        for c in pc_dest.collaborations():
            c.delete()
        pc_source.create(
            message="Let's do this.",
            org_url="https://pythonapi.maps.arcgis.com/home/index.html",
        )

    def test_accept_invite(self):
        pc = self.gis_dest.admin.partnered_collaboration
        collabs = list(pc.collaborations())
        if len(collabs) > 0:
            assert collabs[0].is_active in [True, False]
            assert collabs[0].accept(True)

    @classmethod
    def tearDownClass(cls):
        pc_dest = cls.admin_dest.partnered_collaboration

        for c in pc_dest.collaborations():
            c.delete()


if __name__ == "__main__":
    unittest.main()
