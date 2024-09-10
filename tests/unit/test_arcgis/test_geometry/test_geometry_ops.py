import sys

sys.path.insert(0, r"c:\SVN\geosaurus_master\src")
import unittest

from arcgis.geometry import (
    Geometry,
    Point,
    MultiPoint,
    Polygon,
    Polyline,
    Envelope,
)


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

    def test_area_ops(self):
        assert self.geom.area >= 0

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

    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle

    def test_is_empty(self):
        assert self.geom.is_empty in [True, False]

    def test_is_multipart(self):
        assert self.geom.is_multipart in [False]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    def test_label_point_prop(self):
        assert self.geom.label_point

    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        assert self.geom.length >= 0

    def test_length3D(self):
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

    def test_angle_distance_to(self):
        assert self.geom.angle_distance_to(second_geometry=self.pt2)

    def test_buffer(self):
        assert self.geom.buffer(10)

    def test_boundary(self):
        assert self.geom.boundary()

    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    def test_densify(self):
        g = self.geom.densify(
            method="DISTANCE", distance=0.001, deviation=0.000001
        )
        assert g is None

    def test_difference(self):
        self.geom.difference(self.pt2)

    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        assert self.geom.has_z in [True, False]

    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.pt2)

    def test_touches(self):
        self.geom.touches(self.pt2)

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

    def test_area_ops(self):
        assert self.geom.area >= 0

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

    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle

    def test_is_empty(self):
        assert self.geom.is_empty in [True, False]

    def test_is_multipart(self):
        assert self.geom.is_multipart in [False, True]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    def test_label_point_prop(self):
        assert self.geom.label_point

    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        assert self.geom.length >= 0

    def test_length3D(self):
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

    def test_buffer(self):
        assert self.geom.buffer(10)

    def test_boundary(self):
        g = self.geom
        g.boundary()
        assert self.geom.boundary()

    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    def test_difference(self):
        self.geom.difference(self.pt2)

    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        assert self.geom.has_z in [True, False]

    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.pt2)

    def test_touches(self):
        self.geom.touches(self.pt2)

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

        cls.pt2 = Geometry(
            {"x": 2.22, "y": -1.5, "spatialReference": {"wkid": 4326}}
        )

    def test_area_ops(self):
        assert self.geom.area >= 0

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

    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle

    def test_is_empty(self):
        assert self.geom.is_empty in [True, False]

    def test_is_multipart(self):
        assert self.geom.is_multipart in [False, True]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    def test_label_point_prop(self):
        assert self.geom.label_point

    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        assert self.geom.length >= 0

    def test_length3D(self):
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

    def test_buffer(self):
        assert self.geom.buffer(10)

    def test_boundary(self):
        g = self.geom
        g.boundary()
        assert self.geom.boundary()

    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    def test_densify(self):
        g = self.geom.densify(
            method="DISTANCE", distance=0.001, deviation=0.000001
        )
        assert g

    def test_difference(self):
        self.geom.difference(self.pt2)

    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        g = self.geom
        g.has_z
        assert self.geom.has_z in [True, False]

    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.geom)

    def test_touches(self):
        self.geom.touches(self.pt2)

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

    def test_area_ops(self):
        assert self.geom.area >= 0

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

    def test_hull_rect_prop(self):
        assert self.geom.hull_rectangle

    def test_is_empty(self):
        assert self.geom.is_empty in [True, False]

    def test_is_multipart(self):
        assert self.geom.is_multipart in [False, True]

    def test_is_valid(self):
        assert self.geom.is_valid() in [True, False]

    def test_JSON_prop(self):
        assert self.geom.JSON

    def test_label_point_prop(self):
        assert self.geom.label_point

    def test_last_point(self):
        self.geom.last_point

    def test_length(self):
        assert self.geom.length >= 0

    def test_length3D(self):
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

    def test_angle_distance_to(self):
        assert self.geom.angle_distance_to(second_geometry=self.pt2)

    def test_buffer(self):
        assert self.geom.buffer(10)

    def test_boundary(self):
        g = self.geom
        g.boundary()
        assert self.geom.boundary()

    def test_countains(self):
        assert self.geom.contains(self.pt2) in [True, False]

    def test_convex_hull(self):
        assert self.geom.convex_hull()

    def test_coordinates(self):
        assert self.geom.coordinates

    def test_crosses(self):
        assert self.geom.crosses(self.pt2) in [True, False]

    def test_densify(self):
        g = self.geom.densify(
            method="DISTANCE", distance=0.001, deviation=0.000001
        )
        assert g

    def test_difference(self):
        self.geom.difference(self.pt2)

    def test_disjoint(self):
        assert self.geom.disjoint(self.pt2) in [True, False]

    def test_distance_to(self):
        assert self.geom.distance_to(self.pt2) >= 0

    def test_EWKT(self):
        assert self.geom.EWKT

    def test_get_area(self):
        assert self.geom.get_area(method="PLANAR", units="ACRES") >= 0

    def test_get_length(self):
        assert self.geom.get_length(method="PLANAR", units="METERS") >= 0

    def test_has_m(self):
        g = self.geom

        assert g.has_m in [True, False]

    def test_has_z(self):
        assert self.geom.has_z in [True, False]

    def test_intersect(self):
        assert self.geom.intersect(self.pt2) is None

    def test_overlaps(self):
        assert self.geom.overlaps(self.geom) in [True, False]

    def test_project(self):
        assert self.geom.project_as(spatial_reference=3857)

    def test_query_point_and_distance(self):
        self.geom.query_point_and_distance(second_geometry=self.pt2)

    def test_symmetric_difference(self):
        self.geom.symmetric_difference(self.geom)

    def test_touches(self):
        self.geom.touches(self.pt2)

    def test_within(self):
        self.geom.within(self.pt2)


if __name__ == "__main__":
    unittest.main()
