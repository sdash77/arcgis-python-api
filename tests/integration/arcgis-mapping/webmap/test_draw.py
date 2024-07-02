from arcgis.features import FeatureCollection
from arcgis.geometry import Point, Polyline, Polygon
from arcgis.gis import GIS
from arcgis.map import Map
import unittest
from arcgis.map import symbols

PROFILES = ["your_online_profile"]


class TestDrawOnMap(unittest.TestCase):
    def test_point(self):
        """Test drawing a point"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            pt = Point({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}})
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
            wm.content.draw(
                pt,
                symbol=simple_symbol,
            )
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], FeatureCollection)
            assert (
                wm.content.layers[
                    0
                ].properties.layerDefinition.drawingInfo.renderer.symbol.style
                == "esriSMSDiamond"
            )

    def test_polyline(self):
        """Test drawing a polyline"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            line = {
                "paths": [
                    [
                        [-97.06138],
                        [-97.06133, 32.836],
                        [-97.06124, 32.834],
                        [-97.06127, 32.832],
                    ],
                    [[-97.06326, 32.759], [-97.06298, 32.755]],
                ],
                "spatialReference": {"wkid": 4326},
            }
            polyline = Polyline(line)

            wm.content.draw(polyline)
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], FeatureCollection)

    def test_polygon(self):
        """Test drawing a polygon"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            polygon1 = Polygon(
                {
                    "spatialReference": {"latestWkid": 4326},
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
            wm.content.draw(polygon1)
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], FeatureCollection)


if __name__ == "__main__":
    unittest.main()
