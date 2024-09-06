import unittest
from arcgis.gis import ItemProperties, ItemTypeEnum

class TestItemProperties(unittest.TestCase):
    def test_to_dict_properties_str(self):
        ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP,
            title="ItemPropertiesWebMap",
            text=data,
            properties='super awesome',
        )
        ip_dict = ip.to_dict()
        assert ip_dict
        assert isinstance(ip_dict.get('properties'), str)

    def test_properties_dict(self):
        ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP,
            title="ItemPropertiesWebMap",
            text=data,
            properties={
                'abc': 1234,
            },
        )
        assert isinstance(ip.to_dict()['properties'], str)

if __name__ == '__main__':
    unittest.main()
