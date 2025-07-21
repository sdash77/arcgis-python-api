import unittest
from arcgis.gis import ItemProperties, ItemTypeEnum

class TestItemProperties(unittest.TestCase):
    def test_to_dict_properties_str(self):
        ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP,
            title="ItemPropertiesWebMap",
            properties='super awesome',
            tags="test, item, integration test"
        )
        ip_dict = ip.to_dict()
        assert ip_dict
        assert isinstance(ip_dict.get('properties'), str)
        assert ip.tags == "test, item, integration test"

    def test_to_dict_properties_dict(self):
        ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP,
            title="ItemPropertiesWebMap",
            properties={
                'abc': 1234,
            },
        )
        ip_dict = ip.to_dict()
        assert ip_dict
        assert isinstance(ip_dict.get('properties'), str)

if __name__ == '__main__':
    unittest.main()
