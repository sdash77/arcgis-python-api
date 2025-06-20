import unittest

from arcgis.features import GeoAccessor
from arcgis.geoenrichment import Country, enrich
from arcgis.geoenrichment.enrichment import NamedArea
from arcgis.gis import GIS
from arcgis.geometry import Polygon
import pandas as pd

from integration.geoenrichment.guide_tests.config_guide_tests import dir_data, source, usa_instance


def health_facility_df():
    return pd.read_csv(dir_data / "health.csv")


def analysis_variables():
    var_lst = [
        "TOTPOP_CY",  # Population: Total Population (Esri)
        "DIVINDX_CY",  # Diversity Index (Esri)
        "AVGHHSZ_CY",  # Average Household Size (Esri)
        "MEDAGE_CY",  # Age: Median Age (Esri)
        "MEDHINC_CY",  # Income: Median Household Income (Esri)
        "BACHDEG_CY",  # Education: Bachelor's Degree (Esri)
    ]
    return var_lst


class IntroductionToGeoenrichmentTest(unittest.TestCase):

    def setUp(self):
        self.source_inst = GIS(profile="your_online_profile")
        self.usa_instance_inst = usa_instance()
        self.analysis_variables_inst = analysis_variables()
        self.health_facility_df_inst = health_facility_df()

    def test_create_country(self):
        cntry = Country.get("US", gis=GIS(profile="your_online_profile"))
        assert isinstance(cntry, Country)

    def test_get_subgeographies_zips(self):
        zip1 = self.usa_instance_inst.subgeographies.states["California"].zip5["90018"]
        zip2 = self.usa_instance_inst.subgeographies.states["California"].zip5["90023"]
        zip3 = self.usa_instance_inst.subgeographies.states["California"].zip5["90035"]

        zips_valid_lst = [
            isinstance(zip_code, NamedArea) for zip_code in [zip1, zip2, zip3]
        ]
        assert all(zips_valid_lst)

    def test_enrich_zip_apportionment(self):
        zip1 = self.usa_instance_inst.subgeographies.states["California"].zip5["90018"]
        zip2 = self.usa_instance_inst.subgeographies.states["California"].zip5["90023"]
        zip3 = self.usa_instance_inst.subgeographies.states["California"].zip5["90035"]

        enrich_df = enrich(
            study_areas=[zip1, zip2, zip3], analysis_variables=self.analysis_variables_inst
        )

        assert isinstance(enrich_df, pd.DataFrame)
        assert enrich_df.spatial.length
        assert enrich_df.spatial.area
        assert isinstance(enrich_df.spatial.bbox, Polygon)

    def test_merge_on_zip(self):
        zip1 = self.usa_instance_inst.subgeographies.states["California"].zip5["90018"]
        zip2 = self.usa_instance_inst.subgeographies.states["California"].zip5["90023"]
        zip3 = self.usa_instance_inst.subgeographies.states["California"].zip5["90035"]
        enrich_df = enrich(
            study_areas=[zip1, zip2, zip3], analysis_variables=self.analysis_variables_inst
        )

        self.health_facility_df_inst["Zip Code"] = self.health_facility_df_inst["Zip Code"].apply("str")
        merged = pd.merge(
            enrich_df, self.health_facility_df_inst, left_on="std_geography_id", right_on="Zip Code"
        )
        assert isinstance(merged, pd.DataFrame)


if __name__ == "__main__":

    unittest.main()
