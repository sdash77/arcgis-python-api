import unittest
from arcgis.gis import Item
from arcgis.apps.itemgraph import ItemGraph, ItemNode, create_dependency_graph, load_from_file
import pathlib
import os
import tempfile
from utils.decorators import integration_test, profiles

@integration_test
@profiles.admin_agol
class TestCreateGraph(unittest.TestCase):
    """Test Graph Creation Methods"""
    
    def test_regular_create(self):
        """Create a new graph from a list of StoryMaps"""
        # establish gis connection
        gis = self.gis
        sm_list = gis.content.search("", item_type="StoryMap", max_items=10)
        graph = create_dependency_graph(gis, sm_list)
        graph_items = graph.all_items(out_format = "item")
        assert len(graph_items) >= len(sm_list)
        for item in sm_list:
            assert item in graph_items
    
    def test_related_items_create(self):
        """Create a new graph from an item that has related items,
        and try with reverse dependencies"""
        gis = self.gis
        surv = gis.content.get("d78a3338d1cc485bb61342d00dc65e07")
        # graph with only forward dependencies
        fwd_graph = create_dependency_graph(gis, [surv])
        # graph with forward and reverse dependencies
        rev_graph = create_dependency_graph(gis, [surv], include_reverse=True)
        assert len(rev_graph.all_items()) > len(fwd_graph.all_items())
        fwd_node = fwd_graph.get_node("d78a3338d1cc485bb61342d00dc65e07")
        rev_node = rev_graph.get_node("d78a3338d1cc485bb61342d00dc65e07")
        assert len(fwd_node.contains()) == len(rev_node.contains()) > 0
        assert len(fwd_node.contained_by()) == 0
        assert len(rev_node.contained_by()) > 0
    
    def test_create_from_file(self):
        """Create a new graph from a saved file"""
        gis = self.gis
        path_root = str(pathlib.Path(__file__).parent.resolve())
        path = os.path.join(path_root, "demo_graph.gml")
        no_item_graph = load_from_file(path, gis, False)
        yes_item_graph = load_from_file(path, gis, True)
        assert len(no_item_graph.all_items()) == len(yes_item_graph.all_items()) == 12
        no_node = no_item_graph.get_node("4e373608ba444a639bfaa0c893d3d99d")
        yes_node = yes_item_graph.get_node("4e373608ba444a639bfaa0c893d3d99d")
        assert not no_node.item
        assert isinstance(yes_node.item, Item)

@integration_test
@profiles.admin_agol
class TestGraphFunctions(unittest.TestCase):
    """Test Graph Methods"""

    def test_graph_functions(self):
        gis = self.gis
        path_root = str(pathlib.Path(__file__).parent.resolve())
        path = os.path.join(path_root, "demo_graph.gml")
        graph = load_from_file(path, gis)

        with self.subTest(msg = "listing items"):
            assert isinstance(graph.all_items(), list)
            assert isinstance(graph.all_items()[0], ItemNode)
            assert isinstance(graph.all_items("item")[0], Item)
            assert isinstance(graph.all_items("id")[0], str)
        
        with self.subTest(msg = "adding/deleting items"):
            graph.add_item("123")
            assert len(graph.all_items()) == 13
            graph.delete_item("123")
            assert len(graph.all_items()) == 12
        
        with self.subTest(msg = "adding/deleting relationships"):
            # add relationships between existing nodes
            graph.add_relationship("ce7d9d54fd1249c28809bf00923a19c7", "eefd222765814206ab825c22cfecb13c")
            graph.add_relationship("eefd222765814206ab825c22cfecb13c", "88539e531a3d45fd93e6c6b32bb93572")
            node1 = graph.get_node("ce7d9d54fd1249c28809bf00923a19c7")
            node2 = graph.get_node("eefd222765814206ab825c22cfecb13c")
            node3 = graph.get_node("88539e531a3d45fd93e6c6b32bb93572")
            for out_list in [node1.contains("id"), node1.requires("id"), node3.required_by("id")]:
                assert "eefd222765814206ab825c22cfecb13c" in out_list
            for out_list in [node1.requires("id"), node2.contains("id")]:
                assert "88539e531a3d45fd93e6c6b32bb93572" in out_list
            for out_list in [node2.contained_by("id"), node3.required_by("id")]:
                assert "ce7d9d54fd1249c28809bf00923a19c7" in out_list

            graph.delete_relationship("ce7d9d54fd1249c28809bf00923a19c7", "eefd222765814206ab825c22cfecb13c")
            graph.delete_relationship("eefd222765814206ab825c22cfecb13c", "88539e531a3d45fd93e6c6b32bb93572")

            for out_list in [
                node1.contains(), 
                node1.requires(), 
                node2.contains(), 
                node2.contained_by(),
                node3.required_by(),
                ]:
                assert out_list == []

            # add relationships between nonexistent nodes
            graph.add_relationship("123", "456")
            assert len(graph.all_items()) == 14
            node1 = graph.get_node("123")
            node2 = graph.get_node("456")
            for out_list in [node1.contains("id"), node1.requires("id")]:
                assert "456" in out_list
            for out_list in [node2.contained_by("id"), node2.required_by("id")]:
                assert "123" in out_list
            graph.delete_item("123")
            graph.delete_item("456")
            assert len(graph.all_items()) == 12

        with self.subTest(msg="writing file out and saving"):
            # temp_gml = tempfile.NamedTemporaryFile(suffix="gml")
            temp_dir = tempfile.gettempdir()
            temp_loc = graph.write_to_file(temp_dir + "write_out.gml")
            # read in and check that it's the same as demo_graph.gml

@integration_test
@profiles.admin_agol
class TestNodeFunctions(unittest.TestCase):
    """Test Node Methods"""

    def test_node_functions(self):
        gis = self.gis
        path_root = str(pathlib.Path(__file__).parent.resolve())
        path = os.path.join(path_root, "demo_graph.gml")
        graph = load_from_file(path, gis)
        # node 1 contains node 2, which contains node 3
        node1 = graph.get_node("26411900b96e445ca96745bfb4459d12")
        node2 = graph.get_node("1a914a64a648453ebc3d6e58078f1a40")
        node3 = graph.get_node("e859bcbc593840858872ecfaac5bd3aa")

        with self.subTest(msg="contains"):
            assert isinstance(node1.contains("id"), list)
            assert isinstance(node1.contains("id")[0], str)
            assert isinstance(node1.contains("node")[0], ItemNode)
            assert isinstance(node1.contains("item")[0], Item)
            assert node2.id in node1.contains("id")
            assert node3.id in node2.contains("id")
            assert node3.contains() == []
        
        with self.subTest(msg="contained_by"):
            assert isinstance(node2.contained_by("id"), list)
            assert isinstance(node2.contained_by("id")[0], str)
            assert isinstance(node2.contained_by("node")[0], ItemNode)
            assert isinstance(node2.contained_by("item")[0], Item)
            assert node1.id in node2.contained_by("id")
            assert node2.id in node3.contained_by("id")
            assert node1.contained_by() == []
        
        with self.subTest(msg="requires"):
            assert isinstance(node1.requires("id"), list)
            assert isinstance(node1.requires("id")[0], str)
            assert isinstance(node1.requires("node")[0], ItemNode)
            assert isinstance(node1.requires("item")[0], Item)
            for i in [node2.id, node3.id]:
                assert i in node1.requires("id")
            assert node3.id in node2.requires("id")
            assert node3.requires() == []

        with self.subTest(msg="required_by"):
            assert isinstance(node3.required_by("id"), list)
            assert isinstance(node3.required_by("id")[0], str)
            assert isinstance(node3.required_by("node")[0], ItemNode)
            assert isinstance(node3.required_by("item")[0], Item)
            for i in [node1.id, node2.id]:
                assert i in node3.required_by("id")
            assert node1.id in node2.required_by("id")
            assert node1.required_by() == []

        with self.subTest(msg="misc"):
            assert isinstance(node1.id, str)
            assert node1.id == "26411900b96e445ca96745bfb4459d12"
            assert isinstance(node1.item, Item)
            assert isinstance(node1.graph, ItemGraph)
            assert node1.graph == graph
            assert isinstance(node2._adj_list(), list)
            assert isinstance(node2._adj_list()[0], ItemNode)
            assert len(node2._adj_list()) == 2
            assert len(node1._adj_list()) == len(node3._adj_list()) == 1

@integration_test
@profiles.admin_agol
class TestItemClassFunction(unittest.TestCase):
    """This just involves simple assembly and retrieval of a graph"""

    def test_item_get_dependencies(self):
        gis = self.gis
        exb = gis.content.get("1d69afc7e86c4ab59c4781e67d51fa9c")
        basic_list = exb.get_dependencies()
        deep_basic_list = exb.get_dependencies(deep=True)
        assert isinstance(basic_list, list)
        assert isinstance(basic_list[0], Item)
        assert len(basic_list) == 4
        assert len(deep_basic_list) > 4
        graph = exb.get_dependencies(out_format="graph")
        assert isinstance(graph, ItemGraph)
        id_list = exb.get_dependencies(out_format="id")
        deep_id_list = exb.get_dependencies(deep=True, out_format="id")
        assert isinstance(id_list, list)
        assert isinstance(id_list[0], str)
        assert len(id_list) == 4
        assert len(deep_id_list) > 4

if __name__ == "__main__":
    unittest.main()