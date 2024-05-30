import sys
import logging
import unittest
import pandas as pd
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)
DATA = {
    'features': [
        {
            'geometry': {
                'x': -7751445.7466,
                'y': 5442916.671999998,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 1,
                'FID_': 1,
                'Name': 'Nancy Drew',
                'Birthday': 846662400000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750856.1438,
                'y': 5442547.043399997,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 2,
                'FID_': 2,
                'Name': 'George Fan',
                'Birthday': 850125600000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750607.320699999,
                'y': 5443149.2676,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 3,
                'FID_': 3,
                'Name': 'Bess Marvin',
                'Birthday': 802425600000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750470.287599999,
                'y': 5442263.9619999975,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 4,
                'FID_': 4,
                'Name': 'Ned Nickerson',
                'Birthday': 737798400000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7749997.884199999,
                'y': 5442260.355800003,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 5,
                'FID_': 5,
                'Name': 'Ace',
                'Birthday': 558259200000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7751445.7466,
                'y': 5442916.671999998,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 6,
                'FID_': 1,
                'Name': 'Nancy Drew',
                'Birthday': 846662400000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750856.1438,
                'y': 5442547.043399997,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 7,
                'FID_': 2,
                'Name': 'George Fan',
                'Birthday': 850125600000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750607.320699999,
                'y': 5443149.2676,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 8,
                'FID_': 3,
                'Name': 'Bess Marvin',
                'Birthday': 802425600000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750470.287599999,
                'y': 5442263.9619999975,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 9,
                'FID_': 4,
                'Name': 'Ned Nickerson',
                'Birthday': 737798400000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7749997.884199999,
                'y': 5442260.355800003,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 10,
                'FID_': 5,
                'Name': 'Ace',
                'Birthday': 558259200000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7751445.7466,
                'y': 5442916.671999998,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 11,
                'FID_': 1,
                'Name': 'Nancy Drew',
                'Birthday': 846662400000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750856.1438,
                'y': 5442547.043399997,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 12,
                'FID_': 2,
                'Name': 'George Fan',
                'Birthday': 850125600000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750607.320699999,
                'y': 5443149.2676,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 13,
                'FID_': 3,
                'Name': 'Bess Marvin',
                'Birthday': 802425600000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7750470.287599999,
                'y': 5442263.9619999975,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 14,
                'FID_': 4,
                'Name': 'Ned Nickerson',
                'Birthday': 737798400000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
        {
            'geometry': {
                'x': -7749997.884199999,
                'y': 5442260.355800003,
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
            },
            'attributes': {
                'FID': 15,
                'FID_': 5,
                'Name': 'Ace',
                'Birthday': 558259200000,
                'Affiliatio': 'DrewCrew',
                'Class': 'Human',
            },
        },
    ],
    'objectIdFieldName': 'FID',
    'displayFieldName': 'FID',
    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
    'geometryType': 'esriGeometryPoint',
    'fields': [
        {'name': 'FID', 'type': 'esriFieldTypeOID', 'alias': 'FID'},
        {'name': 'FID_', 'type': 'esriFieldTypeInteger', 'alias': 'FID_'},
        {
            'name': 'Name',
            'type': 'esriFieldTypeString',
            'alias': 'Name',
            'length': 13,
        },
        {
            'name': 'Birthday',
            'type': 'esriFieldTypeDate',
            'alias': 'Birthday',
        },
        {
            'name': 'Affiliatio',
            'type': 'esriFieldTypeString',
            'alias': 'Affiliatio',
            'length': 8,
        },
        {
            'name': 'Class',
            'type': 'esriFieldTypeString',
            'alias': 'Class',
            'length': 5,
        },
    ],
}


@integration_test
class TestApplyEditsSeDF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_online_profile', verify_cert=False, proxy=PROXIES
        )
        cm = cls.gis.content
        rows = []
        for feat in DATA['features'][:5]:
            geom = feat['geometry']
            att = feat['attributes']
            att['SHAPE'] = geom
            rows.append(att)
        df = pd.DataFrame(rows)
        df.spatial.set_geometry("SHAPE")
        cls.item = cm.import_data(df)

    def test_apply_edits_adds(self):
        gis = self.gis
        item = self.item
        lyr: FeatureLayer = item.layers[0]
        count_old = lyr.query(return_count_only=True)
        sdf = lyr.query(as_df=True).head().copy()
        lyr.edit_features(adds=sdf)
        count = lyr.query(return_count_only=True)
        assert count > count_old

    def test_apply_edits_update(self):
        gis = self.gis
        item = self.item
        lyr: FeatureLayer = item.layers[0]
        sdf = lyr.query(as_df=True).head().copy()
        results = lyr.edit_features(updates=sdf)
        assert all(
            [
                res.get("success", False)
                for res in results.get("updateResults", [])
            ]
        )

    @classmethod
    def tearDownClass(cls):
        if cls.item:
            cls.item.delete()


if __name__ == "__main__":
    unittest.main()
