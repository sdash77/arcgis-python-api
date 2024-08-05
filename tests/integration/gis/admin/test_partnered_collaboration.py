import unittest
from arcgis.gis import GIS
from arcgis.gis.admin import PartneredCollabManager
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from types import GeneratorType

enable_verbose_logging()


@profiles.admin_agol
@integration_test
class TestPartneredCollaboration(unittest.TestCase):
    def setUp(self):
        self.gis = GIS(
            profile="your_online_admin_profile", verify_cert=False, proxy=self.proxies
        )
        self.dest_url: str = "https://pythonapi.maps.arcgis.com/home/index.html"

    def test_admin_property(self):
        gis: GIS = self.gis
        assert gis.users.me.role == "org_admin"
        assert gis.admin.partnered_collaboration
        assert isinstance(gis.admin.partnered_collaboration, PartneredCollabManager)

    def test_partnered_collab_properties(self):
        collab = self.gis.admin.partnered_collaboration
        assert collab.properties
        assert isinstance(collab.coordinators, GeneratorType)
        assert collab.limits
        assert collab.session
        assert collab.url

    def test_partnered_collab_coord_properties(self):
        collab = self.gis.admin.partnered_collaboration
        coordinators: list = list(collab.coordinators)
        if len(coordinators) == 0:
            assert (
                self.gis.users.me.role == "org_admin"
                or self.gis.users.me.role_id == "iCCCCCCCCCCCCCCC"
            )
            collab.coordinators = [self.gis.users.me]
            coordinators: list = list(collab.coordinators)
            assert len(list(coordinators)) > 0
            coordinators: list = list(collab.coordinators)
            collab.coordinators = None
            coordinators: list = list(collab.coordinators)
            assert len(list(coordinators)) == 0
        else:
            assert len(coordinators) <= 20

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
