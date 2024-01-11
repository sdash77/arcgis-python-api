import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_issue_10917\src")
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


class TestPartneredCollaboration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_online_profile', verify_cert=False, proxy=PROXIES
        )
        cls.dest_url: str = (
            "https://pythonapi.maps.arcgis.com/home/index.html"
        )

    def test_admin_property(self):
        gis: GIS = self.gis
        assert gis.admin.partnered_collaboration

    def test_partnered_collab_properties(self):
        from types import GeneratorType

        collab = self.gis.admin.partnered_collaboration
        assert collab.properties
        assert isinstance(collab.coordinators, GeneratorType)
        assert collab.limits
        assert collab.session
        assert collab.url

    def test_partnered_collab_properties(self):
        collab = self.gis.admin.partnered_collaboration
        coordinators: list = list(collab.coordinators)
        if len(coordinators) == 0:
            collab.coordinators = [self.gis.users.me]
            coordinators: list = list(collab.coordinators)
            assert len(list(coordinators)) > 0
            coordinators: list = list(collab.coordinators)
            collab.coordinators = None
            coordinators: list = list(collab.coordinators)
            assert len(list(coordinators)) == 0

    def test_create_partnered_collab(self):
        mgr = self.gis.admin.partnered_collaboration
        collab = mgr.create(
            message="Welcome to the collaboration.",
            org_url="https://pythonapi.maps.arcgis.com/home/organization.html",
            org_id=None,
            search_users=False,
        )
        assert collab
        for collab in list(mgr.collaborations()):
            collab.delete()


if __name__ == "__main__":
    unittest.main()
