from typing import Any, Union, Generator, Optional, Sequence

from arcgis.gis import GIS, Item
from arcgis.gis._impl._util import _get_item_url
from arcgis.graph._service import KnowledgeGraph
from arcgis.graph.data_model_types import (
    FieldIndex,
    EntityType,
    RelationshipType,
    NamedObjectTypeMask,
    GraphProperty,
    GraphPropertyMask,
    ConstraintRule,
    ConstraintRuleUpdate,
    GraphDataModel,
)
from arcgis.graph.graph_types import (
    Entity,
    Relationship,
    EntityDelete,
    RelationshipDelete,
    Transform,
    _client_core_to_python_value,
    _python_to_client_core_value,
)
from arcgis.graph.search_types import (
    SearchIndexProperties,
    esriNamedTypeCategory,
)
from arcgis.graph.response_types import (
    UpdateSearchIndexResponse,
    SyncDataModelResponse,
    NamedObjectTypeAddsResponse,
    NamedObjectTypeUpdateResponse,
    NamedObjectTypeDeleteResponse,
    PropertyAddsResponse,
    PropertyUpdateResponse,
    PropertyDeleteResponse,
    IndexAddsResponse,
    IndexDeletesResponse,
    ConstraintRuleAddsResponse,
    ConstraintRuleUpdatesResponse,
    ConstraintRuleDeletesResponse,
    ApplyEditsResponse,
)


class Graph:
    """
    Provides access to the Knowledge Graph service data model and properties, as well as
    methods to search and query the graph.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    url                    Knowledge Graph service URL
    ------------------     --------------------------------------------------------------------
    gis                    an authenticated :class:`arcgis.gis.GIS` object.
    ==================     ====================================================================

    .. code-block:: python

        # Connect to a Knowledge Graph service:

        gis = GIS(url="url", username="username", password="password")
        graph = Graph(url=url, gis=gis)

    """

    def __init__(self, url: str, gis: GIS):
        """initializer"""
        self._knowledge_graph = KnowledgeGraph(
            url=url,
            gis=gis,
        )

    @classmethod
    def fromitem(cls, item: Item):
        """Returns the Knowledge Graph service from an Item"""
        if item.type != "Knowledge Graph":
            raise ValueError(
                "Invalid item type, please provide a 'Knowledge Graph' item."
            )
        if item._gis._use_private_url_only:
            url: str = _get_item_url(item=item)
        else:
            url: str = item.url
        return cls(url=url, gis=item._gis)

    def search(
        self, search: str, category: esriNamedTypeCategory
    ) -> Generator[Sequence[Any], None, None]:
        """
        Allows for the searching of the properties of entities,
        relationships, or both in the graph using a full-text index.

        `Learn more about searching a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-graph-search.htm>`_

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        search              Required String. The search to perform on the Knowledge Graph.
        ----------------    ---------------------------------------------------------------
        category            Required esriNamedTypeCategory.  The category is the location of the full
                            text search.  This can be isolated to either the `entities` or
                            the `relationships`.

                            The allowed values are: both, entities, relationships,
                            both_entity_relationship, and meta_entity_provenance. Both and
                            both_entity_relationship are functionally the same.
        ================    ===============================================================

        .. note::
            Check the `service definition for the Knowledge Graph service <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-hosted-server.htm>`_
            for valid values of category. Not all services support both and both_entity_relationship.

        .. code-block:: python

            # Perform a search on the knowledge graph
            for search_result in graph.search("cat", "both"):
                print(search_result)

            # Perform a search on only entities in the knowledge graph
            for searchentities_result in graph.search("cat", "entities"):
                print(searchentities_result)

        :return: Generator[Sequence[Any], None, None]

        """
        for row in self._knowledge_graph._search(search=search, category=category):
            yield _client_core_to_python_value(client_core_value=row)

    def update_search_index(
        self,
        adds: dict[str, SearchIndexProperties] = {},
        deletes: dict[str, SearchIndexProperties] = {},
    ) -> UpdateSearchIndexResponse:
        """
        Allows users to add or delete search index properties for different entities and
        relationships from the graph's data model. Can only be existent properties for a given
        entity/relationship.

        =========================   ===============================================================
        **Parameter**                **Description**
        -------------------------   ---------------------------------------------------------------
        adds                        Optional dict. The properties to add to the search index,
                                    specified by entity/relationship type.
        -------------------------   ---------------------------------------------------------------
        deletes                     Optional dict. The properties to delete from the search index,
                                    specified by entity/relationship type.
        =========================   ===============================================================

        :return: `UpdateSearchIndexResponse`

        """
        raw_adds: dict[str, Any] = {
            type_name: adds[type_name].model_dump(by_alias=True) for type_name in adds
        }
        raw_deletes: dict[str, Any] = {
            type_name: deletes[type_name].model_dump(by_alias=True)
            for type_name in deletes
        }
        return UpdateSearchIndexResponse.model_validate(
            self._knowledge_graph.update_search_index(
                adds=raw_adds, deletes=raw_deletes
            )
        )

    def query(
        self,
        query: str,
        input_transform: Optional[Transform] = None,
        bind_param: dict[str, Any] = {},
        include_provenance: bool = False,
    ) -> Generator[Sequence[Any], None, None]:
        """
        Query the graph using an openCypher query. Creates a generator of the query results,
        from which users can access each row or add them to a list. See below for example usage.


        ===================    ===============================================================
        **Parameter**           **Description**
        -------------------    ---------------------------------------------------------------
        query                  Required String. Allows you to return the entities and
                               relationships in a graph, as well as the properties of those
                               entities and relationships, by providing an openCypher query.
        -------------------    ---------------------------------------------------------------
        input_transform        Optional Transform. Allows a user to specify custom quantization
                               parameters for input geometry, which dictate how geometries are
                               compressed and transferred to the server. Defaults to lossless
                               WGS84 quantization.
        -------------------    ---------------------------------------------------------------
        bind_param             Optional dict. The bind parameters used to filter
                               query results. Key of each pair is the string name for it,
                               which is how the parameter can be referenced in the query. The
                               value can be any "primitive" type value that may be found as
                               an attribute of an entity or relationship (e.g., string,
                               double, boolean, etc.), a list, an anonymous object,
                               or a geometry.

                               Note: Including bind parameters not used in the query will
                               cause queries to yield nothing on ArangoDB based services,
                               while Neo4j based services will still produce results.
        -------------------    ---------------------------------------------------------------
        include_provenance     Optional boolean. When `True`, provenance entities (metadata)
                               will be included in the query results. Defaults to `False`.
        ===================    ===============================================================

        .. code-block:: python

            # Get a list of all query results
            query_gen = graph.query("MATCH path = (n)-[r]-(n2) RETURN path LIMIT 5")
            results = list(gen)

            # Grab one result at a time
            query_gen = graph.query("MATCH path = (n)-[r]-(n2) RETURN path LIMIT 5")
            first_result = next(query_gen)
            second_result = next(query_gen)

        :return: `Generator[Sequence[Any], None, None]`

        """
        raw_input_transform: Optional[dict[str, Any]] = (
            None
            if input_transform is None
            else input_transform.model_dump(by_alias=True)
        )
        raw_bind_param: dict[str, Any] = {
            key: _python_to_client_core_value(value)
            for key, value in bind_param.items()
        }
        for row in self._knowledge_graph.query_streaming(
            query=query,
            input_transform=raw_input_transform,  # type: ignore
            bind_param=raw_bind_param,
            include_provenance=include_provenance,
        ):
            yield _client_core_to_python_value(client_core_value=row)

    def query_data_model(self) -> GraphDataModel:
        """
        Returns the datamodel for the Knowledge Graph service
        """
        return GraphDataModel.model_validate(self._knowledge_graph.datamodel)

    def sync_data_model(self) -> SyncDataModelResponse:
        """
        Synchronizes the Knowledge Graph Service's data model with any changes made
        in the database. Will return any errors or warnings from the sync.

        .. code-block:: python

            # Synchronize the data model
            sync_result = knowledge_graph.sync_data_model()

        :return: `SyncDataModelResponse`

        """
        return SyncDataModelResponse.model_validate(
            self._knowledge_graph.sync_data_model()
        )

    def apply_edits(
        self,
        adds: Sequence[Union[Entity, Relationship]] = [],
        updates: Sequence[Union[Entity, Relationship]] = [],
        deletes: Sequence[Union[EntityDelete, RelationshipDelete]] = [],
        input_transform: Optional[Transform] = None,
        cascade_delete: bool = False,
        cascade_delete_provenance: bool = False,
    ) -> ApplyEditsResponse:
        """
        Allows users to add new graph entities/relationships, update existing
        entities/relationships, or delete existing entities/relationships.

        =========================   ===============================================================
        **Parameter**                **Description**
        -------------------------   ---------------------------------------------------------------
        adds                        Optional Sequence of Union[Entity, Relationship]. The Sequence of
                                    objects to add to the graph.
        -------------------------   ---------------------------------------------------------------
        updates                     Optional Sequence of Union[Entity, Relationship]. The Sequence of
                                    existent graph objects that are to be updated.
        -------------------------   ---------------------------------------------------------------
        deletes                     Optional Sequence of Union[EntityDelete, RelationshipDelete].
                                    The Sequence of existent objects to remove from the graph.
        -------------------------   ---------------------------------------------------------------
        input_transform             Optional Transform. Allows a user to specify custom quantization
                                    parameters for input geometry, which dictate how geometries are
                                    compressed and transferred to the server. Defaults to lossless
                                    WGS84 quantization.
        -------------------------   ---------------------------------------------------------------
        cascade_delete              Optional boolean. When `True`, relationships connected to
                                    entities that are being deleted will automatically be deleted
                                    as well. When `False`, these relationships must be deleted
                                    manually first. Defaults to `False`.
        -------------------------   ---------------------------------------------------------------
        cascade_delete_provenance   Optional boolean. When `True`, deleting entities/relationships
                                    or setting their property values to null will result in
                                    automatic deletion of associated provenance records. When
                                    `False`, `apply_edits()` will fail if there are provenance
                                    records connected to entities/relationships intended for
                                    deletion or having their properties set to null.
        =========================   ===============================================================

        :return: A `dict` showing the results of the edits.

        """
        raw_adds: list[dict[str, Any]] = [
            named_object.model_dump(by_alias=True) for named_object in adds
        ]
        raw_updates: list[dict[str, Any]] = [
            named_object.model_dump(by_alias=True) for named_object in updates
        ]
        raw_deletes: list[dict[str, Any]] = [
            named_object_delete.model_dump(by_alias=True)
            for named_object_delete in deletes
        ]
        raw_input_transform: Optional[dict[str, Any]] = (
            None
            if input_transform is None
            else input_transform.model_dump(by_alias=True)
        )
        return ApplyEditsResponse.model_validate(
            self._knowledge_graph.apply_edits(
                adds=raw_adds,
                updates=raw_updates,
                deletes=raw_deletes,
                input_transform=raw_input_transform,  # type: ignore
                cascade_delete=cascade_delete,
                cascade_delete_provenance=cascade_delete_provenance,
            )
        )

    def named_object_type_adds(
        self,
        entity_types: Sequence[EntityType] = [],
        relationship_types: Sequence[RelationshipType] = [],
    ) -> NamedObjectTypeAddsResponse:
        """
        Adds entity and relationship types to the data model

        `Learn more about adding named types to a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-add.htm>`_

        ==================  ===============================================================
        **Parameter**        **Description**
        ------------------  ---------------------------------------------------------------
        entity_types        Optional Sequence of EntityType. The Sequence of entity types to add
                            to the data model.
        ------------------  ---------------------------------------------------------------
        relationship_types  Optional Sequence of RelationshipType. The Sequence of relationship
                            types to add to the data model.
        ==================  ===============================================================

        :return: `NamedObjectTypeAddsResponse`

        """
        raw_entity_types: list[dict[str, Any]] = [
            entity_type.model_dump(by_alias=True) for entity_type in entity_types
        ]
        raw_relationship_types: list[dict[str, Any]] = [
            relationship_type.model_dump(by_alias=True)
            for relationship_type in relationship_types
        ]
        return NamedObjectTypeAddsResponse.model_validate(
            self._knowledge_graph.named_object_type_adds(
                entity_types=raw_entity_types,
                relationship_types=raw_relationship_types,
            )
        )

    def named_object_type_update(
        self,
        type_name: str,
        named_type_update: Union[EntityType, RelationshipType],
        mask: NamedObjectTypeMask,
    ) -> NamedObjectTypeUpdateResponse:
        """
        Updates an entity or relationship type in the data model

        `Learn more about updating named types in a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-type-update.htm>`_

        =================   ===============================================================
        **Parameter**        **Description**
        -----------------   ---------------------------------------------------------------
        type_name           Required string. The named type to be updated.
        -----------------   ---------------------------------------------------------------
        named_type_update   Required Union[EntityType, RelationshipType]. The entity or
                            relationship type to be updated.
        -----------------   ---------------------------------------------------------------
        mask                Required NamedObjectTypeMask. The properties of the
                            named type to be updated.
        =================   ===============================================================

        :return: `NamedObjectTypeUpdateResponse`

        """
        return NamedObjectTypeUpdateResponse.model_validate(
            self._knowledge_graph.named_object_type_update(
                type_name=type_name,
                named_type_update=named_type_update.model_dump(by_alias=True),
                mask=mask.model_dump(by_alias=True),
            )
        )

    def named_object_type_delete(self, type_name: str) -> NamedObjectTypeDeleteResponse:
        """
        Deletes an entity or relationship type in the data model

        `Learn more about deleting named types in a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-type-delete.htm>`_

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        type_name           Required string. The named type to be deleted.
        ================    ===============================================================

        .. code-block:: python

            # Delete a named type in the data model
            delete_result = graph.named_object_type_delete("Person")


        :return: `NamedObjectTypeDeleteResponse`

        """
        return NamedObjectTypeDeleteResponse.model_validate(
            self._knowledge_graph.named_object_type_delete(type_name=type_name)
        )

    def graph_property_adds(
        self, type_name: str, graph_properties: Sequence[GraphProperty]
    ) -> PropertyAddsResponse:
        """
        Adds properties to a named type in the data model

        `Learn more about adding properties in a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-type-fields-add.htm>`_

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        type_name           Required string. The entity or relationship type to which the
                            properties will be added.
        ----------------    ---------------------------------------------------------------
        graph_properties    Required Sequence of GraphProperty. The Sequence of properties to add
                            to the named type.
        ================    ===============================================================

        :return: `PropertyAddsResponse`

        """
        raw_graph_properties: list[dict[str, Any]] = [
            graph_property.model_dump(by_alias=True)
            for graph_property in graph_properties
        ]
        return PropertyAddsResponse.model_validate(
            self._knowledge_graph.graph_property_adds(
                type_name=type_name,
                graph_properties=raw_graph_properties,
            )
        )

    def graph_property_update(
        self,
        type_name: str,
        property_name: str,
        graph_property: GraphProperty,
        mask: GraphPropertyMask,
    ) -> PropertyUpdateResponse:
        """
        Updates a property for a named type in the data model

        `Learn more about updating properties in a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-type-fields-update.htm>`_

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        type_name           Required string. The entity or relationship type containing
                            the property to be updated.
        ----------------    ---------------------------------------------------------------
        property_name       Required string. The property to be updated.
        ----------------    ---------------------------------------------------------------
        graph_property      Required GraphProperty. The graph property to be updated.
        ----------------    ---------------------------------------------------------------
        mask                Required GraphPropertyMask. The properties of the
                            field to be updated.
        ================    ===============================================================

        :return: `PropertyUpdateResponse`

        """
        return PropertyUpdateResponse.model_validate(
            self._knowledge_graph.graph_property_update(
                type_name=type_name,
                property_name=property_name,
                graph_property=graph_property.model_dump(by_alias=True),
                mask=mask.model_dump(by_alias=True),
            )
        )

    def graph_property_delete(
        self, type_name: str, property_name: str
    ) -> PropertyDeleteResponse:
        """
        Delete a property for a named type in the data model

        `Learn more about deleting properties in a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-type-fields-delete.htm>`_

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        type_name           Required string. The entity or relationship type containing
                            the property to be deleted.
        ----------------    ---------------------------------------------------------------
        property_name       Required string. The property to be deleted.
        ================    ===============================================================

        .. code-block:: python

            # Delete a named type's property in the data model
            delete_result = graph.graph_property_delete("Person", "Address")


        :return: `PropertyDeleteResponse`

        """
        return PropertyDeleteResponse.model_validate(
            self._knowledge_graph.graph_property_delete(
                type_name=type_name,
                property_name=property_name,
            )
        )

    def graph_property_index_adds(
        self, type_name: str, field_indexes: Sequence[FieldIndex]
    ) -> IndexAddsResponse:
        """
        Adds indexes to a field or multiple fields associated with a named type in the data model.

        `Learn more about adding graph property indexes in a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-type-indexes-add.htm>`_

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        type_name           Required string. The entity or relationship type to add the
                            indexes to.
        ----------------    ---------------------------------------------------------------
        field_indexes       Required Sequence of FieldIndex. The indexes to add for the type.
        ================    ===============================================================

        :return: `IndexAddsResponse`

        """
        raw_field_indexes: list[dict[str, Any]] = [
            field_index.model_dump(by_alias=True) for field_index in field_indexes
        ]
        return IndexAddsResponse.model_validate(
            self._knowledge_graph.graph_property_index_adds(
                type_name=type_name,
                field_indexes=raw_field_indexes,
            )
        )

    def graph_property_index_deletes(
        self, type_name: str, field_indexes: Sequence[str]
    ) -> IndexDeletesResponse:
        """
        Deletes indexes from fields associated with a named type in the data model.

        `Learn more about deleting graph property indexes from a knowledge graph <https://developers.arcgis.com/rest/services-reference/enterprise/kgs-datamodel-edit-namedtypes-type-indexes-delete.htm>`_

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        type_name           Required string. The entity or relationship type to delete the
                            field indexes from.
        ----------------    ---------------------------------------------------------------
        field_indexes       Required Sequence of strings. The field indexes to delete from the
                            type.
        ================    ===============================================================

        .. code-block:: python

            # Delete field indexes from a Knowledge Graph type
            delete_result = graph.graph_property_index_deletes("Project", ["title"])


        :return: `IndexDeletesResponse`

        """
        return IndexDeletesResponse.model_validate(
            self._knowledge_graph.graph_property_index_deletes(
                type_name=type_name,
                field_indexes=[index for index in field_indexes],
            )
        )

    def constraint_rule_adds(
        self, rules: Sequence[ConstraintRule]
    ) -> ConstraintRuleAddsResponse:
        """
        Adds constraint rules for entities & relationships to the data model.

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        rules               Required Sequence of ConstraintRule. Defines the
                            constraint rules to be added.
        ================    ===============================================================

        :return: `ConstraintRuleAddsResponse`

        """
        raw_rules: list[dict[str, Any]] = [
            rule.model_dump(by_alias=True) for rule in rules
        ]
        return ConstraintRuleAddsResponse.model_validate(
            self._knowledge_graph.constraint_rule_adds(rules=raw_rules)
        )

    def constraint_rule_updates(
        self, rules: Sequence[ConstraintRuleUpdate]
    ) -> ConstraintRuleUpdatesResponse:
        """
        Update constraint rules for entities & relationships in the data model.

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        rules               Required Sequence of ConstraintRuleUpdate. Defines the
                            constraint rules to be updated.
        ================    ===============================================================

        :return: `ConstraintRuleUpdatesResponse`

        """
        raw_rules: list[dict[str, Any]] = [
            rule.model_dump(by_alias=True) for rule in rules
        ]
        return ConstraintRuleUpdatesResponse.model_validate(
            self._knowledge_graph.constraint_rule_updates(rules=raw_rules)
        )

    def constraint_rule_deletes(
        self, rule_names: Sequence[str]
    ) -> ConstraintRuleDeletesResponse:
        """
        Deletes existing constraint rules for entities & relationships from the data model.

        ================    ===============================================================
        **Parameter**        **Description**
        ----------------    ---------------------------------------------------------------
        rule_names          Required Sequence of strings. The names of the constraint rules to
                            be deleted, as defined in a rule's 'name' attribute.
        ================    ===============================================================

        .. code-block:: python

            # Delete a constraint rule from the Knowledge Graph's data model.
            graph.constraint_rule_deletes(["constraint_rule_1"])


        :return: `ConstraintRuleDeletesResponse`

        """
        return ConstraintRuleDeletesResponse.model_validate(
            self._knowledge_graph.constraint_rule_deletes(
                rule_names=[rule_name for rule_name in rule_names]
            )
        )
