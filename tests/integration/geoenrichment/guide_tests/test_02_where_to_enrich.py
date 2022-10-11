import unittest

from arcgis.features import GeoAccessor
from arcgis.geoenrichment import Country, enrich, BufferStudyArea
from arcgis.geoenrichment.enrichment import NamedArea
from arcgis.gis import GIS
import pandas as pd

from .config_guide_tests import dir_data, source, usa_instance, local_ba_avail, agol


class WhereToEnrichTest(unittest.TestCase):

    def setUp(self):
        self.usa_instance_inst = usa_instance()

    def test_data_collections(self):
        vars_df = self.usa_instance_inst.data_collections
        assert isinstance(vars_df, pd.DataFrame)
        assert len(vars_df.index.unique()) > 140

    def age_variables_df(self):
        age_df = self.usa_instance_inst.data_collections.loc["Age"]
        return age_df

    def test_enrich_single_address(self):
        age_variables_df_inst = self.age_variables_df()
        single_address = enrich(
            study_areas=["380 New York St Redlands CA 92373"],
            data_collections=["Age"],
            gis=agol,
        )
        assert isinstance(single_address, pd.DataFrame)
        assert all(
            [
                var in single_address.columns
                for var in age_variables_df_inst.analysisVariable.apply(
                    lambda val: val.split(".")[1]
                )
            ]
        )


if __name__ == "__main__":

    unittest.main()
