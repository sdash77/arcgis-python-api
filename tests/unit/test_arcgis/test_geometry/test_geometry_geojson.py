#######################################################################
import unittest


import arcgis

try:

    import importlib.util

    shapely_found = importlib.util.find_spec("shapely")
    found = shapely_found is not None
    if found:
        import shapely
        from shapely.wkt import loads
except:
    found = False


@unittest.skipIf(found == False, "Shapely is required to perform this test case.")
class TestGeoJSONWithShapely(unittest.TestCase):
    def test_polyline(self):
        ###
        ###   POLYLINE TEST
        ###
        LINESTRING_3D = (
            "LINESTRING (517947.10 6368795.07 61.07, 517947.11 6368795.1 161.07)"
        )
        for w in [LINESTRING_3D]:
            shape = shapely.from_wkt(w)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 2154}
            )
            assert arcgis_geom.__geo_interface__
            assert arcgis_geom.has_z == True
            assert arcgis_geom.WKT

    def test_polygon_2D(self):
        ###
        ###   POLYGON TEST
        ###   First is polygon with hole, second is simple polygon
        POLYGONWKT_2D = [
            "POLYGON ((35 10, 45 45, 15 40, 10 20, 35 10),(20 30, 35 35, 30 20, 20 30))",
            "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))",
        ]

        for POLY in POLYGONWKT_2D:
            shape = shapely.from_wkt(POLY)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 4326}
            )
            assert arcgis_geom.__geo_interface__
            assert arcgis_geom.has_z == False

    def test_multipolygon_2D(self):
        MULTIPOLYGONWKT_2D = "MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)), ((15 5, 40 10, 10 20, 5 10, 15 5)))"

        for POLY in [MULTIPOLYGONWKT_2D]:
            shape = shapely.from_wkt(POLY)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 4326}
            )
            assert arcgis_geom.__geo_interface__
            assert arcgis_geom.has_z == False

    def test_polygon_3D(self):
        POLYGONWKT_3D = "MULTIPOLYGON (((30 20 1, 45 40 1, 10 40 1, 30 20 1)), ((15 5 2, 40 10 2, 10 20 0, 5 10 1, 15 5 2)))"

        for POLY in [POLYGONWKT_3D]:
            shape = shapely.from_wkt(POLY)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 4326}
            )

            assert arcgis_geom.__geo_interface__
            assert arcgis_geom.has_z == True

    def test_point_3D(self):

        PTWKTZ = "POINT (30 10 5)"
        for PT in [PTWKTZ]:
            shape = shapely.from_wkt(PT)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 4326}
            )
            assert arcgis_geom.has_z
            assert arcgis_geom.__geo_interface__

    def test_point_2D(self):

        PTWKT = "POINT (30 10)"

        for PT in [PTWKT]:
            shape = shapely.from_wkt(PT)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 4326}
            )
            assert arcgis_geom.has_z == False
            assert arcgis_geom.__geo_interface__

    def test_multipoint_3D(self):
        MULTIPOINTWKT_3D = "MULTIPOINT ((10 40 5), (40 30 10), (20 20 15), (30 10 20))"

        for MPWKT in [MULTIPOINTWKT_3D]:
            shape = shapely.from_wkt(MPWKT)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 4326}
            )

            assert arcgis_geom.__geo_interface__
            assert arcgis_geom.has_z == True

    def test_multipoint_2D(self):

        MULTIPOINTWKT_2D = "MULTIPOINT ((10 40), (40 30), (20 20), (30 10))"
        for MPWKT in [MULTIPOINTWKT_2D]:
            shape = shapely.from_wkt(MPWKT)
            arcgis_geom = arcgis.geometry.Geometry.from_shapely(
                shapely_geometry=shape, spatial_reference={"wkid": 4326}
            )

            assert arcgis_geom.__geo_interface__
            assert arcgis_geom.has_z == False


if __name__ == "__main__":
    unittest.main()
