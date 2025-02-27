import sys

import datetime
import unittest
from concurrent.futures import Future

import pandas as pd
from arcgis.gis import GIS, Item
from arcgis.geometry import Geometry
from arcgis.features import FeatureLayer
from utils.decorators import integration_test, profiles


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
            Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.25, "y": 33.85, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.35, "y": 33.90, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.45, "y": 33.95, "spatialReference": {"wkid": 4326}}),
        ]
        data = [[1, datetime.datetime.now(), True, "BLAHBLAH"]] * len(g)
        df = pd.DataFrame(data=data, columns=["Alpha", "Beta", "Gamma", "Delta"])
        df.spatial.set_geometry(g)
        item = self.gis.content.import_data(df)
        source_item = item.related_items("Service2Data", "forward")[0]
        for i in [item, source_item]:
            i.update({"tags": item.tags + ["ntgrtn-tst"]})
        assert item
        assert isinstance(item, Item)
        fl = item.layers[0]
        assert isinstance(fl, FeatureLayer)
        orig_fields_len = len(fl.properties.fields)
        future = fl.manager.add_to_definition(json_dict=add_field, future=True)
        if isinstance(future, Future):
            res = future.result()
        fl._refresh()
        self.assertLess(
            orig_fields_len,
            len(fl.properties.fields),
            "Field length values are the same when they should differ.",
        )
        item.delete(permanent=True)
        source_item.delete(permanent=True)

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

        g = [
            Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.25, "y": 33.85, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.35, "y": 33.90, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.45, "y": 33.95, "spatialReference": {"wkid": 4326}}),
        ]
        data = [[1, datetime.datetime.now(), True, "BLAHBLAH"]] * len(g)
        df = pd.DataFrame(data=data, columns=["Alpha", "Beta", "Gamma", "Delta"])
        df.spatial.set_geometry(g)
        item = self.gis.content.import_data(df)
        source_item = item.related_items("Service2Data", "forward")[0]
        assert item
        assert isinstance(item, Item)
        for i in [item, source_item]:
            i.update({"tags": item.tags + ["ntgrtn-tst"]})
        fl = item.layers[0]
        assert isinstance(fl, FeatureLayer)
        fl = item.layers[0]
        orig_fields_len = len(fl.properties.fields)
        future = fl.manager.add_to_definition(json_dict=add_field, future=False)
        if isinstance(future, Future):
            res = future.result()
        fl._refresh()
        self.assertLess(
            orig_fields_len,
            len(fl.properties.fields),
            "Field lengths should be different.",
        )
        del_field = {"fields": [{"name": "sdfasdf"}]}
        future = fl.manager.delete_from_definition(json_dict=del_field, future=True)
        if isinstance(future, Future):
            res = future.result()
        fl._refresh()
        self.assertEqual(
            orig_fields_len,
            len(fl.properties.fields),
        )
        item.delete(permanent=True)
        source_item.delete(permanent=True)

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
            Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.25, "y": 33.85, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.35, "y": 33.90, "spatialReference": {"wkid": 4326}}),
            Geometry({"x": -118.45, "y": 33.95, "spatialReference": {"wkid": 4326}}),
        ]
        data = [[1, datetime.datetime.now(), True, "BLAHBLAH"]] * len(g)
        df = pd.DataFrame(data=data, columns=["Alpha", "Beta", "Gamma", "Delta"])
        df.spatial.set_geometry(g)
        item = self.gis.content.import_data(df)
        source_item = item.related_items("Service2Data", "forward")[0]
        assert item
        assert isinstance(item, Item)
        for i in [item, source_item]:
            i.update({"tags": item.tags + ["ntgrtn-tst"]})
        fl = item.layers[0]
        assert isinstance(fl, FeatureLayer)
        orig_fields_len = len(fl.properties.fields)
        res = fl.manager.add_to_definition(json_dict=add_field, future=False)
        fl._refresh()
        self.assertGreater(
            len(fl.properties.fields),
            orig_fields_len,
            "Total number of fields should be more than original layer.",
        )
        future = fl.manager.update_definition(json_dict=up_field, future=True)
        if isinstance(future, Future):
            res = future.result()
        self.assertEqual(len(fl.properties.fields), 6)
        fl._refresh()
        assert "dogcat" in [fld["alias"] for fld in fl.properties.fields]
        item.delete(permanent=True)
        source_item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
