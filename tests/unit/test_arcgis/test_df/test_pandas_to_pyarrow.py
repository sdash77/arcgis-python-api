import sys
import logging
import unittest
import pyarrow
import pandas as pd

import arcgis

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


enable_verbose_logging(__logger__)


class TestPyArrowIntegrations(unittest.TestCase):
    def setUp(self):
        data = {
            'AGE_10_14': {0: 1313, 1: 890, 2: 12750, 3: 790, 4: 3803},
            'AGE_15_19': {0: 1058, 1: 817, 2: 13959, 3: 768, 4: 3779},
            'AGE_20_24': {0: 734, 1: 818, 2: 16966, 3: 699, 4: 3687},
            'AGE_25_34': {0: 2031, 1: 1799, 2: 32135, 3: 1445, 4: 7571},
            'AGE_35_44': {0: 1767, 1: 1235, 2: 27048, 3: 1136, 4: 5559},
            'AGE_45_54': {0: 1446, 1: 1330, 2: 29595, 3: 1134, 4: 4744},
            'AGE_55_64': {0: 1136, 1: 1143, 2: 24177, 3: 935, 4: 3624},
            'AGE_5_9': {0: 1503, 1: 1099, 2: 12933, 3: 959, 4: 4397},
            'AGE_65_74': {0: 665, 1: 721, 2: 12176, 3: 679, 4: 2296},
            'AGE_75_84': {0: 486, 1: 579, 2: 7087, 3: 464, 4: 1222},
            'AGE_85_UP': {0: 209, 1: 229, 2: 3690, 3: 263, 4: 593},
            'AGE_UNDER5': {0: 1468, 1: 1239, 2: 13155, 3: 1073, 4: 4962},
            'AMERI_ES': {0: 67, 1: 418, 2: 1404, 3: 103, 4: 539},
            'ASIAN': {0: 113, 1: 125, 2: 6501, 3: 74, 4: 406},
            'AVE_FAM_SZ': {0: 3.61, 1: 3.31, 2: 2.97, 3: 3.37, 4: 3.51},
            'AVE_HH_SZ': {0: 3.05, 1: 2.74, 2: 2.36, 3: 2.76, 4: 3.0},
            'BLACK': {0: 73, 1: 40, 2: 3043, 3: 45, 4: 300},
            'CAPITAL': {0: ' ', 1: ' ', 2: 'State', 3: ' ', 4: ' '},
            'CLASS': {0: 'city', 1: 'city', 2: 'city', 3: 'city', 4: 'city'},
            'FAMILIES': {0: 3352, 1: 2958, 2: 50647, 3: 2499, 4: 10776},
            'FEMALES': {0: 7066, 1: 5992, 2: 103981, 3: 5209, 4: 23416},
            'FHH_CHILD': {0: 335, 1: 381, 2: 5919, 3: 358, 4: 1755},
            'FID': {0: 1, 1: 2, 2: 3, 3: 4, 4: 5},
            'HAWN_PI': {0: 9, 1: 18, 2: 457, 3: 5, 4: 41},
            'HISPANIC': {0: 884, 1: 2192, 2: 14606, 3: 3460, 4: 16347},
            'HOUSEHOLDS': {0: 4476, 1: 4229, 2: 85704, 3: 3644, 4: 14895},
            'HSEHLD_1_F': {0: 648, 1: 690, 2: 18104, 3: 634, 4: 2250},
            'HSEHLD_1_M': {0: 457, 1: 563, 2: 16605, 3: 498, 4: 1795},
            'HSE_UNITS': {0: 4747, 1: 4547, 2: 92700, 3: 3885, 4: 16323},
            'MALES': {0: 6750, 1: 5907, 2: 101690, 3: 5136, 4: 22821},
            'MARHH_CHD': {0: 1618, 1: 1091, 2: 16708, 3: 950, 4: 4407},
            'MARHH_NO_C': {0: 1131, 1: 1081, 2: 21233, 3: 861, 4: 3113},
            'MED_AGE': {0: 29.6, 1: 30.8, 2: 35.3, 3: 30.9, 4: 28.1},
            'MED_AGE_F': {0: 30.8, 1: 32.1, 2: 36.5, 3: 32.3, 4: 28.9},
            'MED_AGE_M': {0: 28.0, 1: 29.7, 2: 34.4, 3: 29.6, 4: 27.3},
            'MHH_CHILD': {0: 106, 1: 174, 2: 2414, 3: 139, 4: 686},
            'MULT_RACE': {0: 245, 1: 328, 2: 6136, 3: 339, 4: 1646},
            'NAME': {
                0: 'Ammon',
                1: 'Blackfoot',
                2: 'Boise City',
                3: 'Burley',
                4: 'Caldwell',
            },
            'OTHER': {0: 307, 1: 1077, 2: 5139, 3: 1795, 4: 7449},
            'OWNER_OCC': {0: 3205, 1: 2788, 2: 52345, 3: 2183, 4: 9699},
            'PLACEFIPS': {
                0: '1601990',
                1: '1607840',
                2: '1608830',
                3: '1611260',
                4: '1612250',
            },
            'POP2010': {0: 13816, 1: 11899, 2: 205671, 3: 10345, 4: 46237},
            'POPULATION': {0: 15181, 1: 11946, 2: 225405, 3: 10727, 4: 53942},
            'POP_CLASS': {0: 6, 1: 6, 2: 8, 3: 6, 4: 7},
            'RENTER_OCC': {0: 1271, 1: 1441, 2: 33359, 3: 1461, 4: 5196},
            'SHAPE': {
                0: {
                    'x': -12462673.723706163,
                    'y': 5384674.994080178,
                    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
                },
                1: {
                    'x': -12506251.313993266,
                    'y': 5341537.793529328,
                    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
                },
                2: {
                    'x': -12938676.6836459,
                    'y': 5403597.049491232,
                    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
                },
                3: {
                    'x': -12667411.402393516,
                    'y': 5241722.82060674,
                    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
                },
                4: {
                    'x': -12989383.674504517,
                    'y': 5413226.487333952,
                    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
                },
            },
            'ST': {0: 'ID', 1: 'ID', 2: 'ID', 3: 'ID', 4: 'ID'},
            'STFIPS': {0: '16', 1: '16', 2: '16', 3: '16', 4: '16'},
            'VACANT': {0: 271, 1: 318, 2: 6996, 3: 241, 4: 1428},
            'WHITE': {0: 13002, 1: 9893, 2: 182991, 3: 7984, 4: 35856},
        }

        df = pd.DataFrame.from_dict(data)
        df.SHAPE = df.SHAPE.apply(arcgis.geometry.Geometry)
        df.spatial.set_geometry("SHAPE")
        df = df.astype({col: 'int32' for col in df.select_dtypes('int64').columns})
        df = df.convert_dtypes()
        self._df = df

    # ---------------------------------------------------------------------
    def test_from_sedf(self):
        """tests the converting processs of an SeDF to a pyarrow.Table"""
        tbl = self._df.spatial.to_arrow()
        assert tbl
        assert isinstance(tbl, pyarrow.Table)

    # ---------------------------------------------------------------------
    def test_to_sedf(self):
        """tests converting the pyarrow table to sedf"""
        tbl = self._df.spatial.to_arrow()
        sdf = pd.DataFrame.spatial.from_arrow(tbl)
        assert isinstance(sdf, pd.DataFrame)
        assert sdf.spatial.name
        assert all(
            self._df.dtypes == sdf.dtypes
        )  # checks if the dtypes align from the source to the converted sedf


if __name__ == "__main__":
    unittest.main()
