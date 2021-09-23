from arcgis.features import GeoAccessor
from arcgis.geoenrichment import Country, enrich, BufferStudyArea
from arcgis.geoenrichment.enrichment import NamedArea
from arcgis.gis import GIS
import pandas as pd
import pytest

from .config_guide_tests import dir_data, source, usa_instance, local_ba_avail, agol


def test_data_collections(usa_instance):
    vars_df = usa_instance.data_collections
    assert isinstance(vars_df, pd.DataFrame)
    assert len(vars_df.index.unique()) > 140


@pytest.fixture
def age_variables_df(usa_instance):
    age_df = usa_instance.data_collections.loc["Age"]
    return age_df


def test_enrich_single_address(age_variables_df):
    single_address = enrich(
        study_areas=["380 New York St Redlands CA 92373"],
        data_collections=["Age"],
        gis=agol,
    )
    assert isinstance(single_address, pd.DataFrame)
    assert all(
        [
            var in single_address.columns
            for var in age_variables_df.analysisVariable.apply(
                lambda val: val.split(".")[1]
            )
        ]
    )
