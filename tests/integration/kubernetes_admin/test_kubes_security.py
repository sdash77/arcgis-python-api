import sys
sys.path.insert(0, r"C:\SVN\geosaurus_master_kubernetes_issue_security\src")
import unittest
from arcgis.gis import GIS
from arcgis.gis.kubernetes._admin._security import KubeSecurity, KubeSecurityConfig, KubeSecurityIngress, KubeSecuritySAML
from arcgis._impl.common._isd import InsensitiveDict
PROFILES = ['your_kubernetes_profile']

#gis = GIS(url='https://dev0014889.esri.com/gis', username='siteadmin', password='esri.agp1', profile='your_kubernetes_profile', verify_cert=False, trust_env=True)
#del gis

class TestSecutiryKubernetes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._gis = [GIS(profile=profile, verify_cert=False, trust_env=True) for profile in PROFILES]
    #----------------------------------------------------------------------
    def test_get_security(self):
        """tests to see if `KubeSecurity` is returned"""
        for gis in self._gis:
            self.assertIsInstance(gis.admin.security, KubeSecurity)
    #----------------------------------------------------------------------
    def test_get_properties(self):
        """tests to see if `KubeSecurity` properties returns a value"""
        for gis in self._gis:
            self.assertIsInstance(gis.admin.security, KubeSecurity)
            sec = gis.admin.security
            isinstance(sec, KubeSecurity)
            assert isinstance(sec.properties, InsensitiveDict)
            sec._refresh()
    #----------------------------------------------------------------------
    def test_url_property(self):
        """tests getting the URL propert on the security object"""
        for gis in self._gis:
            self.assertIsInstance(gis.admin.security, KubeSecurity)
            sec = gis.admin.security
            assert sec.url
    #----------------------------------------------------------------------
    def test_get_configuration(self):
        """tests getting the configuration class"""
        for gis in self._gis:
            self.assertIsInstance(gis.admin.security.configuration, KubeSecurityConfig)
    #----------------------------------------------------------------------
    def test_get_configuration_properties(self):
        """tests getting the configuration class"""
        for gis in self._gis:
            config = gis.admin.security.configuration
            isinstance(config, KubeSecurityConfig)
            assert config.properties
            assert isinstance(config.properties, InsensitiveDict)
    #----------------------------------------------------------------------
    def test_get_set_configuration_settings(self):
        """tests get/set the configuration settings"""
        for gis in self._gis:
            config = gis.admin.security.configuration
            isinstance(config, KubeSecurityConfig)
            assert config.settings
            assert isinstance(config.settings, dict)
            #config.settings = config.settings
    def test_configuration_test_method(self):
        config_value = {
          "type": "BUILTIN",
          "properties": {}
        }
        for gis in self._gis:
            config = gis.admin.security.configuration
            isinstance(config, KubeSecurityConfig)
            res = config.test(config_value, config_value)
            assert res
    def test_configuration_update_store(self):
        config_value = {
          "type": "BUILTIN",
          "properties": {}
        }
        for gis in self._gis:
            config = gis.admin.security.configuration
            isinstance(config, KubeSecurityConfig)
            res = config.update_stores(config_value, config_value)
            assert res
    def test_security_ingress(self):
        """tests the ingress operations"""

        for gis in self._gis:
            ingress = gis.admin.security.ingress
            assert isinstance(ingress, KubeSecurityIngress)
            assert ingress.settings
    def test_security_saml(self):
        """tests the saml"""

        for gis in self._gis:
            ingress = gis.admin.security.saml
            assert isinstance(ingress, KubeSecuritySAML)
            assert ingress.settings



if __name__ == "__main__":
    unittest.main()