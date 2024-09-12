import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, ContentManager, Item
from arcgis.gis import ItemProperties, ItemTypeEnum
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

data = {
    'operationalLayers': [],
    'baseMap': {
        'baseMapLayers': [
            {
                'id': 'World_Hillshade_3689',
                'layerType': 'ArcGISTiledMapServiceLayer',
                'url': 'https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer',
                'visibility': True,
                'opacity': 1,
                'title': 'World Hillshade',
            },
            {
                'id': 'VectorTile_6451',
                'type': 'VectorTileLayer',
                'layerType': 'VectorTileLayer',
                'title': 'World Topographic Map',
                'styleUrl': 'https://cdn.arcgis.com/sharing/rest/content/items/7dc6cea0b1764a1f9af2e679f642f0f5/resources/styles/root.json',
                'visibility': True,
                'opacity': 1,
            },
        ],
        'title': 'Topographic',
    },
    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
    'authoringApp': 'WebMapViewer',
    'authoringAppVersion': '10.2',
    'version': '2.25',
}




@integration_test
class TestItemProperties(unittest.TestCase):
    def test_add_item(self):
        ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP,
            title="ItemPropertiesWebMap",
            text=data,
        )
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            content = gis.content
            isinstance(content, ContentManager)
            item = content.add(item_properties=ip.to_dict())
            assert item
            assert isinstance(item, Item)
            assert item.get_data(try_json=True)
            assert item.delete()

    def test_add_item(self):
        ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP, title="ItemPropertiesWebMap"
        )
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            content = gis.content
            isinstance(content, ContentManager)
            item = content.add(item_properties=ip.to_dict(), text=data)
            assert item
            assert isinstance(item, Item)
            assert item.get_data(try_json=True)
            assert item.delete()

    def test_from_item(self):
        original_ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP,
            title="ItemPropertiesWebMap",
            text=data,
        )
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            content = gis.content
            isinstance(content, ContentManager)
            item = content.add(
                item_properties=original_ip.to_dict(), text=data
            )
            ip = ItemProperties.fromitem(item)
            assert item.update(ip.to_dict())
            assert item.delete()

    def test_update_item(self):
        original_ip = ItemProperties(
            item_type=ItemTypeEnum.WEB_MAP,
            title="ItemPropertiesWebMap",
            text=data,
        )
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            content = gis.content
            isinstance(content, ContentManager)
            item = content.add(
                item_properties=original_ip.to_dict(), text=data
            )
            ip = ItemProperties.fromitem(item)
            assert item.update(ip.to_dict())
            ip.title = "CHanged the Title"
            assert item.update(ip.to_dict())
            assert item.title == ip.title
            assert item.delete()


if __name__ == "__main__":
    unittest.main()
