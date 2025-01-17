import sys

import datetime
import unittest

import pandas as pd
import arcgis
from arcgis.geometry import Geometry
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer, FeatureLayerCollection
from arcgis.features.managers import FeatureLayerManager, FeatureLayerCollectionManager
from utils.decorators import integration_test, profiles

geoms = [
    Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}}),
    Geometry(
        {
            "points": [
                [-97.06138, 32.837],
                [-97.06133, 32.836],
                [-97.06124, 32.834],
                [-97.06127, 32.832],
            ],
            "spatialReference": {"wkid": 4326},
        }
    ),
    Geometry(
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
    ),
    Geometry(
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
    ),
]


@profiles.enterprise_and_agol
@integration_test
class TestAddUpdateDeleteDef(unittest.TestCase):
    """
    Tests the Add, Update and Delete from Definitions
    """

    def test_add_to_def_fl(self):
        """
        Tests the Feature Layer Manager Add to Definition.
        A future object is returned.
        """
        add_field = {
            "fields": [
                {
                    "name": "sdfasdf",
                    "type": "esriFieldTypeString",
                    "alias": "safa",
                    "nullable": True,
                    "editable": True,
                    "length": 256,
                }
            ]
        }
        g = [
            Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}})
        ] * len(geoms)
        data = [[1, datetime.datetime.now(), True, "BLAHBLAH"]] * len(geoms)
        item = None
        try:
            df = pd.DataFrame(data=data, columns=["Alpha", "Beta", "Gamma", "Delta"])
            df.spatial.set_geometry(g)
            item = self.gis.content.import_data(
                df, name="add_to_def_fl", tags="ntgrtn-tst"
            )
            assert item
            assert isinstance(item, Item)
            fl = item.layers[0]
            assert isinstance(fl, FeatureLayer)
            future = fl.manager.add_to_definition(json_dict=add_field, future=True)
            res = future.result()
            print(res)
        finally:
            if item:
                item.delete(permanent=True)

    def test_update_to_def_fl(self):
        """
        Tests the Update Definition to the Feature Layer
        Works with a Future object.
        """
        add_field = {
            "fields": [
                {
                    "name": "sdfasdf",
                    "type": "esriFieldTypeString",
                    "alias": "safa",
                    "nullable": True,
                    "editable": True,
                    "length": 256,
                }
            ]
        }
        up_field = {
            "fields": [
                {
                    "name": "sdfasdf",
                    "type": "esriFieldTypeString",
                    "alias": "dogcat",
                    "nullable": True,
                    "editable": True,
                    "length": 256,
                }
            ]
        }
        g = [
            Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}})
        ] * len(geoms)
        item = None
        related_data = None
        data = [[1, datetime.datetime.now(), True, "BLAHBLAH"]] * len(geoms)
        try:

            df = pd.DataFrame(data=data, columns=["Alpha", "Beta", "Gamma", "Delta"])
            df.spatial.set_geometry(g)
            item = self.gis.content.import_data(
                df, title="update_to_def_fl", tags="ntgrtn-tst"
            )
            assert item
            assert isinstance(item, Item)
            fl = item.layers[0]
            assert isinstance(fl, FeatureLayer)
            fl.manager.add_to_definition(json_dict=add_field, future=False)
            future = fl.manager.update_definition(json_dict=up_field, future=True)
            res = future.result()
            assert "dogcat" in [fld["alias"] for fld in fl.properties.fields]
            related_data = item.related_items(rel_type="Service2Data")[0]
            assert related_data
        finally:
            if item:
                item.delete(permanent=True)
            if related_data:
                related_data.delete(permanent=True)

    def test_delete_to_def_fl(self):
        """
        Tests the Delete Definition to the Feature Layer
        Works with a Future object.
        """
        add_field = {
            "fields": [
                {
                    "name": "sdfasdf",
                    "type": "esriFieldTypeString",
                    "alias": "safa",
                    "nullable": True,
                    "editable": True,
                    "length": 256,
                }
            ]
        }
        del_field = {"fields": [{"name": "sdfasdf"}]}
        g = [
            Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}})
        ] * len(geoms)
        data = [[1, datetime.datetime.now(), True, "BLAHBLAH"]] * len(geoms)
        item = None
        related_data = None
        try:
            df = pd.DataFrame(data=data, columns=["Alpha", "Beta", "Gamma", "Delta"])
            df.spatial.set_geometry(g)
            item = self.gis.content.import_data(
                df, title="delete_to_def_fl", tags="ntgrtn-tst"
            )
            assert item
            assert isinstance(item, Item)
            fl = item.layers[0]
            assert isinstance(fl, FeatureLayer)
            fl.manager.add_to_definition(json_dict=add_field, future=False)
            future = fl.manager.delete_from_definition(json_dict=del_field, future=True)
            res = future.result()
            assert res
            related_data = item.related_items(rel_type="Service2Data")[0]
        finally:
            if item:
                item.delete(permanent=True)
            if related_data:
                related_data.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
