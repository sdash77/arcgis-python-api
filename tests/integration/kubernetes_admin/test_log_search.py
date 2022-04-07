import sys

sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_7656\src")
import unittest
from arcgis.gis import GIS

try:

    username = "ACadmin"
    password = "ACadmin82"
    url = "https://1091pubbi-1091pubbi.apps.openshift46release.esri.com/web"
    _gis = GIS(url=url, username=username, password=password, verify_cert=False)
    skip = False
except:
    skip = True


@unittest.skipIf(condition=skip, reason="GIS FAILED TO CONNECT")
class TestSearchKubernetesLogs(unittest.TestCase):
    """
    Tests the logs admin search function.
    """

    def test_search_result_count(self):
        isinstance(_gis, GIS)
        logs = _gis.admin.logs
        assert isinstance(
            logs.search(
                query="item",
                sort_by="bestMatch",
                sort_order="desc",
                show_stack=False,
                return_count=True,
            ),
            int,
        )

    def test_search_query(self):
        isinstance(_gis, GIS)
        logs = _gis.admin.logs
        assert isinstance(
            logs.search(
                query="item",
                sort_by="bestMatch",
                sort_order="desc",
                show_stack=False,
                return_count=False,
            ),
            list,
        )

    def test_search_show_stack(self):
        isinstance(_gis, GIS)
        logs = _gis.admin.logs
        messages = logs.search(
            query="item",
            sort_by="time",
            sort_order="asc",
            show_stack=True,
            return_count=False,
        )
        if len(messages) > 0:
            msg = messages[0]
            assert "stackTraces" in msg.keys()


if __name__ == "__main__":
    unittest.main()
