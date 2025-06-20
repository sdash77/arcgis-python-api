import unittest
from unittest.mock import MagicMock, patch
from arcgis.gis import GIS
from arcgis.gis.nb._dataaccess import NotebookDataAccess, NotebookFolder

class TestNotebookDataAccessUpload(unittest.TestCase):
    def setUp(self):
        # Mock GIS object and its dependencies
        self.mock_gis = MagicMock(spec=GIS)
        self.mock_gis._is_arcgisonline = False

        # Add mocks for nested attributes
        self.mock_gis._con = MagicMock()
        self.mock_gis.session = MagicMock()
        self.mock_gis.users = MagicMock()
        self.mock_gis.users.me = MagicMock()
        self.mock_gis.users.me.username = 'testuser'

        self.mock_gis._con.token = 'fake-token'
        self.mock_gis._con.get.return_value = {'Blobs': []}
        self.mock_gis.session.get.return_value.json.return_value = {'Containers': [{'Name': 'testuser'}]}
        self.mock_gis._con.post.return_value = {'status': 'success'}
        self.mock_gis._con.put_raw.return_value.status_code = 200
        self.data_access = NotebookDataAccess('http://fake-url', self.mock_gis)
        # Patch folders to return a mock Home NotebookFolder
        self.mock_home_folder = MagicMock(spec=NotebookFolder)
        self.mock_home_folder.name = 'Home'
        self.data_access.folders = [self.mock_home_folder]

    @patch('arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('arcgis.gis.nb._dataaccess.os.path.isdir')
    @patch('arcgis.gis.nb._dataaccess.os.listdir')
    def test_upload_single_file(self, mock_listdir, mock_isdir, mock_isfile):
        mock_isfile.side_effect = lambda x: x == 'file1.txt'
        mock_isdir.return_value = False
        # Patch _upload_single_file on the Home NotebookFolder
        self.mock_home_folder._upload_single_file = MagicMock(return_value=True)
        self.mock_home_folder.upload = MagicMock(side_effect=lambda f: [self.mock_home_folder._upload_single_file(f, None)])
        result = self.mock_home_folder.upload('file1.txt')
        self.mock_home_folder._upload_single_file.assert_called_once_with('file1.txt', None)
        self.assertEqual(result, [True])

    @patch('arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('arcgis.gis.nb._dataaccess.os.path.isdir')
    @patch('arcgis.gis.nb._dataaccess.os.listdir')
    def test_upload_multiple_files(self, mock_listdir, mock_isdir, mock_isfile):
        files = ['file1.txt', 'file2.txt']
        mock_isfile.side_effect = lambda x: x in files
        mock_isdir.side_effect = lambda x: False
        self.mock_home_folder._upload_single_file = MagicMock(side_effect=[True, False])
        self.mock_home_folder.upload = MagicMock(side_effect=lambda fs: [self.mock_home_folder._upload_single_file(f, None) for f in fs])
        result = self.mock_home_folder.upload(files)
        self.assertEqual(result, [True, False])
        self.assertEqual(self.mock_home_folder._upload_single_file.call_count, 2)

    @patch('arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('arcgis.gis.nb._dataaccess.os.path.isdir')
    @patch('arcgis.gis.nb._dataaccess.os.listdir')
    def test_upload_directory(self, mock_listdir, mock_isdir, mock_isfile):
        mock_isdir.side_effect = lambda x: x == 'mydir'
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        def isfile_side_effect(path):
            return path in ['mydir/file1.txt', 'mydir/file2.txt']
        mock_isfile.side_effect = isfile_side_effect
        self.mock_home_folder._upload_single_file = MagicMock(return_value=True)
        self.mock_home_folder.upload = MagicMock(side_effect=lambda d: [self.mock_home_folder._upload_single_file(f'mydir/{f}', None) for f in mock_listdir.return_value])
        result = self.mock_home_folder.upload('mydir')
        self.assertEqual(result, [True, True])
        self.assertEqual(self.mock_home_folder._upload_single_file.call_count, 2)
        self.mock_home_folder._upload_single_file.assert_any_call('mydir/file1.txt', None)
        self.mock_home_folder._upload_single_file.assert_any_call('mydir/file2.txt', None)

    @patch('arcgis.gis.nb._dataaccess.os.path.isfile')
    @patch('arcgis.gis.nb._dataaccess.os.path.isdir')
    def test_upload_invalid_path(self, mock_isdir, mock_isfile):
        mock_isfile.return_value = False
        mock_isdir.return_value = False
        self.mock_home_folder.upload = MagicMock(side_effect=ValueError('No valid files found to upload. Please provide a valid file path or directory.'))
        with self.assertRaises(ValueError):
            self.mock_home_folder.upload('not_a_file')

    @patch('arcgis.gis.nb._dataaccess.os.path.isfile')
    def test_upload_empty_list(self, mock_isfile):
        mock_isfile.return_value = False
        self.mock_home_folder.upload = MagicMock(side_effect=ValueError('No valid files found to upload. Please provide a valid file path or directory.'))
        with self.assertRaises(ValueError):
            self.mock_home_folder.upload([])

if __name__ == '__main__':
    unittest.main()
