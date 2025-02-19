import json
import datetime
import unittest
from utils.decorators import integration_test, profiles

from arcgis.gis import Item


def _stage_data(gis):
    now = datetime.datetime.now()
    web_map_replace_id = "07a05ca8a10843aba797076d40ca8f36"
    web_map_json = {
        "operationalLayers": [],
        "baseMap": {
            "baseMapLayers": [
                {
                    "id": "layer0",
                    "layerType": "ArcGISTiledMapServiceLayer",
                    "url": "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer",
                    "visibility": True,
                    "opacity": 1,
                    "title": "World Dark Gray Canvas Base",
                },
                {
                    "id": "World_Dark_Gray_Reference_8618",
                    "layerType": "ArcGISTiledMapServiceLayer",
                    "url": "https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Reference/MapServer",
                    "visibility": True,
                    "opacity": 1,
                    "title": "World Dark Gray Reference",
                    "isReference": True,
                },
            ],
            "title": "Dark Gray Canvas",
        },
        "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        "authoringApp": "WebMapViewer",
        "authoringAppVersion": "10.7.1",
        "version": "2.14",
    }
    web_app_json = {
        "source": "7f7c4245f03445e782e9aa4a4d06221d",
        "folderId": None,
        "values": {
            "settings": {
                "layout": {"id": "tab"},
                "layoutOptions": {
                    "description": True,
                    "legend": "panel",
                    "panel": {"position": "left", "size": "medium"},
                    "panelMapOverlap": False,
                },
                "appGeocoders": [
                    {
                        "singleLineFieldName": "SingleLine",
                        "name": "ArcGIS World Geocoding Service",
                        "url": "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer",
                    }
                ],
            },
            "title": "storymapseries",
            "story": {
                "storage": "WEBAPP",
                "entries": [
                    {
                        "title": "SampleTestMap",
                        "contentActions": [],
                        "creaDate": 1585215526817,
                        "status": "PUBLISHED",
                        "media": {
                            "type": "webmap",
                            "webmap": {
                                "id": "07a05ca8a10843aba797076d40ca8f36",
                                "extent": None,
                                "layers": None,
                                "popup": None,
                                "legend": {
                                    "enable": False,
                                    "openByDefault": False,
                                },
                                "altText": "",
                            },
                        },
                        "description": "<p>this is a parking lot. yes it is.</p>\n",
                    },
                    {
                        "title": "funky chickens",
                        "contentActions": [],
                        "creaDate": 1585215549750,
                        "status": "PUBLISHED",
                        "media": {
                            "type": "webmap",
                            "webmap": {
                                "id": "07a05ca8a10843aba797076d40ca8f36",
                                "extent": {
                                    "xmin": -13182572.6587242,
                                    "ymin": 4014063.7634446803,
                                    "xmax": -13180967.481130345,
                                    "ymax": 4014997.7283839607,
                                    "spatialReference": {"wkid": 102100},
                                },
                                "layers": None,
                                "popup": None,
                                "legend": {
                                    "enable": False,
                                    "openByDefault": False,
                                },
                                "altText": "",
                            },
                        },
                        "description": "",
                    },
                ],
            },
            "template": {
                "name": "Map Series",
                "createdWith": "1.14.0-20190116",
                "editedWith": "1.14.0-20190116",
            },
        },
        "_ssl": None,
    }
    web_app_type = "Web Mapping Application"
    web_app_name = f"Map Series {now.microsecond}"
    web_map_name = f"Web Map {now.microsecond}"
    wm_item = gis.content.add(
        {
            "title": web_map_name,
            "type": "Web Map",
            "tags": "test data, erase me",
            "text": json.dumps(web_map_json),
        }
    )
    web_app_json["values"]["story"]["entries"][0]["media"]["webmap"][
        "id"
    ] = wm_item.id
    web_app_item = gis.content.add(
        {
            "title": web_app_name,
            "type": web_app_type,
            "tags": "a,b,c",
            "text": json.dumps(web_app_json),
        }
    )
    web_app_item.update(
        {
            "url": f"{gis._url}/apps/MapSeries/index.html?appid={web_app_item.id}"
        }
    )
    return web_app_item, wm_item


@profiles.enterprise_and_agol
@integration_test
class TestItemCopy(unittest.TestCase):
    """Tests the Copy Method on Item"""

    _app_data = {}

    # ----------------------------------------------------------------------
    def test_copy_item(self):
        """tests copying the story map/web map application"""
        web_app_item, wm_item = _stage_data(self.gis)
        assert isinstance(web_app_item, Item)
        new_item = web_app_item.copy(title="thisisnewtitle1234", tags="ntgrtn-tst")
        assert new_item.title == "thisisnewtitle1234"
        assert new_item.url
        assert new_item.url != web_app_item.url
        assert new_item.delete(permanent=True)

    # ----------------------------------------------------------------------
    def test_copy_notebook_item(self):
        """tests copying the notebook"""
        items = self.gis.content.search("type: Notebook")
        if not items:
            self.skipTest(f"GIS(url={self.gis.url}) has no Notebook items")
        item = items[0]
        item_new = item.copy(tags="ntgrtn-tst")
        assert item_new
        assert item_new.type == item.type
        assert item_new.delete(permanent=True)

    # ----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        for k, v in cls._app_data.items():
            for i in v:
                i.delete()


if __name__ == "__main__":
    unittest.main()
