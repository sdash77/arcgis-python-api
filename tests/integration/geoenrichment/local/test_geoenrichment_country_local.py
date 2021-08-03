import pandas as pd
from typing import Union

from arcgis.geoenrichment import Country, NamedArea
from arcgis.geometry import Polygon
from arcgis.gis import GIS
import pandas as pd


def get_usa_test(gis: Union[str, GIS, None]) -> None:
    cntry = Country.get('USA')
    assert isinstance(cntry, Country)


def get_can_test(gis: Union[str, GIS, None]) -> None:
    cntry = Country.get('CAN')
    assert isinstance(cntry, Country)


def get_usa_2019_test(gis: Union[str, GIS, None]) -> None:
    cntry = Country.get('USA', year=2019)
    assert isinstance(cntry, Country)


def dataset_test(country: Country) -> None:
    ds = country.dataset
    assert ds


def data_collections_test(country: Country) -> None:
    dc_df = country.data_collections
    assert isinstance(dc_df, pd.DataFrame)


def geometry_test(country: Country) -> None:
    geom = country.geometry
    assert isinstance(geom, Polygon)


def levels_test(country: Country) -> None:
    lvls = country.levels
    assert lvls


def reports_test(country: Country) -> None:
    reports_df = country.reports
    assert reports_df


def search_cbsa_chicago(country: Country) -> None:
    areas = country.search('chicago')
    assert areas


def subgeographies_test(country: Country) -> None:
    subgeos = country.subgeographies
    assert isinstance(subgeos, NamedArea)