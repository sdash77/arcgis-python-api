import time
import unittest
import concurrent.futures
from arcgis.gis import ContentManager
from utils.decorators import integration_test, profiles


@profiles.enterprise_and_agol
@integration_test
class TestFeatureLayerCalculate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_path = "./calculate_sd.zip"
        uid = int(time.time())
        cm = cls.gis.content
        assert isinstance(cm, ContentManager)
        cls.add_item = cm.add(
            item_properties={
                "title": f"calculate_sd_{uid}",
                "type": "File Geodatabase",
                "tags": "ntgrtn-tst",
            },
            data=file_path,
        )
        cls.pitem = cls.add_item.publish(
            {"name": f"calculate_sd_{uid}", "tags": "ntgrtn-tst"}
        )

    def test_calculate_basic(self):
        """tests a simple calculate method"""
        fl = self.pitem.layers[0]
        field_to_update = [
            f for f in fl.properties.fields if f.name.upper() == "FIPS_CNTRY"
        ][0]
        field_to_update = field_to_update.name
        res = fl.calculate(
            where="ObjectID < 519",
            calc_expression={"field": field_to_update, "value": "R1"},
            future=False,
        )
        verify_update = fl.query(where=f"{field_to_update} = 'R1'")
        self.assertTrue(
            len(verify_update.features), "No results from calculated attribute."
        )

    def test_calculate_async(self):
        """tests a simple calculate method using the asynchronous method"""
        fl = self.pitem.layers[0]
        field_to_update = [
            f for f in fl.properties.fields if f.name.upper() == "FIPS_CNTRY"
        ][0]
        field_to_update = field_to_update.name
        res = fl.calculate(
            where="ObjectID < 519",
            calc_expression={"field": field_to_update, "value": "R1"},
            future=True,
        )
        self.assertIsNotNone(res, "No result returned")
        self.assertIsInstance(
            res, concurrent.futures.Future, "Result is not a <Future> instance"
        )
        self.assertTrue(res.result(), "Incorrect async result")
        verify_update = fl.query(where=f"{field_to_update} = 'R1'")
        self.assertTrue(
            len(verify_update.features), "No results from calculated attribute."
        )

    @classmethod
    def tearDownClass(cls):
        if cls.pitem:
            cls.pitem.delete(permanent=True)
        if cls.add_item:
            cls.add_item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
