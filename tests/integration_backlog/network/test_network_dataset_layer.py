import unittest

from arcgis.gis import GIS
from arcgis.network import NetworkDatasetLayer
from arcgis._impl.common._isd import InsensitiveDict

gis = GIS(
    url="https://punjab.esri.com/portal",
    username="administrator",
    # password="",
    verify_cert=False,
)
url = "https://punjab.esri.com/server/rest/services/Routing/NetworkAnalysis/NAServer/Routing_ND"


class Test_NetworkDatasetLayer(unittest.TestCase):
    """tests the network dataset layer and it's functionality"""

    def test_get_layer(self):
        """Tests the Creation of the Cost Matrix Layer and Properties"""
        ndl = NetworkDatasetLayer(url, gis)
        assert isinstance(ndl, NetworkDatasetLayer)
        assert ndl.properties

    def test_get_travel_modes(self):
        """Tests the retrieve travel modes call"""
        ndl = NetworkDatasetLayer(url, gis)
        assert ndl.retrieve_travel_modes()
        assert isinstance(ndl.retrieve_travel_modes(), InsensitiveDict)

    def test_location(self):
        """Tests the retrieve locations"""
        ndl = NetworkDatasetLayer(url, gis)
        assert isinstance(ndl, NetworkDatasetLayer)
        locations = [
            "-117,34",
            {
                "displayFieldName": "",
                "geometryType": "esriGeometryPoint",
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "fields": [
                    {
                        "name": "OBJECTID",
                        "type": "esriFieldTypeOID",
                        "alias": "OBJECTID",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": 500,
                    },
                    {
                        "name": "LocationType",
                        "type": "esriFieldTypeInteger",
                        "alias": "LocationType",
                    },
                    {
                        "name": "Attr_TravelTime",
                        "type": "esriFieldTypeDouble",
                        "alias": "Attr_TravelTime",
                    },
                    {
                        "name": "Tag",
                        "type": "esriFieldTypeString",
                        "alias": "Tag",
                        "length": 1000,
                    },
                ],
                "features": [
                    {
                        "attributes": {
                            "ObjectID": 10,
                            "Name": "Stop1",
                            "LocationType": 0,
                            "Attr_TravelTime": 10.0,
                            "TAG": "TAG-001",
                        },
                        "geometry": {"x": -117.16010720299994, "y": 32.709083821000036},
                    },
                    {
                        "attributes": {
                            "ObjectID": 2,
                            "Name": "Stop2",
                            "LocationType": 0,
                            "Attr_TravelTime": 2.0,
                            "TAG": "TAG-002",
                        },
                        "geometry": {"x": -117.16012082899999, "y": 32.710867891000078},
                    },
                ],
            },
        ]
        barriers = {
            "displayFieldName": "",
            "geometryType": "esriGeometryPoint",
            "spatialReference": {"wkid": 4326, "latestWkid": 4326},
            "fields": [
                {"name": "ObjectID", "type": "esriFieldTypeOID", "alias": "ObjectID"},
                {
                    "name": "Name",
                    "type": "esriFieldTypeString",
                    "alias": "Name",
                    "length": 500,
                },
                {
                    "name": "FullEdge",
                    "type": "esriFieldTypeInteger",
                    "alias": "FullEdge",
                },
                {
                    "name": "BarrierType",
                    "type": "esriFieldTypeInteger",
                    "alias": "BarrierType",
                },
            ],
            "features": [
                {
                    "attributes": {
                        "ObjectID": 1,
                        "Name": "PointBarrier1",
                        "FullEdge": 0,
                        "BarrierType": 0,
                    },
                    "geometry": {"x": -117.16013785999996, "y": 32.710149153000032},
                }
            ],
        }
        polyline_barriers = {
            "displayFieldName": "",
            "geometryType": "esriGeometryPolyline",
            "spatialReference": {"wkid": 4326, "latestWkid": 4326},
            "fields": [
                {"name": "ObjectID", "type": "esriFieldTypeOID", "alias": "ObjectID"},
                {
                    "name": "Name",
                    "type": "esriFieldTypeString",
                    "alias": "Name",
                    "length": 500,
                },
                {
                    "name": "BarrierType",
                    "type": "esriFieldTypeInteger",
                    "alias": "BarrierType",
                },
            ],
            "features": [
                {
                    "attributes": {
                        "ObjectID": 1,
                        "Name": "LineBarrier1",
                        "BarrierType": 0,
                    },
                    "geometry": {
                        "paths": [
                            [
                                [-117.15881790299994, 32.721517814000038],
                                [-117.15873274499995, 32.71621669600006],
                            ]
                        ]
                    },
                }
            ],
        }
        polygon_barriers = {
            "displayFieldName": "",
            "geometryType": "esriGeometryPolygon",
            "spatialReference": {"wkid": 4326, "latestWkid": 4326},
            "fields": [
                {"name": "ObjectID", "type": "esriFieldTypeOID", "alias": "ObjectID"},
                {
                    "name": "Name",
                    "type": "esriFieldTypeString",
                    "alias": "Name",
                    "length": 500,
                },
                {
                    "name": "BarrierType",
                    "type": "esriFieldTypeInteger",
                    "alias": "BarrierType",
                },
            ],
            "features": [
                {
                    "attributes": {
                        "ObjectID": 1,
                        "Name": "PolygonBarrier1",
                        "BarrierType": 0,
                    },
                    "geometry": {
                        "rings": [
                            [
                                [-117.16058494299995, 32.715982512000039],
                                [-117.15681667899997, 32.715939932000026],
                                [-117.15690183699996, 32.711809745000039],
                                [-117.16064881099999, 32.71180974400005],
                                [-117.16058494299995, 32.715982512000039],
                            ]
                        ]
                    },
                }
            ],
        }
        for location in locations:
            assert ndl.locate(location)
            assert ndl.locate(location, barriers=barriers)
            assert ndl.locate(
                location,
                polyline_barriers=polyline_barriers,
                polygon_barriers=polygon_barriers,
            )


if __name__ == "__main__":
    unittest.main()
