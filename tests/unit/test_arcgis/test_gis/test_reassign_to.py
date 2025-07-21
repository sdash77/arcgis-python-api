import unittest
from unittest.mock import MagicMock, patch

class TestUserReassignTo(unittest.TestCase):
    def setUp(self):
        # Create a mock GIS and User object
        self.mock_gis = MagicMock()
        self.mock_user = MagicMock()
        self.mock_user._gis = self.mock_gis
        self.mock_user.username = "source_user"
        self.mock_user.items = MagicMock(return_value=[])
        self.mock_user.groups = []
        self.mock_user._check_existance = MagicMock(return_value=True)

    @patch("requests.Response")
    def test_reassign_to_success(self, mock_response):
        # Mock REST API response for success
        self.mock_gis.url = "http://example.com"
        self.mock_gis.session.post.return_value = mock_response
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = MagicMock()

        result = self.mock_user.reassign_to("target_user")
        self.assertTrue(result)
        self.mock_user._check_existance.assert_called_with(username="target_user")

    @patch("requests.Response")
    def test_reassign_to_user_does_not_exist(self, mock_response):
        self.mock_user._check_existance.return_value = False
        with self.assertRaises(ValueError):
            self.mock_user.reassign_to("nonexistent_user")

    @patch("requests.Response")
    def test_reassign_to_api_error(self, mock_response):
        self.mock_gis.url = "http://example.com"
        self.mock_gis.session.post.return_value = mock_response
        mock_response.json.return_value = {"error": "API error"}
        mock_response.raise_for_status = MagicMock()
        with self.assertRaises(Exception):
            self.mock_user.reassign_to("target_user")

if __name__ == "__main__":
    unittest.main()