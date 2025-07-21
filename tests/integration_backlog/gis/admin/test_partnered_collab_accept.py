import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils._logging import enable_verbose_logging
from utils.decorators import profiles, integration_test

enable_verbose_logging()


@profiles.admin_agol
@integration_test
class TestPartneredCollabAccept(unittest.TestCase):
    def setUp(self):
        self.gis_dest = GIS(
            username='python_collaboration',
            password='FrankTheTank1!',
            verify_cert=False,
            proxy=self.proxies,
        )
        self.admin_source = self.gis.admin
        pc_source = self.admin_source.partnered_collaboration

        self.admin_dest = self.gis_dest.admin
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
        else:
            self.skipTest("No collaborations to accept")

    def tearDown(self):
        pc_dest = self.admin_dest.partnered_collaboration

        for c in pc_dest.collaborations():
            c.delete()


if __name__ == "__main__":
    unittest.main()
