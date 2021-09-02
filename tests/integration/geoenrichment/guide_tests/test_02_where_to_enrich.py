from arcgis.features import GeoAccessor
from arcgis.geoenrichment import Country, enrich, BufferStudyArea
from arcgis.geoenrichment.enrichment import NamedArea
from arcgis.gis import GIS
import pandas as pd
import pytest

from .config_guide_tests import dir_data, source, usa_instance, local_ba_avail


def test_data_collections(usa_instance):
    vars_df = usa_instance.data_collections
    assert isinstance(vars_df, pd.DataFrame)
    assert len(vars_df.index.unique()) > 140


@pytest.fixture
def age_variables_df(usa_instance):
    age_df = usa_instance.data_collections.loc['Age']
    return age_df


def test_enrich_single_address(usa_instance, age_variables_df):
    single_address = enrich(study_areas=["380 New York St Redlands CA 92373"], data_collections=['Age'],
                            gis=usa_instance)
    assert isinstance(single_address, pd.DataFrame)
    assert all([col in age_variables_df.analysisVariable.str.split('.') for col in single_address.columns])