import unittest
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles

@profiles.agol
@integration_test
class TestQueryTableLayer(unittest.TestCase):
    """Tests the Query Sub-set functionality of the Table class"""
    @classmethod
    def setUpClass(cls) -> None:
        """
        get test data
        """
        items = cls.gis.content.advanced_search(
            '(car)  (typekeywords:Table)  -type:"Code Attachment" -type:"Featured Items" -type:"Symbol Set" -type:"Color Set" -type:"Windows Viewer Add In" -type:"Windows Viewer Configuration" -type:"Map Area" -typekeywords:"MapAreaPackage"'
        )
        cls.cardiac_arrest_survival_table = items["results"][1].tables[0]
        
        
    def test_query(self):
        df = self.cardiac_arrest_survival_table.query("1=1", as_df=True)
        assert len(df) >= 0
        fs = self.cardiac_arrest_survival_table.query("1=1", as_df=False)
        assert hasattr(fs, "features")

    def test_query_with_ids_only(self):
        total_count = self.cardiac_arrest_survival_table.estimates["count"]
        res = self.cardiac_arrest_survival_table.query(
            where="1=1", return_ids_only=True, return_all_records=False, result_offset=0
        )
        assert "objectIds" in res
        assert len(res["objectIds"]) == total_count
        
    def test_query_with_ids_only_and_offset(self):
        total_count = self.cardiac_arrest_survival_table.estimates["count"]
        res = self.cardiac_arrest_survival_table.query(
            where="1=1", return_ids_only=True, return_all_records=False, result_offset=10
        )
        assert "objectIds" in res
        assert len(res["objectIds"]) == total_count - 10
        
    def test_query_with_ids_only_and_offset_and_count(self):
        res = self.cardiac_arrest_survival_table.query(
            where="1=1", return_ids_only=True, return_all_records=False, result_offset=10, result_record_count=5
        )
        assert "objectIds" in res
        assert len(res["objectIds"]) == 5
    
    def test_query_with_object_ids(self):
        total_count = self.cardiac_arrest_survival_table.estimates["count"]
        object_ids = self.cardiac_arrest_survival_table.query(
            where="1=1", return_ids_only=True, return_all_records=False, result_offset=0
        )["objectIds"]
        object_ids_str = ",".join(map(str, object_ids))
        res = self.cardiac_arrest_survival_table.query(
            where="1=1", return_all_records=False, object_ids=object_ids_str
        )
        assert len(res.features) == total_count
             
if __name__ == "__main__":
    unittest.main()
