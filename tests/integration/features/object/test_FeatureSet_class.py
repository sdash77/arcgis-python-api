# -------------------------------------------------------------------------------
# Name:        Feature class tests
# Purpose:     Tests for checking the save function of the feature class works properly.
# -------------------------------------------------------------------------------
import unittest
from arcgis import features
from integration.config import QALAB_ROOT_PATH
import datetime
import os
import tempfile
from utils.decorators import integration_test, profiles
from arcgis.auth.tools import LazyLoader

arcgismapping = LazyLoader("arcgis.map")


@profiles.enterprise_and_agol
@integration_test
class Test_Feature_class(unittest.TestCase):
    """
    Test to check if a UserManager object works with builtin portal
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(
            cls.qalab_base_path, "features_mod_FeatureSet_cls"
        )

        print("==================================================================")
        print("Beginning tests in Test_Feature_class")
        # endregion

    def test_save_featureSet_withFeatures_to_csv_method(self):
        """
        Test to check if the save function operates successfully when a non-empty featureSet is to be saved to a CSV file
        :return:
        """
        try:
            temp = None
            # using Living Atlas curated content Transportation item
            item_id = "c68d7c5e350c47cb9ad7ac491c327115"
            content = self.gis.content.get(item_id)

            layer = content.layers[0]
            features_req = layer.query(where="Nombre = 'Espana'")

            csv_file = r"generatedCSVfile_ferroviaria.csv"
            path = tempfile.gettempdir()
            temp = features_req.save(path, csv_file)

            print(temp)

            self.assertEqual(
                temp, os.path.join(path, csv_file), "CSV file not created successfully"
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_save_featureSet_withoutFeatures_to_csv_method(self):
        """
        Test to check if the save function operates successfully when an empty featureSet is to be saved to a CSV file
        :return:
        """
        try:
            # using Living Atlas curated content Transportation item
            item_id = "c68d7c5e350c47cb9ad7ac491c327115"
            content = self.gis.content.get(item_id)

            layer = content.layers[0]
            features_req = layer.query(where="OBJECTID = -1")

            csv_file = r"generatedCSVfile_nofeat.csv"
            path = tempfile.gettempdir()
            temp = features_req.save(path, csv_file)

            self.assertEqual(
                temp, os.path.join(path, csv_file), "CSV file not created successfully"
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_create_featureSet_withFeatures_from_geojson_method(self):
        """
        Test to check if the from_geojson function operates successfully when a non-empty featureSet is to be created
        from GeoJSON file
        :return:
        """
        try:
            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": "EONET_4176",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [
                                [128.9, -8.7],
                                [129.1, -8.7],
                                [128.9, -9.1],
                                [129.1, -9.4],
                                [129, -9.6],
                                [128.8, -9.4],
                                [128.5, -9.3],
                            ],
                            "date": [
                                "2019-05-09T00:00:00Z",
                                "2019-05-09T06:00:00Z",
                                "2019-05-09T12:00:00Z",
                                "2019-05-09T18:00:00Z",
                                "2019-05-10T00:00:00Z",
                                "2019-05-10T06:00:00Z",
                                "2019-05-10T12:00:00Z",
                            ],
                            "spatialReference": {"wkid": 4326},
                        },
                        "properties": {
                            "id": "EONET_4176",
                            "title": "Tropical Cyclone Lili",
                            "date": "2019-05-09T00:00:00Z",
                            "OBJECTID": 7,
                            "SHAPE": {
                                "paths": [
                                    [
                                        [128.9, -8.7],
                                        [129.1, -8.7],
                                        [128.9, -9.1],
                                        [129.1, -9.4],
                                        [129, -9.6],
                                        [128.8, -9.4],
                                        [128.5, -9.3],
                                    ]
                                ],
                                "spatialReference": {"wkid": 4326},
                            },
                        },
                    },
                    {
                        "type": "Feature",
                        "id": "EONET_4178",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [24.7758, 56.08683],
                            "date": "2019-05-07T16:27:00Z",
                        },
                        "properties": {
                            "id": "EONET_4178",
                            "title": "Wildfires - Lithuania and Latvia",
                            "date": "2019-05-07T16:27:00Z",
                            "OBJECTID": 8,
                            "SHAPE": {
                                "x": 24.7758,
                                "y": 56.08683,
                                "spatialReference": {"wkid": 4326},
                            },
                        },
                    },
                    {
                        "type": "Feature",
                        "id": "EONET_354",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [127.84286499023438, 1.6633016286241373],
                                    [127.84286499023438, 1.7379700300000804],
                                    [127.91641235351562, 1.7379700300000804],
                                    [127.91641235351562, 1.6633016286241373],
                                    [127.84286499023438, 1.6633016286241373],
                                ]
                            ],
                            "date": ["2016-03-16T00:00:00Z"],
                        },
                        "properties": {
                            "id": "EONET_354",
                            "title": "Dukono Volcano, Indonesia",
                            "date": "2016-03-16T00:00:00Z",
                            "OBJECTID": 114,
                            "SHAPE": {
                                "rings": [
                                    [
                                        [127.84286499023438, 1.6633016286241373],
                                        [127.84286499023438, 1.7379700300000804],
                                        [127.91641235351562, 1.7379700300000804],
                                        [127.91641235351562, 1.6633016286241373],
                                        [127.84286499023438, 1.6633016286241373],
                                    ]
                                ],
                                "spatialReference": {"wkid": 4326},
                            },
                        },
                    },
                ],
            }

            from arcgis.features import Feature, FeatureSet, FeatureCollection
            from arcgis.geometry import Geometry

            f_set = FeatureSet.from_geojson(geojson)
            self.assertIsNotNone(f_set, "from_geojson failed!")

            fc = FeatureCollection.from_featureset(
                f_set,
                symbol=None,
                name="Natural Disaster Feed Events Feature Collection",
            )
            self.assertEqual(len(fc.query()), 3, "from_featureset failed!")

            df = fc.query().sdf
            map_g = self.gis.map()
            for ea in fc.query():
                msg = (
                    "Failed to get geoextent from ",
                    ea.geometry_type,
                    " - ",
                    ea.get_value("title"),
                    " - ",
                    ea.geometry,
                    " - ",
                    ea.get_value("date"),
                )
                self.assertIsInstance(Geometry(ea.geometry).extent, tuple, msg)

                if ea.get_value("type") == "LineString":
                    df_sel = df[df["OBJECTID"] == ea.attributes["OBJECTID"]]
                    df_sel.spatial.plot(
                        map_widget=map_g,
                        name=ea.get_value("title"),
                    )

                elif ea.get_value("type") == "Point":
                    df_sel = df[df["OBJECTID"] == ea.attributes["OBJECTID"]]
                    df_sel.spatial.plot(
                        map_widget=map_g,
                        name=ea.get_value("title"),
                    )
                else:  # Polygon
                    df_sel = df[df["OBJECTID"] == ea.attributes["OBJECTID"]]
                    # create the simple renderer dataclass
                    simple_renderer = arcgismapping.renderers.SimpleRenderer(
                        symbol=arcgismapping.symbols.SimpleMarkerSymbolEsriSMS(
                            style=arcgismapping.symbols.SimpleMarkerSymbolStyle.esriSMSCircle,
                            color=[255, 0, 0, 255],
                            size=12,
                            outline=arcgismapping.symbols.SimpleLineSymbolEsriSLS(
                                style=arcgismapping.symbols.SimpleLineSymbolStyle.esriSLSSolid,
                                color=[0, 0, 0, 255],
                                width=1,
                            ),
                        )
                    )
                    df_sel.spatial.plot(
                        map_widget=map_g,
                        name=ea.get_value("title"),
                        renderer=simple_renderer,
                    )

            wm_title = "Unit Test Natural Disasters (FC only) Collection"
            wm_item = self.gis.content.search(wm_title, item_type="Web Map")
            if wm_item:
                wm_item[0].delete()
            web_map_properties = {
                "title": wm_title,
                "snippet": "This web map contains multiple FC",
                "tags": "ArcGIS Python API, Unit Test",
            }

            wm_item = map_g.save(item_properties=web_map_properties)
            self.assertIsNotNone(wm_item, "save failed!")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_create_featureSet_with_one_feature(self):
        line_fs = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "geometry": {"paths": [[[-80.7, 35.1], [-80.8, 35.2]]]},
                        "attributes": {"ObjectID": 1},
                    }
                ],
                "objectIdFieldName": "ObjectID",
                "spatialReference": {"wkid": 4326},
                #         "geometryType": "esriGeometryPolyline",
                "fields": [
                    {
                        "name": "ObjectID",
                        "alias": "ObjectID",
                        "type": "esriFieldTypeOID",
                        "sqlType": "sqlTypeOther",
                    }
                ],
            }
        )
        assert line_fs.geometry_type

    def tearDown(self):
        print("------------------------------------------------------------------\n")


if __name__ == "__main__":
    unittest.main()
