from networkx import DiGraph
from arcgis.gis import Item, GIS
from ._get_dependencies import _get_item_dependencies


class ItemNode:
    """
    An ItemNode is a node in an ItemGraph. It represents an item in the graph and contains methods to
    interact with the graph and other items in the graph. It is not intended to be created directly by
    the user, but rather as a part of the ItemGraph class. The nodes are very simple- the only properties
    they contain are the item ID, a reference to the graph they're tied to, and in most cases, a
    reference to the item they're tied to. Cases where an item will not be included:
    1. The item does not exist, or is not accessible to the user (e.g. outside of the organization)
    2. The graph is being reconstructed from a list of item ID's and the item has not been fetched yet
    In this second case, other methods will be used to fetch the item when needed, in order to maximize
    efficiency when creating a large graph.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    graph               Required ItemGraph. The graph instance that the node is associated
                        with.
    ---------------     --------------------------------------------------------------------
    itemid              Required String. The item ID of the item that the node represents.
    ---------------     --------------------------------------------------------------------
    item                Optional Item. An instance of the item that the node represents.
    ===============     ====================================================================
    """

    def __init__(self, graph, itemid: str, item=None):
        self.id = itemid
        self.graph = graph
        if item:
            self.item = item

    def _adj_list(self):
        """
        Returns a list of all items that are directly connected to this item.
        """
        neighbors = []
        neighbors.extend(self.contains())
        neighbors.extend(self.contained_by())
        # do join
        return neighbors

    def contains(self, out_format: str = "id"):
        """
        Compiles all of the items that this item directly contains. Can be returned in either
        the format of a list of item ID's, a list of item instances, or a list of graph nodes.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        out_format          Optional string. Options are "id", "item", and "node". Default is
                            "id".

                            .. note::
                                If this is set to "item", and an item instance is not
                                accessible, the item ID will be returned for that item instead.
        ===============     ====================================================================

        :return:
            A list of item ID's or items.
        """

        out_format = out_format.lower()
        # if returning items or nodes instead of just id's...
        if out_format != "id":
            items = []
            for c in self.graph.successors(self.id):
                node = self.graph.get_item(c)
                # if node format, append node
                if out_format == "node":
                    items.append(node)
                    continue
                # otherwise, try to append the item
                if node.item:
                    items.append(node.item)
                # otherwise, grab it
                else:
                    item = self.graph.gis.content.get(c)
                    if item != None:
                        items.append(item)
                    # if there's no item available, append id
                    else:
                        items.append(c)
            return items
        # if not items, just return list of id's
        else:
            return list(self.graph.successors(self.id))

    def contained_by(self, out_format: str = "id"):
        """
        Compiles all of the items that directly contain this item. Can be returned in either
        the format of a list of item ID's, a list of item instances, or a list of graph nodes.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        out_format          Optional string. Options are "id", "item", and "node". Default is
                            "id".

                            .. note::
                                If this is set to "item", and an item instance is not
                                accessible, the item ID will be returned for that item instead.
        ===============     ====================================================================

        :return:
            A list of item ID's or items.
        """

        out_format = out_format.lower()
        # if returning items instead of just id's...
        if out_format != "id":
            items = []
            for p in self.graph.predecessors(self.id):
                node = self.graph.get_item(p)
                # if node format, append node
                if out_format == "node":
                    items.append(node)
                    continue
                # otherwise, try to append the item
                if node.item:
                    items.append(node.item)
                # otherwise, grab it
                else:
                    item = self.graph.gis.content.get(p)
                    if item != None:
                        items.append(item)
                    # if there's no item available, append id
                    else:
                        items.append(p)
            return items
        # if not items, just return list of id's
        else:
            return list(self.graph.predecessors(self.id))

    def requires(self, out_format: str = "id"):
        """
        Compiles a deep list of all items that this item requires to exist. For example, if an
        item contains a WebMap item that itself contains a Feature Service item, then both of
        them will be returned in the output list. Can be returned in either the format of a
        list of item ID's, a list of item instances, or a list of graph nodes.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        out_format          Optional string. Options are "id", "item", and "node". Default is
                            "id".

                            .. note::
                                If this is set to "item", and an item instance is not
                                accessible, the item ID will be returned for that item instead.
        ===============     ====================================================================

        :return:
            A list of item ID's or items.
        """

        out_format = out_format.lower()
        item_list = []

        # recursive function to create deep list
        def _requires(itemid):
            # if id's...
            if out_format == "id":
                item = itemid
            # if returning items or nodes...
            else:
                # grab the node
                node = self.graph.get_item(itemid)
                # if node format, use node
                if out_format == "node":
                    item = node
                # otherwise, check if item was included when node was created
                else:
                    item = node.item
                    if not item:
                        item = self.graph.gis.content.get(itemid)
                    # if still not, just use the item id
                    if not item:
                        item = itemid

            # if we haven't visited it already, process it
            if item not in item_list:
                # run the recursion first so we get all the way to the leaf nodes
                # this ensures that any cloning will take care of stuff in right order
                for child in self.graph.successors(itemid):
                    _requires(child)
                item_list.append(item)

        _requires(self.id)
        # remove the original item, we don't need to include the self
        item_list.pop()
        return item_list

    def required_by(self, out_format: str = "id"):
        """
        Compiles a deep list of all items that require this item to exist. For example, if this
        item is a Feature Service found in a WebMap that is then itself found in a Dashboard,
        both of those items will be in the output list, on the condition that they have been
        indexed into the ItemGraph. Can be returned in either the format of a list of item ID's,
        a list of item instances, or a list of graph nodes.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        out_format          Optional string. Options are "id", "item", and "node". Default is
                            "id".

                            .. note::
                                If this is set to "item", and an item instance is not
                                accessible, the item ID will be returned for that item instead.
        ===============     ====================================================================

        :return:
            A list of item ID's or items.
        """

        out_format = out_format.lower()
        item_list = []

        # recursive function to create deep list
        def _required_by(itemid):
            # if id's...
            if out_format == "id":
                item = itemid
            # if returning items or nodes...
            else:
                # grab the node
                node = self.graph.get_item(itemid)
                # if node format, use node
                if out_format == "node":
                    item = node
                # otherwise, check if item was included when node was created
                else:
                    item = node.item
                    if not item:
                        item = self.graph.gis.content.get(itemid)
                    # if still not, just use the item id
                    if not item:
                        item = itemid

            # if we haven't visited it already, process it
            if item not in item_list:
                item_list.append(item)
                # run recursively
                for parent in self.graph.predecessors(itemid):
                    _required_by(parent)

        _required_by(self.id)
        # remove the original item, we don't need to include the self
        item_list.pop(0)
        return item_list


class ItemGraph(DiGraph):
    """
    An ItemGraph is a directional dependency graph that represents relationships between
    items. An item is deemed to be dependent upon another item if the other item appears in
    the first item's data, structure, or dependent items property- the relationship type of
    this graph can be intepreted as "Item A needs Item B to exist". Users can retrieve an
    item in the graph via an item's item ID (assuming the item has been indexed into the
    graph), at which point they'll get an ItemNode to work with. Users can manually add
    items or relationships to the graph if desired, but most of the time this will be taken
    care by other functions, such as the create_item_graph function. The graph is built on
    top of the NetworkX DiGraph class, meaning it also inherits all of its methods and
    properties as well.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    gis                 Required GIS. The GIS instance that the graph is associated with.
    ===============     ====================================================================

    """

    def __init__(self, gis: GIS):
        super().__init__()
        self.gis = gis

    def _create_tree(self, itemid: str):
        """
        Private method to create a tree structure of the graph starting from a given item ID.
        Items will not get repeated, meaning that even if one item is traversed multiple times
        during construction of the tree, it will only exist once in the tree. This is useful
        for visualizing the dependencies of an item in a hierarchical way.
        """
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
        """
        Adds a relationship to the graph. This relationship is directional: the parent item
        contains the child item, so the parent item is dependent upon the child. If either
        item is not already in the graph, they will be automatically added.

        .. note::
            Relationships cannot go both ways- an item cannot be both dependent upon and
            a dependency of the same item. Attempting to add a relationship will fail if
            the inverse already exists.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        parent              Required string. The item ID of the parent item.
        ---------------     --------------------------------------------------------------------
        child               Required string. The item ID of the child item.
        ===============     ====================================================================
        """

        if parent not in self:
            self.add_item(parent)
        if child not in self:
            self.add_item(child)

        if parent in self and child in self.predecessors(parent):
            raise ValueError(
                "An item cannot be both dependent upon and a dependency of the same item."
            )
        self.add_edge(parent, child)

    def delete_relationship(self, parent: str, child: str):
        """
        Deletes a relationship from the graph. The relationship is directional, so it is
        important to properly specify which item is the parent and which is the child.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        parent              Required string. The item ID of the parent item.
        ---------------     --------------------------------------------------------------------
        child               Required string. The item ID of the child item.
        ===============     ====================================================================
        """
        self.remove_edge(parent, child)

    def add_item(self, itemid: str, item=None):
        """
        Adds an item to the graph. The item ID is required, but the item itself is optional.
        Creates an ItemNode with the item ID and item. Will usually be called by other functions
        and not by users.
        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        itemid              Required string. The item ID of the item to add.
        ---------------     --------------------------------------------------------------------
        item                Optional Item. An instance of the item to add.
        ===============     ====================================================================
        """
        node = ItemNode(self, itemid, item)
        self.add_node(itemid, data=node)

    def delete_item(self, itemid: str):
        """
        Deletes an item from the graph. Associated relationships will also be removed.
        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        itemid              Required string. The item ID of the item to remove.
        ===============     ====================================================================
        """
        self.remove_node(itemid)

    def get_item(self, itemid: str):
        """
        Returns an ItemNode of the item in the graph with the given item ID. If the item is not
        in the graph, None will be returned.
        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        itemid              Required string. The item ID of the item to retrieve.
        ===============     ====================================================================
        """
        try:
            return self.nodes[itemid]["data"]
        except:
            return None

    def all_items(self):
        """
        Returns a list of the item ID's of all items in the graph.
        """
        return list(self.nodes())


def create_item_graph(gis: GIS, item_list: list[Item, str], outside_org: bool = True):
    """
    Creates an ItemGraph from a list of items. The function recursively explores the dependencies
    of each item involved that's part of the organization, encompassing the full dependency tree
    of each source item. Contains an option to include items from outside the organization;
    if they are included, they are not explored for dependencies, but are still part of the
    graph.
    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    gis                 Required GIS. The GIS instance that the graph is associated with.
    ---------------     --------------------------------------------------------------------
    item_list           Required list. A list of items to include in the graph. Items can be
                        either Item instances or item ID's.
    ---------------     --------------------------------------------------------------------
    outside_org         Optional boolean. When True, items outside of the organization will
                        be included in the graph (but still not explored for their
                        dependencies). When False, only items owned by users in the org will
                        be included in the graph. Default is True.
    ===============     ====================================================================

    :return:
            An ItemGraph with all of the relevant items and relationships.
    """

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
                if not outside_org:
                    continue
                graph.add_item(dep, dep_item)
                graph.add_relationship(item.itemid, dep)

            # if an item in our org, add it and check its dependencies
            else:
                graph.add_item(dep, dep_item)
                graph.add_relationship(item.itemid, dep)
                _add_deps(dep_item)

    for item in item_list:
        # first grab our item
        if isinstance(item, str):
            item = gis.content.get(item)

        # if valid, add it and check its dependencies
        if item:
            graph.add_item(item.itemid, item)
            _add_deps(item)

    return graph
