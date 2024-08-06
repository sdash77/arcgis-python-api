import unittest
from arcgis.gis import GIS, ContentManager
from utils.decorators import integration_test

profiles = ["your_online_profile", "your_enterprise_profile", "your_kubernetes_profile"]
wm = {
    "operationalLayers": [],
    "baseMap": {
        "baseMapLayers": [
            {
                "id": "defaultBasemap",
                "layerType": "ArcGISTiledMapServiceLayer",
                "url": "http://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
                "visibility": True,
                "opacity": 1,
                "title": "Topographic",
            },
            {
                "id": "wms_3449",
                "url": "http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                "visibility": True,
                "visibleLayers": ["nexrad-n0r"],
                "opacity": 1,
                "title": "IEM WMS Service",
                "showLegend": True,
                "type": "WMS",
                "layerType": "WMS",
                "version": "1.3.0",
                "mapUrl": "http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                "layers": [
                    {"name": "nexrad-n0r", "title": "NEXRAD BASE REFLECT CURRENT"},
                    {
                        "name": "nexrad-n0r-900913",
                        "title": "NEXRAD BASE REFLECT (GOOGLE)",
                    },
                    {
                        "name": "nexrad-n0r-900913-m05m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M5 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m10m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M10 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m15m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M15 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m20m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M20 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m25m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M25 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m30m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M30 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m35m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M35 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m40m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M40 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m45m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M45 MINS",
                    },
                    {
                        "name": "nexrad-n0r-900913-m50m",
                        "title": "NEXRAD BASE REFLECT (GOOGLE) M50 MINS",
                    },
                    {"name": "nexrad-n0r-m05m", "title": "NEXRAD BASE REFLECT M5 MINS"},
                    {
                        "name": "nexrad-n0r-m10m",
                        "title": "NEXRAD BASE REFLECT M10 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m15m",
                        "title": "NEXRAD BASE REFLECT M15 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m20m",
                        "title": "NEXRAD BASE REFLECT M20 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m25m",
                        "title": "NEXRAD BASE REFLECT M25 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m30m",
                        "title": "NEXRAD BASE REFLECT M30 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m35m",
                        "title": "NEXRAD BASE REFLECT M35 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m40m",
                        "title": "NEXRAD BASE REFLECT M40 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m45m",
                        "title": "NEXRAD BASE REFLECT M45 MINS",
                    },
                    {
                        "name": "nexrad-n0r-m50m",
                        "title": "NEXRAD BASE REFLECT M50 MINS",
                    },
                ],
                "spatialReferences": [900913, 4326, 102100, 3857],
                "extent": [[-126, 24], [-66, 50]],
                "maxWidth": 2048,
                "maxHeight": 2048,
            },
        ],
        "title": "Topographic",
    },
    "spatialReference": {"wkid": 102100, "latestWkid": 3857},
    "authoringApp": "WebMapViewer",
    "authoringAppVersion": "4.1",
    "version": "2.1",
}


def create_item(gis):
    """creates a dummy item on the GIS"""
    import json, uuid

    return gis.content.add(
        item_properties={
            "title": uuid.uuid4().hex,
            "type": "Web Map",
            "tags": "erase, me",
            "text": json.dumps(wm),
        }
    )


@integration_test
class TestCMCanDelete(unittest.TestCase):
    def test_can_delete(self):
        import copy

        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            content = gis.content
            assert isinstance(content, ContentManager)

            item = create_item(gis=gis)
            item.protect(False)
            res = content.can_delete(item)
            assert res
            assert isinstance(res, dict)
            assert res["success"] == True
            item.protect(True)
            res = content.can_delete(item)
            assert res["success"] == False
            item.protect(False)
            assert item.delete()

    def test_can_delete_item(self):
        """
        tests if can_delete on Item
        """
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            content = gis.content
            assert isinstance(content, ContentManager)

            item = create_item(gis=gis)
            item.protect(False)
            res = item.can_delete
            assert res

            item.protect(True)
            res = item.can_delete
            assert res == False
            item.protect(False)
            assert item.delete()


@integration_test
class TestPermanentDelete(unittest.TestCase):
    def test_permanent_delete(self):
        # As of now, only available in ArcGIS Online
        gis = GIS(profile="your_dev_profile", verify_cert=False)  # devext
        content = gis.content
        assert isinstance(content, ContentManager)
        user = gis.users.me
        rb = user.recyclebin
        num_items_before = len(list(rb.content))

        item = create_item(gis=gis)
        res = content.delete_items([item], permanent=True)
        assert res

        num_items_after = len(list(rb.content))
        assert num_items_after == num_items_before


if __name__ == "__main__":
    unittest.main()
