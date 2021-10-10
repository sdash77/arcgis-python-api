import pandas as pd
from typing import Union

from arcgis.geoenrichment import Country
from arcgis.geoenrichment.enrichment import NamedArea
from arcgis.geometry import Polygon
from arcgis.gis import GIS
import pandas as pd


def usa_test(gis: Union[str, GIS, None]) -> None:
    cntry = Country("USA", gis=gis)
    assert isinstance(cntry, Country)


def get_usa_test(gis: Union[str, GIS, None]) -> None:
    cntry = Country.get("USA", gis=gis)
    assert isinstance(cntry, Country)


def get_can_test(gis: Union[str, GIS, None]) -> None:
    cntry = Country.get("CAN", gis=gis)
    assert isinstance(cntry, Country)


def get_usa_2019_test(gis: Union[str, GIS, None]) -> None:
    cntry = Country.get("USA", gis=gis, year=2019)
    assert isinstance(cntry, Country)


def dataset_test(country: Country) -> None:
    ds = country.dataset
    assert isinstance(ds, str)
    assert "ESRI" in ds


def data_collections_test(country: Country) -> None:
    dc_df = country.data_collections
    assert isinstance(dc_df, pd.DataFrame)


def enrich_variables_test(country: Country) -> None:
    ev_df = country.enrich_variables
    assert isinstance(ev_df, pd.DataFrame)


def geometry_test(country: Country) -> None:
    geom = country.geometry
    assert isinstance(geom, Polygon)


def levels_test(country: Country) -> None:
    lvls = country.levels
    assert lvls


def reports_test(country: Country) -> None:
    reports_df = country.reports
    assert isinstance(reports_df, pd.DataFrame)


def search_cbsa_chicago(country: Country) -> None:
    areas = country.search("chicago")
    assert areas


def subgeographies_test(country: Country) -> None:
    subgeos = country.subgeographies
    assert isinstance(subgeos, NamedArea)
