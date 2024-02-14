import unittest
from unittest import mock

mock_data = {
    "http": "http://host:123",
    "https": "https://host:456",
    "ftp": "http://host:789",
}
from arcgis.auth.tools._util import merge_proxies, detect_proxy
from arcgis.auth.tools._util import assemble_url, parse_url


class TestUtilityFunctions(unittest.TestCase):
    def test_assemble_url_proxy(self):
        fake_url = "https://www.amazing_sites.com:65535/foo/bar"
        parsed = parse_url(fake_url)
        assert (
            assemble_url(parsed) == "https://www.amazing_sites.com:65535/foo"
        )

    def test_assemble_url(self):
        fake_url = "https://www.amazing_sites.com/foo/bar/toast/chicken/hotdog23?f=json"
        parsed = parse_url(fake_url)
        assert assemble_url(parsed) == "https://www.amazing_sites.com/foo"


class TestProxyDetection(unittest.TestCase):
    """
    Tests the merge_proxies and detect_proxy method
    """

    def test_detect_proxy(self):
        """tests the default detect proxy method"""
        with mock.patch("urllib.request.getproxies", return_value=mock_data):
            assert detect_proxy()
            assert detect_proxy(False)
            assert detect_proxy(True)["https"].find("https") == -1

    def test_merge_proxy(self):
        """tests the merge proxy setup"""
        with mock.patch("urllib.request.getproxies", return_value=mock_data):
            assert merge_proxies() is None
            assert merge_proxies(detect=True) == mock_data
            assert (
                merge_proxies(
                    proxy_host="proxy_host", proxy_port="8888", detect=True
                )
                == mock_data
            )
            assert merge_proxies(
                proxy_host="proxy_host", proxy_port="8888", detect=False
            ) == {
                "http": "http://proxy_host:8888",
                "https": "https://proxy_host:8888",
            }

            assert merge_proxies(
                proxy_dict={"http": "127.0.0.1:8787"},
                proxy_host="proxy_host",
                proxy_port="8888",
                detect=True,
            ) == {
                "http": "127.0.0.1:8787",
                "https": "http://host:456",
                "ftp": "http://host:789",
            }
            assert merge_proxies(
                proxy_dict={"http": "127.0.0.1:8787"},
                detect=True,
            ) == {
                "http": "127.0.0.1:8787",
                "https": "http://host:456",
                "ftp": "http://host:789",
            }


if __name__ == "__main__":
    unittest.main()
