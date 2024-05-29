import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item, User
from arcgis.features import FeatureLayerCollection
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

profiles = ["your_online_profile", "your_enterprise_profile"]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

@integration_test
class Test_EnterpriseWebhooks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = "https://pythonapi.playground.esri.com/portal/home"
        username = "arcgispyapibot"
        password = "geosaurus_automation123"
        
        gis: GIS = GIS(
            url=url,
            username=username,
            password=password,
            proxy=PROXIES,
            verify_cert=False,
            use_gen_token=True,
        )
        user: User = gis.users.me
        user.update(security_question=2, security_answer="Redlands")
        gis: GIS = GIS(
            url=url,
            username=username,
            password=password,
            proxy=PROXIES,
            verify_cert=False,
        )
        cls.item = gis.content.get("e893e87eae6f40739527575c62527cc6")
        cls.gis = gis

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
            if service._url.find("Power_Plants_USA.FeatureServer") > -1
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
