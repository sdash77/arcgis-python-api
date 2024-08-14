import unittest
import uuid
import arcgis.gis._impl._util as gis_utils

class TestGisUtils(unittest.TestCase):
    def test_is_valid_item_id_100_valid_uuid_hex(self):
        """Tests the is_valid_item_id method with 100 valid uuid hexes"""
        uuid_hexes = [uuid.uuid4().hex for _ in range(100)]
        assert all(gis_utils.is_valid_item_id(uuid_hex) for uuid_hex in uuid_hexes)
    
    def test_is_valid_item_id_100_invalid_uuid_hex(self):
        """Tests the is_valid_item_id method with 10 invalid uuid hexes"""
        invalid_uuid_hexes = [uuid.uuid4().hex[:-5] for _ in range(10)]
        assert all(not gis_utils.is_valid_item_id(invalid_uuid_hex) for invalid_uuid_hex in invalid_uuid_hexes)

if __name__ == "__main__":
    unittest.main()