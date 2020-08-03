import unittest
import pandas as pd
import concurrent.futures
from arcgis.features import FeatureLayer
from arcgis.gis import GIS, ProfileManager

PROFILES = [None]#['your_online_profile']
###########################################################################

class TestQueryAnalytics(unittest.TestCase):
    """
    Tests the new functionality of the queryanalytics functionality on 
    FeatureLayer
    """
    #----------------------------------------------------------------------
    def test_query(self):
        """Tests the simple query analytics call"""
        url = "https://servicesdev1.arcgis.com/lidGgNLxw9LL0SbI/arcgis/rest/services/counties/FeatureServer/0"
        gis = GIS(profile=PROFILES[0], verify_cert=False)
        fl = FeatureLayer(url, gis=gis)
        analytics = [{
            "analyticType": "CUME_DIST",
            "onAnalyticField": "POP1990",
            "outAnalyticFieldName": "CumDistance",
            "analyticParameters" : {
                "orderBy": "POP1990",
                "partitionBy" : "state_name"
            }
        }]
        result = fl.query_analytics(where="1=1",
                                    out_analytics=analytics,
                                    future=False)
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0
        assert "CumDistance" in result.columns
    ##----------------------------------------------------------------------
    def test_query_async(self):
        """Tests the simple query analytics call"""
        url = "https://servicesdev1.arcgis.com/lidGgNLxw9LL0SbI/arcgis/rest/services/counties/FeatureServer/0"
        gis = GIS(profile=PROFILES[0], verify_cert=False)
        fl = FeatureLayer(url, gis=gis)
        analytics = [{
            "analyticType": "CUME_DIST",
            "onAnalyticField": "POP1990",
            "outAnalyticFieldName": "CumDistance",
            "analyticParameters" : {
                "orderBy": "POP1990",
                "partitionBy" : "state_name"
            }
        }]
        result = fl.query_analytics(where="1=1",
                                    out_analytics=analytics,
                                    future=True)
        assert isinstance(result, concurrent.futures.Future)
        result = result.result()
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0
        assert "CumDistance" in result.columns
    #----------------------------------------------------------------------
    def test_query_async_less_than_100(self):
        """Tests the simple query analytics call"""
        url = "https://servicesdev1.arcgis.com/lidGgNLxw9LL0SbI/arcgis/rest/services/counties/FeatureServer/0"
        gis = GIS(profile=PROFILES[0], verify_cert=False)
        fl = FeatureLayer(url, gis=gis)
        analytics = [{
            "analyticType": "CUME_DIST",
            "onAnalyticField": "POP1990",
            "outAnalyticFieldName": "CumDistance",
            "analyticParameters" : {
                "orderBy": "POP1990",
                "partitionBy" : "state_name"
            }
        }]

        result = fl.query_analytics(where=f"{fl.properties.objectIdField} <= 50",
                                    out_analytics=analytics,
                                    future=True)
        assert isinstance(result, concurrent.futures.Future)
        result = result.result()
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 50
        assert "CumDistance" in result.columns
    
###########################################################################
if __name__ == "__main__":
    unittest.main()
    