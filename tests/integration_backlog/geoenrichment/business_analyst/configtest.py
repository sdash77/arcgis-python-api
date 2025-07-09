import pandas as pd

from arcgis.gis import GIS
from arcgis.geoenrichment._business_analyst import BusinessAnalyst, Country
import pytest

from ..configtest import (
    _get_filtered_enrich_variables
)


@pytest.fixture(scope='session')
def ba_local() -> BusinessAnalyst:
    ba = BusinessAnalyst('local')
    return ba


@pytest.fixture(scope='session')
def usa_local(ba_local: BusinessAnalyst) -> Country:
    usa = ba_local.get_country('USA')
    return usa


@pytest.fixture(scope='session')
def usa_enrich_vars_local(usa_local: Country) -> pd.DataFrame:
    sel_vars = _get_filtered_enrich_variables(usa_local)
    return sel_vars


@pytest.fixture(scope='session')
def ba_agol(gis_agol: GIS) -> BusinessAnalyst:
    ba = BusinessAnalyst(gis_agol)
    return ba


@pytest.fixture(scope='session')
def usa_agol(ba_agol: BusinessAnalyst) -> Country:
    usa = ba_agol.get_country('USA')
    return usa


@pytest.fixture(scope='session')
def usa_enrich_vars_agol(usa_agol: Country) -> pd.DataFrame:
    sel_vars = _get_filtered_enrich_variables(usa_agol)
    return sel_vars


@pytest.fixture(scope='session')
def universal_enrich_vars(ba_agol: BusinessAnalyst) -> pd.DataFrame:
    enrich_vars = ba_agol.enrich_variables
    return enrich_vars
