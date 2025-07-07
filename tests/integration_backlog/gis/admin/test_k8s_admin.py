import unittest
from arcgis.gis.kubernetes._admin.kadmin import KubernetesAdmin
from arcgis.gis.kubernetes._admin._system import SystemManager
from arcgis.gis.kubernetes._admin._adaptors import WebAdaptorManager
from utils.decorators import integration_test, profiles


@profiles.admin_k8s
@integration_test
class TestKubernetesAdmin(unittest.TestCase):
    """General Test Cases for Kubernetes"""
    
    def test_properties(self):
        """tests the properties off of the GIS Kubernetes Admin Class"""

        admin = self.gis.admin
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
        assert admin.jobs
    
    def test_scheduled_task(self):
        admin = self.gis.admin
        assert isinstance(admin, KubernetesAdmin)
        assert isinstance(list(admin.scheduled_tasks()), list)
    
    def test_jobs(self):
        from arcgis.gis.kubernetes._admin._jobs import JobManager

        admin = self.gis.admin
        assert isinstance(admin, KubernetesAdmin)
        assert isinstance(admin.jobs, JobManager)

    def test_system_container_images(self):
        if self.gis.version > [2024, 1]:        
            admin = self.gis.admin
            assert isinstance(admin, KubernetesAdmin)
            assert isinstance(admin.system, SystemManager)
            sm = admin.system
            assert sm.container_images
    
    def test_system(self):

        admin = self.gis.admin
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
        assert sm.web_adaptors
        assert isinstance(sm.web_adaptors, WebAdaptorManager)
        assert sm.web_adaptors.configuration
        assert sm.architecture_profiles
        assert sm.architecture_profiles.standard
        assert sm.architecture_profiles.enhanced
        assert sm.architecture_profiles.development
        assert sm.licenses
    
    def test_overview(self):
        admin = self.gis.admin
        assert isinstance(admin, KubernetesAdmin)
        assert admin.overview
        assert admin.overview.properties
        assert admin.overview.config
    
    def test_orgs(self):
        assert self.gis.admin.organizations.properties
        assert self.gis.admin.organizations.orgs[0].properties
    
    def test_mode(self):
        assert self.gis.admin.mode.properties
    
    def test_license(self):
        assert self.gis.admin.license.properties
    
    def test_datastores(self):
        assert self.gis.admin.datastores
        assert self.gis.admin.datastores.properties
        assert isinstance(self.gis.admin.datastores.stores, list)


if __name__ == "__main__":
    unittest.main()
