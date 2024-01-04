import unittest
from arcgis.auth.tools import parse_url
from urllib.parse import ParseResult


class TestParseUrl(unittest.TestCase):
    """tests the parse_url"""

    def test_parse_url(self):
        """tests the parse url process"""
        parsed = parse_url(url="https://www.arcgis.com")
        assert parsed
        assert isinstance(parsed, ParseResult)
        assert parsed.scheme == "https"
        assert parsed.netloc == "www.arcgis.com"
        assert not parsed.path
        assert not parsed.params
        assert not parsed.query
        assert not parsed.fragment


if __name__ == "__main__":
    unittest.main()
