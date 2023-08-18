"""
Tests the functionality of the knowledge graph
"""
import sys

sys.path.insert(0, r"YOUR PATH HERE")
import unittest
from arcgis.gis import GIS


try:
    from arcgis.graph import KnowledgeGraph

    # url = "https://dev0018783.esri.com/server/rest/services/Hosted/KGS_PanamaPapers/KnowledgeGraphServer"
    url = "https://dev0022980.esri.com/server/rest/services/Hosted/python_testing/KnowledgeGraphServer"
    gis = GIS(
        # "https://dev0018783.esri.com/portal/",
        "https://dev0022980.esri.com/portal",
        "publisher2",
        "esri.agp123",
        # verify_cert=False,
        trust_env=True,
    )
    kg = KnowledgeGraph(url, gis=gis)
    print("Logged in as: " + gis.properties.user.username)
    SKIP = False
except:
    SKIP = True


@unittest.skipIf(SKIP, "Cannot login or get service")
class TestImport(unittest.TestCase):
    def test_import(self):
        from arcgis.graph import KnowledgeGraph

    def test_search(self):
        items = gis.content.search("type:Knowledge Graph")
        if len(items) > 0:
            assert isinstance(KnowledgeGraph.fromitem(items[0]), KnowledgeGraph)


@unittest.skipIf(SKIP, "Cannot login or get service")
class TestKGMethods(unittest.TestCase):
    """tests the methods"""

    def test_simple_query(self):
        q = """MATCH (n) RETURN n.objectid, n.geometry, n LIMIT 10"""
        result = kg.query(query=q)  # "MATCH (n) RETURN n LIMIT 10")
        assert isinstance(result, (list, tuple))
        if len(result) > 0:
            assert isinstance(result[0], list)

    def test_search(self):
        search = kg.search("China")
        assert isinstance(search, list)

    def test_validate_import(self):
        kg._validate_import()

    def test_apply_edits(self):
        import time
        with self.subTest(msg="Add test"):
            add_dict = {
                "_objectType": "entity",
                "_typeName": "Person",
                "_id": "{3e16d8fe-7f68-45ef-805a-a54d78995472}".upper(),
                "_properties": {
                    "name": "Pikachu",
                }
            }

            res = kg.apply_edits(adds = [add_dict])
            assert isinstance(res, dict)
            time.sleep(1)
            assert len(kg.search("Pikachu")) > 0

        with self.subTest(msg="Update test"):
            update_dict = {
                "_objectType": "entity",
                "_typeName": "Person",
                "_id": "{3e16d8fe-7f68-45ef-805a-a54d78995472}".upper(),
                "_properties": {
                    "name": "Raichu",
                }
            }

            res = kg.apply_edits(updates = [update_dict])
            assert isinstance(res, dict)
            time.sleep(1)
            assert len(kg.search("Raichu")) > 0
        
        with self.subTest(msg="Delete test"):
            delete_dict = {
                "_objectType": "entity",
                "_typeName": "Person",
                "_ids": ["{3e16d8fe-7f68-45ef-805a-a54d78995472}".upper()]
            }

            res = kg.apply_edits(deletes = [delete_dict])
            assert isinstance(res, dict)
            time.sleep(1)
            assert len(kg.search("Raichu")) == 0


@unittest.skipIf(SKIP, "Cannot login or get service")
class TestKGService(unittest.TestCase):
    """tests the properties"""

    def test_datamodel(self):
        """tests getting the datamodel"""
        dm = kg.datamodel
        assert isinstance(dm, dict)

    def test_properties(self):
        props = kg.properties
        assert props


if __name__ == "__main__":
    unittest.main()
