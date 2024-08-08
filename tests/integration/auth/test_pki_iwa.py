import os
import unittest
from arcgis.gis import GIS
from utils import INTEGRATION_TESTS_DIR
from pathlib import Path
from utils.decorators import credentials, integration_test
import requests

try:
    fp = os.path.join(INTEGRATION_TESTS_DIR, "auth", "dataset_test_123a.zip")
except:
    fp = Path(Path.cwd(), "integration", "auth", "dataset_test_123a.zip")


@integration_test
@credentials.enterprise_all_iwa
class TestIWAConnections(unittest.TestCase):
    """Tests IWA access to portal/server"""
    def setUp(self):
        try:
            self.gis = GIS(url=self.portal_url, verify_cert=False)
        except requests.exceptions.RequestException:
            # TODO: failure is not very descriptive
            # requests.exceptions.RequestException: A general exception was raised: Expecting value: line 1 column 1 (char 0)
            # consider raising an invalid credentials exception with a more descriptive message
            print("Failed to connect to IWA GIS using integration method, attempting to pass credentials")
            self.gis = GIS(url=self.portal_url, verify_cert=False, username=self.username, password=self.password)

    def test_login(self):
        assert self.gis
        assert self.gis.users.me

    def test_geocoding(self):
        """tests geocoding with IWA"""
        from arcgis.geocoding import get_geocoders

        assert self.gis
        geocoders = get_geocoders(self.gis)
        if len(geocoders) == 0:
            self.skipTest("No geocoders available")
        assert geocoders[0]._geocode(
            address="12 york street, camden, NJ"
        )

    def test_publish_fgdb(self):
        """tests publishing an item via IWA"""
        assert self.gis
        assert self.gis.users.me
        for i in self.gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = self.gis.content.add(
            {
                "title": "amazing_test_data_109",
                "type": "File Geodatabase",
                "tags": "erase me",
            },
            data=fp,
        )
        pitem = item.publish()
        assert pitem
        assert pitem.layers
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()


@integration_test
@credentials.enterprise_all_pki
class TestPKIConnections(unittest.TestCase):
    """Tests PKI access to portal/server"""
    def setUp(self):
        self.gis = GIS(
            url=self.portal_url,
            cert_file=self.cert,
            password=self.password,
            verify_cert=False,
        )

    def test_login(self):
        assert self.gis
        assert self.gis.users.me

    def test_publish_fgdb(self):
        """tests publishing an item via PKI"""
        assert self.gis
        assert self.gis.users.me

        for i in self.gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = self.gis.content.add(
            {
                "title": "amazing_test_data_109",
                "type": "File Geodatabase",
                "tags": "erase me",
            },
            data=fp,
        )
        pitem = item.publish()
        assert pitem
        assert pitem.layers
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()

    def test_geocoding(self):
        """tests using geocoding with PKI"""
        assert self.gis
        from arcgis.geocoding import get_geocoders
        geocoders = get_geocoders(self.gis)
        if len(geocoders) == 0:
            self.skipTest("No geocoders available")
        
        assert geocoders[0]._geocode(
            address="12 york street, camden, NJ"
        )


if __name__ == "__main__":
    unittest.main()
