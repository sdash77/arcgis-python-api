import sys

sys.path.insert(0, r"c:\SVN\geosaurus_master\src")
import unittest

from arcgis.gis import GIS
from arcgis.gis.kubernetes._admin.kadmin import KubernetesAdmin


profiles = [
    "your_kubernetes_profile"
]  # profile names go here #'your_online_profile', 'your_enterprise_profile',
VERIFY_CERT = False  # Boolean T/F


class TestKubernetesAdmin(unittest.TestCase):
    """General Test Cases for Kubernetes"""

    def setUp(self):
        self._gis = GIS(profile=profiles[0], verify_cert=VERIFY_CERT, trust_env=True)

    def test_properties(self):
        """tests the properties off of the GIS Kubernetes Admin Class"""

        admin = self._gis.admin
        assert isinstance(admin, KubernetesAdmin)
        assert admin.logs
        assert admin.datastores
        assert admin.category_schema
        assert admin.license

        assert admin.metadata
        assert admin.overview
        assert admin.mode
        assert admin.organizations

        assert admin.security
        assert admin.services
        assert admin.services_catalog
        assert admin.social_providers
        assert admin.system
        assert admin.uploads
        assert admin.usage

    def test_scheduled_task(self):
        admin = self._gis.admin
        assert isinstance(admin, KubernetesAdmin)
        assert isinstance(admin.scheduled_tasks(), list)

    def test_system(self):
        from arcgis.gis.kubernetes._admin._system import (
            Server,
            ServerDefaults,
            ServerManager,
            SystemManager,
        )

        admin = self._gis.admin
        assert isinstance(admin, KubernetesAdmin)
        assert isinstance(admin.system, SystemManager)
        sm = admin.system
        sm.properties
        assert sm.content.languages
        # sm.architecture_profiles

        assert sm.deployments
        assert sm.deployments.deployment_properties
        assert sm.indexer.status
        assert sm.recovery
        assert isinstance(sm.recovery.settings, dict)
        assert isinstance(sm.recovery.stores, list)
        servers = sm.servers
        assert servers

        assert sm.servers
        assert sm.indexer
        assert sm.url

    def test_overview(self):
        admin = self._gis.admin
        assert isinstance(admin, KubernetesAdmin)
        assert admin.overview
        assert admin.overview.properties
        assert admin.overview.config

    def test_orgs(self):
        assert self._gis.admin.organizations.properties
        assert self._gis.admin.organizations.orgs[0].properties

    def test_mode(self):
        assert self._gis.admin.mode.properties

    def test_license(self):
        assert admin.license.properties

    def test_datastores(self):
        assert self._gis.admin.datastores
        assert self._gis.admin.datastores.properties
        assert isinstance(self._gis.admin.datastores.stores, list)


if __name__ == "__main__":
    unittest.main()
