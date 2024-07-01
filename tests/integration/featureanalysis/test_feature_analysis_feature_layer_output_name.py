import string
import random
import unittest
from arcgis.features.analysis import aggregate_points
from utils.decorators import integration_test, profiles


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


@profiles.agol
@integration_test
class TestPassingDictionaries(unittest.TestCase):
    """Tests passing in output names as dictionaries to WebGIS Tools"""

    def test_analysis_on_existing_fl(self):
        """tests adding to an existing feature layer"""
        print(self.gis.url)
        point_item = self.gis.content.get("1923d4e74ac947dab4f8c94d2c2a7a9c")
        polygon_item = self.gis.content.get("4880937c7c684b9ead67e2570d946fbf")
        point_layer = point_item.layers[0]
        polygon_layer = polygon_item.layers[0]
        # 1). Step 1 - create an initial output:
        agg_init = aggregate_points(
            point_layer=point_layer,
            polygon_layer=polygon_layer,
            keep_boundaries_with_no_points=False,
            summary_fields=["DeclValNu mean", "DeclValNu2 mean"],
            group_by_field="ZIP_code",
            output_name="agg" + id_generator(),
        )
        existing_lyr = agg_init.layers[0]
        # 2). Step 2. Take output from step 1 and pass in the feature layer.
        agg_add_item = aggregate_points(
            point_layer=point_layer,
            polygon_layer=polygon_layer,
            keep_boundaries_with_no_points=False,
            summary_fields=["DeclValNu mean", "DeclValNu2 mean"],
            group_by_field="ZIP_code",
            output_name=existing_lyr,
        )
        assert agg_add_item.itemid == agg_init.itemid
        assert agg_add_item.layers[0].url == agg_init.layers[0].url
        assert agg_add_item.delete()


if __name__ == "__main__":
    unittest.main()
