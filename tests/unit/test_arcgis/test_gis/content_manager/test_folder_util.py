import unittest
import io
import uuid
import arcgis.gis._impl._content_manager.folder._util as folder_util

class TestFolderUtil(unittest.TestCase):
    """Tests for gis content_manager folder utils"""

    def test_create_upload_tuple_bytes_io(self):
        """Tests the create_upload_tuple method"""
        random_bytes = uuid.uuid4().bytes
        random_filename = f"{uuid.uuid4().hex}.txt"
        upload_tuple = folder_util.create_upload_tuple(io.BytesIO(random_bytes), file_name=random_filename)
        self.assertEqual(len(upload_tuple), 3)
        self.assertEqual(upload_tuple[0], random_filename)
        self.assertEqual(upload_tuple[1].read(), random_bytes)

    def test_create_upload_tuple_string_io(self):
        """Tests the create_upload_tuple method"""
        random_string = uuid.uuid4().hex
        random_filename = f"{uuid.uuid4().hex}.txt"
        upload_tuple = folder_util.create_upload_tuple(io.StringIO(random_string), file_name=random_filename)
        self.assertEqual(len(upload_tuple), 3)
        self.assertEqual(upload_tuple[0], random_filename)
        self.assertEqual(upload_tuple[1].read(), random_string)
    
    def test_create_upload_tuple_string_io_raises_no_filename(self):
        """Tests the create_upload_tuple method"""
        with self.assertRaises(ValueError):
            random_string = uuid.uuid4().hex
            folder_util.create_upload_tuple(io.StringIO(random_string))

    def test_create_upload_tuple_raises_file_not_found(self):
        """Tests the create_upload_tuple method"""
        with self.assertRaises(ValueError):
            random_filename = f"{uuid.uuid4().hex}.txt"
            folder_util.create_upload_tuple(random_filename)
    
    def test_process_parameters_no_change(self):
        """Tests the process_parameters method"""
        parameters = {
            "a": "b",
            "c": "d",
            "e": "f"
        }
        processed_parameters = folder_util._process_parameters(parameters)
        self.assertEqual(processed_parameters, parameters)
    
    def test_process_parameters_nested_objects(self):
        """Tests the process_parameters method jsonify's nested dicts"""
        parameters = {
            "a": "b",
            "c": {
                "d": "e",
                "f": "g"
            }
        }
        processed_parameters = folder_util._process_parameters(parameters)
        self.assertEqual(processed_parameters, {
            "a": "b",
            "c": '{"d": "e", "f": "g"}',
        })

if __name__ == "__main__":
    unittest.main()