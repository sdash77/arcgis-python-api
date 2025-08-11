import time
import unittest
import pandas as pd
from arcgis.geometry import Geometry
from arcgis.features import Feature, FeatureSet, FeatureLayer
from utils.decorators import integration_test, profiles
from utils.data_utils import cleanup_published_items
from integration.config import get_json_resource


@profiles.enterprise_and_agol
@integration_test
class TestFeatureLayerEditFeatures(unittest.TestCase):
    """Tests the FeatureLayer.edit_features method"""

    @classmethod
    def setUpClass(cls):
        cls.items = []
        cls.uid = int(time.time())

    def setUp(self):
        test_data = get_edit_features_test_data(self.gis)
        sdf = pd.DataFrame(test_data)
        sdf.SHAPE = sdf.SHAPE.apply(lambda x: Geometry(x))
        sdf.spatial.set_geometry("SHAPE")

        self._sdf = sdf

    def test_sedf_adds(self):
        item = self.gis.content.import_data(
            self._sdf, title=f"sedf_adds_{self.uid}", tags="ntgrtn-tst"
        )
        self.items.append(item)
        resp = item.layers[0].edit_features(adds=self._sdf)
        assert resp["addResults"]

    def test_sedf_updates(self):
        """tests performing the updates with SeDF"""
        item = self.gis.content.import_data(
            self._sdf, title=f"sedf_updates_{self.uid}", tags="ntgrtn-tst"
        )
        self.items.append(item)
        update_sdf = self._sdf.head().copy()
        update_sdf["OBJECTID"] = range(len(update_sdf))
        update_sdf["OBJECTID"] += 1
        respupdate = item.layers[0].edit_features(updates=update_sdf)
        assert respupdate["updateResults"]

    def test_deletes(self):
        """tests performing the updates with SeDF"""
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_deletes_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            sdf = item.layers[0].query(as_df=True)
            oidfld = "OBJECTID"
            for fld in sdf.columns:
                if item.layers[0].properties.objectIdField.lower() == fld.lower():
                    oidfld = fld
                    break

            resp = item.layers[0].edit_features(deletes=sdf[oidfld].tolist())
            assert resp["deleteResults"]
        except Exception as e:
            raise e

    def test_featureset_adds(self):
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_fs_adds_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            sdf = self._sdf.head().copy()
            sdf_updates = self._sdf.tail().copy()
            sdf_updates["OBJECTID"] = range(len(sdf_updates))
            sdf_updates["OBJECTID"] += 1
            fs = sdf_updates.spatial.to_featureset()
            assert fs
            fs_adds = sdf.spatial.to_featureset()

            resp = item.layers[0].edit_features(adds=fs_adds)
            assert resp["addResults"]
        except Exception as e:
            raise e

    def test_featureset_updates(self):
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_fs_updates_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            sdf = item.layers[0].query(as_df=True)
            sdf_updates = sdf.tail().copy().head()
            sdf_updates["OBJECTID"] = range(len(sdf_updates))
            sdf_updates["OBJECTID"] += 1

            resp = item.layers[0].edit_features(
                updates=sdf_updates.spatial.to_featureset()
            )

            assert resp["updateResults"]
        except Exception as e:
            raise e

    def test_dict_adds(self):
        """
        Tests adding content via List[Dict[str, Any]
        """
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_dict_adds_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            sdf = self._sdf.head().copy()
            fs = sdf.spatial.to_featureset()
            adds = [feat.as_dict for feat in fs.features]
            resp = item.layers[0].edit_features(adds=adds)
            assert resp["addResults"]
        except Exception as e:
            raise e

    def test_dict_updates(self):
        """
        Tests updates content via List[Dict[str, Any]
        """
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_dict_updates_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            sdf = self._sdf.head().copy()
            fs = sdf.spatial.to_featureset()
            updates = [feat.as_dict for feat in fs.features]
            resp = item.layers[0].edit_features(updates=updates)
            assert resp["updateResults"]
        except Exception as e:
            raise e

    def test_list_features_adds(self):
        """
        Tests updates content via List[Feature]
        """
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_list_adds_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            sdf = self._sdf.head().copy()
            fs = sdf.spatial.to_featureset()
            features = fs.features
            lyr = item.layers[0]
            resp = lyr.edit_features(adds=features)
            assert resp
        except Exception as e:
            raise e

    def test_list_features_adds_no_attributes(self):
        """
        Tests updates content via List[Feature]
        """
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_list_adds_no_attr_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            feature_layer: FeatureLayer = item.layers[0]

            geometry = Geometry(
                {"y": 32.1, "x": 32.1, "spatialReference": {"wkid": 4326}}
            )

            # this throws the error
            resp = feature_layer.edit_features(adds=[Feature(geometry=geometry)])
            assert resp
        except Exception as e:
            raise e

    @unittest.skip("not yet")
    def test_asset_maps(self):
        try:
            item = self.gis.content.import_data(
                self._sdf, title=f"sedf_asset_maps_{self.uid}", tags="ntgrtn-tst"
            )
            self.items.append(item)
            feature_layer: FeatureLayer = item.layers[0]

            adds = [
                {
                    "attributes": {
                        "case_": "HZ104460",
                        "VALUE": 94820.37,
                        "secondary": "OVER $500",
                        "location_d": "CONSTRUCTION SITE",
                        "GlobalID": "{064185b3-d827-fa42-a9bb-aff1ccb9b6a1}",
                    }
                }
            ]
            asset_maps = {
                "adds": [
                    {
                        "globalId": "{c9e887e9-c8bd-4014-be62-03e5b0f7b25f}",
                        "parentGlobalId": "{064185b3-d827-fa42-a9bb-aff1ccb9b6a1}",
                        "assetName": "geometry.glb",
                        "assetHash": "6486ee53c8faba18045ef29d382f1c8227bde3a25d37f7a62fe0d2259a3a14dd",
                        "flags": ["PROJECT_VERTICES"],
                    }
                ]
            }
            # this throws the error
            resp = feature_layer.edit_features(adds=adds, asset_maps=asset_maps)
        except Exception as e:
            raise e

    @classmethod
    def generate_test_data(cls):
        test_data = get_json_resource("features/edit.json")
        if cls.gis._is_arcgisonline:
            # datetime offset not supported in hosted enterprise FLs
            # test using DateTimeOffset with AGOL
            for feature in test_data:
                if "ts" in feature:
                    feature["ts"] = Timestamp(feature["ts"])

        return test_data

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.items)


if __name__ == "__main__":
    unittest.main()
