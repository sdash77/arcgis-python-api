import sys

# sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import unittest
from arcgis.auth.tools import parse_url
from urllib.parse import ParseResult


class TestParseURL(unittest.TestCase):
    """tests the parse_url"""

    def test_parse_url(self):
        """tests the parse url process"""
        assert parse_url(url="https://www.arcgis.com")
        assert isinstance(parse_url(url="https://www.arcgis.com"), ParseResult)


if __name__ == "__main__":
    unittest.main()
