import unittest
import pandas as pd
import concurrent.futures
from arcgis.features import FeatureLayer
from arcgis.gis import GIS, ProfileManager
from utils.decorators import integration_test, profiles

# Use World Countries Feature Layer item: 2ef6f1c2b2e04e68b30c54899d82d123
###########################################################################


@profiles.agol
@integration_test
class TestQueryAnalytics(unittest.TestCase):
    """
    Tests the new functionality of the queryanalytics functionality on
    FeatureLayer
    """

    # ----------------------------------------------------------------------
    def test_query(self):
        """Tests the simple query analytics call"""
        url = "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/World_Countries/FeatureServer/0"
        fl = FeatureLayer(url, gis=self.gis)
        analytics = [
            {
                "analyticType": "CUME_DIST",
                "onAnalyticField": "POP2007",
                "outAnalyticFieldName": "Cumulative_Distrib",
                "analyticParameters": {"orderBy": "POP2007", "partitionBy": "STATUS"},
            }
        ]
        result = fl.query_analytics(
            where="POP2007 > 0", out_analytics=analytics, future=False
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0
        assert "Cumulative_Distrib" in result.columns

    ##----------------------------------------------------------------------
    def test_query_async(self):
        """Tests the simple query analytics call"""
        url = "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/World_Countries/FeatureServer/0"
        fl = FeatureLayer(url, gis=self.gis)
        analytics = [
            {
                "analyticType": "CUME_DIST",
                "onAnalyticField": "POP2007",
                "outAnalyticFieldName": "Cumulative_Distrib",
                "analyticParameters": {
                    "orderBy": "POP2007",
                    "partitionBy": "STATUS",
                },
            }
        ]
        result = fl.query_analytics(where="1=1", out_analytics=analytics, future=True)
        assert isinstance(result, concurrent.futures.Future)
        result = result.result()
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0
        assert "Cumulative_Distrib" in result.columns

    ## ----------------------------------------------------------------------
    def test_query_async_less_than_100(self):
        """Tests the simple query analytics call"""
        url = "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/World_Countries/FeatureServer/0"
        fl = FeatureLayer(url, gis=self.gis)
        analytics = [
            {
                "analyticType": "CUME_DIST",
                "onAnalyticField": "POP2007",
                "outAnalyticFieldName": "Cumulative_Distrib",
                "analyticParameters": {
                    "orderBy": "POP2007",
                    "partitionBy": "STATUS",
                },
            }
        ]

        result = fl.query_analytics(
            where=f"{fl.properties.objectIdField} <= 100",
            out_analytics=analytics,
            future=True,
        )
        assert isinstance(result, concurrent.futures.Future)
        result = result.result()
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 100
        assert "Cumulative_Distrib" in result.columns


###########################################################################
if __name__ == "__main__":
    unittest.main()
