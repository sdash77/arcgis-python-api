import unittest
import pandas as pd
import concurrent.futures
from utils.decorators import integration_test, profiles


data = [
    {
        "FID": 1,
        "FID_1": 1.0,
        "id": 12.0,
        "name": "Paeroa Domain",
        "areahectar": 5.7401,
        "SHAPE_Leng": 0.01036701182584,
        "SHAPE_Area": 5.842267309e-06,
        "Shape__Area": 91108.265625,
        "Shape__Length": 1262.64617186528,
        "SHAPE": {
            "rings": [
                [
                    [19555988.3754161, -4492173.63357922],
                    [19555908.4132901, -4492270.05311721],
                    [19555891.4823748, -4492290.46427856],
                    [19555844.9198808, -4492346.61741638],
                    [19555686.8505453, -4492218.54060424],
                    [19555667.6825535, -4492203.01887177],
                    [19555648.4823904, -4492187.46031855],
                    [19555628.7094885, -4492171.43837116],
                    [19555610.0504494, -4492156.31876554],
                    [19555598.7003141, -4492147.12510671],
                    [19555592.8823122, -4492134.51789819],
                    [19555581.0352468, -4492108.80466955],
                    [19555569.5527526, -4492083.88888856],
                    [19555557.7612355, -4492058.30032236],
                    [19555538.8153261, -4492017.18937994],
                    [19555569.9311275, -4491994.01566375],
                    [19555601.5539893, -4491970.44891409],
                    [19555614.4833028, -4491969.48791621],
                    [19555625.1162066, -4491968.69334193],
                    [19555627.0608468, -4491968.54961252],
                    [19555640.0830009, -4491967.57348539],
                    [19555650.0126994, -4491966.83662715],
                    [19555652.0708855, -4491966.67706793],
                    [19555664.61726, -4491965.73960502],
                    [19555675.4055658, -4491964.94054823],
                    [19555677.3709114, -4491964.79625853],
                    [19555689.772348, -4491963.86285831],
                    [19555701.1191437, -4491963.02261607],
                    [19555701.853407, -4491962.9639196],
                    [19555714.4930673, -4491962.02365527],
                    [19555727.0913167, -4491961.08465182],
                    [19555740.39266, -4491960.08779251],
                    [19555751.2534348, -4491959.28649476],
                    [19555752.8047833, -4491959.16658027],
                    [19555765.3719745, -4491958.22841759],
                    [19555772.1133716, -4491994.73865524],
                    [19555780.9437902, -4492002.05991],
                    [19555781.4473996, -4492008.520191],
                    [19555788.1186653, -4492008.01489479],
                    [19555815.4905696, -4492030.69847405],
                    [19555807.7485217, -4492031.46153323],
                    [19555832.3447858, -4492044.66987642],
                    [19555900.4791047, -4492100.98952702],
                    [19555921.8003494, -4492118.60754249],
                    [19555988.3754161, -4492173.63357922],
                ]
            ],
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
    {
        "FID": 2,
        "FID_1": 2.0,
        "id": 13.0,
        "name": "Primrose Hill Recreation Reserve",
        "areahectar": 3.9948,
        "SHAPE_Leng": 0.009853325081233,
        "SHAPE_Area": 4.066026563e-06,
        "Shape__Area": 63409.1875,
        "Shape__Length": 1196.50992446609,
        "SHAPE": {
            "rings": [
                [
                    [19556346.300307, -4492336.05629265],
                    [19556187.7393846, -4492377.86026006],
                    [19556165.0501347, -4492393.29931591],
                    [19556142.3683432, -4492380.75611449],
                    [19556122.1783271, -4492365.41570214],
                    [19556083.6037859, -4492413.32798245],
                    [19556064.3241406, -4492397.55757755],
                    [19556045.3198998, -4492381.99383297],
                    [19556025.6478533, -4492365.90644593],
                    [19556006.2405246, -4492350.01339143],
                    [19555986.3243545, -4492333.7182969],
                    [19555957.6434443, -4492310.2387628],
                    [19555927.4668454, -4492285.53978579],
                    [19555939.0550931, -4492271.21265178],
                    [19555969.145976, -4492296.54522899],
                    [19555982.1025628, -4492281.11878346],
                    [19555986.8454411, -4492275.45559399],
                    [19555993.9756771, -4492266.97293339],
                    [19556000.2534284, -4492259.4989349],
                    [19556017.4242373, -4492242.08465534],
                    [19556021.736643, -4492237.69575208],
                    [19555993.3686519, -4492203.99698204],
                    [19556007.4805124, -4492186.54370935],
                    [19556023.074258, -4492167.24338167],
                    [19556056.7556397, -4492125.56787361],
                    [19556072.5695753, -4492105.9963056],
                    [19556088.1834697, -4492086.68281746],
                    [19556118.9580769, -4492116.41248601],
                    [19556206.0616823, -4492200.56266947],
                    [19556346.300307, -4492336.05629265],
                ]
            ],
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
        },
    },
]


@profiles.agol
@integration_test
class TestApplyEditsAsync(unittest.TestCase):
    def test_async_edits(self):

        df = pd.DataFrame(data)
        item = self.gis.content.import_data(
            df, title="test_async_edits", tags="ntgrtn-tst"
        )
        edit_data = [
            {
                "geometry": {
                    "rings": [
                        [
                            [19536507.772708487, -4490968.119315104],
                            [19542546.29794301, -4492879.045022231],
                            [19541399.742518734, -4497006.644549624],
                            [19535131.90619936, -4494331.348559647],
                            [19536507.772708487, -4490968.119315104],
                        ]
                    ],
                    "spatialReference": {"wkid": 102100, "latestWkid": 3857},
                },
                "attributes": {
                    "FID_1": None,
                    "id": None,
                    "name": None,
                    "areahectar": None,
                    "SHAPE_Leng": None,
                    "SHAPE_Area": None,
                },
            }
        ]
        fl = item.layers[0]
        try:
            feat_count = fl.query(return_count_only=True)
            res = fl.edit_features(adds=edit_data, future=True)
            assert isinstance(res, concurrent.futures.Future)
            result = res.result()
            assert result
            assert bool(result[0]["addResults"])
            assert fl.query(return_count_only=True) == feat_count + 1
        finally:
            for itm in item.related_items("Service2Data", "forward"):
                itm.delete(permanent=True)
            item.delete(permanent=True)

    def test_async_updates(self):

        df = pd.DataFrame(data)
        item = self.gis.content.import_data(
            df, title="test_async_edits", tags="ntgrtn-tst"
        )
        fl = item.layers[0]
        try:
            features = fl.query(
                where="1=1",
                out_fields=["fid", "areahectar"],
            ).sdf.copy(deep=True)

            features.columns = features.columns.str.lower()
            features.loc[features["fid"] > 0, "areahectar"] = (
                features["areahectar"] * 107639.1042
            )
            feature_set = features.spatial.to_featureset()
            updates = fl.edit_features(updates=feature_set, future=True).result()
            self.assertEqual(
                2,
                len(updates[0].get("updateResults")),
                "Incorrect number of updated features",
            )
            result_feature_set = fl.query(
                where="areahectar > 617859",
                out_fields=["fid", "areahectar"],
            ).sdf.spatial.to_featureset()
            self.assertEqual(1, len(result_feature_set), "Incorrect updated features")
        finally:
            for itm in item.related_items("Service2Data", "forward"):
                itm.delete(permanent=True)
            item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
