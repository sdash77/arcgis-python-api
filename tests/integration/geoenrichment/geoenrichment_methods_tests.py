import pandas as pd
from typing import Union

from arcgis.geoenrichment import (
    Country,
    get_countries,
    create_report,
    enrich,
    standard_geography_query,
    service_limits,
)
from arcgis.gis import GIS

from .geoenrich_data import (
    address_list_str,
    address_list_json,
    key_enrich_list_web,
    block_group_df,
    block_group_points_df,
)


def get_countries_test(gis: GIS = None, as_df=None) -> None:
    if as_df is not None:
        cntrs = get_countries(gis, as_df=as_df)
    else:
        cntrs = get_countries(gis)
    assert cntrs


def enrich_iterable_dict_addresses_test(gis: GIS = None) -> None:
    usa = Country('usa', gis=gis)
    er = usa.enrich(address_list_json, enrich_variables=key_enrich_list_web)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def enrich_iterable_geometry_test(gis: GIS = None) -> None:
    geom_lst = list(block_group_df.SHAPE)
    usa = Country('usa', gis=gis)
    er = usa.enrich(geom_lst, enrich_variables=key_enrich_list_web)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def enrich_iterable_buffer_study_areas_test(gis: GIS = None) -> None:
    geom_lst = list(block_group_points_df.SHAPE)
    usa = Country('usa', gis=gis)
    er = usa.enrich(geom_lst, enrich_variables=key_enrich_list_web)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def enrich_sedf_test(gis: GIS = None) -> None:
    usa = Country('usa', gis=gis)
    er = usa.enrich(block_group_df, enrich_variables=key_enrich_list_web)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def get_named_areas_test(gis: GIS = None) -> None:
    cntry = Country.get("usa", gis=gis)
    zip90018 = cntry.subgeographies.states["California"].zip5["90018"]
    assert zip90018
