import datetime
import time
import uuid
import unittest
import pandas as pd

from utils.decorators import integration_test, profiles
from utils.data_utils import cleanup_folders
from integration.config import (
    get_resource_path,
    get_json_resource,
    INTEGRATION_TEST_ITEM_TAG,
)

from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer, Table
from arcgis.features.analysis import aggregate_points


@profiles.agol
@integration_test
class TestAggregatePoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.agg_pts_test_folder = cls.gis.content.folders._get_or_create(
            "aa_aggregate_points"
        )
        cls.restaurant_data = get_json_resource(
            relative_path="/features/restaurants.json"
        )

        # add point layer to portal
        cls.sdf = pd.DataFrame(cls.restaurant_data)
        cls.restaurants_item = cls.gis.content.import_data(
            df=cls.sdf,
            folder=cls.agg_pts_test_folder.name,
            title=f"restaurants_agg_{uuid.uuid4().hex[:4]}",
            tags=INTEGRATION_TEST_ITEM_TAG,
        )
        cls.restaurants_lyr = cls.restaurants_item.layers[0]
        cls.restaurants_source = cls.restaurants_item.related_items(
            "Service2Data", "forward"
        )[0]

        # Publicly available Census Block Group Boundaries: Living Atlas
        cls.census_blks_item = cls.gis.content.get("2f5e592494d243b0aa5c253e75e792a4")
        cls.census_blks_lyr = cls.census_blks_item.layers[0]

        if not cls.restaurants_lyr:
            unittest.skip("No points layer to aggregate.")
        if not cls.census_blks_lyr:
            unittest.skip("No polygon layer to aggregate points for.")

    @classmethod
    def tearDownClass(cls):
        cleanup_folders(folder_names=[cls.agg_pts_test_folder.name], gis=cls.gis)

    def setUp(self):
        self.start_time = time.perf_counter()

    def tearDown(self):
        end_time = time.perf_counter()
        elapsed = end_time - self.start_time
        print(
            f"\n{'-' * 50}\n\n{self._testMethodName} ran in {elapsed/60:.2f} minutes\n\n{'-' * 50}\n"
        )

    def test_aggregate_group_by(self):
        self.assertEqual(
            self.restaurants_lyr.properties.geometryType,
            "esriGeometryPoint",
            "Feature layer is not point geometry.",
        )

        # create aggregate layer
        test_id = uuid.uuid4().hex[:6]
        output_name = "agg_pts_groupby_" + test_id

        agg_results_item = aggregate_points(
            point_layer=self.restaurants_lyr,
            polygon_layer=self.census_blks_lyr,
            keep_boundaries_with_no_points=False,
            group_by_field="TYPE",
            output_name=output_name,
        )
        agg_results_item.move(self.agg_pts_test_folder)

        self.assertIsInstance(
            agg_results_item, Item, "Output when specifying output_name not an item."
        )
        self.assertIsInstance(
            agg_results_item.layers[0],
            FeatureLayer,
            "Item layers output is not a FeatureLayer object.",
        )
        self.assertEqual(
            len(agg_results_item.layers[0].query().features),
            19,
            "Incorrect number of records returned, should be 19.",
        )
        self.assertTrue(
            agg_results_item.tables, "Summary table not created as expected."
        )
        self.assertIsInstance(
            agg_results_item.tables[0],
            Table,
            "Item tables output is not a Table object.",
        )
        self.assertIn(
            "Join_ID".lower(),
            [fld["name"].lower() for fld in agg_results_item.layers[0].properties.fields],
            "No Join_ID field in aggregate_points results feature layer.",
        )

        join_value = (
            agg_results_item.layers[0]
            .query(
                where="TRACT_FIPS = '011710' AND BLOCKGROUP = '1'",
                out_fields=["Join_ID"],
                as_df=True,
            )
            .loc[0]
            .Join_ID
        )

        self.assertEqual(
            agg_results_item.tables[0].query(
                where=f"Join_ID = {join_value}", return_count_only=True
            ),
            2,
            "Known Join_ID results not 2 as expected.",
        )
    @unittest.skip("for now")
    def test_aggregate_overwrite(self):
        """tests overwriting an Item layer using the context param"""

        # create layer that will be overwritten
        test_id = uuid.uuid4().hex[:6]
        output_name = "overwrite_test_agg_" + test_id
        target_item = aggregate_points(
            point_layer=self.restaurants_lyr,
            polygon_layer=self.census_blks_lyr,
            keep_boundaries_with_no_points=False,
            group_by_field="TYPE",
            output_name=output_name,
        )
        target_item.move(self.agg_pts_test_folder)

        self.assertIsInstance(target_item, Item, "Analysis output is not an item.")
        target_lyr = target_item.layers[0]
        self.assertIsInstance(
            target_lyr, FeatureLayer, "Item is not a feature service with layers."
        )
        self.assertIn(
            "Join_ID",
            [fld["name"] for fld in target_lyr.properties.fields],
            "Join_ID field not in aggregate analysis results.",
        )
        self.assertIn(
            "Point_Count",
            [fld["name"] for fld in target_lyr.properties.fields],
            "Point_count field not in aggregate analysis results.",
        )
        self.assertIn(
            "TYPE",
            [fld["name"] for fld in target_item.tables[0].properties.fields],
            "TYPE field not in aggregate analysis results.",
        )

        ## perform overwrite
        overwrite_agg_item = aggregate_points(
            point_layer=self.restaurants_lyr,
            polygon_layer=self.census_blks_lyr,
            keep_boundaries_with_no_points=False,
            group_by_field="OPTIONS",
            output_name=target_lyr,
            context={"overwrite": True},
        )
        self.assertIsInstance(
            overwrite_agg_item,
            Item,
            "Operation with overwrite context did not output item.",
        )
        self.assertEqual(
            overwrite_agg_item.id,
            target_item.id,
            "Item id did not remain the same with overwrite",
        )
        self.assertIn(
            "OPTIONS",
            [f["name"] for f in overwrite_agg_item.tables[0].properties.fields],
            "OPTIONS column not in overwrite output as expected.",
        )
        # overwrite should not append. Only one layer and one table should be present
        self.assertEqual(
            len(overwrite_agg_item.layers),
            1,
            "Overwritten item should have same number of layers as original.",
        )
        self.assertEqual(
            len(overwrite_agg_item.tables),
            1,
            "Overwritten item should have same number of tables as original.",
        )


if __name__ == "__main__":
    unittest.main()
