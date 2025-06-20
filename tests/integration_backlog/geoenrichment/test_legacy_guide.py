import unittest

from arcgis.features import FeatureSet
from arcgis.geoenrichment import Country
from arcgis.geoenrichment._business_analyst._utils import pep8ify
import pandas as pd
from arcgis.geoenrichment import enrich

from integration.geoenrichment.configtest import (
    does_not_raise,
    skip_if_no_agol,
    usa_agol,
)
from utils.decorators import integration_test


def assert_enrich_results(enrich_res, cntry):
    assert isinstance(enrich_res, pd.DataFrame)
    assert enrich_res.spatial.validate()
    enrich_var_cols = [
        pep8ify(val) for val in cntry.enrich_variables["enrich_field_name"]
    ]
    enrich_res_cols = list(enrich_res.columns)
    assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


in_memory_dict = {
    "features": [
        {
            "geometry": {
                "paths": [
                    [
                        [-80.76612999999998, 35.05131000000006],
                        [-80.76619999999997, 35.05123000000003],
                        [-80.76619999999997, 35.05078000000003],
                        [-80.76665999999994, 35.05077000000006],
                        [-80.76781999999997, 35.05075000000005],
                        [-80.76817999999997, 35.05079000000006],
                        [-80.76842999999997, 35.05087000000003],
                        [-80.76874999999995, 35.05097000000006],
                        [-80.76940999999994, 35.051030000000026],
                        [-80.76944999999995, 35.05189000000007],
                        [-80.76945999999998, 35.052080000000046],
                        [-80.76948999999996, 35.052730000000054],
                        [-80.76949999999994, 35.05296000000004],
                        [-80.76951999999994, 35.05335000000008],
                        [-80.76952999999997, 35.053540000000055],
                        [-80.76963999999998, 35.05692000000005],
                        [-80.76979999999998, 35.058280000000025],
                        [-80.76979999999998, 35.05848000000003],
                        [-80.76979999999998, 35.058640000000025],
                        [-80.76980999999995, 35.058890000000076],
                        [-80.76981999999998, 35.05968000000007],
                        [-80.76985999999994, 35.06058000000007],
                        [-80.76987999999994, 35.06107000000003],
                        [-80.76989999999995, 35.06147000000004],
                        [-80.76994999999994, 35.06225000000006],
                        [-80.76996999999994, 35.06253000000004],
                        [-80.76998999999995, 35.062830000000076],
                        [-80.77002999999996, 35.063630000000046],
                        [-80.77003999999994, 35.06382000000008],
                        [-80.77005999999994, 35.06419000000005],
                        [-80.77008999999998, 35.06472000000008],
                        [-80.77018999999996, 35.06567000000007],
                        [-80.77070999999995, 35.06734000000006],
                        [-80.77112999999997, 35.06794000000008],
                        [-80.77176999999995, 35.06828000000007],
                        [-80.77279999999996, 35.069030000000055],
                        [-80.77311999999995, 35.069560000000024],
                        [-80.77361999999994, 35.07109000000003],
                        [-80.77366999999998, 35.07129000000003],
                        [-80.77374999999995, 35.07176000000004],
                        [-80.77368999999999, 35.07223000000005],
                        [-80.77355999999997, 35.07269000000008],
                        [-80.77337999999997, 35.073120000000074],
                        [-80.77328999999997, 35.07336000000004],
                        [-80.77314999999999, 35.07372000000004],
                        [-80.77307999999994, 35.07391000000007],
                        [-80.77299999999997, 35.074100000000044],
                        [-80.77288999999996, 35.07451000000003],
                        [-80.77282999999994, 35.07481000000007],
                        [-80.77279999999996, 35.07526000000007],
                        [-80.77278999999999, 35.07537000000008],
                        [-80.77276999999998, 35.07566000000003],
                        [-80.77274999999997, 35.075860000000034],
                        [-80.77270999999996, 35.07618000000008],
                        [-80.77220999999997, 35.07871000000006],
                        [-80.77218999999997, 35.07889000000006],
                        [-80.77218999999997, 35.07938000000007],
                        [-80.77221999999995, 35.07991000000004],
                        [-80.77227999999997, 35.08044000000007],
                        [-80.77228999999994, 35.08051000000006],
                        [-80.77234999999996, 35.08081000000004],
                        [-80.77242999999999, 35.081120000000055],
                        [-80.77255999999994, 35.081570000000056],
                        [-80.77268999999995, 35.08203000000003],
                        [-80.77284999999995, 35.08257000000003],
                        [-80.77295999999996, 35.08293000000003],
                        [-80.77301999999997, 35.083120000000065],
                        [-80.77368999999999, 35.085320000000024],
                        [-80.77419999999995, 35.08675000000005],
                        [-80.77430999999996, 35.087060000000065],
                        [-80.77464999999995, 35.08802000000003],
                        [-80.77483999999998, 35.08856000000003],
                        [-80.77516999999995, 35.08952000000005],
                        [-80.77519999999998, 35.08961000000005],
                        [-80.77544999999998, 35.090310000000045],
                        [-80.77568999999994, 35.09099000000003],
                        [-80.77629999999994, 35.09266000000002],
                        [-80.77636999999999, 35.09283000000005],
                        [-80.77648999999997, 35.093180000000075],
                        [-80.77655999999996, 35.093380000000025],
                        [-80.77676999999994, 35.09397000000007],
                        [-80.77681999999999, 35.094130000000064],
                        [-80.77689999999996, 35.09436000000005],
                        [-80.77691999999996, 35.09442000000007],
                        [-80.77699999999999, 35.09462000000008],
                        [-80.77714999999995, 35.09507000000008],
                        [-80.77712999999994, 35.095210000000066],
                        [-80.77736999999996, 35.09590000000003],
                        [-80.77745999999996, 35.09614000000005],
                        [-80.77780999999999, 35.097120000000075],
                        [-80.77783999999997, 35.09720000000004],
                        [-80.77801999999997, 35.09773000000007],
                        [-80.77839999999998, 35.098960000000034],
                        [-80.77847999999994, 35.09925000000004],
                        [-80.77853999999996, 35.09948000000003],
                        [-80.77857999999998, 35.09962000000007],
                        [-80.77865999999995, 35.09994000000006],
                        [-80.77868999999998, 35.100100000000054],
                        [-80.77884999999998, 35.10006000000004],
                        [-80.77912999999995, 35.10000000000008],
                        [-80.78098999999997, 35.09957000000003],
                        [-80.78153999999995, 35.09938000000005],
                        [-80.78174999999999, 35.09930000000003],
                        [-80.78208999999998, 35.09917000000007],
                        [-80.78219999999999, 35.09913000000006],
                        [-80.78276999999997, 35.09997000000004],
                        [-80.78244999999998, 35.10018000000008],
                        [-80.78212999999994, 35.10051000000004],
                        [-80.78188999999998, 35.100400000000036],
                        [-80.78158999999994, 35.10026000000005],
                        [-80.78156132899994, 35.10029909700006],
                    ]
                ]
            },
            "attributes": {
                "ObjectID": 1,
                "Total_TravelTime": 8.396586152962726,
                "Total_Miles": 4.103800719027698,
                "Total_Kilometers": 6.604425425545643,
            },
        }
    ],
    "objectIdFieldName": "ObjectID",
    "spatialReference": {"wkid": 4326},
    "geometryType": "esriGeometryPolyline",
    "fields": [
        {
            "name": "ObjectID",
            "alias": "ObjectID",
            "type": "esriFieldTypeOID",
            "sqlType": "sqlTypeOther",
        },
        {
            "name": "Total_TravelTime",
            "alias": "Total_TravelTime",
            "type": "esriFieldTypeDouble",
            "sqlType": "sqlTypeOther",
        },
        {
            "name": "Total_Miles",
            "alias": "Total_Miles",
            "type": "esriFieldTypeDouble",
            "sqlType": "sqlTypeOther",
        },
        {
            "name": "Total_Kilometers",
            "alias": "Total_Kilometers",
            "type": "esriFieldTypeDouble",
            "sqlType": "sqlTypeOther",
        },
    ],
}
test_feature_set = FeatureSet.from_dict(in_memory_dict)


@integration_test
class TestLegacyGuide(unittest.TestCase):
    def setUp(self):
        self.usa_agol_inst = usa_agol()

    @skip_if_no_agol
    def test_introduction_enrich_01_agol(self, expectation=does_not_raise()):
        with expectation:
            analysis_variables = [
                "TOTPOP_CY",  # Population: Total Population (Esri)
                "DIVINDX_CY",  # Diversity Index (Esri)
                "AVGHHSZ_CY",  # Average Household Size (Esri)
                "MEDAGE_CY",  # Age: Median Age (Esri)
                "MEDHINC_CY",  # Income: Median Household Income (Esri)
                "BACHDEG_CY",  # Education: Bachelor's Degree (Esri)
            ]

            usa = Country("US", gis=self.usa_agol_inst._gis)
            zip1 = usa.subgeographies.states["California"].zip5["90018"]
            zip2 = usa.subgeographies.states["California"].zip5["90023"]
            zip3 = usa.subgeographies.states["California"].zip5["90035"]

            enrich_res = usa.enrich(
                [zip1, zip2, zip3], enrich_variables=analysis_variables
            )

            assert_enrich_results(enrich_res, usa)

    @skip_if_no_agol
    def test_enrich_single_address_agol(self, expectation=does_not_raise()):
        with expectation:
            enrich_res = self.usa_agol_inst.enrich(
                study_areas=["380 New York St Redlands CA 92373"],
                data_collections=["Age"],
            )
            assert_enrich_results(enrich_res, self.usa_agol_inst)

    @skip_if_no_agol
    def test_enrich_feature_set_direct_enrich_wrong_data_colleciton_agol(self):
        from arcgis.geoenrichment import enrich

        with self.assertRaises(AssertionError):
            enrich_res = enrich(
                study_areas=test_feature_set.sdf,
                data_collections=["Age"],
                gis=self.usa_agol_inst._gis,
            )
            assert_enrich_results(enrich_res, self.usa_agol_inst)

    @skip_if_no_agol
    def test_enrich_feature_set_data_collection_agol(self):
        with does_not_raise():
            enrich_res = enrich(
                study_areas=test_feature_set.sdf, data_collections=["Age"]
            )
            assert isinstance(enrich_res, pd.DataFrame)
            assert enrich_res.iloc[0]["has_data"] == 1


if __name__ == "__main__":

    unittest.main()
