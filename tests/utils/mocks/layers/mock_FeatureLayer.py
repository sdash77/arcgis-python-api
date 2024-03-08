from unittest.mock import MagicMock

from utils.mocks.mock_arcgisconnection import MockArcGISConnection

from arcgis._impl.common._mixins import PropertyMap


class MockFeatureLayer(MagicMock):
    _dynamic_layer = None
    _token = "da78c9fb55bb5e44e44c6f88ee7d4ee4"
    url = "https://example.com/server/rest/services/Hosted/CamerTraps/FeatureServer"
    _url = url
    _con = MockArcGISConnection()
    properties = PropertyMap(
        {
            "supportsAppend": True,
            "supportedAppendFormats": [
                "csv",
                "excel",
                "featureCollection",
                "featureService",
                "filegdb",
                "geoPackage",
                "geojson",
                "jsonl",
                "shapefile",
                "sqlite",
            ],
        }
    )
