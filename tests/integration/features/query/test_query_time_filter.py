import unittest
import pandas as pd
from arcgis.features import FeatureLayer
from utils.decorators import integration_test, profiles
from datetime import datetime

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
    def test_query_time_filter(self):
        """Tests the simple query analytics call"""
        url = "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/World_Countries/FeatureServer/0"
        fl = FeatureLayer(url, gis=self.gis)
        start_time = datetime(2025, 1, 1)
        end_time = datetime.now()
        time_range = [start_time, end_time]
        result = fl.query(where='1=1', time_filter=time_range, as_df=True)
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0


###########################################################################
if __name__ == "__main__":
    unittest.main()