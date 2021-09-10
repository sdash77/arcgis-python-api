import sys

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus\\src")
import unittest
import os
from arcgis.gis import GIS
from arcgis.apps.tracker import LocationTrackingManager
from arcgis.gis.server.sm import ServerManager
from arcgis.gis.admin._socialproviders import SocialProviders
from arcgis.gis.admin._metadata import MetadataManager
from arcgis.gis.admin._machines import Machines
from arcgis.gis.admin._security import Security, PasswordPolicy
from arcgis.gis.admin._site import Site
from arcgis.gis.admin._logs import Logs
from arcgis.gis.admin._federation import Federation
from arcgis.gis.admin._system import System
from arcgis.gis.admin._license import LicenseManager
from arcgis.gis.admin._livingatlas import LivingAtlas
from arcgis.gis.admin._wh import WebhookManager
from arcgis.gis.admin import (
    PortalAdminManager,
    CollaborationManager,
    CategoryManager,
    IdentityProviderManager,
)
from datetime import datetime


ent_admin = GIS(profile="your_enterprise_profile", verify_cert=False)

# create an admin
admin = PortalAdminManager(
    url="https://pythonapi.playground.esri.com/portal//sharing/rest/", gis=ent_admin
)


class TestPortalAdminManager(unittest.TestCase):
    def test_properties(self):
        ux_manager = admin.ux
        assert ux_manager
        assert ux_manager

        collabs = admin.collaborations
        assert isinstance(collabs, CollaborationManager)
        assert collabs

        schemas = admin.category_schema
        assert isinstance(schemas, CategoryManager)
        assert schemas

        identity_provider = admin.idp
        assert isinstance(identity_provider, IdentityProviderManager)
        assert identity_provider

        track = admin.location_tracking
        assert isinstance(track, LocationTrackingManager)
        assert track

        social_providers = admin.social_providers
        assert isinstance(social_providers, SocialProviders)
        assert social_providers

        metadata = admin.metadata
        assert isinstance(metadata, MetadataManager)
        assert metadata

        server = admin.servers
        assert isinstance(server, ServerManager)
        assert server.properties is not None

        machines = admin.machines
        assert isinstance(machines, Machines)
        assert machines

        security = admin.security
        assert isinstance(security, Security)
        assert security

        site = admin.site
        assert isinstance(site, Site)
        assert site

        logs = admin.logs
        assert isinstance(logs, Logs)

        federation = admin.federation
        assert isinstance(federation, Federation)
        assert federation

        system = admin.system
        assert isinstance(system, System)
        assert system

        pass_policy = admin.password_policy
        assert isinstance(pass_policy, PasswordPolicy)
        assert pass_policy

        license = admin.license
        assert isinstance(license, LicenseManager)
        assert license

        living_atlas = admin.living_atlas
        assert isinstance(living_atlas, LivingAtlas)
        assert living_atlas

        webhook = admin.webhooks
        assert isinstance(webhook, WebhookManager)
        assert webhook

        mode = admin.mode
        assert isinstance(mode, dict)
        assert mode

    def test_scheduled_tasks(self):
        """
        tests if receive scheduled tasks, if any
        """
        tasks = admin.scheduled_tasks()
        assert isinstance(tasks, list)

    def test_get_history(self):
        """
        tests if receive login history
        """
        if ent_admin._portal.is_arcgisonline:
            today = datetime.now()
            history = admin.history(start_date=today)
            assert isinstance(history, str)
            assert history
            os.remove(history)


if __name__ == "__main__":
    unittest.main()
