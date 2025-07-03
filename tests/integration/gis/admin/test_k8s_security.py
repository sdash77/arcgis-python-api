import unittest
from arcgis.gis import GIS
from arcgis.gis.kubernetes._admin._security import (
    KubeSecurity,
    KubeSecurityConfig,
    KubeSecurityIngress,
    KubeSecuritySAML,
)
from arcgis._impl.common._isd import InsensitiveDict
from utils.decorators import integration_test, profiles


@profiles.admin_k8s
@integration_test
class TestSecutiryKubernetes(unittest.TestCase):

    # ----------------------------------------------------------------------
    def test_get_security(self):
        """tests to see if `KubeSecurity` is returned"""
        self.assertIsInstance(self.gis.admin.security, KubeSecurity)

    # ----------------------------------------------------------------------
    def test_get_properties(self):
        """tests to see if `KubeSecurity` properties returns a value"""
        self.assertIsInstance(self.gis.admin.security, KubeSecurity)
        sec = self.gis.admin.security
        isinstance(sec, KubeSecurity)
        assert isinstance(sec.properties, InsensitiveDict)
        sec._refresh()

    # ----------------------------------------------------------------------
    def test_url_property(self):
        """tests getting the URL propert on the security object"""
        self.assertIsInstance(self.gis.admin.security, KubeSecurity)
        sec = self.gis.admin.security
        assert sec.url

    # ----------------------------------------------------------------------
    def test_get_configuration(self):
        """tests getting the configuration class"""
        self.assertIsInstance(self.gis.admin.security.configuration, KubeSecurityConfig)

    # ----------------------------------------------------------------------
    def test_get_configuration_properties(self):
        """tests getting the configuration class"""
        config = self.gis.admin.security.configuration
        isinstance(config, KubeSecurityConfig)
        assert config.properties
        assert isinstance(config.properties, InsensitiveDict)

    # ----------------------------------------------------------------------
    def test_get_set_configuration_settings(self):
        """tests get/set the configuration settings"""
        config = self.gis.admin.security.configuration
        isinstance(config, KubeSecurityConfig)
        assert config.settings
        assert isinstance(config.settings, dict)
        # config.settings = config.settings

    def test_configuration_test_method(self):
        config_value = {"type": "BUILTIN", "properties": {}}
        config = self.gis.admin.security.configuration
        isinstance(config, KubeSecurityConfig)
        res = config.test(config_value, config_value)
        assert res

    @unittest.skip("Skip until get back to our own k8s environment")
    def test_configuration_update_store(self):
        config_value = {"type": "BUILTIN", "properties": {}}
        config = self.gis.admin.security.configuration
        isinstance(config, KubeSecurityConfig)
        res = config.update_stores(config_value, config_value)
        assert res

    def test_security_ingress(self):
        """tests the ingress operations"""

        ingress = self.gis.admin.security.ingress
        assert isinstance(ingress, KubeSecurityIngress)
        assert ingress.settings

    def test_security_saml(self):
        """tests the saml"""

        ingress = self.gis.admin.security.saml
        assert isinstance(ingress, KubeSecuritySAML)
        assert ingress.settings


if __name__ == "__main__":
    unittest.main()
