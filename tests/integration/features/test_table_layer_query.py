import unittest
from arcgis.features import Table
from arcgis.gis import GIS


class TestQueryTableLayer(unittest.TestCase):
    """Tests the Query Sub-set functionality of the Table class"""
    def test_query(self):
        gis = GIS(profile='your_online_profile', verify_cert=False)
        items = gis.content.advanced_search('(car)  (typekeywords:Table)  -type:"Code Attachment" -type:"Featured Items" -type:"Symbol Set" -type:"Color Set" -type:"Windows Viewer Add In" -type:"Windows Viewer Configuration" -type:"Map Area" -typekeywords:"MapAreaPackage"')
        
        df = items['results'][1].tables[0].query("1=1", as_df=True)
        assert len(df) >= 0
        fs = items['results'][1].tables[0].query("1=1", as_df=False)
        assert hasattr(fs, 'features')


if __name__ == "__main__":
    unittest.main()