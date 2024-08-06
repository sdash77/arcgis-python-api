import unittest
from utils.decorators import integration_test, profiles


@profiles.admin_k8s
@integration_test
class TestSearchKubernetesLogs(unittest.TestCase):
    """
    Tests the logs admin search function.
    """

    def test_search_result_count(self):
        logs = self.gis.admin.logs
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
        logs = self.gis.admin.logs
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
        logs = self.gis.admin.logs
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
