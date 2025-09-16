import sys
import json
import os, uuid
import tempfile
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.agonb import snapshot as _agosnapshot
from arcgis.gis.nb import _snapshot as _entsnapshot
from arcgis.notebook import list_snapshots, create_snapshot
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from arcgis.gis.kubernetes._admin.notebooks._snapshot import  KubeSnapshot
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()

notebook_json = {'metadata': {'kernelspec': {'name': 'python3',
                             'display_name': 'Python 3 (ipykernel)',
                             'language': 'python'},
              'language_info': {'name': 'python',
                                'version': '3.11.11',
                                'mimetype': 'text/x-python',
                                'codemirror_mode': {'name': 'ipython',
                                                    'version': 3},
                                'pygments_lexer': 'ipython3',
                                'nbconvert_exporter': 'python',
                                'file_extension': '.py'}},
 'nbformat_minor': 4,
 'nbformat': 4,
 'cells': [{'cell_type': 'markdown',
            'source': '## Welcome to your notebook.\n',
            'metadata': {}},
           {'cell_type': 'markdown',
            'source': '#### Run this cell to connect to your GIS and get '
                      'started:',
            'metadata': {}},
           {'cell_type': 'code',
            'source': "print('hello world')",
            'metadata': {'trusted': False},
            'outputs': [],
            'execution_count': None},
           {'cell_type': 'markdown',
            'source': '#### Now you are ready to start!',
            'metadata': {}},
           {'cell_type': 'code',
            'source': '',
            'metadata': {'trusted': False},
            'outputs': [],
            'execution_count': None}]}


@integration_test
@profiles.admin_devent
class TestAGOLNotebookManager(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        assert cls._item.delete()

    @classmethod
    def setUpClass(cls):
        cls._gis = cls.gis
        d = tempfile.gettempdir()
        fp = os.path.join(d, f"test_nbs{uuid.uuid4().hex[:4]}.ipynb")
        writer = open(fp, "w")
        writer.write(json.dumps(notebook_json))
        writer.close()
        if cls._gis._is_agol:
            notebookRuntimeVersion = "8.0"
        elif cls._gis._is_kubernetes:
            notebookRuntimeVersion = "13.0"
        else:
            notebookRuntimeVersion = "9.0"

        cls._item = cls._gis.content.add(
            {
                "type": "Notebook",
                "tags": "delete me",
                "extension" : "ipynb",
                "title": f"item_{uuid.uuid4().hex[:6]}",
                "properties": {
                    "notebookRuntimeName": "ArcGIS Notebook Python 3 Standard",
                    "notebookRuntimeVersion": notebookRuntimeVersion,
                },
            },
            data=fp,
        )

    def test_snapshots(self):
        """tests the AGO snapshot function"""
        res = create_snapshot(self._item, name="abcd2")
        assert res
        if self.gis._is_agol:
            assert isinstance(res, _agosnapshot.SnapShot)
        elif self.gis._is_kubernetes:
            assert isinstance(res, KubeSnapshot)
        else:
            assert isinstance(res, _entsnapshot.SnapShot)

    def test_list_snapshots(self):
        """tests the list_snapshots method"""
        res = create_snapshot(self._item, name="abcd2")
        assert len(self._item.snapshots) == len(list_snapshots(self._item))


if __name__ == "__main__":
    unittest.main()
