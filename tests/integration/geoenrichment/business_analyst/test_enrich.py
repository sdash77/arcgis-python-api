from typing import Union, Iterable

from arcgis.geoenrichment._business_analyst import BusinessAnalyst, Country
from arcgis.geoenrichment._business_analyst._utils import pep8ify
import pandas as pd
import pytest

from .configtest import (
    does_not_raise,
    skip_if_no_local,
    skip_if_no_agol,
    gis_agol,
    ba_agol,
    ba_local,
    usa_local,
    usa_agol,
    usa_enrich_vars_local,
    usa_enrich_vars_agol,
    point_df
)


def enrich_proximity_straight_line_area_overlap_test(usa: Country,
                                                     point_df: pd.DataFrame,
                                                     enrich_vars: pd.DataFrame,
                                                     expectation: object = does_not_raise()) -> None:
    with expectation:
        enrich_res = usa.enrich(point_df,
                                enrich_variables=enrich_vars,
                                proximity_type='driving_time',
                                proximity_value=[3, 5, 12],
                                proximity_area_overlap=True
                                )
        assert isinstance(enrich_res, pd.DataFrame)


def enrich_proximity_straight_line_area_no_overlap_test(usa: Country,
                                                        point_df: pd.DataFrame,
                                                        enrich_vars: pd.DataFrame,
                                                        expectation: object = does_not_raise()) -> None:
    with expectation:
        enrich_res = usa.enrich(point_df,
                                enrich_variables=enrich_vars,
                                proximity_type='driving_time',
                                proximity_value=[3, 5, 12],
                                proximity_area_overlap=False
                                )
        assert isinstance(enrich_res, pd.DataFrame)


@skip_if_no_agol
def test_enrich_proximity_straight_line_area_overlap_agol(usa_agol: Country,
                                                          point_df: pd.DataFrame,
                                                          usa_enrich_vars_agol: pd.DataFrame):
    enrich_proximity_straight_line_area_overlap_test(usa_agol, point_df, usa_enrich_vars_agol)


@skip_if_no_agol
def test_enrich_proximity_straight_line_area_no_overlap_agol(usa_agol: Country,
                                                          point_df: pd.DataFrame,
                                                          usa_enrich_vars_agol: pd.DataFrame):
    enrich_proximity_straight_line_area_no_overlap_test(usa_agol, point_df, usa_enrich_vars_agol)