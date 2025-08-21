from arcgis.geoenrichment._business_analyst import Country
import pandas as pd

from integration.geoenrichment.business_analyst.configtest import (
    does_not_raise,
    skip_if_no_agol,
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


@skip_if_no_agol
def test_enrich_with_buffer_study_areas_and_analysis_variables(usa_agol: Country,
                                                          point_df: pd.DataFrame,
                                                          usa_enrich_vars_agol: pd.DataFrame):
    from arcgis.features import FeatureLayerCollection
    from arcgis.geoenrichment import BufferStudyArea
    public_school_URL = 'https://services3.arcgis.com/fdvHcZVgB2QSRNkL/ArcGIS/rest/services/SchoolSites2021/FeatureServer'
    public_school_item = FeatureLayerCollection(public_school_URL)
    public_school_sedf = pd.DataFrame.spatial.from_layer(public_school_item.layers[0])
    public_school = public_school_sedf[(public_school_sedf['Status'] == 'Active') 
                                    & ((public_school_sedf['Virtual'] == 'N') | (public_school_sedf['Virtual'] == 'C'))]
    public_school = public_school[public_school['CountyName'] == 'San Diego'] 
    middle_school = public_school[(public_school['SchoolLevel'] =='Middle')]
    middle_school = middle_school[middle_school['EnrollTotal'] > 0] #subset to non empty school
    import numpy as np
    idx = np.random.choice(range(50), 5)
    middle_school_subset = middle_school.iloc[idx]

    school_drive_time = []
    for shape in middle_school_subset.SHAPE: 
        school_drive_time.append(BufferStudyArea(area=shape, radii=[8], units="Minutes", travel_mode="Driving Time"))

    analysis_variables = [
    'TOTPOP_CY',
    'DIVINDX_CY',
    'AVGHHSZ_CY',
    'MEDAGE_CY',
    'MEDHINC_CY',
    'BACHDEG_CY',
    'ACS0NOHI',
    'ACS19NOHI',
    'ACS35NOHI',
    'UNEMPRT_CY',
    'ACS18NOPC',
    'ACSNONET',
    'ACSSNAP',
    'ACSPUBTRAN'
    ]
    usa = Country("USA")
    middle_school_enriched = usa.enrich(study_areas=school_drive_time, enrich_variables=analysis_variables)
    middle_school_enriched
