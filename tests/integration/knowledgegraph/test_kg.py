"""
Tests the functionality of the knowledge graph
"""
import sys

# sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
import unittest
from arcgis.gis import GIS


try:
    from arcgis.graph import KnowledgeGraph

    url = "https://dev0018783.esri.com/server/rest/services/Hosted/KGS_PanamaPapers/KnowledgeGraphServer"
    gis = GIS(
        "https://dev0018783.esri.com/portal/",
        "publisher2",
        "esri.agp123",
        verify_cert=False,
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
        items = gis.content.search('type:Knowledge Graph')
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
