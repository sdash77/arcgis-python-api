import unittest
from unittest.mock import MagicMock, patch
from arcgis.gis import GIS
from src.arcgis.gis.nb._dataaccess import NotebookDataAccess

class TestNotebookDataAccessUpload(unittest.TestCase):
    def setUp(self):
        # Mock GIS object and its dependencies
        self.mock_gis = MagicMock(spec=GIS)
        self.mock_gis._is_arcgisonline = False
        self.mock_gis.users.me.username = 'testuser'
        self.mock_gis._con.token = 'fake-token'
        self.mock_gis._con.get.return_value = {'Blobs': []}
        self.mock_gis.session.get.return_value.json.return_value = {'Containers': [{'Name': 'testuser'}]}
        self.mock_gis._con.post.return_value = {'status': 'success'}
        self.mock_gis._con.put_raw.return_value.status_code = 200
        self.data_access = NotebookDataAccess('http://fake-url', self.mock_gis)

    @patch('src.arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('src.arcgis.gis.nb._dataaccess.os.path.isdir')
    @patch('src.arcgis.gis.nb._dataaccess.os.listdir')
    def test_upload_single_file(self, mock_listdir, mock_isdir, mock_isfile):
        mock_isfile.side_effect = lambda x: x == 'file1.txt'
        mock_isdir.return_value = False
        # Patch _upload_single_file to avoid real upload
        self.data_access._upload_single_file = MagicMock(return_value=True)
        result = self.data_access.upload('file1.txt')
        self.data_access._upload_single_file.assert_called_once_with('file1.txt', None)
        self.assertEqual(result, [True])

    @patch('src.arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('src.arcgis.gis.nb._dataaccess.os.path.isdir')
    @patch('src.arcgis.gis.nb._dataaccess.os.listdir')
    def test_upload_multiple_files(self, mock_listdir, mock_isdir, mock_isfile):
        files = ['file1.txt', 'file2.txt']
        mock_isfile.side_effect = lambda x: x in files
        mock_isdir.return_value = False
        self.data_access._upload_single_file = MagicMock(side_effect=[True, False])
        result = self.data_access.upload(files)
        self.assertEqual(result, [True, False])
        self.assertEqual(self.data_access._upload_single_file.call_count, 2)

    @patch('src.arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('src.arcgis.gis.nb._dataaccess.os.path.isdir')
    @patch('src.arcgis.gis.nb._dataaccess.os.listdir')
    def test_upload_directory(self, mock_listdir, mock_isdir, mock_isfile):
        mock_isdir.side_effect = lambda x: x == 'mydir'
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        def isfile_side_effect(path):
            return path in ['mydir/file1.txt', 'mydir/file2.txt']
        mock_isfile.side_effect = isfile_side_effect
        self.data_access._upload_single_file = MagicMock(return_value=True)
        result = self.data_access.upload('mydir')
        self.assertEqual(result, [True, True])
        self.assertEqual(self.data_access._upload_single_file.call_count, 2)
        self.data_access._upload_single_file.assert_any_call('mydir/file1.txt', None)
        self.data_access._upload_single_file.assert_any_call('mydir/file2.txt', None)

    @patch('src.arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('src.arcgis.gis.nb._dataaccess.os.path.isdir')
    def test_upload_invalid_path(self, mock_isdir, mock_isfile):
        mock_isfile.return_value = False
        mock_isdir.return_value = False
        with self.assertRaises(ValueError):
            self.data_access.upload('not_a_file')

    @patch('src.arcgis.gis.nb._dataaccess.os.path.isfile')
    def test_upload_empty_list(self, mock_isfile):
        mock_isfile.return_value = False
        with self.assertRaises(ValueError):
            self.data_access.upload([])

if __name__ == '__main__':
    unittest.main()
