from typing import Optional

from arcgis.gis import GIS
from arcgis.geoenrichment import Country
import pytest

from .configtest import (
    skip_if_no_agol,
    skip_if_no_local,
    does_not_raise,
    gis_pro,
    gis_agol,
    _agol_url as agol_url,
    _agol_user as agol_user,
    _agol_pass as agol_pass
)


def create_country_test(iso3: str, gis: GIS, expectation, year: Optional[int] = None) -> None:
    with expectation:
        cntry = Country(iso3, gis=gis, year=year)
        assert isinstance(cntry, Country)


# including to ensure credentials correctly getting loaded from config and also ensure not lower level issues
def test_create_gis():
    gis = GIS(agol_url, username=agol_user, password=agol_pass)
    assert isinstance(gis, GIS)
    assert gis._con._auth != 'ANON'


@skip_if_no_local
def test_create_country_usa_local(gis_pro):
    create_country_test('usa', gis=gis_pro, expectation=does_not_raise())


@skip_if_no_local
def test_create_country_can_local(gis_pro):
    create_country_test('can', gis=gis_pro, expectation=does_not_raise())


@skip_if_no_agol
def test_create_country_usa_agol(gis_agol):
    create_country_test('usa', gis=gis_agol, expectation=does_not_raise())


@skip_if_no_agol
def test_create_country_can_agol(gis_agol):
    create_country_test('can', gis=gis_agol, expectation=does_not_raise())
