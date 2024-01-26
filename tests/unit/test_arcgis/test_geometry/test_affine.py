import unittest
from arcgis.geometry.affine import skew, scale, rotate, translate
from arcgis.geometry import Geometry

#############################################################################
class TestAffine(unittest.TestCase):
    """
    tests the affine functions on dictionaries and arcgis.Geometry objects.
    """

    def setUp(self):
        self.shapes = [
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
            },
            {"x": 50, "y": 60},
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
            },
            {
                "points": [
                    [-97.06138, 32.837],
                    [-97.06133, 32.836],
                    [-97.06124, 32.834],
                    [-97.06127, 32.832],
                ],
                "spatialReference": {"wkid": 4326},
            },
        ]

    def test_translate(self):
        res = []
        for shape in self.shapes:
            val_dict = isinstance(translate(shape, -10, 10), dict)
            val_geom = isinstance(translate(Geometry(shape), -10, 10), Geometry)
            res.append(val_dict)
            res.append(val_geom)
        self.assertTrue(all(res))

    def test_skew(self):
        res = []
        for shape in self.shapes:
            val_dict = isinstance(skew(shape, x_angle=45, y_angle=-20), dict)
            val_geom = isinstance(
                skew(Geometry(shape), x_angle=45, y_angle=-20), Geometry
            )
            res.append(val_dict)
            res.append(val_geom)
        self.assertTrue(all(res))

    def test_rotate(self):
        res = []
        for shape in self.shapes:
            val_dict = isinstance(rotate(shape, 45), dict)
            val_geom = isinstance(rotate(Geometry(shape), 45), Geometry)
            res.append(val_dict)
            res.append(val_geom)
        self.assertTrue(all(res))

    def test_scale(self):
        res = []
        for shape in self.shapes:
            val_dict = isinstance(scale(shape, 45, 45), dict)
            val_geom = isinstance(scale(Geometry(shape), 45, 45), Geometry)
            res.append(val_dict)
            res.append(val_geom)
        self.assertTrue(all(res))

    def test_scale_on_geom(self):
        res = []
        for shape in self.shapes:
            g = Geometry(shape)
            res.append(isinstance(g.scale(0.10, 0.20), Geometry))
            res.append(isinstance(g.scale(0.10, 0.10, True), Geometry))
        self.assertTrue(all(res))

    def test_rot_on_geom(self):
        res = []
        for shape in self.shapes:
            g = Geometry(shape)
            res.append(isinstance(g.rotate(theta=25), Geometry))
            res.append(isinstance(g.rotate(25, True), Geometry))
        self.assertTrue(all(res))

    def test_skew_on_geom(self):
        res = []
        for shape in self.shapes:
            g = Geometry(shape)
            res.append(isinstance(g.skew(25, 0, inplace=False), Geometry))
            res.append(isinstance(g.skew(45, 45, inplace=True), Geometry))
        self.assertTrue(all(res))

    def test_translate_on_geom(self):
        res = []
        for shape in self.shapes:
            g = Geometry(shape)
            res.append(isinstance(g.translate(x_offset=3, y_offset=3), Geometry))
            res.append(
                isinstance(g.translate(x_offset=3, y_offset=3, inplace=True), Geometry)
            )
        self.assertTrue(all(res))


if __name__ == "__main__":
    unittest.main()
