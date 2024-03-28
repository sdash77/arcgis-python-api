import sys

sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
sys.path.insert(1, r"C:\SVN\geosaurus_master\tests")
import os
import unittest
from arcgis.gis import GIS
from utils import INTEGRATION_TESTS_DIR
from pathlib import Path
from utils.decorators import integration_test


try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser
PKI_URLS = {}
IWA_URLS = {}
if "pki" in get_config_parser():
    PKI_URLS['pki'] = dict(get_config_parser()['pki'])
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

if "java_pki" in get_config_parser():
    PKI_URLS['java_pki'] = dict(get_config_parser()['java_pki'])
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."
if "linux_pki" in get_config_parser():
    PKI_URLS['linux_pki'] = dict(get_config_parser()['linux_pki'])
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

if "iwa" in get_config_parser():
    IWA_URLS['iwa'] = dict(get_config_parser()['iwa'])
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

if "multiiwa" in get_config_parser():
    IWA_URLS['multiiwa'] = dict(get_config_parser()['multiiwa'])
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

try:
    fp = os.path.join(INTEGRATION_TESTS_DIR, "gis", "dataset_test_123a.zip")
except:
    fp = Path(Path.cwd(), "integration", "gis", "dataset_test_123a.zip")
"""


try:
    PKI_ESRI_CERT = os.path.join(
        INTEGRATION_TESTS_DIR, "gis", "gisproadv1.pfx"
    )
except:
    PKI_ESRI_CERT = Path(Path.cwd(), "integration", "gis", "gisproadv1.pfx")

try:
    PKI_ORACLE_CERT = os.path.join(
        INTEGRATION_TESTS_DIR, "gis", "EsriJDeveloper.pfx"
    )
except:
    PKI_ORACLE_CERT = Path(
        Path.cwd(), "integration", "gis", "EsriJDeveloper.pfx"
    )

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
IWA_DUEL_ESRI = "https://rqawintest99pt.ags.esri.com/gis"

"""


#########################################################################################
@integration_test
class TestIWAConnections(unittest.TestCase):
    """Tests IWA access to portal/server"""

    #########################################################################################
    def test_iwa_login(self):
        url = IWA_URLS['iwa']['url']
        gis = GIS(url=url, verify_cert=False)
        assert gis.users.me

    #########################################################################################
    def test_duel_iwa_login(self):
        url = IWA_URLS['multiiwa']['url']
        gis = GIS(url=url, verify_cert=False)
        assert gis.users.me

    #########################################################################################
    def test_iwa_geocoding(self):
        """tests using geocoding with PKI"""
        from arcgis.geocoding import get_geocoders

        url = IWA_URLS['iwa']['url']
        gis = GIS(url=url, verify_cert=False)
        geocoders = get_geocoders(gis)
        if len(geocoders) > 0:
            assert geocoders[0]._geocode(
                address="12 york street, camden, NJ"
            )
        del gis

    #########################################################################################
    def test_iwa_publish_server(self):
        """tests accessing a service via IWA"""
        url = IWA_URLS['iwa']['url']
        gis = GIS(url=url, verify_cert=False)
        assert gis.users.me
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = gis.content.add(
            {
                "title": "amazing_test_data_109",
                "type": "File Geodatabase",
                "tags": "erase me",
            },
            data=fp,
        )
        pitem = item.publish()
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()

    #########################################################################################
    def test_duel_iwa_publish_server(self):
        """tests accessing a service via IWA"""
        url = IWA_URLS['multiiwa']['url']
        gis = GIS(url=url, verify_cert=False)
        assert gis.users.me
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = gis.content.add(
            {
                "title": "amazing_test_data_109",
                "type": "File Geodatabase",
                "tags": "erase me",
            },
            data=fp,
        )

        pitem = item.publish()
        assert pitem
        pitem.delete()
        item.delete()

        del gis


#########################################################################################
@integration_test
class TestPKIConnections(unittest.TestCase):
    #########################################################################################
    def test_pki_login(self):
        url = PKI_URLS['pki']['url']
        cert = PKI_URLS['pki']['cert']
        password = PKI_URLS['pki']['password']
        gis = GIS(
            url=url,
            cert_file=cert,
            password=password,
            verify_cert=False,
        )
        assert gis.users.me.username
        del gis

    def test_pki_login_java(self):
        url = PKI_URLS['java_pki']['url']
        cert = PKI_URLS['java_pki']['cert']
        password = PKI_URLS['java_pki']['password']
        gis = GIS(
            url=url,
            cert_file=cert,
            password=password,
            verify_cert=False,
        )
        assert gis.users.me.username
        del gis

    #########################################################################################
    def test_pki_access_server_WIN(self):
        """tests publishing then accessing the layers"""
        url = PKI_URLS['pki']['url']
        cert = PKI_URLS['pki']['cert']
        password = PKI_URLS['pki']['password']
        gis = GIS(
            url=url,
            cert_file=cert,
            password=password,
            verify_cert=False,
        )
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass

        item = gis.content.add(
            {
                "title": "amazing_test_data_109",
                "type": "File Geodatabase",
                "tags": "erase me",
            },
            data=fp,
        )
        pitem = item.publish()
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()

        del gis

    #########################################################################################
    def test_pki_access_server_JAVA(self):
        """tests publishing then accessing the layers"""
        url = PKI_URLS['java_pki']['url']
        cert = PKI_URLS['java_pki']['cert']
        password = PKI_URLS['java_pki']['password']
        gis = GIS(
            url=url,
            cert_file=cert,
            password=password,
            verify_cert=False,
        )
        for i in gis.content.search("amazing_test_data_109"):
            try:
                i.delete()
            except:
                pass
        item = gis.content.add(
            {
                "title": "amazing_test_data_109",
                "type": "File Geodatabase",
                "tags": "erase me",
            },
            data=fp,
        )
        pitem = item.publish()
        assert pitem.layers[0].properties
        pitem.delete()
        item.delete()
        del gis

    #########################################################################################
    def test_pki_geocoding(self):
        """tests using geocoding with PKI"""
        from arcgis.geocoding import get_geocoders

        url = PKI_URLS['java_pki']['url']
        cert = PKI_URLS['java_pki']['cert']
        password = PKI_URLS['java_pki']['password']
        gis = GIS(
            url=url,
            cert_file=cert,
            password=password,
            verify_cert=False,
        )
        geocoders = get_geocoders(gis)
        if len(geocoders) > 0:
            assert geocoders[0]._geocode(
                address="12 york street, camden, NJ"
            )
        del gis


if __name__ == "__main__":
    unittest.main()
