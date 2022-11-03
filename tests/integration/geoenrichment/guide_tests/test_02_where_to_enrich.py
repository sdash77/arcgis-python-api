import sys

# sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\tests")
# sys.path.insert(1, r"C:\ipython_workfolder\geosaurus\src")
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


if __name__ == "__main__":

    unittest.main()
