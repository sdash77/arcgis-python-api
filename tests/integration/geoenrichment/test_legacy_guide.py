from typing import Union, Iterable

from arcgis.geoenrichment import Country
from arcgis.geoenrichment._business_analyst._utils import pep8ify
import pandas as pd
import pytest

from .configtest import (
    does_not_raise,
    skip_if_no_local,
    skip_if_no_agol,
    usa_local,
    usa_local_enrich_vars,
    usa_agol,
    usa_agol_enrich_vars,
    polygon_df,
    line_df,
    point_df,
    stdgeo_srs,
)


@skip_if_no_agol
def test_introduction_enrich_01_agol(usa_agol, expectation=does_not_raise()):
    with expectation:

        analysis_variables = [
            'TOTPOP_CY',  # Population: Total Population (Esri)
            'DIVINDX_CY',  # Diversity Index (Esri)
            'AVGHHSZ_CY',  # Average Household Size (Esri)
            'MEDAGE_CY',  # Age: Median Age (Esri)
            'MEDHINC_CY',  # Income: Median Household Income (Esri)
            'BACHDEG_CY',  # Education: Bachelor's Degree (Esri)
        ]

        usa = Country('US', gis=usa_agol._gis)
        zip1 = usa.subgeographies.states['California'].zip5['90018']
        zip2 = usa.subgeographies.states['California'].zip5['90023']
        zip3 = usa.subgeographies.states['California'].zip5['90035']

        enrich_res = usa.enrich([zip1, zip2, zip3], enrich_variables=analysis_variables)

        assert isinstance(enrich_res, pd.DataFrame)
        assert enrich_res.spatial.validate()
        enrich_var_cols = [pep8ify(val) for val in usa.enrich_variables['enrich_field_name']]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def test_enrich_single_address_agol(usa_agol, expectation=does_not_raise()):
    with expectation:
        enrich_res = usa_agol.enrich(study_areas=["380 New York St Redlands CA 92373"], data_collections=['Age'])

        assert isinstance(enrich_res, pd.DataFrame)
        assert enrich_res.spatial.validate()
        enrich_var_cols = [pep8ify(val) for val in usa_agol.enrich_variables['enrich_field_name']]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])
