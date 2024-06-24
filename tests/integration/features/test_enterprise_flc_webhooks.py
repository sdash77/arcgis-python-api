import unittest
from arcgis.gis import GIS, Item, User
from arcgis.features import FeatureLayerCollection
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_enterprise
@integration_test
class Test_EnterpriseWebhooks(unittest.TestCase):

    def setUp(self):
        user: User = self.gis.users.me
        self.item = self.gis.content.get("fe51286deb144446a7dba666ebe1521d")
        self.gis = self.gis

    def test_webhook_mgr(self):
        flc = FeatureLayerCollection.fromitem(self.item)
        mgr = flc.manager
        whm_from_gis = mgr.webhook_manager
        assert whm_from_gis

    def test_accessing_from_service(self):
        servers = self.gis.admin.servers
        server = servers.get("HOSTING_SERVER")[0]
        services = server.services
        services = [
            service
            for service in servers.get("HOSTING_SERVER")[0].services.list("Hosted")
            if service._url.find("a4f2ee.FeatureServer") > -1
        ]
        service = services[0]
        whm = service.webhook_manager
        assert whm.properties
        assert isinstance(whm.list, list)
        assert whm.enable_hooks()
        assert whm.disable_hooks()
        assert whm.enable_hooks()
        assert whm.delete_all_hooks()
        hook = whm.create(
            name="simple_create",
            hook_url="https://en1dx5cd33emv.x.pipedream.net",
        )
        try:
            hook2 = whm.create(
                name="simple_create",
                hook_url="https://en1dx5cd33emv.x.pipedream.net",
            )
        except ValueError as va:
            print(va)
        except Exception as e:
            print(e)
        assert len(whm.list) > 0
        assert all([hook.delete() for hook in whm.list])
        assert len(whm.list) == 0
        hook = whm.create(
            name="simple_create",
            hook_url="https://en1dx5cd33emv.x.pipedream.net",
        )
        hook.edit(name="new_name")
        assert hook.properties["name"] == "new_name"
        assert hook.delete()


if __name__ == "__main__":
    unittest.main()
