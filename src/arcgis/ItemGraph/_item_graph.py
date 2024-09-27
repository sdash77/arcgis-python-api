from networkx import DiGraph
from arcgis.gis import Item, GIS
from ._get_dependencies import _get_item_dependencies

class ItemNode:
    def __init__(self, graph, itemid: str):
        self.id = itemid
        self.graph = graph
        self.item = graph.gis.content.get(itemid)

    def _adj_list(self):
        neighbors = []
        neighbors.extend(self.contains())
        neighbors.extend(self.contained_by())
        # do join
        return neighbors
    
    def contains(self):
        return list(self.graph.successors(self.id))
    
    def contained_by(self):
        return list(self.graph.predecessors(self.id))
    
    def requires(self):
        item_list = []
        def _requires(itemid):
            if itemid not in item_list:
                item_list.append(itemid)
                for child in self.graph.successors(itemid):
                    _requires(child)
        _requires(self.id)
        item_list.remove(self.id)
        return item_list

    def required_by(self):
        item_list = []
        def _required_by(itemid):
            if itemid not in item_list:
                item_list.append(itemid)
                for parent in self.graph.predecessors(itemid):
                    _required_by(parent)
        _required_by(self.id)
        item_list.remove(self.id)
        return item_list

class ItemGraph(DiGraph):
    def __init__(self, gis: GIS):
        super().__init__()
        self.gis = gis

    def _create_tree(self, itemid: str):
        tree = {}
        visited = []
        def _assemble_tree(itemid, tree):
            tree[itemid] = {}
            for child in self.successors(itemid):
                if child not in visited:
                    visited.append(child)
                    _assemble_tree(child, tree[itemid])
        
        _assemble_tree(itemid, tree)
        return tree
    
    def add_relationship(self, parent: str, child: str):
        if parent in self and child in self.predecessors(parent):
            raise ValueError("An item cannot be both dependent upon and a dependency of the same item.")
        self.add_edge(parent, child)
        
    def delete_relationship(self, parent: str, child: str):
        self.remove_edge(parent, child)
    
    def add_item(self, itemid: str):
        self.add_node(itemid)

    def delete_item(self, itemid: str):
        self.remove_node(itemid)
    
    def get_item(self, itemid: str):
        return ItemNode(self, itemid)
    
    def all_items(self):
        return list(self.nodes())
    

def create_item_graph(gis: GIS, item_list: list[Item, str], exclude_outside: bool = False):

    graph = ItemGraph(gis)

    def _add_deps(item: Item):
        
        deps = _get_item_dependencies(item, gis)
        for dep in deps:

            # check if we've already checked this item before
            if dep in graph:
                graph.add_relationship(item.itemid, dep)
                continue

            dep_item = gis.content.get(dep)

            # check if item is outside of the organization
            if not dep_item or gis.url not in dep_item.homepage:
                if exclude_outside:
                    continue
                graph.add_relationship(item.itemid, dep)

            # if an item in our org, add it and check its dependencies
            else:
                graph.add_relationship(item.itemid, dep)
                _add_deps(dep_item)

    for item in item_list:
        # first grab our item
        if isinstance(item, str):
            item = gis.content.get(item)
        
        # if valid, add it and check its dependencies
        if item:
            graph.add_item(item.itemid)
            _add_deps(item)
    
    return graph

# class Node:
#     def __init__(self, itemid, **kwargs):
#         self.id = itemid
#         self.adjacency_list = []
#         self.found_in = []
#         self.contains = []
#         self.data = kwargs

# class Graph:
#     def __init__(self):
#         self.node_list = {}
#         self.adjacency_list = 

#     def add_node(self, itemid):
#         if itemid not in self.node_list:
#             self.node_list[itemid] = Node(itemid)

#     def get_vertices(self):
#         return list(self.adjacency_list.keys())

#     def get_edges(self):
#         edges = []
#         for vertex in self.adjacency_list:
#             for neighbor in self.adjacency_list[vertex]:
#                 edges.append((vertex, neighbor))
#         return edges

#     def __str__(self):
#         return str(self.adjacency_list)