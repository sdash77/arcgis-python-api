import time
import unittest
import pandas as pd
from arcgis.features import FeatureLayer, FeatureSet
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from utils.data_utils import cleanup_published_items


enable_verbose_logging()
DATA = {
    "features": [
        {
            "geometry": {
                "x": -7751445.7466,
                "y": 5442916.671999998,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 1,
                "FID_": 1,
                "Name": "Nancy Drew",
                "Birthday": 846662400000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750856.1438,
                "y": 5442547.043399997,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 2,
                "FID_": 2,
                "Name": "George Fan",
                "Birthday": 850125600000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750607.320699999,
                "y": 5443149.2676,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 3,
                "FID_": 3,
                "Name": "Bess Marvin",
                "Birthday": 802425600000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750470.287599999,
                "y": 5442263.9619999975,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 4,
                "FID_": 4,
                "Name": "Ned Nickerson",
                "Birthday": 737798400000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7749997.884199999,
                "y": 5442260.355800003,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 5,
                "FID_": 5,
                "Name": "Ace",
                "Birthday": 558259200000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7751445.7466,
                "y": 5442916.671999998,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 6,
                "FID_": 1,
                "Name": "Nancy Drew",
                "Birthday": 846662400000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750856.1438,
                "y": 5442547.043399997,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 7,
                "FID_": 2,
                "Name": "George Fan",
                "Birthday": 850125600000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750607.320699999,
                "y": 5443149.2676,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 8,
                "FID_": 3,
                "Name": "Bess Marvin",
                "Birthday": 802425600000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750470.287599999,
                "y": 5442263.9619999975,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 9,
                "FID_": 4,
                "Name": "Ned Nickerson",
                "Birthday": 737798400000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7749997.884199999,
                "y": 5442260.355800003,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 10,
                "FID_": 5,
                "Name": "Ace",
                "Birthday": 558259200000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7751445.7466,
                "y": 5442916.671999998,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 11,
                "FID_": 1,
                "Name": "Nancy Drew",
                "Birthday": 846662400000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750856.1438,
                "y": 5442547.043399997,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 12,
                "FID_": 2,
                "Name": "George Fan",
                "Birthday": 850125600000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750607.320699999,
                "y": 5443149.2676,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 13,
                "FID_": 3,
                "Name": "Bess Marvin",
                "Birthday": 802425600000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7750470.287599999,
                "y": 5442263.9619999975,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 14,
                "FID_": 4,
                "Name": "Ned Nickerson",
                "Birthday": 737798400000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
        {
            "geometry": {
                "x": -7749997.884199999,
                "y": 5442260.355800003,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
            "attributes": {
                "FID": 15,
                "FID_": 5,
                "Name": "Ace",
                "Birthday": 558259200000,
                "Affiliatio": "DrewCrew",
                "Class": "Human",
            },
        },
    ],
    "objectIdFieldName": "FID",
    "displayFieldName": "FID",
    "spatialReference": {"wkid": 102100, "latestWkid": 3857},
    "geometryType": "esriGeometryPoint",
    "fields": [
        {"name": "FID", "type": "esriFieldTypeOID", "alias": "FID"},
        {"name": "FID_", "type": "esriFieldTypeInteger", "alias": "FID_"},
        {
            "name": "Name",
            "type": "esriFieldTypeString",
            "alias": "Name",
            "length": 13,
        },
        {
            "name": "Birthday",
            "type": "esriFieldTypeDate",
            "alias": "Birthday",
        },
        {
            "name": "Affiliatio",
            "type": "esriFieldTypeString",
            "alias": "Affiliatio",
            "length": 8,
        },
        {
            "name": "Class",
            "type": "esriFieldTypeString",
            "alias": "Class",
            "length": 5,
        },
    ],
}


@profiles.enterprise_and_agol
@integration_test
class TestApplyEditsSeDF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = []
        uid = int(time.time())
        for feat in DATA["features"][:5]:
            geom = feat["geometry"]
            att = feat["attributes"]
            att["SHAPE"] = geom
            rows.append(att)
        df = pd.DataFrame(rows)
        df.spatial.set_geometry("SHAPE")
        cls.item = cls.gis.content.import_data(
            df, title=f"edit_sedf_{uid}", tags="ntgrtn-tst"
        )

    def test_apply_edits_adds(self):
        lyr: FeatureLayer = self.item.layers[0]
        count_old = lyr.query(return_count_only=True)
        sdf = lyr.query(as_df=True).head().copy()
        print(sdf)
        res = lyr.edit_features(adds=sdf, future=True)
        count = lyr.query(return_count_only=True)
        assert count > count_old

    def test_apply_edits_update(self):
        lyr: FeatureLayer = self.item.layers[0]
        sdf = lyr.query(as_df=True).head().copy()
        results = lyr.edit_features(updates=sdf)
        assert all(
            [res.get("success", False) for res in results.get("updateResults", [])]
        )

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.item])


if __name__ == "__main__":
    unittest.main()
