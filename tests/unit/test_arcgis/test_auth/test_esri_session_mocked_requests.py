import json
import unittest
from unittest.mock import patch

try:
    import requests_mock

    SKIPME = False
except ImportError:
    SKIPME = True
from arcgis.auth import EsriSession

mock_resp = json.dumps({"version": "8.3"})
mock_url = "https://www.arcgis.com/sharing/rest?f=json"


@unittest.skipIf(SKIPME, "requests_mock not found.")
class TestEsriSessionMockedRequests(unittest.TestCase):
    """
    Tests the EsriSession HTTP Methods
    """

    def test_get(self):
        """tests the get method"""
        with requests_mock.Mocker() as m:
            m.get(mock_url, text=mock_resp)
            assert EsriSession().get(mock_url).text == mock_resp
            assert (
                EsriSession().get(mock_url, allow_redirects=True).text
                == mock_resp
            )

    def test_post(self):
        """tests the post method"""
        with requests_mock.Mocker() as m:
            m.post(mock_url, text=mock_resp)
            assert (
                EsriSession().post(mock_url, allow_redirects=True).text
                == mock_resp
            )

    def test_put(self):
        """tests the put method"""
        with requests_mock.Mocker() as m:
            m.put(mock_url, text=mock_resp)
            assert EsriSession().put(mock_url).text == mock_resp

    def test_options(self):
        """tests the options method"""
        with requests_mock.Mocker() as m:
            m.options(mock_url, text=mock_resp)
            assert EsriSession().options(mock_url).text == mock_resp

    def test_head(self):
        """tests the Head method"""
        with requests_mock.Mocker() as m:
            m.head(mock_url, text=mock_resp)
            assert EsriSession().head(mock_url).text == mock_resp

    def test_patch(self):
        """tests the patch method"""
        with requests_mock.Mocker() as m:
            m.patch(mock_url, text=mock_resp)
            assert EsriSession().patch(mock_url).text == mock_resp

    def test_delete(self):
        """tests the delete method"""
        with requests_mock.Mocker() as m:
            m.delete(mock_url, text=mock_resp)
            assert EsriSession().delete(mock_url).text == mock_resp


@unittest.skipIf(SKIPME, "requests_mock not found.")
class TestEsriSessionClass(unittest.TestCase):
    """
    Tests the options on the EsriSession class
    """

    def test_defaults_esri_sesion(self):
        """Simple request off of EsriSession"""
        with requests_mock.Mocker() as m:
            m.get(mock_url, text=mock_resp)
            es = EsriSession()
            assert es.get(url=mock_url)

    def test_verify_cert_false(self):
        """tests that the verify_cert=False raises InsecureWarning Message"""
        with requests_mock.Mocker() as m:
            m.get(mock_url, real_http=True)
            with self.assertWarns(Warning):
                es = EsriSession(verify_cert=False)
                assert es.get(url=mock_url)

    @requests_mock.mock()
    def test_headers(self, mock_for_requests):
        """tests the headers and operations"""
        API_URL = "https://someapi.com"
        expected_headers = {
            "User-Agent": "EsriSession/0.0.1",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "FakeHeader": "PinkFloyd",
            "referer": "http",
        }
        with EsriSession(headers=expected_headers) as es:
            expected = "some_text"
            mock_for_requests.get(
                API_URL + "/someendpoint",
                headers=expected_headers,
                text=expected,
            )
            response = es.get(API_URL + "/someendpoint")
            self.assertEqual(response.headers, expected_headers)
            self.assertEqual(response.text, expected)
            self.assertEqual(es.headers, expected_headers)
            es.headers = {"crab": "carp"}
            self.assertNotEqual(es.headers, expected_headers)
            es.update_headers(values={"fish": "goat"})
            self.assertEqual(es.headers, {"crab": "carp", "fish": "goat"})

    def test_referer(self):
        """tests the referer"""
        es = EsriSession(referer="TomHanks")
        self.assertEqual(es.referer, "TomHanks")
        es.referer = "http"
        self.assertEqual(es.referer, "http")

    def test_verify_setter_triggers_adapter_rebuild(self):
        _session = EsriSession()
        with patch.object(_session, "_rebuild_adapter") as mock_rebuild:
            _session.verify = not _session.verify  # flip the value
            mock_rebuild.assert_called_once_with(verify=_session.verify)

    def test_verify_setter_no_rebuild_if_same_value(self):
        _session = EsriSession()
        with patch.object(_session, "_rebuild_adapter") as mock_rebuild:
            _session.verify = _session.verify  # set to same value
            mock_rebuild.assert_not_called()

    def test_verify_setter_raises_on_invalid_type(self):
        _session = EsriSession()
        with self.assertRaises(ValueError):
            _session.verify = "not-a-boolean"


if __name__ == "__main__":
    unittest.main()
