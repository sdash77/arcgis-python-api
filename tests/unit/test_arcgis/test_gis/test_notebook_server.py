import unittest
from unittest.mock import patch, PropertyMock, MagicMock

from arcgis.gis import GIS

class TestGISNotebookServer(unittest.TestCase):
    def setUp(self):
        # Patch AGOLNotebookManager and NotebookServer globally for all tests
        patcher1 = patch("arcgis.gis.agonb.AGOLNotebookManager")
        patcher2 = patch("arcgis.gis.nb.NotebookServer")
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.mock_agol_manager = patcher1.start()
        self.mock_nb_server = patcher2.start()

    def make_gis(self):
        gis = GIS.__new__(GIS)
        gis._portal = MagicMock()
        gis._registered_servers = MagicMock()
        return gis

    def test_arcgisonline_with_notebook_url(self):
        gis = self.make_gis()
        gis._portal.is_arcgisonline = True
        gis._registered_servers.return_value = {
            "urls": {
                "notebooks": {
                    "https": ["notebook.example.com"]
                }
            }
        }
        mock_mgr = MagicMock()
        self.mock_agol_manager.return_value = mock_mgr

        result = gis.notebook_server
        self.mock_agol_manager.assert_called_once_with(url="https://notebook.example.com/admin", gis=gis)
        self.assertEqual(result, [mock_mgr])

    def test_arcgisenterprise_with_notebook_servers(self):
        gis = self.make_gis()
        gis._portal.is_arcgisonline = False
        gis.admin = True
        with patch.object(GIS, 'servers', new_callable=PropertyMock) as mock_servers, \
             patch.object(GIS, '_is_kubernetes', new_callable=PropertyMock) as mock_is_k8s, \
             patch.object(GIS, '_use_private_url_only', new_callable=PropertyMock) as mock_private_url:
            mock_servers.return_value = {
                "servers": [
                    {
                        "serverFunction": "NotebookServer",
                        "adminUrl": "https://ent.example.com/nb"
                    }
                ]
            }
            mock_is_k8s.return_value = False
            mock_private_url.return_value = False

            mock_nb = MagicMock()
            self.mock_nb_server.return_value = mock_nb
            mock_nb.properties = {}

            result = gis.notebook_server
            self.mock_nb_server.assert_called_once_with("https://ent.example.com/nb/admin", gis)
            self.assertEqual(result, [mock_nb])

    def test_no_notebook_server(self):
        gis = self.make_gis()
        gis._portal.is_arcgisonline = True
        gis._registered_servers.return_value = {}
        result = gis.notebook_server
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()