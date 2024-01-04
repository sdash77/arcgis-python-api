import unittest
from arcgis.auth.tools import parse_url
from urllib.parse import ParseResult


class TestParseURL(unittest.TestCase):
    """tests the parse_url"""

    def test_parse_url(self):
        """tests the parse url process"""
        parsed = parse_url(url="https://www.arcgis.com")
        assert parsed
        assert isinstance(
            parsed, ParseResult
        )


if __name__ == "__main__":
    unittest.main()
