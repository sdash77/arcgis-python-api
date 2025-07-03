import sys
sys.path.insert(0, r"C:\svn\geosaurus_issue_13340\src")
sys.path.insert(1, r"C:\svn\geosaurus_issue_13340\tests")
import json
import os, uuid
import tempfile
import unittest
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


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
        if cls.gis._is_agol:
            notebookRuntimeVersion = "8.0"
        elif cls.gis._is_kubernetes:
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

    def test_execute_notebook(self):
        """tests the AGOL execute notebook method"""
        gis = self._gis
        from arcgis.notebook import execute_notebook

        res = execute_notebook(
            item=self._item,
            timeout=50,
            update_portal_item=True,
            parameters=None,
            save_parameters=False,
            server_index=0,
            gis=gis,
            future=False,
        )
        assert isinstance(res, dict)
        assert "jobUrl" in res

    def test_open_notebook_future(self):
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        mgr = gis.notebook_server[0]
        if gis._is_agol:
            nbm = mgr.notebooksmanager
            open_result = nbm.open_notebook(
                itemid=self._item,
                templateid=None,
                nb_runtimeid=None,
                template_nb=None,
                instance_type=None,
                future=True,
            )
        else:
            nbm = mgr.notebooks
            open_result = nbm.open_notebook(
                itemid=self._item.id,
                future=True,
            )
        assert isinstance(open_result, Job)
        assert open_result.result()

    def test_open_notebook(self):

        gis = self._gis
        mgr = gis.notebook_server[0]
        if gis._is_agol:
            nbm = mgr.notebooksmanager
            open_result = nbm.open_notebook(
                itemid=self._item,
                templateid=None,
                nb_runtimeid=None,
                template_nb=None,
                instance_type=None,
                future=False,
            )
        else:
            nbm = mgr.notebooks
            open_result = nbm.open_notebook(
                itemid=self._item.id,
                future=False,
            )

        assert open_result

    def test_execute_notebook_future(self):
        """tests the AGOL execute notebook method"""
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        from arcgis.notebook import execute_notebook

        res = execute_notebook(
            item=self._item,
            timeout=50,
            update_portal_item=True,
            parameters=None,
            save_parameters=False,
            server_index=0,
            gis=gis,
            future=True,
        )
        assert isinstance(res, Job)
        assert res.result()


if __name__ == "__main__":
    unittest.main()
