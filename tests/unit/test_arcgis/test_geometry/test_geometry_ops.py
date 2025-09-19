import sys
import unittest

from arcgis.geometry import (
    Geometry,
    Point,
    MultiPoint,
    Polygon,
    Polyline,
    Envelope,
)

try:
    import arcpy

    SKIP_ARCPY = False
except:
    SKIP_ARCPY = True


###########################################################################
class TestPointGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geom = Point(
            {"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}}
        )
        cls.pt2 = Geometry(
            {"x": 2.22, "y": -1.5, "spatialReference": {"wkid": 4326}}
        )
        cls.pt3 = Point(
            {
                'x': 1501210.1001409742,
                'y': 567718.5333534777,
                'spatialReference': {'wkid': 4326},
            }
        )

    def test_dot_notation(self):
        assert self.geom.x
        assert self.geom.y
        self.geom.y = 35
        assert self.geom.y == 35
        assert self.pt3.spatialReference

    def test_bracket(self):
        assert self.geom['x']
        assert self.geom['y']
        self.geom['y'] = 34
        assert self.geom['y'] == 34
        assert self.pt3['spatialReference']

    def test_area_ops(self):
        if SKIP_ARCPY == False:
            assert self.geom.area >= 0

    def test_centroid_prop(self):
        assert self.geom.centroid or self.geom.centroid is None

    def test_extent_prop(self):
        assert self.geom.extent

    def test_first_point(self):
        assert self.geom.first_point

    def test_geometry_type(self):
        assert self.geom.geometry_type

    def test_geoextent_prop(self):
        assert self.geom.geoextent

    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle or self.geom.hull_rectangle is None

    def test_is_empty(self):
        assert self.geom.is_empty in [True, False]

    def test_is_multipart(self):
        assert self.geom.is_multipart in [False, None]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    def test_label_point_prop(self):
        assert self.geom.label_point or self.geom.label_point is None

    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        if SKIP_ARCPY == False:
            assert self.geom.length >= 0

    def test_length3D(self):
        if SKIP_ARCPY == False:
            assert self.geom.length3D >= 0

    def test_part_count(self):
        assert self.geom.part_count >= 0

    def test_point_count(self):
        assert self.geom.point_count >= 0

    def test_SR(self):
        assert self.geom.spatial_reference

    def test_true_centroid(self):
        assert self.geom.true_centroid

    def test_WKB(self):
        assert self.geom.WKB

    def test_WKT(self):
        assert self.geom.WKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_angle_distance_to(self):
        assert self.geom.angle_distance_to(second_geometry=self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_buffer(self):
        assert self.geom.buffer(10)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_boundary(self):
        assert self.geom.boundary()

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_densify(self):
        g = self.geom.densify(
            method="DISTANCE", distance=0.001, deviation=0.000001
        )
        assert g is None

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_difference(self):
        self.geom.difference(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        assert self.geom.has_z in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_touches(self):
        self.geom.touches(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_within(self):
        self.geom.within(self.pt2)


###########################################################################
class TestMultiPointGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geom = MultiPoint(
            {
                "points": [
                    [-97.06138, 32.837],
                    [-97.06133, 32.836],
                    [-97.06124, 32.834],
                    [-97.06127, 32.832],
                ],
                "spatialReference": {"wkid": 4326},
            }
        )
        cls.pt2 = Geometry(
            {"x": 2.22, "y": -1.5, "spatialReference": {"wkid": 4326}}
        )

    def test_dot_notation(self):
        assert self.geom.points

        assert self.geom.spatialReference

    def test_bracket(self):
        assert self.geom['points']
        assert self.geom['spatialReference']

    def test_area_ops(self):
        if SKIP_ARCPY == False:
            assert self.geom.area >= 0

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_centroid_prop(self):
        assert self.geom.centroid

    def test_extent_prop(self):
        assert self.geom.extent

    def test_first_point(self):
        assert self.geom.first_point

    def test_geometry_type(self):
        assert self.geom.geometry_type

    def test_geoextent_prop(self):
        assert self.geom.geoextent

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle

    def test_is_empty(self):
        assert self.geom.is_empty in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_is_multipart(self):
        assert self.geom.is_multipart in [False, True]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_label_point_prop(self):
        assert self.geom.label_point

    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        if SKIP_ARCPY == False:
            assert self.geom.length >= 0

    def test_length3D(self):
        if SKIP_ARCPY == False:
            assert self.geom.length3D >= 0

    def test_part_count(self):
        assert self.geom.part_count >= 0

    def test_point_count(self):
        assert self.geom.point_count >= 0

    def test_SR(self):
        assert self.geom.spatial_reference

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_true_centroid(self):
        assert self.geom.true_centroid

    def test_WKB(self):
        assert self.geom.WKB

    def test_WKT(self):
        assert self.geom.WKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_buffer(self):
        assert self.geom.buffer(10)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_boundary(self):
        g = self.geom
        g.boundary()
        assert self.geom.boundary()

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_difference(self):
        self.geom.difference(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        assert self.geom.has_z in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_touches(self):
        self.geom.touches(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_within(self):
        self.geom.within(self.pt2)


###########################################################################
class TestPolylineGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geom = Polyline(
            {
                "paths": [
                    [
                        [-97.06138, 32.837],
                        [-97.06133, 32.836],
                        [-97.06124, 32.834],
                        [-97.06127, 32.832],
                    ],
                    [[-97.06326, 32.759], [-97.06298, 32.755]],
                ],
                "spatialReference": {"wkid": 4326},
            }
        )

        cls.geom_curved = Polyline(
            {
                "curvePaths": [
                    [
                        [[-97.06138, 32.837], [-97.06133, 32.836], [-97.06124, 32.834], [-97.06127, 32.832]],
                    ],
                    [[-97.06326, 32.759], [-97.06298, 32.755]],
                ],
                "spatialReference": {"wkid": 4326}
            }
        )

        cls.empty = Polyline(
            {
                "paths": [], 
                "spatialReference": {"wkid": 4326}
            }
        )

        cls.empty_curved = Polyline(
            {
                "curvePaths": [], 
                "spatialReference": {"wkid": 4326}
            }
        )

        cls.pt2 = Geometry(
            {"x": 2.22, "y": -1.5, "spatialReference": {"wkid": 4326}}
        )

    def test_dot_notation(self):
        assert self.geom.paths

        assert self.geom.spatialReference

    def test_bracket(self):
        assert self.geom['paths']
        assert self.geom['spatialReference']

    def test_area_ops(self):
        if SKIP_ARCPY == False:
            assert self.geom.area >= 0

    def test_centroid_prop(self):
        self.geom.centroid

    def test_extent_prop(self):
        assert self.geom.extent

    def test_first_point(self):
        assert self.geom.first_point

    def test_geometry_type(self):
        assert self.geom.geometry_type

    def test_geoextent_prop(self):
        assert self.geom.geoextent

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle

    def test_is_empty(self):
        self.assertEqual(self.geom.is_empty, False)
        self.assertEqual(self.empty.is_empty, True)
        self.assertEqual(self.geom_curved.is_empty, False)
        self.assertEqual(self.empty_curved.is_empty, True)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_is_multipart(self):
        assert self.geom.is_multipart in [False, True]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_label_point_prop(self):
        assert self.geom.label_point

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        if SKIP_ARCPY == False:
            assert self.geom.length >= 0

    def test_length3D(self):
        if SKIP_ARCPY == False:
            assert self.geom.length3D >= 0

    def test_part_count(self):
        assert self.geom.part_count >= 0

    def test_point_count(self):
        assert self.geom.point_count >= 0

    def test_SR(self):
        assert self.geom.spatial_reference

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_true_centroid(self):
        assert self.geom.true_centroid

    def test_WKB(self):
        assert self.geom.WKB

    def test_WKT(self):
        assert self.geom.WKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_buffer(self):
        assert self.geom.buffer(10)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_boundary(self):
        g = self.geom
        g.boundary()
        assert self.geom.boundary()

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_densify(self):
        g = self.geom.densify(
            method="DISTANCE", distance=0.001, deviation=0.000001
        )
        assert g

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_difference(self):
        self.geom.difference(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        g = self.geom
        g.has_z
        assert self.geom.has_z in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.geom)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_touches(self):
        self.geom.touches(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_within(self):
        self.geom.within(self.pt2)


###########################################################################
class TestPolygonGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geom = Polygon(
            {
                "rings": [
                    [
                        [-97.06138, 32.837],
                        [-97.06133, 32.836],
                        [-97.06124, 32.834],
                        [-97.06127, 32.832],
                        [-97.06138, 32.837],
                    ],
                    [
                        [-97.06326, 32.759],
                        [-97.06298, 32.755],
                        [-97.06153, 32.749],
                        [-97.06326, 32.759],
                    ],
                ],
                "spatialReference": {"wkid": 4326},
            }
        )

        cls.pt2 = Geometry(
            {"x": 2.22, "y": -1.5, "spatialReference": {"wkid": 4326}}
        )

    def test_dot_notation(self):
        assert self.geom.rings

        assert self.geom.spatialReference

    def test_bracket(self):
        assert self.geom['rings']
        assert self.geom['spatialReference']

    def test_area_ops(self):
        assert self.geom.area >= 0

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_centroid_prop(self):
        assert self.geom.centroid

    def test_extent_prop(self):
        assert self.geom.extent

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_first_point(self):
        assert self.geom.first_point

    def test_geometry_type(self):
        assert self.geom.geometry_type

    def test_geoextent_prop(self):
        assert self.geom.geoextent

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle

    def test_is_empty(self):
        assert self.geom.is_empty in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_is_multipart(self):
        assert self.geom.is_multipart in [False, True]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_label_point_prop(self):
        assert self.geom.label_point

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        if SKIP_ARCPY == False:
            assert self.geom.length >= 0

    def test_length3D(self):
        if SKIP_ARCPY == False:
            assert self.geom.length3D >= 0

    def test_part_count(self):
        assert self.geom.part_count >= 0

    def test_point_count(self):
        assert self.geom.point_count >= 0

    def test_SR(self):
        assert self.geom.spatial_reference

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_true_centroid(self):
        assert self.geom.true_centroid

    def test_WKB(self):
        assert self.geom.WKB

    def test_WKT(self):
        assert self.geom.WKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_angle_distance_to(self):
        assert self.geom.angle_distance_to(second_geometry=self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_buffer(self):
        assert self.geom.buffer(10)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_boundary(self):
        g = self.geom
        g.boundary()
        assert self.geom.boundary()

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_densify(self):
        g = self.geom.densify(
            method="DISTANCE", distance=0.001, deviation=0.000001
        )
        assert g

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_difference(self):
        self.geom.difference(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        assert self.geom.has_z in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.geom)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_touches(self):
        self.geom.touches(self.pt2)

    @unittest.skipIf(SKIP_ARCPY, "No arcpy")
    def test_within(self):
        self.geom.within(self.pt2)


if __name__ == "__main__":
    unittest.main()
