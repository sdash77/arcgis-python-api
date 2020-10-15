import os
import sys
#sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_issue_4074\src")
import unittest
from arcgis.gis import GIS

try:
    from utils import NOTEBOOK_TESTS_DIR
    fp = os.path.join(NOTEBOOK_TESTS_DIR, "dataset_test_123a.zip")

except:
    fp = r"./dataset_test_123a.zip"

try:
    from utils import NOTEBOOK_TESTS_DIR
    PKI_ESRI_CERT = os.path.join(NOTEBOOK_TESTS_DIR, "gisproadv1.pfx")

except:
    PKI_ESRI_CERT = r"./gisproadv1.pfx"

try:
    from utils import NOTEBOOK_TESTS_DIR
    PKI_ORACLE_CERT = os.path.join(NOTEBOOK_TESTS_DIR, "EsriJDeveloper.pfx")

except:
    PKI_ORACLE_CERT = r"./EsriJDeveloper.pfx"

if os.path.isfile(PKI_ESRI_CERT) == False:
    SKIP_ORACLE = True
else:
    SKIP_ORACLE = False


PKI_JAVA = "https://rqawinjpki06pt.ags.esri.com/gis"
PKI_WIN = "https://rqawinpki03pt.ags.esri.com/gis"

PKI_ESRI_PW = "portalaccount1"


PKI_ORACLE = "https://wdcintelgx.dev.geocloud.com/portal"
PKI_ORACLE_PW = "password"

IWA_ESRI = "https://rqawiniwa02pt.ags.esri.com/gis"
IWA_DUEL_ESRI = "https://rqawinmiwa05pt.ags.esri.com/gis"
#########################################################################################
class TestIWAConnections(unittest.TestCase):
    """Tests IWA access to portal/server"""
    #########################################################################################
    def test_iwa_login(self):
        url =IWA_ESRI
        gis = GIS(url=url, verify_cert=False)
        assert gis.users.me
    #########################################################################################
    def test_duel_iwa_login(self):
        url =IWA_DUEL_ESRI
        gis = GIS(url=url, verify_cert=False)
        assert gis.users.me
    #########################################################################################
    def test_iwa_geocoding(self):
        """tests using geocoding with PKI"""
        from arcgis.geocoding import get_geocoders
        gis = GIS(url=IWA_ESRI, verify_cert=False)
        geocoders = get_geocoders(gis)
        if len(geocoders) > 0:
            assert geocoders[0]._geocode(address="12 york street, camden, NJ")
        del gis
    #########################################################################################
    def test_iwa_publish_server(self):
        """tests accessing a service via IWA"""
        gis = GIS(url=IWA_ESRI, verify_cert=False)
        assert gis.users.me
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = gis.content.add({
            "title" : "amazing_test_data_109",
            "type" : "File Geodatabase",
            "tags" : "erase me"
        },
                               data=fp)
        pitem = item.publish()
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()
    #########################################################################################
    def test_duel_iwa_publish_server(self):
        """tests accessing a service via IWA"""
        gis = GIS(url=IWA_DUEL_ESRI, verify_cert=False)
        assert gis.users.me
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = gis.content.add({
            "title" : "amazing_test_data_109",
            "type" : "File Geodatabase",
            "tags" : "erase me"
        },
                               data=fp)
        pitem = item.publish()
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()

        del gis

#########################################################################################
class TestPKIConnections(unittest.TestCase):
    #########################################################################################
    def test_pki_login(self):

        gis = GIS(url=PKI_WIN, cert_file=PKI_ESRI_CERT, password=PKI_ESRI_PW, verify_cert=False)
        assert gis.users.me.username.lower().find('gisproadv1') > -1
        del gis
        gis = GIS(url=PKI_JAVA, cert_file=PKI_ESRI_CERT, password=PKI_ESRI_PW, verify_cert=False)
        assert gis.users.me.username.lower().find('gisproadv1') > -1
        del gis
    #########################################################################################
    @unittest.skipIf(SKIP_ORACLE, "MISSING CERTIFICATE")
    def test_oracle_webgate(self):
        """tests oracle's webgate pki like login"""
        try:

            gis = GIS(url=PKI_ORACLE, cert_file=PKI_ORACLE_CERT, password=PKI_ORACLE_PW, verify_cert=False)
            assert gis.users.me.username.lower().find('esrideveloper01') > -1
            #########################################################################################
            for i in gis.content.search("amazing_test_data_109"):
                try:
                    i.delete()
                except:
                    pass
            #########################################################################################
            item = gis.content.add({
                "title" : "amazing_test_data_109",
                "type" : "File Geodatabase",
                "tags" : "erase me"
            },
                                   data=fp)
            pitem = item.publish()
            assert pitem.layers[0].properties
            pitem.delete()
            item.delete()

            del gis
        except:
            pass
    #########################################################################################
    def test_pki_access_server_WIN(self):
        """tests publishing then accessing the layers"""
        gis = GIS(url=PKI_WIN, cert_file=PKI_ESRI_CERT, password=PKI_ESRI_PW, verify_cert=False)
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = gis.content.add({
            "title" : "amazing_test_data_109",
            "type" : "File Geodatabase",
            "tags" : "erase me"
        },
                               data=fp)
        pitem = item.publish()
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()

        del gis

    #########################################################################################
    def test_pki_access_server_JAVA(self):
        """tests publishing then accessing the layers"""
        gis = GIS(url=PKI_JAVA, cert_file=PKI_ESRI_CERT, password=PKI_ESRI_PW, verify_cert=False)
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass
        item = gis.content.add({
            "title" : "amazing_test_data_109",
            "type" : "File Geodatabase",
            "tags" : "erase me"
        },
                               data=fp)
        pitem = item.publish()
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()
        del gis
    #########################################################################################
    def test_pki_geocoding(self):
        """tests using geocoding with PKI"""
        from arcgis.geocoding import get_geocoders
        gis = GIS(url=PKI_JAVA, cert_file=PKI_ESRI_CERT, password=PKI_ESRI_PW, verify_cert=False)
        geocoders = get_geocoders(gis)
        if len(geocoders) > 0:
            assert geocoders[0]._geocode(address="12 york street, camden, NJ")
        del gis

if __name__ == "__main__":
    unittest.main()
