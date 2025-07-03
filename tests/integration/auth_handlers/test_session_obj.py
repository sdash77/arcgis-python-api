import json
import unittest
from arcgis.auth import EsriSession, EsriWindowsAuth
from requests_toolbelt.adapters.host_header_ssl import HostHeaderSSLAdapter

from utils.decorators import integration_test


@integration_test
class TestBasicEsriSession(unittest.TestCase):
    """tests some basic properties"""

    def test_es_mounted(self):
        es = EsriSession(check_hostname=False)

    def test_es_referer(self):
        es = EsriSession(referer="")
        assert es.referer == ""

    def test_es_referer_null(self):
        es = EsriSession(referer=None)
        assert es.referer == ""

    def test_es_close(self):
        es = EsriSession(referer=None)
        es.close()

    def test_es_close(self):
        es = EsriSession()
        assert es.update_headers("fish") == False

    def test_es_no_referer(self):
        es = EsriSession()
        es._session.headers.pop("referer", None)
        assert es.referer in [False, None]

    def test_es_verify_cert(self):
        es = EsriSession()
        assert isinstance(es.verify, bool)

    def test_mount(self):
        es = EsriSession()
        es.mount("https://", HostHeaderSSLAdapter())

    def test_adapters(self):
        es = EsriSession()
        es.mount("https://", HostHeaderSSLAdapter())
        assert es.adapters

    def test_auth_basic(self):
        es = EsriSession()
        es.auth = ("apple", "sharing")
        assert es.auth

    def test_stream(self):
        es = EsriSession(stream=True)
        assert es.stream == True
        es.stream = False
        assert es.stream == False
        es.stream = "foo"
        assert es.stream == False
        del es


if __name__ == "__main__":
    unittest.main()
