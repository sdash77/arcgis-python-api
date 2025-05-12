import os
import tempfile
import unittest
from utils.decorators import integration_test, profiles
from arcgis.apps.itemgraph import create_dependency_graph, load_from_file


@profiles.admin_enterprise
@integration_test
class TestGraphDependencies(unittest.TestCase):

    def test_dependency_graph(self):
        # pythonapitestnb org, use an admin profile

        bad_map = self.gis.content.get("ba1de9bd8c834089ba46c61d260dcd2a")
        map_with_fs = self.gis.content.get("b9345eeadcee4bef9ac13ed88e647025")

        # test 1: graph still gets created even when analyzing corrupted item
        graph = create_dependency_graph(self.gis, [bad_map, map_with_fs])
        graph_nodes = graph.nodes
        assert len(graph_nodes.items()) == 4
        assert graph is not None

        # test 2: graph nodes get created properly from file even when services have underscores
        tempdir = tempfile.mkdtemp()
        out_path = graph.write_to_file(os.path.join(tempdir, "gml_file.gml"))
        self.assertTrue(os.path.exists(out_path), "Could not find gml file")
        graph2 = load_from_file(out_path, self.gis, True)
        fs_node = graph2.get_node(
            "https://oceans1.arcgis.com/arcgis/rest/services/USA_Drilling_Platforms/FeatureServer/0"
        )
        assert (
            fs_node.id
            == "https://oceans1.arcgis.com/arcgis/rest/services/USA_Drilling_Platforms/FeatureServer/0"
        )
        assert isinstance(fs_node.contained_by(), list)

    def test_story_map_dependencies(self):
        story_map = self.gis.content.get("ba1de9bd8c834089ba46c61d260dcd2a")
        graph = create_dependency_graph(self.gis, [story_map])
        graph_nodes = graph.nodes
        self.assertIsNotNone(graph_nodes.items(), "Story map deps not found")
        self.assertGreaterEqual(1, len(graph_nodes.items()), "Missing graph items")
        nodes_list = [n for n in graph_nodes]
        item_from_graph = self.gis.content.get(nodes_list[0])
        self.assertEqual(
            "StoryMap",
            item_from_graph.type,
            f"Unexpected item type: {item_from_graph.type}",
        )

    def test_web_map_dependencies(self):
        item = self.gis.content.get("0e28eb3472854ff6a6831aa3769a1fda")
        graph = create_dependency_graph(self.gis, [item])
        graph_nodes = graph.nodes
        self.assertIsNotNone(graph_nodes.items(), "Story map deps not found")
        self.assertGreaterEqual(3, len(graph_nodes.items()), "Missing graph items")
        for node in graph_nodes:
            item = self.gis.content.get(node)
            self.assertTrue(
                item.type in ["Map Service", "Web Map", "StoryMap"],
                f"Unexpected item type found: {item.type}",
            )

    def test_feature_layer_dependencies(self):
        item = self.gis.content.get("b84064f8638c47e89bfd3edb49acb628")
        graph = create_dependency_graph(self.gis, [item])
        graph_nodes = graph.nodes
        self.assertIsNotNone(graph_nodes.items(), "Story map deps not found")
        self.assertGreaterEqual(2, len(graph_nodes.items()), "Missing graph items")
        for node in graph_nodes:
            item = self.gis.content.get(node)
            self.assertTrue(
                item.type in ["Feature Service", "Service Definition"],
                f"Unexpected item type found: {item.type}",
            )
