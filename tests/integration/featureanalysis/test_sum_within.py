import unittest, os
import json, uuid

import pandas as pd

from arcgis import GIS
from arcgis.features.summarize_data import aggregate_points, summarize_within
from arcgis.features import FeatureCollection, FeatureSet

PROFILES = ["your_online_profile", "your_enterprise_profile"]


def create_gis(profile: str) -> GIS:
    return GIS(
        profile=profile,
        verify_cert=False,
        trust_env=True,
    )


class FeatureAnalysisSumWithin(unittest.TestCase):
    def test_no_sum_layer(self):

        # Input feature collection path
        feat_collection_path = (
            r"\\qalab_server\pyunit\ArcGISOnline\featureCollections\france_cities.json"
        )
        if os.path.isfile(feat_collection_path):
            for profile in PROFILES:
                with open(feat_collection_path) as json_file:
                    point_data = FeatureCollection(json.load(json_file))

                output_sw = summarize_within(
                    sum_within_layer=None,
                    summary_layer=point_data,
                    sum_shape=True,
                    group_by_field=None,
                    minority_majority=False,
                    percent_shape=False,
                    output_name=f"SW_nopoly{uuid.uuid4().hex[:4]}",
                    context=None,
                    estimate=False,
                    future=True,
                    bin_type="HEXAGON",
                    bin_size=10,
                    bin_size_unit="Miles",
                    gis=create_gis(profile),
                )
                result = output_sw.result()
                assert result
                result.delete()

    def test_with_sum_layer(self):

        # Input feature collection path
        feat_collection_path = (
            r"\\qalab_server\pyunit\ArcGISOnline\featureCollections\france_cities.json"
        )

        if os.path.isfile(feat_collection_path):
            for profile in PROFILES:
                with open(feat_collection_path) as json_file:
                    point_data = FeatureCollection(json.load(json_file))
                sdf = FeatureSet.from_dict(dict(point_data.layer)["featureSet"]).sdf
                geom = sdf.spatial.bbox
                row = [[1, geom, "full_extent"]]
                columns = ["OBJECTID", "SHAPE", "description"]
                sdf = pd.DataFrame(row, columns=columns)
                sdf.spatial.name
                sdf.spatial.set_geometry("SHAPE")
                output_sw = summarize_within(
                    sum_within_layer=sdf.spatial.to_feature_collection(),
                    summary_layer=point_data,
                    sum_shape=True,
                    group_by_field=None,
                    minority_majority=False,
                    percent_shape=False,
                    output_name=f"SW_nopoly{uuid.uuid4().hex[:4]}",
                    context=None,
                    estimate=False,
                    future=True,
                    gis=create_gis(profile),
                )
                result = output_sw.result()
                assert result
                result.delete()


if __name__ == "__main__":
    unittest.main()
