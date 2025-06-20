import unittest
import os, json
import arcgis
from arcgis.gis import GIS
from arcgis.gis.nb import NotebookServer, NotebookManager
from arcgis.gis.tasks._schedule import TaskManager, Task
from arcgis.gis.tasks._schedule import Run
from utils.decorators import integration_test, profiles


json_data = '{"cells":[{"metadata":{},"cell_type":"markdown","source":"## Welcome to your notebook.\\n"},{"metadata":{},"cell_type":"markdown","source":"#### Run this cell to connect to your GIS and get started:"},{"metadata":{"trusted":false},"cell_type":"code","source":"#from arcgis.gis import GIS\\n#gis = GIS(\\"home\\")\\nprint(\'hello\')","execution_count":1,"outputs":[{"output_type":"stream","text":"hello\\n","name":"stdout"}]},{"metadata":{},"cell_type":"markdown","source":"#### Now you are ready to start!"},{"metadata":{"trusted":false},"cell_type":"code","source":"","execution_count":null,"outputs":[]}],"metadata":{"language_info":{"name":"python","version":"3.9.11","mimetype":"text/x-python","codemirror_mode":{"name":"ipython","version":3},"pygments_lexer":"ipython3","nbconvert_exporter":"python","file_extension":".py"},"kernelspec":{"name":"python3","display_name":"Python 3 (ipykernel)","language":"python"}},"nbformat":4,"nbformat_minor":2}'


@profiles.admin_enterprise
@integration_test
class TestNotebookService(unittest.TestCase):
    """
    Tests the Services Manager and Service class for notebook server
    This is 10.8.1+ Functionality Tests for Notebook Server
    """

    def test_get_services_manager(self):
        """tests that the snapshot manager is returned."""
        servers = self.gis.admin.servers.list()
        for s in servers:
            if type(s).__name__ == "NotebookServer":
                nbs = s
                mgr = nbs.services
                assert mgr
                assert mgr.properties
                assert isinstance(mgr.services, (tuple, list))
                assert isinstance(mgr.types, dict)
                break

    def test_services_add_ops(self):
        """tests the create notebook service tool"""
        mgr = None
        servers = self.gis.admin.servers.list()
        for s in servers:
            if type(s).__name__ == "NotebookServer":
                nbs = s
                mgr = nbs.services
                break
        if mgr:
            runtimes = nbs.notebooks.runtimes
            runtimes[0].properties
            nb_item = self.gis.content.add(
                item_properties={
                    "type": "Notebook",
                    "title": "nb_title",
                    "properties": {
                        "notebookRuntimeName": "ArcGIS Notebook Python 3 Standard",
                        "notebookRuntimeVersion": "9.0",
                    },
                    "text": json_data,
                }
            )
            item_tool = mgr.create(nb_item, "title", "description")
            assert item_tool
            assert mgr.services
            if len(mgr.services) > 0:
                for s in mgr.services:
                    assert s.properties
            assert nb_item.delete()
            assert item_tool.delete()


if __name__ == "__main__":
    unittest.main()
