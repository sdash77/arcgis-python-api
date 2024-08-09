import unittest
from arcgis._impl.tools import _GeometryService
from arcgis._impl._async.jobs import GeometryJob
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestGSSettingSR(unittest.TestCase):
    """
    Tests that async operations set the spatial reference on the geometry objects
    """

    def test_setting_spatial_reference(self):
        """tests if geometry service sets the output spatial reference"""
        from arcgis.geometry.functions import intersect
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ],
                    "spatialReference": {"wkid": 4326},
                }
            ),
            Geometry(
                {
                    "paths": [[[32, 17], [31, 17], [30, 17], [30, 16]]],
                    "spatialReference": {"wkid": 4326},
                }
            ),
        ]
        geom = Geometry(
            {
                "rings": [
                    [[-117, 34], [-116, 34], [-117, 33], [-117, 34]],
                    [[-115, 44], [-114, 43], [-115, 43], [-115, 44]],
                ],
                "spatialReference": {"wkid": 4326},
            }
        )
        sr = 4326
        gis = self.gis
        geom_async = intersect(
            spatial_ref=sr,
            geometries=geoms,
            geometry=geom,
            gis=None,
            future=True,
        )
        assert geom_async
        assert "spatialReference" in geom_async.result()[0]


@integration_test
@profiles.enterprise_and_agol
class TestGeometryService(unittest.TestCase):
    """Tests the underlying Geometry Service"""

    def test_gs_area_and_lengths(self):
        """Tests the areas and lengths using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        polygons = [
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
        ]
        lengthUnit = 9095
        areaUnit = 9095
        calculationType = "preserveShape"
        sr = 4326
        j = gs.areas_and_lengths(
            polygons,
            lengthUnit,
            areaUnit,
            calculationType,
            sr=sr,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_auto_complete(self):
        """Tests the autocomplete using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        polygons = [
            {
                "rings": [
                    [[0, 0], [110, 0], [110, -60], [0, -60], [0, 0]],
                    [
                        [120, 0],
                        [180, 0],
                        [180, -60],
                        [120, -60],
                        [120, 0],
                    ],
                ]
            }
        ]
        polylines = [{"paths": [[[109, 0], [121, 0]], [[109, -60], [121, -60]]]}]
        sr = 4269
        j = gs.auto_complete(polygons, polylines, sr, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_buffer(self):
        """Tests the buffer using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        from arcgis.geometry import Geometry

        a = Geometry({"x": -8575158.562007815, "y": 4705980.159522079})
        geometries = [a]
        inSR = 4269
        outSR = None
        bufferSR = None
        distances = [10, 50]
        unit = 9035
        unionResults = False
        geodesic = True
        j = gs.buffer(
            geometries,
            inSR,
            distances,
            unit,
            outSR=outSR,
            bufferSR=bufferSR,
            unionResults=unionResults,
            geodesic=geodesic,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_convex_hull(self):
        """Tests the buffer using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            ),
            Geometry({"paths": [[[32, 17], [31, 17], [30, 17], [30, 16]]]}),
        ]
        j = gs.convex_hull(geometries=geoms, sr=4326, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_cutter(self):
        """Tests the cutter using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        from arcgis.geometry import Geometry

        cutter = Geometry(
            {
                "paths": [
                    [[-117, 34], [-116, 34], [-117, 33]],
                    [[-115, 44], [-114, 43], [-115, 43]],
                ]
            }
        )
        target = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            )
        ]
        j = gs.cut(cutter=cutter, target=target, sr=4326, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_densify(self):
        """Tests the densify using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        from arcgis.geometry import Geometry

        target = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            )
        ]
        j = gs.densify(
            geometries=target,
            sr=4326,
            maxSegmentLength=10,
            lengthUnit=9001,
            geodesic=True,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_difference(self):
        """Tests the difference using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        from arcgis.geometry import Geometry

        target = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            ),
            Geometry(
                {
                    "paths": [
                        [
                            [32.49, 17.83],
                            [31.96, 17.59],
                            [30.87, 17.01],
                            [30.11, 16.86],
                        ]
                    ]
                }
            ),
        ]
        g = Geometry(
            {
                "rings": [
                    [[-117, 34], [-116, 34], [-117, 33], [-117, 34]],
                    [[-115, 44], [-114, 43], [-115, 43], [-115, 44]],
                ]
            }
        )
        j = gs.difference(geometries=target, sr=4326, geometry=g, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_distance(self):
        """Tests the distance using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        from arcgis.geometry import Geometry

        target = Geometry({"x": -118.15, "y": 33.80})
        g = Geometry({"x": -95.23, "y": 31.71})
        geodesic = True
        sr = 4326
        j = gs.distance(
            sr=sr,
            geometry1=target,
            geometry2=g,
            distanceUnit="",
            geodesic=geodesic,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_from_geo_coordinate_string(self):
        """Tests the to_geo_coordinate_string using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)

        strings = [
            "ZGQA5999999900000000",
            "EJCE3864000012728040",
            "NKBH1196052000273924",
        ]
        conversionType = "GeoRef"
        sr = 4326
        j = gs.from_geo_coordinate_string(
            sr,
            strings,
            conversionType,
            conversionMode=None,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_generalize(self):
        """Tests the generalize using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "rings": [
                        [
                            [-87, 40],
                            [-87.1, 40.3],
                            [-87.2, 40.5],
                            [-87.2, 40.6],
                            [-86.8, 40.6],
                            [-86.7, 40.6],
                            [-86.7, 40.4],
                            [-86.7, 40.2],
                            [-87, 40],
                        ]
                    ]
                }
            )
        ]
        max_dev = 20
        units = 9035
        sr = 4326
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.generalize(
            sr,
            geometries=geoms,
            maxDeviation=max_dev,
            deviationUnit=units,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_intersect(self):
        """Tests the intersect using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            ),
            Geometry({"paths": [[[32, 17], [31, 17], [30, 17], [30, 16]]]}),
        ]
        geom = Geometry(
            {
                "rings": [
                    [[-117, 34], [-116, 34], [-117, 33], [-117, 34]],
                    [[-115, 44], [-114, 43], [-115, 43], [-115, 44]],
                ]
            }
        )
        sr = 4326
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.intersect(sr=sr, geometries=geoms, geometry=geom, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_label_points(self):
        """Tests the label points using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "rings": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            ),
            Geometry({"rings": [[[32, 17], [31, 17], [30, 17], [30, 16]]]}),
        ]

        sr = 4326
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.label_points(sr=sr, polygons=geoms, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_lengths(self):
        """Tests the lengths using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            ),
            Geometry({"paths": [[[32, 17], [31, 17], [30, 17], [30, 16]]]}),
        ]

        sr = 4326
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.lengths(
            sr=sr,
            polylines=geoms,
            lengthUnit=9001,
            calculationType="preserveShape",
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_offset(self):
        """Tests the offset using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [Geometry({"paths": [[[0, 0], [2000, 2000], [3000, 0]]]})]
        off_dist = 1000
        sr = 2229
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.offset(
            geometries=geoms,
            offsetDistance=off_dist,
            offsetUnit=9001,
            sr=sr,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_project(self):
        """Tests the project using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            ),
            Geometry({"paths": [[[32, 17], [31, 17], [30, 17], [30, 16]]]}),
        ]
        # off_dist = 1000
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.project(geometries=geoms, inSR=4326, outSR=3857, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_relation(self):
        """Tests the relation using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry({"x": -104.5, "y": 34.74}),
            Geometry({"x": -63.53, "y": 10.23}),
        ]
        geoms2 = [
            Geometry(
                {
                    "paths": [
                        [[-117, 34], [-116, 34], [-117, 33]],
                        [[-115, 44], [-114, 43], [-115, 43]],
                    ]
                }
            ),
            Geometry({"paths": [[[32, 17], [31, 17], [30, 17], [30, 16]]]}),
        ]
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.relation(
            geometries1=geoms,
            geometries2=geoms2,
            sr=4326,
            relationParam="",
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_reshape(self):
        """Tests the reshape using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = Geometry(
            {
                "rings": [
                    [[-117, 34], [-116, 34], [-117, 33], [-117, 34]],
                    [[-115, 44], [-114, 43], [-115, 43], [-115, 44]],
                ]
            }
        )

        reshaper = Geometry(
            {"paths": [[[-116.9, 33.8], [-116.9, 33], [-116, 33], [-116, 33.8]]]}
        )

        sr = 4326
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.reshape(sr=sr, target=geoms, reshaper=reshaper, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_simplify(self):
        """Tests the simplify using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry(
                {
                    "rings": [
                        [[-117, 34], [-116, 34], [-117, 33], [-117, 34]],
                        [[-115, 44], [-114, 43], [-115, 43], [-115, 44]],
                    ]
                }
            )
        ]

        sr = 4326
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.simplify(sr=sr, geometries=geoms, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_to_geo_coordinate_string(self):
        """Tests the to_geo_coordinate_string using auth and no auth"""
        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        from arcgis.geometry import Geometry

        # target = Geometry({"x": -118.15, "y": 33.80})
        # g = Geometry({"x": -95.23, "y": 31.71})
        # geodesic = True
        sr = 4326
        j = gs.to_geo_coordinate_string(
            sr=sr,
            coordinates=[[10, 10], [10, 20], [30, 30]],
            conversionType="MGRS",
            conversionMode="mgrsDefault",
            numOfDigits=8,
            addSpaces=True,
            rounding=False,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_union(self):
        """Tests the union using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            {"rings": [[[0, 0], [0, 1000000], [1000000, -1000000], [0, 0]]]},
            {"rings": [[[0, 0], [0, 1000000], [1000000, 1000000], [0, 0]]]},
        ]

        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.union(sr=3857, geometries=geoms, future=True)
        assert isinstance(j, GeometryJob)
        assert j.result()

    def test_gs_trim_extend(self):
        """Tests the trim_extend using auth and no auth"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry({"paths": [[[6805512, 1843725], [6805496, 1844963]]]}),
            Geometry({"paths": [[[6805532, 1842246], [6805523, 1842901]]]}),
        ]

        to_geom = Geometry(
            {
                "paths": [
                    [
                        [6804206, 1843554],
                        [6805395, 1843570],
                        [6805514, 1843607],
                        [6805740, 1843619],
                    ]
                ]
            }
        )

        sr = 2229
        how = 1

        gis = self.gis
        url = gis.properties.helperServices.geometry.url
        gs = _GeometryService(url=url, gis=gis)
        assert isinstance(gs, _GeometryService)
        j = gs.trim_extend(
            sr,
            polylines=geoms,
            trimExtendTo=to_geom,
            extendHow=how,
            future=True,
        )
        assert isinstance(j, GeometryJob)
        assert j.result()


if __name__ == "__main__":
    unittest.main()
