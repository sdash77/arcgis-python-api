from configparser import ConfigParser
from contextlib import contextmanager
import os
from pathlib import Path
from warnings import warn

from arcgis.features import GeoAccessor
from arcgis.geoenrichment import Country
from arcgis.geoenrichment._business_analyst._utils import (
    local_business_analyst_avail,
    local_ba_data_avail,
    module_avail,
)
from arcgis.gis import GIS
import pandas as pd
import unittest

__all__ = ['usa_local', 'usa_local_enrich_vars', 'usa_agol', 'usa_agol_enrich_vars',
           'polygon_df', 'line_df', 'point_df', 'stdgeo_srs']

# get the path to the data resources
_dir_test_geoenrichment = Path(__file__).parent
_dir_data = _dir_test_geoenrichment / "geoenrich_data"

# if present, use python dotenv, but roll back to configparser if not
if module_avail("dotenv"):
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())

# see if credentials are available for ArcGIS Online and flag if cannot connect for any reason
try:
    gis = GIS(profile="your_online_profile")
except Exception as e:
    gis = GIS(
        url="https://geosaurus.maps.arcgis.com",
        username="headless_testing",
        password="Esr!3801",
    )
agol_avail = True

abbreviated_test = True

# use configfile if still not set

config = ConfigParser()
config.read(_dir_test_geoenrichment / 'config.ini')
_agol_url, _agol_user, _agol_pass = (
    "https://geosaurus.maps.arcgis.com",
    gis._username,
    gis._password,
)


def _get_filtered_enrich_variables(usa: Country) -> pd.DataFrame:
    # get the available enrichment variables
    ev = usa.enrich_variables

    # create filter for all race, ethnicity, industry and occupation variables
    race_variable_names = ev[
        (ev.data_collection == 'raceandhispanicorigin')
        | (ev.data_collection == 'Age_by_Sex_by_Race_Profile_rep')
        | (ev.data_collection == 'agebyracebysex')
        | (ev.data_collection == 'occupation')
        | (ev.data_collection == 'industry')
        ].name

    # filter to just variables we are interested in
    sel_vars = ev[
        (ev.name.str.endswith('CY'))  # retrieve all current year variables
        & (~ev.name.isin(race_variable_names))  # exclude all race and ethnicity variables
        & (~ev.alias.str.contains('\${0,1}\d*K{0,1}-\${0,1}\d+'))  # exclude income range count variables
        & (~ev.alias.str.contains('\d{1,2}-\d{1,2}'))  # exclude five year age ranges
        & (~ev.alias.str.contains('Age <{0,1}\d{1,2}'))  # exclude exact year age counts
        & (~ev.alias.str.contains('[6|7|8]5\+$'))  # exclude all the senior dependent grouped age variables
        & (~ev.alias.str.contains('\(Esri|ESRI\S\)'))  # exclude yr over yr variables (captured in summary stats)
        ].drop_duplicates('name').reset_index(drop=True)

    return sel_vars


# if the local environment is configured with arcpy (Pro), Business Analyst and local data
if local_business_analyst_avail() and local_ba_data_avail():
    local_ba_avail = True
else:
    local_ba_avail = False
    warn(
        "Cannot test the Business Analyst using local resources since ArcGIS Pro with the Business Analyst "
        "extension with at least one country's data is not installed."
    )


# way to flag tests in an environment without ArcGIS Pro
skip_if_no_local = unittest.skipIf(local_ba_avail is not True,
                                      reason='ArcGIS Pro with BA and data is not available.')

# way to flag tests if ArcGIS Online connection not available
skip_if_no_agol = unittest.skipIf(agol_avail is False,
                                     reason='A connection to ArcGIS Online is not available.')


# REFERENCE: https://docs.pytest.org/en/6.2.x/example/parametrize.html#parametrizing-conditional-raising
@contextmanager
def does_not_raise():
    yield


def usa_local():
    return Country('usa', gis=GIS('pro'))


def usa_local_enrich_vars():
    usa_local_inst = usa_local()
    return _get_filtered_enrich_variables(usa_local_inst)


def gis_pro():
    gis = GIS('pro')
    return gis


def gis_agol()->GIS:
    gis = GIS(_agol_url, username=_agol_user, password=_agol_pass)
    return gis


def usa_agol()->GIS:
    gis = GIS(_agol_url, username=_agol_user, password=_agol_pass)
    return Country('usa', gis=gis)


def usa_agol_enrich_vars():
    usa_agol_inst = usa_agol()
    return _get_filtered_enrich_variables(usa_agol_inst)


# get path to testing data directory
_dir_data = Path(__file__).parent / 'geoenrich_data'


def polygon_df():
    df = pd.read_pickle(_dir_data / 'block_group_df.pkl')
    df.spatial.set_geometry('SHAPE')
    return df


def stdgeo_srs():
    polygon_df_inst = polygon_df()
    bg_id_lst = polygon_df_inst['ID']
    return bg_id_lst


def line_df():
    df = pd.read_pickle(_dir_data / 'lines_df.pkl')
    df.spatial.set_geometry('SHAPE')
    return df


def point_df():
    df = pd.read_pickle(_dir_data / 'points_df.pkl')
    df.spatial.set_geometry('SHAPE')
    return df
