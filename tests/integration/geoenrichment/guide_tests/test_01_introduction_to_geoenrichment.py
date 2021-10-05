from arcgis.features import GeoAccessor
from arcgis.geoenrichment import Country, enrich
from arcgis.geoenrichment.enrichment import NamedArea
from arcgis.gis import GIS
import pandas as pd
import pytest

from .config_guide_tests import dir_data, source, usa_instance


@pytest.fixture
def health_facility_df():
    return pd.read_csv(dir_data / "health.csv")


@pytest.fixture
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


def test_create_country(source):
    cntry = Country.get("US", gis=source)
    assert isinstance(cntry, Country)


def test_get_subgeographies_zips(usa_instance):

    zip1 = usa_instance.subgeographies.states["California"].zip5["90018"]
    zip2 = usa_instance.subgeographies.states["California"].zip5["90023"]
    zip3 = usa_instance.subgeographies.states["California"].zip5["90035"]

    zips_valid_lst = [
        isinstance(zip_code, NamedArea) for zip_code in [zip1, zip2, zip3]
    ]
    assert all(zips_valid_lst)


def test_enrich_zip_apportionment(usa_instance, analysis_variables):

    zip1 = usa_instance.subgeographies.states["California"].zip5["90018"]
    zip2 = usa_instance.subgeographies.states["California"].zip5["90023"]
    zip3 = usa_instance.subgeographies.states["California"].zip5["90035"]

    enrich_df = enrich(
        study_areas=[zip1, zip2, zip3], analysis_variables=analysis_variables
    )

    assert isinstance(enrich_df, pd.DataFrame)
    assert enrich_df.spatial.validate()


def test_merge_on_zip(usa_instance, analysis_variables, health_facility_df):
    zip1 = usa_instance.subgeographies.states["California"].zip5["90018"]
    zip2 = usa_instance.subgeographies.states["California"].zip5["90023"]
    zip3 = usa_instance.subgeographies.states["California"].zip5["90035"]
    enrich_df = enrich(
        study_areas=[zip1, zip2, zip3], analysis_variables=analysis_variables
    )

    health_facility_df["Zip Code"] = health_facility_df["Zip Code"].apply("str")
    merged = pd.merge(
        enrich_df, health_facility_df, left_on="StdGeographyID", right_on="Zip Code"
    )
    assert isinstance(merged, pd.DataFrame)
