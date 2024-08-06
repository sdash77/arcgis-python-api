import unittest
from arcgis import GIS

from arcgis.features import GeoAccessor
from arcgis.geoenrichment import enrich
import pandas as pd

from integration.geoenrichment.guide_tests.config_guide_tests import usa_instance


class WhereToEnrichTest(unittest.TestCase):

    def setUp(self):
        self.usa_instance_inst = usa_instance()

    def test_data_collections(self):
        vars_df = self.usa_instance_inst.data_collections
        assert isinstance(vars_df, pd.DataFrame)
        assert len(vars_df.index.unique()) > 100

    def age_variables_df(self):
        age_df = self.usa_instance_inst.data_collections.loc["Age"]
        return age_df

    def test_enrich_single_address(self):
        age_variables_df_inst = self.age_variables_df()
        single_address = enrich(
            study_areas=["380 New York St Redlands CA 92373"],
            data_collections=["Age"],
            gis=GIS(profile="your_online_profile"),
        )
        assert isinstance(single_address, pd.DataFrame)
        assert single_address.iloc[0]["has_data"] == 1
        assert single_address.iloc[0]["SHAPE"]
    
    def test_enrich_point(self):
        from arcgis.geometry import Point
        pt = Point({"x" : -117.1956, "y" : 34.0572, "spatialReference" : {"wkid" : 4326}})
        enriched = enrich(study_areas=[pt], data_collections=['KeyGlobalFacts'], proximity_value='15', return_geometry=False)
        assert isinstance(enriched, pd.DataFrame)
        assert enriched.iloc[0]["has_data"] == 1
        assert enriched.iloc[0]["SHAPE"]

    def test_enrich_polyline(self):
        from arcgis.geometry import Polyline

        line = Polyline({"paths":[[[-13048580,4036370],[-13046151,4036366]]],
                 "spatialReference":{"wkid":102100}})
        enriched = enrich(study_areas=[line], data_collections=['Age'])

        assert isinstance(enriched, pd.DataFrame)
        assert enriched.iloc[0]["has_data"] == 1
        assert enriched.iloc[0]["SHAPE"]

    def test_enrich_polygon(self):
        from arcgis.geometry import Polygon
        poly = Polygon({"rings":[[[-117.185412,34.063170],[-122.81,37.81],
                        [-117.200570,34.057196],[-117.185412,34.063170]]],
                        "spatialReference":{"wkid":4326}})

        enriched = enrich(study_areas=[poly], data_collections=['Age'])

        assert isinstance(enriched, pd.DataFrame)
        assert enriched.iloc[0]["has_data"] == 1
        assert enriched.iloc[0]["SHAPE"]


if __name__ == "__main__":

    unittest.main()
