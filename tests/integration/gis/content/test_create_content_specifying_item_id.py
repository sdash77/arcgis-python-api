import os
import uuid
import datetime
import tempfile
import unittest
import pandas as pd
from arcgis.geometry import Geometry
from arcgis._impl.common._utils import zipws
import json
from utils.decorators import integration_test, profiles

g1 = Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}})
g2 = Geometry({"x": -117.15, "y": 34.80, "spatialReference": {"wkid": 4326}})
g3 = Geometry({"x": -116.15, "y": 35.80, "spatialReference": {"wkid": 4326}})
g4 = Geometry({"x": -115.15, "y": 36.80, "spatialReference": {"wkid": 4326}})

webmap = {
    "operationalLayers": [],
    "baseMap": {
        "baseMapLayers": [
            {
                "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
                "layerType": "ArcGISTiledMapServiceLayer",
                "resourceInfo": {
                    "currentVersion": 10.3,
                    "mapName": "Layers",
                    "supportsDynamicLayers": False,
                    "layers": [
                        {
                            "id": 0,
                            "name": "Citations",
                            "parentLayerId": -1,
                            "defaultVisibility": False,
                            "subLayerIds": "Portal for ArcGIS",
                            "minScale": 0,
                            "maxScale": 0,
                        }
                    ],
                    "tables": [],
                    "spatialReference": {"wkid": 102100, "latestWkid": 3857},
                    "singleFusedMapCache": True,
                    "tileInfo": {
                        "rows": 256,
                        "cols": 256,
                        "dpi": 96,
                        "format": "JPEG",
                        "compressionQuality": 90,
                        "origin": {"x": -20037508.342787, "y": 20037508.342787},
                        "spatialReference": {"wkid": 102100, "latestWkid": 3857},
                        "lods": [
                            {
                                "level": 0,
                                "resolution": 156543.03392800014,
                                "scale": 591657527.591555,
                            },
                            {
                                "level": 1,
                                "resolution": 78271.51696399994,
                                "scale": 295828763.795777,
                            },
                            {
                                "level": 2,
                                "resolution": 39135.75848200009,
                                "scale": 147914381.897889,
                            },
                            {
                                "level": 3,
                                "resolution": 19567.87924099992,
                                "scale": 73957190.948944,
                            },
                            {
                                "level": 4,
                                "resolution": 9783.93962049996,
                                "scale": 36978595.474472,
                            },
                            {
                                "level": 5,
                                "resolution": 4891.96981024998,
                                "scale": 18489297.737236,
                            },
                            {
                                "level": 6,
                                "resolution": 2445.98490512499,
                                "scale": 9244648.868618,
                            },
                            {
                                "level": 7,
                                "resolution": 1222.992452562495,
                                "scale": 4622324.434309,
                            },
                            {
                                "level": 8,
                                "resolution": 611.4962262813797,
                                "scale": 2311162.217155,
                            },
                            {
                                "level": 9,
                                "resolution": 305.74811314055756,
                                "scale": 1155581.108577,
                            },
                            {
                                "level": 10,
                                "resolution": 152.87405657041106,
                                "scale": 577790.554289,
                            },
                            {
                                "level": 11,
                                "resolution": 76.43702828507324,
                                "scale": 288895.277144,
                            },
                            {
                                "level": 12,
                                "resolution": 38.21851414253662,
                                "scale": 144447.638572,
                            },
                            {
                                "level": 13,
                                "resolution": 19.10925707126831,
                                "scale": 72223.819286,
                            },
                            {
                                "level": 14,
                                "resolution": 9.554628535634155,
                                "scale": 36111.909643,
                            },
                            {
                                "level": 15,
                                "resolution": 4.77731426794937,
                                "scale": 18055.954822,
                            },
                            {
                                "level": 16,
                                "resolution": 2.388657133974685,
                                "scale": 9027.977411,
                            },
                            {
                                "level": 17,
                                "resolution": 1.1943285668550503,
                                "scale": 4513.988705,
                            },
                            {
                                "level": 18,
                                "resolution": 0.5971642835598172,
                                "scale": 2256.994353,
                            },
                            {
                                "level": 19,
                                "resolution": 0.29858214164761665,
                                "scale": 1128.497176,
                            },
                            {
                                "level": 20,
                                "resolution": 0.14929107082380833,
                                "scale": 564.248588,
                            },
                            {
                                "level": 21,
                                "resolution": 0.07464553541190416,
                                "scale": 282.124294,
                            },
                            {
                                "level": 22,
                                "resolution": 0.03732276770595208,
                                "scale": 141.062147,
                            },
                            {
                                "level": 23,
                                "resolution": 0.01866138385297604,
                                "scale": 70.5310735,
                            },
                        ],
                    },
                    "initialExtent": {
                        "xmin": -28848255.049479112,
                        "ymin": -2077452.082122866,
                        "xmax": 28848255.049479112,
                        "ymax": 16430757.376790084,
                        "spatialReference": {"wkid": 102100, "latestWkid": 3857},
                    },
                    "fullExtent": {
                        "xmin": -20037507.067161843,
                        "ymin": -19971868.880408604,
                        "xmax": 20037507.067161843,
                        "ymax": 19971868.88040863,
                        "spatialReference": {"wkid": 102100, "latestWkid": 3857},
                    },
                    "minScale": 591657527.591555,
                    "maxScale": 70.5310735,
                    "units": "esriMeters",
                    "supportedImageFormatTypes": "PNG32,PNG24,PNG,JPG,DIB,TIFF,EMF,PS,PDF,GIF,SVG,SVGZ,BMP",
                    "capabilities": "Map,Tilemap,Query,Data",
                    "supportedQueryFormats": "JSON, AMF",
                    "exportTilesAllowed": False,
                    "maxRecordCount": 100,
                    "maxImageHeight": 4096,
                    "maxImageWidth": 4096,
                    "supportedExtensions": "KmlServer",
                },
            }
        ],
        "title": "Topographic",
    },
    "spatialReference": {"wkid": 102100, "latestWkid": 3857},
    "version": "2.10",
    "authoringApp": "ArcGISPythonAPI",
    "authoringAppVersion": "1.8.0",
}


@profiles.enterprise
@integration_test
class TestItemByItemId(unittest.TestCase):
    """
    Tests the 10.8.1 Create Items with user specified UUID
    Only works for Enterprise
    """

    @classmethod
    def setUpClass(cls):
        cls.folder = cls.gis.content.folders._get_or_create(
            folder="integration_testing_gis_content_folder_add_with_id",
            owner=cls.gis._username,
        )

    @classmethod
    def tearDownClass(cls):
        if cls.folder:
            cls.folder.delete(permanent=True)

    def test_add_set_item_id(self):
        """tests setting an ItemID"""
        myuid = uuid.uuid4().hex
        item = self.folder.add(
            item_properties={
                "title": "test_add_item_with_id",
                "type": "Web Map",
                "text": json.dumps(webmap),
                "tags": "integration_testing",
            },
            item_id=myuid,
        ).result()
        assert item.itemid.lower() == myuid.lower()
        assert item.delete(permanent=True)

    def test_add_set_item_id_error_raised(self):
        """tests create 2 items with same id"""
        myuid = uuid.uuid4().hex
        item1 = self.folder.add(
            item_properties={
                "title": "test_add_item_with_same_id",
                "type": "Web Map",
                "text": json.dumps(webmap),
                "tags": "integration_testing"
            },
            item_id=myuid,
        ).result()
        assert item1.itemid == myuid

        with self.assertRaises(Exception) as context:
            item2 = self.folder.add(
                item_properties={
                    "title": "test_add_item_with_same_id",
                    "type": "Web Map",
                    "text": json.dumps(webmap),
                    "tags": "integration_testing",
                },
                item_id=myuid,
            ).result()
        assert item1.delete(permanent=True)
        #if item2:
        #    item2.delete(permanent=True)

    def test_import_data_sedf(self):
        """
        tests the setting of the UID value to a specific value for
        publishing/importing content
        """
        data = {
            "OBJECTID": [1, 2, 3, 4],
            "SHAPE": [g1, g2, g3, g4],
            "NAME": ["a", "b", "c", "d"],
        }
        df = pd.DataFrame(data)
        df.spatial.name
        myuid = uuid.uuid4().hex
        item = self.gis.content.import_data(df, title="test_import_data_with_id", item_id=myuid)
        assert item.itemid == myuid

        related_items = item.related_items("Service2Data", "forward")
        assert item.delete(permanent=True)
        for item in related_items:
            item.delete(permanent=True)

    def test_create_service(self):
        """tests the create_service and setting a item id"""
        myuid = uuid.uuid4().hex
        service_item = self.gis.content.create_service(
            name=f"test_create_service_with_id", item_id=myuid
        )
        assert myuid == service_item.itemid
        assert service_item.delete(permanent=True)

    def test_add_publish_workflow(self):
        """tests the add/publish workflow on Enterprise"""
        data = {
            "OBJECTID": [1, 2, 3, 4],
            "SHAPE": [g1, g2, g3, g4],
            "NAME": ["a", "b", "c", "d"],
        }
        df = pd.DataFrame(data)
        df.spatial.name

        now = datetime.datetime.now()
        myshapefile_uuid = uuid.uuid4().hex
        myservice_uuid = uuid.uuid4().hex
        with tempfile.TemporaryDirectory() as d:
            mydata = os.path.join(d, "export_data.shp")
            data = df.spatial.to_featureclass(mydata)
            temp_zip = os.path.join(d, f"test_add_publish_flow_{uuid.uuid4().hex[:5]}.zip")
            zipws(path=d, outfile=temp_zip, keep=False)
            shp_item = self.folder.add(
                item_id=myshapefile_uuid,
                item_properties={
                    "title": f"test_add_publish_flow_with_id",
                    "tags": "integration_testing",
                    "type": "Shapefile",
                },
                file=temp_zip,
            ).result()
            shp_pitem = shp_item.publish(
                publish_parameters={"name": f"test_publish_with_id_{now.microsecond}"},
                item_id=myservice_uuid,
            )
            assert shp_pitem.itemid == myservice_uuid
            assert shp_item.itemid == myshapefile_uuid
            assert shp_item.delete(permanent=True)
            assert shp_pitem.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
