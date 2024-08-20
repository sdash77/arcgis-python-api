import os, sys
import logging
import tempfile
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ["your_online_profile", "your_enterprise_profile"]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

import base64

base64_img = (
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAA"
    "LEwEAmpwYAAAB1klEQVQ4jY2TTUhUURTHf+fy/HrjhNEX2KRGiyIXg8xgSURuokX"
    "LxFW0qDTaSQupkHirthK0qF0WQQQR0UCbwCQyw8KCiDbShEYLJQdmpsk3895p4aS"
    "v92ass7pcfv/zP+fcc4U6kXKe2pTY3tjSUHjtnFgB0VqchC/SY8/293S23f+6VEj"
    "9KKwCoPDNIJdmr598GOZNJKNWTic7tqb27WwNuuwGvVWrAit84fsmMzE1P1+1TiK"
    "MVKvYUjdBvzPZXCwXzyhyWNBgVYkgrIow09VJMznpyebWE+Tdn9cEroBSc1JVPS+"
    "6moh5Xyjj65vEgBxafGzWetTh+rr1eE/c/TMYg8hlAOvI6JP4KmwLgJ4qD0TIbli"
    "TB+sunjkbeLekKsZ6Zc8V027aBRoBRHVoduDiSypmGFG7CrcBEyDHA0ZNfNphC0D"
    "6amYa6ANw3YbWD4Pn3oIc+EdL36V3od0A+MaMAXmA8x2Zyn+IQeQeBDfRcUw3B+2"
    "PxwZ/EdtTDpCPQLMh9TKx0k3pXipEVlknsf5KoNzGyOe1sz8nvYtTQT6yyvTjIax"
    "smHGB9pFx4n3jIEfDePQvCIrnn0J4B/gA5J4XcRfu4JZuRAw3C51OtOjM3l2bMb8"
    "Br5eXCsT/w/EAAAAASUVORK5CYII="
)

base64_img_bytes = base64_img.encode("utf-8")

wm_data = {
    "operationalLayers": [],
    "baseMap": {
        "baseMapLayers": [
            {
                "id": "World_Hillshade_3689",
                "opacity": 1,
                "title": "World Hillshade",
                "url": "https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer",
                "visibility": True,
                "layerType": "ArcGISTiledMapServiceLayer",
            },
            {
                "id": "VectorTile_6451",
                "opacity": 1,
                "title": "World Topographic Map",
                "visibility": True,
                "layerType": "VectorTileLayer",
                "styleUrl": "https://cdn.arcgis.com/sharing/rest/content/items/7dc6cea0b1764a1f9af2e679f642f0f5/resources/styles/root.json",
            },
        ],
        "title": "Topographic",
    },
    "authoringApp": "ArcGISMapViewer",
    "authoringAppVersion": "10.1",
    "initialState": {
        "viewpoint": {
            "targetGeometry": {
                "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                "xmin": -13604291.156816924,
                "ymin": 3444876.6403288073,
                "xmax": -12159937.070340617,
                "ymax": 4522332.991036365,
            }
        }
    },
    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
    "version": "2.24",
}


@integration_test
class TestItemDeleteThumbnail(unittest.TestCase):
    def test_delete_item_thumbnail(self):
        fp = None
        item = None
        try:

            fp = os.path.join(tempfile.gettempdir(), "decoded_image.png")
            with open(fp, "wb") as file_to_save:
                decoded_image_data = base64.decodebytes(base64_img_bytes)
                file_to_save.write(decoded_image_data)

            for profile in profiles:
                gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
                item = gis.content.add(
                    item_properties={
                        "type": "Web Map",
                        "title": "TestWebMapDeleteMe",
                        "text": wm_data,
                    },
                    thumbnail=fp,
                )
                assert item.thumbnail
                assert item.delete_thumbnail()
                assert item.thumbnail in [None, ""]
                item.delete()
                del gis, item
                item = None
                gis = None
        except:
            if item:
                item.delete()
            raise
        finally:
            if fp and os.path.isfile(fp):
                os.remove(fp)


if __name__ == "__main__":
    unittest.main()
