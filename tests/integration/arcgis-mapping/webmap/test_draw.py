from arcgis.features import FeatureCollection
from arcgis.geometry import Point, Polyline, Polygon
from arcgis.gis import GIS
from arcgis.map import Map
import unittest
from arcgis.map import symbols
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestDrawOnMap(unittest.TestCase):

    def setUp(self):
        # create webmap
        self.wm = Map(location="Dallas, TX", gis=self.gis)
        assert self.wm

    def test_point(self):
        """Test drawing a point"""

        pt = Point({"x": -96.80, "y": 32.78, "spatialReference": {"wkid": 4326}})
        assert pt
        simple_symbol = symbols.SimpleMarkerSymbolEsriSMS(
            style=symbols.SimpleMarkerSymbolStyle.esri_sms_diamond,
            color=[255, 140, 0, 255],
            size=14,
            outline=symbols.SimpleLineSymbolEsriSLS(
                color=[255, 140, 0, 255],
                width=1,
                style=symbols.SimpleLineSymbolStyle.esri_sls_solid,
            ),
        )
        self.wm.content.draw(
            pt,
            symbol=simple_symbol,
        )
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], FeatureCollection)
        fc = self.wm.content.layers[0]
        assert fc.properties.layers
        fc_lyr = fc.properties["layers"][0]
        assert "featureSet" in list(fc_lyr.keys())
        assert (
            self.wm.content.layers[0]
            .properties.layers[0]
            .layerDefinition.drawingInfo.renderer.symbol.style
            == "esriSMSDiamond"
        )

    def test_polyline(self):
        """Test drawing a polyline"""

        line = {
            "paths": [
                [
                    [-97.06138, 32.838],
                    [-97.06133, 32.836],
                    [-97.06124, 32.834],
                    [-97.06127, 32.832],
                    [-97.06121, 32.830],
                ],
                [[-97.06326, 32.759], [-97.06298, 32.755]],
            ],
            "spatialReference": {"wkid": 4326},
        }

        simple_line_symbol = symbols.SimpleLineSymbolEsriSLS(
            style=symbols.SimpleLineSymbolStyle.esri_sls_solid,
            color=[51, 51, 255, 255],
            width=4,
        )

        polyline = Polyline(line)

        self.wm.content.draw(shape=polyline, symbol=simple_line_symbol)

        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], FeatureCollection)
        assert (
            self.wm.content.layers[0]
            .properties["layers"][0]["layerDefinition"]["drawingInfo"]["renderer"][
                "symbol"
            ]
            .style
            == "esriSLSSolid"
        )

    def test_polygon(self):
        """Test drawing a polygon"""

        polygon1 = Polygon(
            {
                "spatialReference": {"wkid": 4326},
                "rings": [
                    [
                        [-97.06587202923951, 32.75656343500563],
                        [-97.07033522518535, 32.75454232619796],
                        [-97.07179434702324, 32.75443405154119],
                        [-97.073596791488, 32.75475887587208],
                        [-97.07501299810983, 32.75475887587208],
                        [-97.07492716677937, 32.75616643554153],
                        [-97.07595713555828, 32.75602207118053],
                        [-97.07115061698558, 32.75887321736912],
                        [-97.06930525730476, 32.75890930713694],
                        [-97.06479914614289, 32.75739351976198],
                        [-97.06587202923951, 32.75656343500563],
                    ]
                ],
            }
        )

        simple_poly_symbol = symbols.SimpleFillSymbolEsriSFS(
            style=symbols.SimpleFillSymbolStyle.esri_sfs_solid,
            color=[255, 51, 0, 255],
            outline=symbols.SimpleLineSymbolEsriSLS(
                style=symbols.SimpleLineSymbolStyle.esri_sls_solid,
                color=[128, 128, 128, 255],
                width=2,
            ),
        )

        self.wm.content.draw(polygon1)

        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], FeatureCollection)
        assert (
            self.wm.content.layers[0]
            .properties["layers"][0]["layerDefinition"]["drawingInfo"]["renderer"][
                "symbol"
            ]
            .outline.style
            == "esriSLSSolid"
        )
        assert (
            self.wm.content.layers[0]
            .properties["layers"][0]["layerDefinition"]["drawingInfo"]["renderer"][
                "symbol"
            ]
            .style
            == "esriSFSSolid"
        )


if __name__ == "__main__":
    unittest.main()
