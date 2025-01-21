from typing import Any, Optional, Union
from requests import Response
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from uuid import UUID

import unittest
import gzip

from google.protobuf.internal.decoder import _DecodeVarint32  # type: ignore

from test_helpers import TestConstants, TestHelpers
from esriPBuffer import EsriTypes_pb2
from esriPBuffer.EsriExtendedTypes import EsriExtendedTypes_pb2
from esriPBuffer.graph import (
    AddConstraintRulesRequest_pb2,
    AddConstraintRulesResponse_pb2,
    AddFieldsRequest_pb2,
    AddFieldsResponse_pb2,
    AddIndexesRequest_pb2,
    AddIndexesResponse_pb2,
    AddNamedTypesRequest_pb2,
    AddNamedTypesResponse_pb2,
    ApplyEditsRequest_pb2,
    ApplyEditsResponse_pb2,
    DataModelTypes_pb2,
    DeleteConstraintRulesRequest_pb2,
    DeleteConstraintRulesResponse_pb2,
    DeleteFieldRequest_pb2,
    DeleteFieldResponse_pb2,
    DeleteIndexesRequest_pb2,
    DeleteIndexesResponse_pb2,
    DeleteNamedTypeResponse_pb2,
    EsriGraphTypes_pb2,
    QueryDataModelResponse_pb2,
    QueryRequest_pb2,
    QueryTypes_pb2,
    SearchQueryRequest_pb2,
    SyncDataModelResponse_pb2,
    UpdateConstraintRulesRequest_pb2,
    UpdateConstraintRulesResponse_pb2,
    UpdateFieldRequest_pb2,
    UpdateFieldResponse_pb2,
    UpdateNamedTypeRequest_pb2,
    UpdateNamedTypeResponse_pb2,
    UpdateSearchIndexRequest_pb2,
    UpdateSearchIndexResponse_pb2,
)

from arcgis.gis import Item
from arcgis.geometry import Geometry
from arcgis.graph import (
    EntityType,
    RelationshipType,
    GraphProperty,
    NamedObjectTypeMask,
    GraphDataModel,
    GraphObject,
    Entity,
    Relationship,
    EntityDelete,
    RelationshipDelete,
    Transform,
    SearchIndexProperties,
    UpdateSearchIndexResponse,
    SyncDataModelResponse,
    NamedObjectTypeAddsResponse,
    NamedObjectTypeUpdateResponse,
    NamedObjectTypeDeleteResponse,
    ApplyEditsResponse,
    PropertyAddsResponse,
    PropertyUpdateResponse,
    PropertyDeleteResponse,
    GraphPropertyMask,
    IndexAddsResponse,
    IndexDeletesResponse,
    FieldIndex,
    ConstraintRuleAddsResponse,
    ConstraintRuleUpdatesResponse,
    ConstraintRuleDeletesResponse,
    RelationshipExclusionRule,
    SetOfNamedTypes,
    RelationshipExclusionRuleUpdate,
    ConstraintRuleMask,
    ConstraintRule,
    UpdateSetOfNamedTypes,
    KnowledgeGraph,
)


class TestGraph(unittest.TestCase):
    def test_fromitem_success(self):
        item: Item = Item(
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={},
            ),
            itemid="123",
            itemdict={
                "type": "Knowledge Graph",
                "url": TestConstants.FAKE_SERVICE,
            },
        )
        graph: KnowledgeGraph = KnowledgeGraph.fromitem(item=item)
        self.assertEqual(TestConstants.FAKE_SERVICE, graph._url)

    def test_update_search_index_success(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = UpdateSearchIndexRequest_pb2.GraphUpdateSearchIndexRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertTrue("Person" in pbf_request.add_search_properties)
            self.assertEqual(
                1, len(pbf_request.add_search_properties["Person"].property_names)
            )
            self.assertEqual(
                "name", pbf_request.add_search_properties["Person"].property_names[0]
            )
            self.assertTrue("Vehicle" in pbf_request.delete_search_properties)
            self.assertEqual(
                1, len(pbf_request.delete_search_properties["Vehicle"].property_names)
            )
            self.assertEqual(
                "model",
                pbf_request.delete_search_properties["Vehicle"].property_names[0],
            )
            pbf_response = UpdateSearchIndexResponse_pb2.GraphUpdateSearchIndexResponse()  # type: ignore
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/searchIndex/update": mock_service_func,
                },
            ),
        )
        response: Union[dict, UpdateSearchIndexResponse] = graph.update_search_index(
            adds={
                "Person": SearchIndexProperties(property_names=["name"]),
            },
            deletes={
                "Vehicle": SearchIndexProperties(property_names=["model"]),
            },
            as_dict=False,
        )
        self.assertIsInstance(response, UpdateSearchIndexResponse)
        if not isinstance(response, UpdateSearchIndexResponse):
            self.fail(
                msg="Expected response to be an instance of UpdateSearchIndexResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" not in results)

    def test_update_search_index_error(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = UpdateSearchIndexRequest_pb2.GraphUpdateSearchIndexRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertTrue("Person" in pbf_request.add_search_properties)
            self.assertEqual(
                1, len(pbf_request.add_search_properties["Person"].property_names)
            )
            self.assertEqual(
                "name", pbf_request.add_search_properties["Person"].property_names[0]
            )
            self.assertTrue("Vehicle" in pbf_request.delete_search_properties)
            self.assertEqual(
                1, len(pbf_request.delete_search_properties["Vehicle"].property_names)
            )
            self.assertEqual(
                "model",
                pbf_request.delete_search_properties["Vehicle"].property_names[0],
            )
            pbf_response = UpdateSearchIndexResponse_pb2.GraphUpdateSearchIndexResponse()  # type: ignore
            pbf_response.error.error_message = "something bad happened"
            pbf_response.error.error_code = 123
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/searchIndex/update": mock_service_func,
                },
            ),
        )
        response: Union[dict, UpdateSearchIndexResponse] = graph.update_search_index(
            adds={
                "Person": SearchIndexProperties(property_names=["name"]),
            },
            deletes={
                "Vehicle": SearchIndexProperties(property_names=["model"]),
            },
            as_dict=False,
        )
        if not isinstance(response, UpdateSearchIndexResponse):
            self.fail(
                msg="Expected response to be an instance of UpdateSearchIndexResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error = results["error"]
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])

    def test_search(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = SearchQueryRequest_pb2.GraphSearchRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual("abc", pbf_request.search_query)
            self.assertIsNone(pbf_request.identifier_array.WhichOneof("array_type"))
            self.assertEqual(0, len(pbf_request.named_type_filter))
            self.assertEqual(EsriGraphTypes_pb2.esriNamedTypeCategory.esriTypeBothEntityRelationship, pbf_request.type_category_filter)  # type: ignore
            self.assertEqual(EsriTypes_pb2.EsriTypes.GeometryType.esriGeometryTypePoint, pbf_request.spatial_filter.geometryType)  # type: ignore
            self.assertIsNone(
                pbf_request.spatial_filter.WhichOneof("compressed_geometry")
            )
            self.assertEqual(0.0, pbf_request.input_transform.scale.xScale)
            self.assertEqual(0.0, pbf_request.input_transform.scale.yScale)
            self.assertEqual(0.0, pbf_request.input_transform.scale.zScale)
            self.assertEqual(0.0, pbf_request.input_transform.scale.mScale)
            self.assertEqual(0.0, pbf_request.input_transform.translate.xTranslate)
            self.assertEqual(0.0, pbf_request.input_transform.translate.yTranslate)
            self.assertEqual(0.0, pbf_request.input_transform.translate.zTranslate)
            self.assertEqual(0.0, pbf_request.input_transform.translate.mTranslate)
            self.assertEqual(0, pbf_request.input_spat_ref.wkid)
            self.assertEqual(0, pbf_request.input_spat_ref.lastestWkid)
            self.assertEqual(0, pbf_request.input_spat_ref.vcsWkid)
            self.assertEqual(0, pbf_request.input_spat_ref.latestVcsWkid)
            self.assertEqual("", pbf_request.input_spat_ref.wkt)
            self.assertEqual(0, pbf_request.input_spat_ref.sdesrid)
            self.assertEqual("", pbf_request.input_spat_ref.wkt2)
            self.assertEqual(EsriTypes_pb2.EsriTypes.esriSpatialRel.esriSpatialRelIntersects, pbf_request.spatial_relation)  # type: ignore
            self.assertEqual(EsriTypes_pb2.EsriTypes.esriFeatureEncoding.esriDefault, pbf_request.feature_encoding)  # type: ignore
            self.assertEqual(0, pbf_request.out_spat_ref.wkid)
            self.assertEqual(0, pbf_request.out_spat_ref.lastestWkid)
            self.assertEqual(0, pbf_request.out_spat_ref.vcsWkid)
            self.assertEqual(0, pbf_request.out_spat_ref.latestVcsWkid)
            self.assertEqual("", pbf_request.out_spat_ref.wkt)
            self.assertEqual(0, pbf_request.out_spat_ref.sdesrid)
            self.assertEqual("", pbf_request.out_spat_ref.wkt2)
            self.assertEqual(0, pbf_request.datum_transform.wkid)
            self.assertEqual("", pbf_request.datum_transform.wkt)
            self.assertEqual("", pbf_request.datum_transform.transformDirection)
            self.assertEqual("", pbf_request.datum_transform.transformJson)
            self.assertEqual(0, pbf_request.datum_transform.fromSR.wkid)
            self.assertEqual(0, pbf_request.datum_transform.fromSR.lastestWkid)
            self.assertEqual(0, pbf_request.datum_transform.fromSR.vcsWkid)
            self.assertEqual(0, pbf_request.datum_transform.fromSR.latestVcsWkid)
            self.assertEqual("", pbf_request.datum_transform.fromSR.wkt)
            self.assertEqual(0, pbf_request.datum_transform.fromSR.sdesrid)
            self.assertEqual("", pbf_request.datum_transform.fromSR.wkt2)
            self.assertEqual(0, pbf_request.datum_transform.toSR.wkid)
            self.assertEqual(0, pbf_request.datum_transform.toSR.lastestWkid)
            self.assertEqual(0, pbf_request.datum_transform.toSR.vcsWkid)
            self.assertEqual(0, pbf_request.datum_transform.toSR.latestVcsWkid)
            self.assertEqual("", pbf_request.datum_transform.toSR.wkt)
            self.assertEqual(0, pbf_request.datum_transform.toSR.sdesrid)
            self.assertEqual("", pbf_request.datum_transform.toSR.wkt2)
            self.assertFalse(pbf_request.apply_vcs_projection)
            self.assertEqual(0.0, pbf_request.quantization_params.extent.XMin)
            self.assertEqual(0.0, pbf_request.quantization_params.extent.YMin)
            self.assertEqual(0.0, pbf_request.quantization_params.extent.XMax)
            self.assertEqual(0.0, pbf_request.quantization_params.extent.YMax)
            self.assertEqual(
                0, pbf_request.quantization_params.extent.SpatialReference.wkid
            )
            self.assertEqual(
                0, pbf_request.quantization_params.extent.SpatialReference.lastestWkid
            )
            self.assertEqual(
                0, pbf_request.quantization_params.extent.SpatialReference.vcsWkid
            )
            self.assertEqual(
                0, pbf_request.quantization_params.extent.SpatialReference.latestVcsWkid
            )
            self.assertEqual(
                "", pbf_request.quantization_params.extent.SpatialReference.wkt
            )
            self.assertEqual(
                0, pbf_request.quantization_params.extent.SpatialReference.sdesrid
            )
            self.assertEqual(
                "", pbf_request.quantization_params.extent.SpatialReference.wkt2
            )
            self.assertEqual(0.0, pbf_request.quantization_params.extent.ZMin)
            self.assertEqual(0.0, pbf_request.quantization_params.extent.MMin)
            self.assertEqual(0.0, pbf_request.quantization_params.extent.ZMax)
            self.assertEqual(0.0, pbf_request.quantization_params.extent.MMax)
            self.assertEqual(EsriGraphTypes_pb2.QuantizationParameters.QuantizeMode.view, pbf_request.quantization_params.mode)  # type: ignore
            self.assertEqual(0.0, pbf_request.quantization_params.tolerance)
            self.assertEqual(0, pbf_request.start_index)
            self.assertEqual(1000, pbf_request.max_num_results)
            self.assertFalse(pbf_request.return_search_context)
            self.assertEqual("", pbf_request.out_time_zone.tz_id)
            self.assertEqual(QueryTypes_pb2.TimestampOffsetFormat.TS_FORMAT_EPOCH_MS, pbf_request.out_timestamp_offset_format)  # type: ignore
            self.assertEqual(QueryTypes_pb2.DateOnlyFormat.DATE_FORMAT_DATE_ONLY_EPOCH_DAY, pbf_request.out_date_only_format)  # type: ignore
            self.assertEqual(QueryTypes_pb2.TimeOnlyFormat.TIME_FORMAT_MILLISECONDS_OF_DAY, pbf_request.out_time_only_format)  # type: ignore
            self.assertEqual(QueryTypes_pb2.DurationFormat.DURATION_FORMAT_DURATION_COMPONENTS, pbf_request.out_duration_format)  # type: ignore
            return TestHelpers.mock_query_response()

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={
                    TestConstants.FAKE_SERVICE: TestHelpers.mock_properties,
                    f"{TestConstants.FAKE_SERVICE}/dataModel/queryDataModel": TestHelpers.mock_query_data_model,
                },
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/graph/search": mock_service_func,
                },
            ),
        )
        for result in graph.search(search="abc", category="both", as_dict=False):
            TestHelpers.validate_query_response(test_case=self, result=result)

    def test_query(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = QueryRequest_pb2.GraphQueryRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual("match (n) return n", pbf_request.open_cypher_query)
            self.assertEqual(
                "abc123",
                pbf_request.parameters["string_value"].primitive_value.string_value,
            )
            self.assertEqual(
                1.2300000190734863,
                pbf_request.parameters["double_value"].primitive_value.float_value,
            )
            self.assertEqual(
                123, pbf_request.parameters["sint64_value"].primitive_value.sint64_value
            )
            self.assertTrue(
                pbf_request.parameters["bool_value"].primitive_value.bool_value
            )
            self.assertEqual(
                UUID("12345678-1234-5678-1234-567812345678").bytes,
                pbf_request.parameters["uuid_value"].primitive_value.uuid_value,
            )
            self.assertEqual(
                b"\x01\xff\xa5Z",
                pbf_request.parameters["blob_value"].primitive_value.blob_value,
            )
            self.assertEqual(
                1,
                pbf_request.parameters[
                    "geometry_value"
                ].primitive_value.geometry_value.geometry.lengths[0],
            )
            self.assertEqual(
                3,
                pbf_request.parameters[
                    "geometry_value"
                ].primitive_value.geometry_value.geometry.coords[0],
            )
            self.assertEqual(
                2,
                pbf_request.parameters[
                    "geometry_value"
                ].primitive_value.geometry_value.geometry.coords[1],
            )
            self.assertEqual(
                False,
                pbf_request.parameters["null_value"].primitive_value.null_tag,
            )
            self.assertEqual(
                -154742400000,
                pbf_request.parameters["datetime_value"].primitive_value.datetime_value,
            )
            self.assertEqual(
                -154742400000,
                pbf_request.parameters[
                    "timestamp_offset_value"
                ].primitive_value.timestamp_offset_value.date_time_offset.local_epoch_ms,
            )
            self.assertEqual(
                68400,
                pbf_request.parameters[
                    "timestamp_offset_value"
                ].primitive_value.timestamp_offset_value.date_time_offset.utc_offset,
            )
            self.assertEqual(
                -1791,
                pbf_request.parameters[
                    "date_only_value"
                ].primitive_value.date_only_value.epoch_days,
            )
            self.assertEqual(
                62340000,
                pbf_request.parameters[
                    "time_only_value"
                ].primitive_value.time_only_value.milliseconds_of_day,
            )
            self.assertEqual(
                2,
                pbf_request.parameters[
                    "duration_value"
                ].primitive_value.duration_value.duration_components.days,
            )
            self.assertEqual(
                "hello",
                pbf_request.parameters["any_value_array"]
                .array_value.any_value_array.values[0]
                .primitive_value.string_value,
            )
            self.assertEqual(
                123,
                pbf_request.parameters["any_value_array"]
                .array_value.any_value_array.values[1]
                .primitive_value.sint64_value,
            )
            self.assertEqual(
                1.23,
                pbf_request.parameters["float_array"].array_value.double_array.value[0],
            )
            self.assertEqual(
                4.56,
                pbf_request.parameters["float_array"].array_value.double_array.value[1],
            )
            self.assertEqual(
                UUID("12345678-1234-5678-1234-567812345678").bytes * 2,
                pbf_request.parameters["uuid_array"].array_value.uuid_array,
            )
            self.assertEqual(
                "geometry_value",
                pbf_request.parameters["object_value"].object_value.properties[0].key,
            )
            self.assertEqual(
                1,
                pbf_request.parameters["object_value"]
                .object_value.properties[0]
                .value.primitive_value.geometry_value.geometry.lengths[0],
            )
            self.assertEqual(
                3,
                pbf_request.parameters["object_value"]
                .object_value.properties[0]
                .value.primitive_value.geometry_value.geometry.coords[0],
            )
            self.assertEqual(
                2,
                pbf_request.parameters["object_value"]
                .object_value.properties[0]
                .value.primitive_value.geometry_value.geometry.coords[1],
            )
            self.assertEqual(
                "object_value",
                pbf_request.parameters["object_value"].object_value.properties[1].key,
            )
            self.assertEqual(
                "name",
                pbf_request.parameters["object_value"]
                .object_value.properties[1]
                .value.object_value.properties[0]
                .key,
            )
            self.assertEqual(
                "Cameron",
                pbf_request.parameters["object_value"]
                .object_value.properties[1]
                .value.object_value.properties[0]
                .value.primitive_value.string_value,
            )
            self.assertEqual(1.1, pbf_request.input_transform.scale.xScale)
            self.assertEqual(1.1, pbf_request.input_transform.scale.yScale)
            self.assertEqual(4.4, pbf_request.input_transform.scale.zScale)
            self.assertEqual(6.6, pbf_request.input_transform.scale.mScale)
            self.assertEqual(2.2, pbf_request.input_transform.translate.xTranslate)
            self.assertEqual(3.3, pbf_request.input_transform.translate.yTranslate)
            self.assertEqual(5.5, pbf_request.input_transform.translate.zTranslate)
            self.assertEqual(7.7, pbf_request.input_transform.translate.mTranslate)
            self.assertEqual(QueryRequest_pb2.ProvenanceBehavior.INCLUDE, pbf_request.provenance_behavior)  # type: ignore
            return TestHelpers.mock_query_response()

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/graph/query": mock_service_func,
                },
            ),
        )
        for result in graph.query_streaming(
            query="match (n) return n",
            input_transform=Transform(
                xy_resolution=1.1,
                x_false_origin=2.2,
                y_false_origin=3.3,
                z_resolution=4.4,
                z_false_origin=5.5,
                m_resolution=6.6,
                m_false_origin=7.7,
            ),
            bind_param={
                "string_value": "abc123",
                "double_value": 1.23,
                "sint64_value": 123,
                "bool_value": True,
                "uuid_value": UUID("12345678-1234-5678-1234-567812345678"),
                "blob_value": b"\x01\xff\xa5Z",
                "geometry_value": Geometry({"x": 5, "y": 6}),
                "null_value": None,
                "datetime_value": datetime(year=1965, month=2, day=5),
                "timestamp_offset_value": datetime(
                    year=1965, month=2, day=5, tzinfo=ZoneInfo("US/Eastern")
                ),
                "date_only_value": date(year=1965, month=2, day=5),
                "time_only_value": time(hour=17, minute=19),
                "duration_value": timedelta(days=2),
                "any_value_array": ["hello", 123],
                "float_array": [1.23, 4.56],
                "uuid_array": [
                    UUID("12345678-1234-5678-1234-567812345678"),
                    UUID("12345678-1234-5678-1234-567812345678"),
                ],
                "object_value": GraphObject(
                    properties={
                        "geometry_value": Geometry({"x": 5, "y": 6}),
                        "object_value": GraphObject(
                            properties={
                                "name": "Cameron",
                            }
                        ),
                    },
                ),
            },
            include_provenance=True,
            as_dict=False,
        ):
            TestHelpers.validate_query_response(test_case=self, result=result)

    def test_query_data_model_success(self):
        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/queryDataModel": TestHelpers.mock_query_data_model,
                },
                post_requests={},
            ),
        )
        data_model: Union[dict, GraphDataModel] = graph.query_data_model(as_dict=False)
        if not isinstance(data_model, GraphDataModel):
            self.fail(msg="Expected response to be an instance of GraphDataModel.")
        results: dict[str, Any] = data_model.model_dump(by_alias=True)
        self.assertTrue("data_model_timestamp" in results)
        self.assertEqual(123, results["data_model_timestamp"])
        self.assertTrue("spatial_reference" in results)
        spatial_reference: dict[str, Any] = results["spatial_reference"]
        self.assertTrue("wkid" in spatial_reference)
        self.assertEqual(4326, spatial_reference["wkid"])
        self.assertTrue("entity_types" in results)
        entity_types: dict[str, Any] = results["entity_types"]
        self.assertTrue("Person" in entity_types)
        entity_type: dict[str, Any] = entity_types["Person"]
        self.assertTrue("name" in entity_type)
        self.assertEqual("Person", entity_type["name"])
        self.assertTrue("alias" in entity_type)
        self.assertEqual("", entity_type["alias"])
        self.assertTrue("role" in entity_type)
        self.assertEqual("esriGraphNamedObjectRegular", entity_type["role"])
        self.assertTrue("strict" in entity_type)
        self.assertFalse(entity_type["strict"])
        self.assertTrue("properties" in entity_type)
        properties: dict[str, Any] = entity_type["properties"]
        self.assertTrue("name" in properties)
        property: dict[str, Any] = properties["name"]
        self.assertTrue("name" in property)
        self.assertEqual("name", property["name"])
        self.assertTrue("alias" in property)
        self.assertEqual("", property["alias"])
        self.assertTrue("fieldType" in property)
        self.assertEqual("esriFieldTypeString", property["fieldType"])
        self.assertTrue("hasZ" in property)
        self.assertFalse(property["hasZ"])
        self.assertTrue("hasM" in property)
        self.assertFalse(property["hasM"])
        self.assertTrue("nullable" in property)
        self.assertTrue(property["nullable"])
        self.assertTrue("editable" in property)
        self.assertTrue(property["editable"])
        self.assertTrue("visible" in property)
        self.assertTrue(property["visible"])
        self.assertTrue("required" in property)
        self.assertFalse(property["required"])
        self.assertTrue("isSystemMaintained" in property)
        self.assertFalse(property["isSystemMaintained"])
        self.assertTrue("role" in property)
        self.assertEqual("esriGraphPropertyRegular", property["role"])
        self.assertTrue("domain" in property)
        self.assertEqual("", property["domain"])
        self.assertTrue("name" in properties)
        property: dict[str, Any] = properties["creator"]
        self.assertTrue("name" in property)
        self.assertEqual("creator", property["name"])
        self.assertTrue("alias" in property)
        self.assertEqual("", property["alias"])
        self.assertTrue("fieldType" in property)
        self.assertEqual("esriFieldTypeString", property["fieldType"])
        self.assertTrue("hasZ" in property)
        self.assertFalse(property["hasZ"])
        self.assertTrue("hasM" in property)
        self.assertFalse(property["hasM"])
        self.assertTrue("nullable" in property)
        self.assertTrue(property["nullable"])
        self.assertTrue("editable" in property)
        self.assertTrue(property["editable"])
        self.assertTrue("visible" in property)
        self.assertTrue(property["visible"])
        self.assertTrue("required" in property)
        self.assertFalse(property["required"])
        self.assertTrue("isSystemMaintained" in property)
        self.assertFalse(property["isSystemMaintained"])
        self.assertTrue("role" in property)
        self.assertEqual("esriGraphPropertyUNSPECIFIED", property["role"])
        self.assertTrue("domain" in property)
        self.assertEqual("", property["domain"])
        self.assertTrue("field_indexes" in entity_type)
        field_indexes: dict[str, Any] = entity_type["field_indexes"]
        self.assertTrue("idx" in field_indexes)
        field_index: dict[str, Any] = field_indexes["idx"]
        self.assertTrue("name" in field_index)
        self.assertEqual("idx", field_index["name"])
        self.assertTrue("fields" in field_index)
        fields: list[str] = field_index["fields"]
        self.assertEqual(2, len(fields))
        self.assertEqual("a", fields[0])
        self.assertEqual("b", fields[1])
        self.assertTrue("isAscending" in field_index)
        self.assertFalse(field_index["isAscending"])
        self.assertTrue("isUnique" in field_index)
        self.assertFalse(field_index["isUnique"])
        self.assertTrue("relationship_types" in results)
        relationship_types: dict[str, Any] = results["relationship_types"]
        self.assertTrue("Owns" in relationship_types)
        relationship_type: dict[str, Any] = relationship_types["Owns"]
        self.assertTrue("name" in relationship_type)
        self.assertEqual("Owns", relationship_type["name"])
        self.assertTrue("alias" in relationship_type)
        self.assertEqual("", relationship_type["alias"])
        self.assertTrue("role" in relationship_type)
        self.assertEqual("esriGraphNamedObjectRegular", relationship_type["role"])
        self.assertTrue("strict" in relationship_type)
        self.assertFalse(relationship_type["strict"])
        self.assertTrue("properties" in relationship_type)
        self.assertTrue("field_indexes" in relationship_type)
        self.assertTrue("end_points" in relationship_type)
        end_points: list[dict[str, Any]] = relationship_type["end_points"]
        self.assertEqual(1, len(end_points))
        end_point: dict[str, Any] = end_points[0]
        self.assertTrue("origin_entity_type" in end_point)
        self.assertEqual("Person", end_point["origin_entity_type"])
        self.assertTrue("dest_entity_type" in end_point)
        self.assertEqual("Vehicle", end_point["dest_entity_type"])
        self.assertTrue("meta_entity_types" in results)
        self.assertTrue("strict" in results)
        self.assertFalse(results["strict"])
        self.assertTrue("objectid_property" in results)
        self.assertEqual("", results["objectid_property"])
        self.assertTrue("globalid_property" in results)
        self.assertEqual("", results["globalid_property"])
        self.assertTrue("search_indexes" in results)
        search_indexes: dict[str, Any] = results["search_indexes"]
        self.assertTrue("searchIdx" in search_indexes)
        search_index: dict[str, Any] = search_indexes["searchIdx"]
        self.assertTrue("name" in search_index)
        self.assertEqual("searchIdx", search_index["name"])
        self.assertTrue("supported_category" in search_index)
        self.assertEqual("UNSPECIFIED", search_index["supported_category"])
        self.assertTrue("analyzers" in search_index)
        analyzers: list[dict[str, Any]] = search_index["analyzers"]
        self.assertEqual(1, len(analyzers))
        analyzer: dict[str, Any] = analyzers[0]
        self.assertTrue("name" in analyzer)
        self.assertEqual("en", analyzer["name"])
        self.assertTrue("search_properties" in search_index)
        search_properties: dict[str, Any] = search_index["search_properties"]
        self.assertTrue("Person" in search_properties)
        person_search_properties: dict[str, Any] = search_properties["Person"]
        self.assertTrue("property_names" in person_search_properties)
        person_property_names: list[str] = person_search_properties["property_names"]
        self.assertEqual(1, len(person_property_names))
        self.assertEqual("name", person_property_names[0])
        self.assertTrue("identifier_info" in results)
        identifier_info: dict[str, Any] = results["identifier_info"]
        self.assertTrue("identifier_mapping_info" in identifier_info)
        identifier_mapping_info: dict[str, Any] = identifier_info[
            "identifier_mapping_info"
        ]
        self.assertTrue("identifier_info_type" in identifier_mapping_info)
        self.assertEqual(
            "esriIdentifierInfoTypeUniformProperty",
            identifier_mapping_info["identifier_info_type"],
        )
        self.assertTrue("uniform_property" in identifier_mapping_info)
        uniform_property: dict[str, Any] = identifier_mapping_info["uniform_property"]
        self.assertTrue("identifier_property_name" in uniform_property)
        self.assertEqual("globalid", uniform_property["identifier_property_name"])
        self.assertTrue("identifier_generation_info" in identifier_info)
        identifier_generation_info: dict[str, Any] = identifier_info[
            "identifier_generation_info"
        ]
        self.assertTrue("uuid_method_hint" in identifier_generation_info)
        self.assertEqual("esriUUIDESRI", identifier_generation_info["uuid_method_hint"])
        self.assertTrue("arcgis_managed" in results)
        self.assertFalse(results["arcgis_managed"])
        self.assertTrue("provenance_source_type_values" in results)
        provenance_source_type_values: dict[str, Any] = results[
            "provenance_source_type_values"
        ]
        self.assertTrue("value_behavior_array" in provenance_source_type_values)
        value_behavior_array: list[dict[str, Any]] = provenance_source_type_values[
            "value_behavior_array"
        ]
        self.assertEqual(1, len(value_behavior_array))
        value_behavior: dict[str, Any] = value_behavior_array[0]
        self.assertTrue("behavior" in value_behavior)
        self.assertEqual("String", value_behavior["behavior"])
        self.assertTrue("value" in value_behavior)
        self.assertEqual("abc123", value_behavior["value"])
        self.assertTrue("constraint_rules" in results)
        constraint_rules: dict[str, Any] = results["constraint_rules"]
        self.assertTrue("rule" in constraint_rules)
        constraint_rule: dict[str, Any] = constraint_rules["rule"]
        self.assertTrue("name" in constraint_rule)
        self.assertEqual("rule", constraint_rule["name"])
        self.assertTrue("alias" in constraint_rule)
        self.assertEqual("", constraint_rule["alias"])
        self.assertTrue("disabled" in constraint_rule)
        self.assertFalse(constraint_rule["disabled"])
        self.assertTrue("role" in constraint_rule)
        self.assertEqual(
            "esriGraphConstraintRuleRoleUNSPECIFIED", constraint_rule["role"]
        )
        self.assertTrue("type" in constraint_rule)
        self.assertEqual(
            "esriGraphRelationshipExclusionRuleType", constraint_rule["type"]
        )
        self.assertTrue("relationship_exclusion_rule" in constraint_rule)
        relationship_exclusion_rule: dict[str, Any] = constraint_rule[
            "relationship_exclusion_rule"
        ]
        self.assertTrue("origin_entity_types" in relationship_exclusion_rule)
        origin_entity_types: dict[str, Any] = relationship_exclusion_rule[
            "origin_entity_types"
        ]
        self.assertTrue("set" in origin_entity_types)
        origin_entity_types_set: list[str] = origin_entity_types["set"]
        self.assertEqual(1, len(origin_entity_types_set))
        self.assertEqual("Person", origin_entity_types_set[0])
        self.assertTrue("relationship_types" in relationship_exclusion_rule)
        relationship_types: dict[str, Any] = relationship_exclusion_rule[
            "relationship_types"
        ]
        self.assertTrue("set_complement" in relationship_types)
        relationship_types_set_complement: list[str] = relationship_types[
            "set_complement"
        ]
        self.assertEqual(0, len(relationship_types_set_complement))
        self.assertTrue("destination_entity_types" in relationship_exclusion_rule)
        destination_entity_types: dict[str, Any] = relationship_exclusion_rule[
            "destination_entity_types"
        ]
        self.assertTrue("set_complement" in destination_entity_types)
        destination_entity_types_set_complement: list[str] = destination_entity_types[
            "set_complement"
        ]
        self.assertEqual(0, len(destination_entity_types_set_complement))
        self.assertTrue("notRelRule" in constraint_rules)
        constraint_rule: dict[str, Any] = constraint_rules["notRelRule"]
        self.assertTrue("name" in constraint_rule)
        self.assertEqual("notRelRule", constraint_rule["name"])
        self.assertTrue("alias" in constraint_rule)
        self.assertEqual("", constraint_rule["alias"])
        self.assertTrue("disabled" in constraint_rule)
        self.assertFalse(constraint_rule["disabled"])
        self.assertTrue("role" in constraint_rule)
        self.assertEqual(
            "esriGraphConstraintRuleRoleHasDocument", constraint_rule["role"]
        )
        self.assertTrue("type" in constraint_rule)
        self.assertEqual(
            "esriGraphConstraintRuleTypeUNSPECIFIED", constraint_rule["type"]
        )

    def test_query_data_model_database_native_identifier(self):
        def mock_service_func() -> Response:
            pbf_response = QueryDataModelResponse_pb2.GraphDataModel()  # type: ignore
            pbf_response.identifier_info.mapping_info.native_identifier.SetInParent()
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/queryDataModel": mock_service_func,
                },
                post_requests={},
            ),
        )
        data_model: Union[dict, GraphDataModel] = graph.query_data_model(as_dict=False)
        if not isinstance(data_model, GraphDataModel):
            self.fail(msg="Expected response to be an instance of GraphDataModel.")
        results: dict[str, Any] = data_model.model_dump(by_alias=True)
        self.assertTrue("identifier_info" in results)
        identifier_info: dict[str, Any] = results["identifier_info"]
        self.assertTrue("identifier_mapping_info" in identifier_info)
        identifier_mapping_info: dict[str, Any] = identifier_info[
            "identifier_mapping_info"
        ]
        self.assertTrue("identifier_info_type" in identifier_mapping_info)
        self.assertEqual(
            "esriIdentifierInfoTypeDatabaseNative",
            identifier_mapping_info["identifier_info_type"],
        )
        self.assertTrue("native_identifier" in identifier_mapping_info)
        self.assertEqual("", identifier_mapping_info["native_identifier"])
        self.assertTrue("identifier_generation_info" in identifier_info)
        identifier_generation_info: dict[str, Any] = identifier_info[
            "identifier_generation_info"
        ]
        self.assertTrue("uuid_method_hint" in identifier_generation_info)
        self.assertEqual(
            "esriMethodHintUNSPECIFIED", identifier_generation_info["uuid_method_hint"]
        )

    def test_sync_data_model_success(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNone(data)
            pbf_response = SyncDataModelResponse_pb2.SyncDataModelResponse()  # type: ignore
            pbf_result_success = pbf_response.named_type_sync_results.add()
            pbf_result_success.typeName = "SuccessType"
            pbf_result_error = pbf_response.named_type_sync_results.add()
            pbf_result_error.typeName = "ErrorType"
            pbf_result_error.error.error_code = 123
            pbf_result_error.error.error_message = "error"
            pbf_warning = pbf_result_error.warnings.add()
            pbf_warning.error_code = 456
            pbf_warning.error_message = "warning"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/syncDataModel": mock_service_func,
                },
            ),
        )
        response: Union[dict, SyncDataModelResponse] = graph.sync_data_model(
            as_dict=False
        )
        if not isinstance(response, SyncDataModelResponse):
            self.fail(
                msg="Expected response to be an instance of SyncDataModelResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertFalse("error" in results)
        self.assertFalse("warnings" in results)
        self.assertTrue("named_type_sync_results" in results)
        named_type_sync_results: list[dict[str, Any]] = results[
            "named_type_sync_results"
        ]
        self.assertEqual(2, len(named_type_sync_results))
        result_success: dict[str, Any] = named_type_sync_results[0]
        self.assertTrue("typeName" in result_success)
        self.assertEqual("SuccessType", result_success["typeName"])
        self.assertFalse("error" in result_success)
        self.assertFalse("warnings" in result_success)
        result_error: dict[str, Any] = named_type_sync_results[1]
        self.assertTrue("typeName" in result_error)
        self.assertEqual("ErrorType", result_error["typeName"])
        self.assertTrue("error" in result_error)
        error: dict[str, Any] = result_error["error"]
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("error_message" in error)
        self.assertEqual("error", error["error_message"])
        self.assertTrue("warnings" in result_error)
        warnings: list[dict[str, Any]] = result_error["warnings"]
        self.assertEqual(1, len(warnings))
        warning: dict[str, Any] = warnings[0]
        self.assertTrue("error_code" in warning)
        self.assertEqual(456, warning["error_code"])
        self.assertTrue("error_message" in warning)
        self.assertEqual("warning", warning["error_message"])

    def test_sync_data_model_error(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNone(data)
            pbf_response = SyncDataModelResponse_pb2.SyncDataModelResponse()  # type: ignore
            pbf_response.error.error_message = "something bad happened"
            pbf_response.error.error_code = 123
            pbf_warning = pbf_response.warnings.add()
            pbf_warning.error_code = 456
            pbf_warning.error_message = "warning"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/syncDataModel": mock_service_func,
                },
            ),
        )
        response: Union[dict, SyncDataModelResponse] = graph.sync_data_model(
            as_dict=False
        )
        if not isinstance(response, SyncDataModelResponse):
            self.fail(
                msg="Expected response to be an instance of SyncDataModelResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error = results["error"]
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("warnings" in results)
        warnings: list[dict[str, Any]] = results["warnings"]
        self.assertEqual(1, len(warnings))
        warning: dict[str, Any] = warnings[0]
        self.assertTrue("error_code" in warning)
        self.assertEqual(456, warning["error_code"])
        self.assertTrue("error_message" in warning)
        self.assertEqual("warning", warning["error_message"])
        self.assertFalse("named_type_sync_results" in results)

    def test_apply_edits(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            if data is None:
                self.fail()
            pbf_header = ApplyEditsRequest_pb2.GraphApplyEditsHeader()  # type: ignore
            next_pos, pos = _DecodeVarint32(data, 0)
            pbf_header.ParseFromString(data[pos : pos + next_pos])
            self.assertEqual(4326, pbf_header.spatialReference.wkid)
            self.assertEqual(0, pbf_header.spatialReference.lastestWkid)
            self.assertEqual(0, pbf_header.spatialReference.latestVcsWkid)
            self.assertEqual(0, pbf_header.spatialReference.sdesrid)
            self.assertEqual(0, pbf_header.spatialReference.vcsWkid)
            self.assertEqual("", pbf_header.spatialReference.wkt)
            self.assertEqual("", pbf_header.spatialReference.wkt2)
            self.assertTrue(pbf_header.cascade_delete)
            self.assertTrue(pbf_header.cascade_delete_provenance)
            self.assertEqual(1.1, pbf_header.input_transform.scale.xScale)
            self.assertEqual(1.1, pbf_header.input_transform.scale.yScale)
            self.assertEqual(4.4, pbf_header.input_transform.scale.zScale)
            self.assertEqual(6.6, pbf_header.input_transform.scale.mScale)
            self.assertEqual(2.2, pbf_header.input_transform.translate.xTranslate)
            self.assertEqual(3.3, pbf_header.input_transform.translate.yTranslate)
            self.assertEqual(5.5, pbf_header.input_transform.translate.zTranslate)
            self.assertEqual(7.7, pbf_header.input_transform.translate.mTranslate)
            pos += next_pos
            while pos < len(data):
                pbf_frame = ApplyEditsRequest_pb2.GraphApplyEditsFrame()  # type: ignore
                next_pos, pos = _DecodeVarint32(data, pos)
                compressed_bytes: bytes = data[pos : pos + next_pos]
                decompressed_bytes: bytes = gzip.decompress(compressed_bytes)
                pbf_frame.ParseFromString(decompressed_bytes)
                self.assertTrue("AddEntityType" in pbf_frame.adds.entities)
                pbf_entity_adds = pbf_frame.adds.entities["AddEntityType"]
                self.assertEqual(1, len(pbf_entity_adds.entity_adds))
                pbf_entity_add = pbf_entity_adds.entity_adds[0]
                self.assertEqual(
                    "abc123", pbf_entity_add.entity.id.primitive_value.string_value
                )
                self.assertEqual(1, len(pbf_entity_add.entity.properties))
                pbf_entity_add_property = pbf_entity_add.entity.properties[0]
                self.assertEqual("name", pbf_entity_add_property.key)
                self.assertEqual(
                    "AddEntity",
                    pbf_entity_add_property.value.primitive_value.string_value,
                )
                self.assertTrue("AddRelType" in pbf_frame.adds.relationships)
                pbf_rel_adds = pbf_frame.adds.relationships["AddRelType"]
                self.assertEqual(1, len(pbf_rel_adds.relationship_adds))
                pbf_rel_add = pbf_rel_adds.relationship_adds[0]
                self.assertFalse(pbf_rel_add.relationship.id.primitive_value.null_tag)
                self.assertEqual(0, len(pbf_rel_add.relationship.properties))
                self.assertEqual(
                    "abc123", pbf_rel_add.origin_id.primitive_value.string_value
                )
                self.assertEqual(
                    "def456", pbf_rel_add.dest_id.primitive_value.string_value
                )
                self.assertTrue("UpdateEntityType" in pbf_frame.updates.entities)
                pbf_entity_updates = pbf_frame.updates.entities["UpdateEntityType"]
                self.assertEqual(1, len(pbf_entity_updates.namedObjectUpdates))
                pbf_entity_update = pbf_entity_updates.namedObjectUpdates[0]
                self.assertEqual(
                    123, pbf_entity_update.update_id.primitive_value.sint64_value
                )
                self.assertEqual(1, len(pbf_entity_update.properties))
                pbf_entity_update_property = pbf_entity_update.properties[0]
                self.assertEqual("dob", pbf_entity_update_property.key)
                self.assertEqual(
                    870739200000,
                    pbf_entity_update_property.value.primitive_value.datetime_value,
                )
                self.assertTrue("UpdateRelType" in pbf_frame.updates.relationships)
                pbf_rel_updates = pbf_frame.updates.relationships["UpdateRelType"]
                self.assertEqual(0, len(pbf_rel_updates.namedObjectUpdates))
                self.assertTrue("Person" in pbf_frame.deletes.deleted_entity_ids)
                pbf_delete_entity_id_set = pbf_frame.deletes.deleted_entity_ids[
                    "Person"
                ]
                self.assertEqual(
                    1, len(pbf_delete_entity_id_set.id_array.any_value_array.values)
                )
                pbf_id_value = pbf_delete_entity_id_set.id_array.any_value_array.values[
                    0
                ]
                self.assertEqual(0.123, pbf_id_value.primitive_value.double_value)
                self.assertTrue("Owns" in pbf_frame.deletes.deleted_relationship_ids)
                pbf_delete_relationship_id_set = (
                    pbf_frame.deletes.deleted_relationship_ids["Owns"]
                )
                self.assertEqual(
                    0,
                    len(pbf_delete_relationship_id_set.id_array.any_value_array.values),
                )
                pos += next_pos
            pbf_response = ApplyEditsResponse_pb2.GraphApplyEditsResult()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "uh oh"
            pbf_response.entity_add_results["Person"].errors[0].error_code = 123
            pbf_response.entity_add_results["Person"].errors[0].error_message = "uh oh"
            pbf_response.entity_add_results[
                "Person"
            ].id_array.string_array.value.append("abc123")
            pbf_response.entity_add_results[
                "Person"
            ].id_array.string_array.value.append("def456")
            pbf_response.cascading_relationship_delete_results[
                "Owns"
            ].relationship_delete_results.id_array.string_array.value.append("ghi789")
            pbf_response.cascading_relationship_delete_results[
                "Owns"
            ].origin_entity_id_array.string_array.value.append("abc123")
            pbf_response.cascading_relationship_delete_results[
                "Owns"
            ].dest_entity_id_array.string_array.value.append("def456")
            pbf_end_point = pbf_response.rel_type_schema_changes[
                "Owns"
            ].new_end_points.add()
            pbf_end_point.origin_entity_type = "Person"
            pbf_end_point.destination_entity_type = "Vehicle"
            pbf_response.cascading_provenance_delete_results.provenance_delete_results.id_array.string_array.value.append(
                "xyz123"
            )
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/queryDataModel": TestHelpers.mock_query_data_model,
                },
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/graph/applyEdits": mock_service_func,
                },
            ),
        )
        response: Union[dict, ApplyEditsResponse] = graph.apply_edits(
            adds=[
                Entity(
                    type_name="AddEntityType",
                    id="abc123",
                    properties={
                        "name": "AddEntity",
                    },
                ),
                Relationship(
                    type_name="AddRelType",
                    properties={},
                    origin_entity_id="abc123",
                    destination_entity_id="def456",
                ),
            ],
            updates=[
                Entity(
                    type_name="UpdateEntityType",
                    id=123,
                    properties={
                        "dob": datetime(year=1997, month=8, day=5),
                    },
                ),
                Relationship(
                    type_name="UpdateRelType",
                    properties={},
                    origin_entity_id="jkl123",
                    destination_entity_id="mno456",
                ),
            ],
            deletes=[
                EntityDelete(
                    type_name="Person",
                    ids=[0.123],
                ),
                RelationshipDelete(
                    type_name="Owns",
                    ids=[],
                ),
            ],
            input_transform=Transform(
                xy_resolution=1.1,
                x_false_origin=2.2,
                y_false_origin=3.3,
                z_resolution=4.4,
                z_false_origin=5.5,
                m_resolution=6.6,
                m_false_origin=7.7,
            ),
            cascade_delete=True,
            cascade_delete_provenance=True,
            as_dict=False,
        )
        if not isinstance(response, ApplyEditsResponse):
            self.fail(msg="Expected response to be an instance of ApplyEditsResponse.")
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertEqual("uh oh", error["error_message"])
        self.assertEqual(123, error["error_code"])
        self.assertTrue("editsResult" in results)
        edits_result: dict[str, Any] = results["editsResult"]
        self.assertTrue("Person" in edits_result)
        person_edits_result: dict[str, Any] = edits_result["Person"]
        self.assertTrue("addResults" in person_edits_result)
        person_add_results: list[dict[str, Any]] = person_edits_result["addResults"]
        self.assertEqual(2, len(person_add_results))
        person_add_result_0: dict[str, Any] = person_add_results[0]
        self.assertTrue("id" in person_add_result_0)
        self.assertEqual("abc123", person_add_result_0["id"])
        self.assertTrue("error" in person_add_result_0)
        person_add_result_0_error: dict[str, Any] = person_add_result_0["error"]
        self.assertEqual("uh oh", person_add_result_0_error["error_message"])
        self.assertEqual(123, person_add_result_0_error["error_code"])
        person_add_result_1: dict[str, Any] = person_add_results[1]
        self.assertTrue("id" in person_add_result_1)
        self.assertEqual("def456", person_add_result_1["id"])
        self.assertFalse("error" in person_add_result_1)
        self.assertTrue("cascadedDeletes" in results)
        cascaded_deletes: dict[str, Any] = results["cascadedDeletes"]
        self.assertTrue("Owns" in cascaded_deletes)
        owns_cascaded_deletes: list[dict[str, Any]] = cascaded_deletes["Owns"]
        self.assertEqual(1, len(owns_cascaded_deletes))
        owns_cascaded_deletes_0: dict[str, Any] = owns_cascaded_deletes[0]
        self.assertTrue("id" in owns_cascaded_deletes_0)
        self.assertEqual("ghi789", owns_cascaded_deletes_0["id"])
        self.assertTrue("originId" in owns_cascaded_deletes_0)
        self.assertEqual("abc123", owns_cascaded_deletes_0["originId"])
        self.assertTrue("destId" in owns_cascaded_deletes_0)
        self.assertEqual("def456", owns_cascaded_deletes_0["destId"])
        self.assertTrue("relationshipSchemaChanges" in results)
        relationship_schema_changes: dict[str, Any] = results[
            "relationshipSchemaChanges"
        ]
        self.assertTrue("Owns" in relationship_schema_changes)
        owns_relationship_schema_changes: dict[str, Any] = relationship_schema_changes[
            "Owns"
        ]
        self.assertTrue("new_end_points" in owns_relationship_schema_changes)
        new_end_points: list[dict[str, Any]] = owns_relationship_schema_changes[
            "new_end_points"
        ]
        self.assertEqual(1, len(new_end_points))
        new_end_point: dict[str, Any] = new_end_points[0]
        self.assertTrue("origin_entity_type" in new_end_point)
        self.assertEqual("Person", new_end_point["origin_entity_type"])
        self.assertTrue("dest_entity_type" in new_end_point)
        self.assertEqual("Vehicle", new_end_point["dest_entity_type"])
        self.assertTrue("cascadedProvenanceDeletes" in results)
        cascaded_provenance_deletes: list[dict[str, Any]] = results[
            "cascadedProvenanceDeletes"
        ]
        self.assertEqual(1, len(cascaded_provenance_deletes))
        cascaded_provenance_delete: dict[str, Any] = cascaded_provenance_deletes[0]
        self.assertTrue("id" in cascaded_provenance_delete)
        self.assertEqual("xyz123", cascaded_provenance_delete["id"])

    def test_named_object_type_adds(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = AddNamedTypesRequest_pb2.GraphNamedObjectTypeAddsRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual(1, len(pbf_request.entity_types))
            pbf_entity_type = pbf_request.entity_types[0]
            self.assertEqual("Person", pbf_entity_type.entity.name)
            self.assertEqual("", pbf_entity_type.entity.alias)
            self.assertEqual(DataModelTypes_pb2.esriGraphNamedObjectRole.esriGraphNamedObjectRegular, pbf_entity_type.entity.role)  # type: ignore
            self.assertEqual(2, len(pbf_entity_type.entity.properties))
            pbf_name_property = pbf_entity_type.entity.properties[0]
            self.assertEqual("name", pbf_name_property.name)
            self.assertEqual("", pbf_name_property.alias)
            self.assertEqual(EsriExtendedTypes_pb2.FieldType.esriFieldTypeString, pbf_name_property.fieldType)  # type: ignore
            self.assertEqual(EsriTypes_pb2.EsriTypes.GeometryType.esriGeometryTypePoint, pbf_name_property.geometryType)  # type: ignore
            self.assertEqual(0, len(pbf_name_property.defaultValue))
            self.assertFalse(pbf_name_property.not_nullable)
            self.assertFalse(pbf_name_property.not_editable)
            self.assertFalse(pbf_name_property.not_visible)
            self.assertFalse(pbf_name_property.required)
            self.assertFalse(pbf_name_property.isSystemMaintained)
            self.assertEqual("", pbf_name_property.domain)
            self.assertFalse(pbf_name_property.hasZ)
            self.assertFalse(pbf_name_property.hasM)
            self.assertEqual(DataModelTypes_pb2.GraphPropertyRole.Regular, pbf_name_property.role)  # type: ignore
            pbf_location_property = pbf_entity_type.entity.properties[1]
            self.assertEqual("location", pbf_location_property.name)
            self.assertEqual("", pbf_location_property.alias)
            self.assertEqual(EsriExtendedTypes_pb2.FieldType.esriFieldTypeGeometry, pbf_location_property.fieldType)  # type: ignore
            self.assertEqual(EsriTypes_pb2.EsriTypes.GeometryType.esriGeometryTypePoint, pbf_location_property.geometryType)  # type: ignore
            self.assertEqual(0, len(pbf_name_property.defaultValue))
            self.assertFalse(pbf_location_property.not_nullable)
            self.assertFalse(pbf_location_property.not_editable)
            self.assertFalse(pbf_location_property.not_visible)
            self.assertFalse(pbf_location_property.required)
            self.assertFalse(pbf_location_property.isSystemMaintained)
            self.assertEqual("", pbf_location_property.domain)
            self.assertFalse(pbf_location_property.hasZ)
            self.assertFalse(pbf_location_property.hasM)
            self.assertEqual(DataModelTypes_pb2.GraphPropertyRole.Regular, pbf_location_property.role)  # type: ignore
            self.assertEqual(1, len(pbf_entity_type.entity.field_indexes))
            pbf_field_index = pbf_entity_type.entity.field_indexes[0]
            self.assertEqual("myIdx", pbf_field_index.name)
            self.assertTrue(pbf_field_index.isAscending)
            self.assertTrue(pbf_field_index.isUnique)
            self.assertEqual("abc,def", pbf_field_index.fields)
            self.assertFalse(pbf_entity_type.entity.strict)
            self.assertEqual(1, len(pbf_request.relationship_types))
            pbf_relationship_type = pbf_request.relationship_types[0]
            self.assertEqual("Owns", pbf_relationship_type.relationship.name)
            self.assertEqual("", pbf_relationship_type.relationship.alias)
            self.assertEqual(DataModelTypes_pb2.esriGraphNamedObjectRole.esriGraphNamedObjectRegular, pbf_relationship_type.relationship.role)  # type: ignore
            self.assertEqual(0, len(pbf_relationship_type.relationship.properties))
            self.assertEqual(0, len(pbf_relationship_type.relationship.field_indexes))
            self.assertFalse(pbf_relationship_type.relationship.strict)
            pbf_response = AddNamedTypesResponse_pb2.GraphNamedObjectTypeAddsResponse()  # type: ignore
            pbf_response.error.error_message = "something bad happened"
            pbf_response.error.error_code = 123
            pbf_entity_add_result = pbf_response.entity_add_results.add()
            pbf_entity_add_result.name = "Person"
            pbf_entity_add_result.error.error_message = "entity error"
            pbf_entity_add_result.error.error_code = 456
            pbf_relationship_add_result = pbf_response.relationship_add_results.add()
            pbf_relationship_add_result.name = "Owns"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/add": mock_service_func,
                },
            ),
        )
        response: Union[dict, NamedObjectTypeAddsResponse] = (
            graph.named_object_type_adds(
                entity_types=[
                    EntityType(
                        name="Person",
                        properties=[
                            GraphProperty(
                                name="name",
                                field_type="esriFieldTypeString",
                            ),
                            GraphProperty(
                                name="location",
                                field_type="esriFieldTypeGeometry",
                                geometry_type="esriGeometryPoint",
                            ),
                        ],
                        field_indexes=[
                            FieldIndex(
                                name="myIdx",
                                is_ascending=True,
                                is_unique=True,
                                fields=["abc", "def"],
                            ),
                        ],
                    )
                ],
                relationship_types=[
                    RelationshipType(
                        name="Owns",
                        properties=[],
                    )
                ],
                as_dict=False,
            )
        )
        if not isinstance(response, NamedObjectTypeAddsResponse):
            self.fail(
                msg="Expected response to be an instance of NamedObjectTypeAddsResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("entityAddResults" in results)
        entity_add_results: list[dict[str, Any]] = results["entityAddResults"]
        self.assertEqual(1, len(entity_add_results))
        entity_add_result: dict[str, Any] = entity_add_results[0]
        self.assertTrue("name" in entity_add_result)
        self.assertEqual("Person", entity_add_result["name"])
        self.assertTrue("error" in entity_add_result)
        entity_add_result_error: dict[str, Any] = entity_add_result["error"]
        self.assertTrue("error_message" in entity_add_result_error)
        self.assertEqual("entity error", entity_add_result_error["error_message"])
        self.assertTrue("error_code" in entity_add_result_error)
        self.assertEqual(456, entity_add_result_error["error_code"])
        self.assertTrue("relationshipAddResults" in results)
        relationship_add_results: list[dict[str, Any]] = results[
            "relationshipAddResults"
        ]
        self.assertEqual(1, len(relationship_add_results))
        relationship_add_result: dict[str, Any] = relationship_add_results[0]
        self.assertTrue("name" in relationship_add_result)
        self.assertEqual("Owns", relationship_add_result["name"])
        self.assertFalse("error" in relationship_add_result)

    def test_named_object_type_update_success(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = UpdateNamedTypeRequest_pb2.GraphNamedObjectTypeUpdateRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertTrue(pbf_request.entity_update.mask.update_name)
            self.assertTrue(pbf_request.entity_update.mask.update_alias)
            self.assertTrue(pbf_request.entity_update.mask.update_role)
            self.assertTrue(pbf_request.entity_update.mask.update_strict)
            self.assertEqual(
                "Person", pbf_request.entity_update.entity_type.entity.name
            )
            pbf_response = UpdateNamedTypeResponse_pb2.GraphNamedObjectTypeUpdateResponse()  # type: ignore
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/queryDataModel": TestHelpers.mock_query_data_model,
                },
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/update": mock_service_func,
                },
            ),
        )
        response: Union[dict, NamedObjectTypeUpdateResponse] = (
            graph.named_object_type_update(
                type_name="Person",
                named_type_update=EntityType(name="Person", properties=[]),
                mask=NamedObjectTypeMask(
                    update_name=True,
                    update_alias=True,
                    update_role=True,
                    update_strict=True,
                ),
                as_dict=False,
            )
        )
        if not isinstance(response, NamedObjectTypeUpdateResponse):
            self.fail(
                msg="Expected response to be an instance of NamedObjectTypeUpdateResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertFalse("error" in results)

    def test_named_object_type_update_error(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = UpdateNamedTypeRequest_pb2.GraphNamedObjectTypeUpdateRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertTrue(
                pbf_request.relationship_update.mask.named_object_type_mask.update_name
            )
            self.assertTrue(
                pbf_request.relationship_update.mask.named_object_type_mask.update_alias
            )
            self.assertTrue(
                pbf_request.relationship_update.mask.named_object_type_mask.update_role
            )
            self.assertTrue(
                pbf_request.relationship_update.mask.named_object_type_mask.update_strict
            )
            self.assertEqual(
                "Owns",
                pbf_request.relationship_update.relationship_type.relationship.name,
            )
            pbf_response = UpdateNamedTypeResponse_pb2.GraphNamedObjectTypeUpdateResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/queryDataModel": TestHelpers.mock_query_data_model,
                },
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Owns/update": mock_service_func,
                },
            ),
        )
        response: Union[dict, NamedObjectTypeUpdateResponse] = (
            graph.named_object_type_update(
                type_name="Owns",
                named_type_update=RelationshipType(name="Owns", properties=[]),
                mask=NamedObjectTypeMask(
                    update_name=True,
                    update_alias=True,
                    update_role=True,
                    update_strict=True,
                ),
                as_dict=False,
            )
        )
        if not isinstance(response, NamedObjectTypeUpdateResponse):
            self.fail(
                msg="Expected response to be an instance of NamedObjectTypeUpdateResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])

    def test_named_object_type_delete_success(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNone(data)
            pbf_response = DeleteNamedTypeResponse_pb2.GraphNamedObjectTypeDeleteResponse()  # type: ignore
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/delete": mock_service_func,
                },
            ),
        )
        response: Union[dict, NamedObjectTypeDeleteResponse] = (
            graph.named_object_type_delete(type_name="Person", as_dict=False)
        )
        if not isinstance(response, NamedObjectTypeDeleteResponse):
            self.fail(
                msg="Expected response to be an instance of NamedObjectTypeDeleteResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertFalse("error" in results)

    def test_named_object_type_delete_error(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNone(data)
            pbf_response = DeleteNamedTypeResponse_pb2.GraphNamedObjectTypeDeleteResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/delete": mock_service_func,
                },
            ),
        )
        response: Union[dict, NamedObjectTypeDeleteResponse] = (
            graph.named_object_type_delete(type_name="Person", as_dict=False)
        )
        if not isinstance(response, NamedObjectTypeDeleteResponse):
            self.fail(
                msg="Expected response to be an instance of NamedObjectTypeDeleteResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])

    def test_graph_property_adds(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = AddFieldsRequest_pb2.GraphPropertyAddsRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual(2, len(pbf_request.graph_properties))
            self.assertEqual("name", pbf_request.graph_properties[0].name)
            self.assertEqual(EsriExtendedTypes_pb2.FieldType.esriFieldTypeString, pbf_request.graph_properties[0].fieldType)  # type: ignore
            self.assertEqual(DataModelTypes_pb2.GraphPropertyRole.Regular, pbf_request.graph_properties[0].role)  # type: ignore
            self.assertEqual("location", pbf_request.graph_properties[1].name)
            self.assertEqual(EsriExtendedTypes_pb2.FieldType.esriFieldTypeGeometry, pbf_request.graph_properties[1].fieldType)  # type: ignore
            self.assertEqual(DataModelTypes_pb2.GraphPropertyRole.Regular, pbf_request.graph_properties[1].role)  # type: ignore
            pbf_response = AddFieldsResponse_pb2.GraphPropertyAddsResponse()  # type: ignore
            pbf_response.error.error_message = "something bad happened"
            pbf_response.error.error_code = 123
            pbf_property_add_result_0 = pbf_response.property_add_results.add()
            pbf_property_add_result_0.name = "name"
            pbf_property_add_result_0.error.error_message = "property error"
            pbf_property_add_result_0.error.error_code = 456
            pbf_property_add_result_1 = pbf_response.property_add_results.add()
            pbf_property_add_result_1.name = "dob"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/fields/add": mock_service_func,
                },
            ),
        )
        response: Union[dict, PropertyAddsResponse] = graph.graph_property_adds(
            type_name="Person",
            graph_properties=[
                GraphProperty(
                    name="name",
                    field_type="esriFieldTypeString",
                ),
                GraphProperty(
                    name="location",
                    field_type="esriFieldTypeGeometry",
                    geometry_type="esriGeometryPoint",
                ),
            ],
            as_dict=False,
        )
        if not isinstance(response, PropertyAddsResponse):
            self.fail(
                msg="Expected response to be an instance of PropertyAddsResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("propertyAddResults" in results)
        property_add_results: list[dict[str, Any]] = results["propertyAddResults"]
        self.assertEqual(2, len(property_add_results))
        property_add_result_0: dict[str, Any] = property_add_results[0]
        self.assertTrue("name" in property_add_result_0)
        self.assertEqual("name", property_add_result_0["name"])
        self.assertTrue("error" in property_add_result_0)
        property_error: dict[str, Any] = property_add_result_0["error"]
        self.assertEqual(456, property_error["error_code"])
        self.assertEqual("property error", property_error["error_message"])
        property_add_result_1: dict[str, Any] = property_add_results[1]
        self.assertTrue("name" in property_add_result_1)
        self.assertEqual("dob", property_add_result_1["name"])
        self.assertFalse("error" in property_add_result_1)

    def test_graph_property_update_success(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = UpdateFieldRequest_pb2.GraphPropertyUpdateRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertTrue(pbf_request.mask.update_name)
            self.assertTrue(pbf_request.mask.update_alias)
            self.assertTrue(pbf_request.mask.update_field_type)
            self.assertTrue(pbf_request.mask.update_geometry_type)
            self.assertTrue(pbf_request.mask.update_default_value)
            self.assertTrue(pbf_request.mask.update_nullable)
            self.assertTrue(pbf_request.mask.update_editable)
            self.assertTrue(pbf_request.mask.update_visible)
            self.assertTrue(pbf_request.mask.update_required)
            self.assertTrue(pbf_request.mask.update_domain)
            self.assertTrue(pbf_request.mask.update_has_z)
            self.assertTrue(pbf_request.mask.update_has_m)
            self.assertEqual("name", pbf_request.graph_property.name)
            self.assertEqual(EsriExtendedTypes_pb2.FieldType.esriFieldTypeString, pbf_request.graph_property.fieldType)  # type: ignore
            self.assertEqual(DataModelTypes_pb2.GraphPropertyRole.Regular, pbf_request.graph_property.role)  # type: ignore
            self.assertEqual("name", pbf_request.property_name)
            pbf_response = UpdateFieldResponse_pb2.GraphPropertyUpdateResponse()  # type: ignore
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/fields/update": mock_service_func,
                },
            ),
        )
        response: Union[dict, PropertyUpdateResponse] = graph.graph_property_update(
            type_name="Person",
            property_name="name",
            graph_property=GraphProperty(name="name", field_type="esriFieldTypeString"),
            mask=GraphPropertyMask(
                update_name=True,
                update_alias=True,
                update_field_type=True,
                update_geometry_type=True,
                update_has_m=True,
                update_has_z=True,
                update_default_value=True,
                update_nullable=True,
                update_editable=True,
                update_visible=True,
                update_required=True,
                update_domain=True,
            ),
            as_dict=False,
        )
        if not isinstance(response, PropertyUpdateResponse):
            self.fail(
                msg="Expected response to be an instance of PropertyUpdateResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertFalse("error" in results)

    def test_graph_property_update_error(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = UpdateFieldRequest_pb2.GraphPropertyUpdateRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertTrue(pbf_request.mask.update_name)
            self.assertTrue(pbf_request.mask.update_alias)
            self.assertTrue(pbf_request.mask.update_field_type)
            self.assertTrue(pbf_request.mask.update_geometry_type)
            self.assertTrue(pbf_request.mask.update_default_value)
            self.assertTrue(pbf_request.mask.update_nullable)
            self.assertTrue(pbf_request.mask.update_editable)
            self.assertTrue(pbf_request.mask.update_visible)
            self.assertTrue(pbf_request.mask.update_required)
            self.assertTrue(pbf_request.mask.update_domain)
            self.assertTrue(pbf_request.mask.update_has_z)
            self.assertTrue(pbf_request.mask.update_has_m)
            self.assertEqual("name", pbf_request.graph_property.name)
            self.assertEqual(EsriExtendedTypes_pb2.FieldType.esriFieldTypeString, pbf_request.graph_property.fieldType)  # type: ignore
            self.assertEqual(DataModelTypes_pb2.GraphPropertyRole.Regular, pbf_request.graph_property.role)  # type: ignore
            self.assertEqual("name", pbf_request.property_name)
            pbf_response = UpdateFieldResponse_pb2.GraphPropertyUpdateResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/fields/update": mock_service_func,
                },
            ),
        )
        response: Union[dict, PropertyUpdateResponse] = graph.graph_property_update(
            type_name="Person",
            property_name="name",
            graph_property=GraphProperty(name="name", field_type="esriFieldTypeString"),
            mask=GraphPropertyMask(
                update_name=True,
                update_alias=True,
                update_field_type=True,
                update_geometry_type=True,
                update_has_m=True,
                update_has_z=True,
                update_default_value=True,
                update_nullable=True,
                update_editable=True,
                update_visible=True,
                update_required=True,
                update_domain=True,
            ),
            as_dict=False,
        )
        if not isinstance(response, PropertyUpdateResponse):
            self.fail(
                msg="Expected response to be an instance of PropertyUpdateResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])

    def test_graph_property_delete_success(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = DeleteFieldRequest_pb2.GraphPropertyDeleteRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual("name", pbf_request.name)
            pbf_response = DeleteFieldResponse_pb2.GraphPropertyDeleteResponse()  # type: ignore
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/fields/delete": mock_service_func,
                },
            ),
        )
        response: Union[dict, PropertyDeleteResponse] = graph.graph_property_delete(
            type_name="Person", property_name="name", as_dict=False
        )
        if not isinstance(response, PropertyDeleteResponse):
            self.fail(
                msg="Expected response to be an instance of PropertyDeleteResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertFalse("error" in results)

    def test_graph_property_delete_error(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = DeleteFieldRequest_pb2.GraphPropertyDeleteRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual("name", pbf_request.name)
            pbf_response = DeleteFieldResponse_pb2.GraphPropertyDeleteResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/fields/delete": mock_service_func,
                },
            ),
        )
        response: Union[dict, PropertyDeleteResponse] = graph.graph_property_delete(
            type_name="Person", property_name="name", as_dict=False
        )
        if not isinstance(response, PropertyDeleteResponse):
            self.fail(
                msg="Expected response to be an instance of PropertyDeleteResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])

    def test_graph_property_index_adds(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = AddIndexesRequest_pb2.GraphPropertyIndexAddsRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual(1, len(pbf_request.field_indexes))
            self.assertEqual("myIdx", pbf_request.field_indexes[0].name)
            self.assertEqual("name,dob", pbf_request.field_indexes[0].fields)
            self.assertTrue(pbf_request.field_indexes[0].isAscending)
            self.assertTrue(pbf_request.field_indexes[0].isUnique)
            pbf_response = AddIndexesResponse_pb2.GraphPropertyIndexAddsResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            pbf_result_0 = pbf_response.index_add_results.add()
            pbf_result_0.name = "myIdx0"
            pbf_result_0.error.error_code = 456
            pbf_result_0.error.error_message = "index error"
            pbf_result_1 = pbf_response.index_add_results.add()
            pbf_result_1.name = "myIdx1"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/indexes/add": mock_service_func,
                },
            ),
        )
        response: Union[dict, IndexAddsResponse] = graph.graph_property_index_adds(
            type_name="Person",
            field_indexes=[
                FieldIndex(
                    name="myIdx",
                    is_ascending=True,
                    is_unique=True,
                    fields=["name", "dob"],
                ),
            ],
            as_dict=False,
        )
        if not isinstance(response, IndexAddsResponse):
            self.fail(msg="Expected response to be an instance of IndexAddsResponse.")
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("indexAddResults " in results)
        index_add_results: list[dict[str, Any]] = results["indexAddResults "]
        self.assertEqual(2, len(index_add_results))
        index_add_result_0: dict[str, Any] = index_add_results[0]
        self.assertTrue("name" in index_add_result_0)
        self.assertEqual("myIdx0", index_add_result_0["name"])
        self.assertTrue("error" in index_add_result_0)
        index_error: dict[str, Any] = index_add_result_0["error"]
        self.assertEqual(456, index_error["error_code"])
        self.assertEqual("index error", index_error["error_message"])
        index_add_result_1: dict[str, Any] = index_add_results[1]
        self.assertTrue("name" in index_add_result_1)
        self.assertEqual("myIdx1", index_add_result_1["name"])
        self.assertFalse("error" in index_add_result_1)

    def test_graph_property_index_deletes(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = DeleteIndexesRequest_pb2.GraphPropertyIndexDeleteRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual(1, len(pbf_request.name))
            self.assertEqual("myIdx", pbf_request.name[0])
            pbf_response = DeleteIndexesResponse_pb2.GraphIndexDeleteResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            pbf_result_0 = pbf_response.index_delete_results.add()
            pbf_result_0.name = "myIdx0"
            pbf_result_0.error.error_code = 456
            pbf_result_0.error.error_message = "index error"
            pbf_result_1 = pbf_response.index_delete_results.add()
            pbf_result_1.name = "myIdx1"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE}/dataModel/edit/namedTypes/Person/indexes/delete": mock_service_func,
                },
            ),
        )
        response: Union[dict, IndexDeletesResponse] = (
            graph.graph_property_index_deletes(
                type_name="Person", field_indexes=["myIdx"], as_dict=False
            )
        )
        if not isinstance(response, IndexDeletesResponse):
            self.fail(
                msg="Expected response to be an instance of IndexDeletesResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("indexDeleteResults " in results)
        index_delete_results: list[dict[str, Any]] = results["indexDeleteResults "]
        self.assertEqual(2, len(index_delete_results))
        index_delete_result_0: dict[str, Any] = index_delete_results[0]
        self.assertTrue("name" in index_delete_result_0)
        self.assertEqual("myIdx0", index_delete_result_0["name"])
        self.assertTrue("error" in index_delete_result_0)
        index_error: dict[str, Any] = index_delete_result_0["error"]
        self.assertEqual(456, index_error["error_code"])
        self.assertEqual("index error", index_error["error_message"])
        index_delete_result_1: dict[str, Any] = index_delete_results[1]
        self.assertTrue("name" in index_delete_result_1)
        self.assertEqual("myIdx1", index_delete_result_1["name"])
        self.assertFalse("error" in index_delete_result_1)

    def test_constraint_rule_adds(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = AddConstraintRulesRequest_pb2.GraphConstraintRuleAddsRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual(1, len(pbf_request.constraint_rules))
            self.assertEqual("rule", pbf_request.constraint_rules[0].name)
            self.assertEqual(DataModelTypes_pb2.ConstraintRuleRole.ConstraintRuleRole_Regular, pbf_request.constraint_rules[0].role)  # type: ignore
            self.assertEqual(
                1,
                len(
                    pbf_request.constraint_rules[
                        0
                    ].relationship_exclusion_rule.origin_entity_types.set.value
                ),
            )
            self.assertEqual(
                "Provenance",
                pbf_request.constraint_rules[
                    0
                ].relationship_exclusion_rule.origin_entity_types.set.value[0],
            )
            self.assertEqual(
                "set_complement",
                pbf_request.constraint_rules[
                    0
                ].relationship_exclusion_rule.relationship_types.WhichOneof(
                    "type_of_set"
                ),
            )
            self.assertEqual(
                0,
                len(
                    pbf_request.constraint_rules[
                        0
                    ].relationship_exclusion_rule.relationship_types.set_complement.value
                ),
            )
            self.assertEqual(
                "set_complement",
                pbf_request.constraint_rules[
                    0
                ].relationship_exclusion_rule.destination_entity_types.WhichOneof(
                    "type_of_set"
                ),
            )
            self.assertEqual(
                0,
                len(
                    pbf_request.constraint_rules[
                        0
                    ].relationship_exclusion_rule.destination_entity_types.set_complement.value
                ),
            )
            pbf_response = AddConstraintRulesResponse_pb2.GraphConstraintRuleAddsResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            pbf_result_0 = pbf_response.constraint_rule_add_results.add()
            pbf_result_0.name = "rule0"
            pbf_result_0.error.error_code = 456
            pbf_result_0.error.error_message = "rule error"
            pbf_warning = pbf_result_0.warnings.add()
            pbf_warning.error_code = 789
            pbf_warning.error_message = "rule warning"
            pbf_result_1 = pbf_response.constraint_rule_add_results.add()
            pbf_result_1.name = "rule1"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE_ADMIN_URL}/dataModel/constraintRules/add": mock_service_func,
                },
            ),
        )
        response: Union[dict, ConstraintRuleAddsResponse] = graph.constraint_rule_adds(
            rules=[
                RelationshipExclusionRule(
                    name="rule",
                    origin_entity_types=SetOfNamedTypes(set=["Provenance"]),
                    relationship_types=SetOfNamedTypes(),
                    destination_entity_types=SetOfNamedTypes(),
                ),
            ],
            as_dict=False,
        )
        if not isinstance(response, ConstraintRuleAddsResponse):
            self.fail(
                msg="Expected response to be an instance of ConstraintRuleAddsResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("constraint_rule_add_results" in results)
        rule_add_results: list[dict[str, Any]] = results["constraint_rule_add_results"]
        self.assertEqual(2, len(rule_add_results))
        rule_add_result_0: dict[str, Any] = rule_add_results[0]
        self.assertTrue("name" in rule_add_result_0)
        self.assertEqual("rule0", rule_add_result_0["name"])
        self.assertTrue("error" in rule_add_result_0)
        rule_error: dict[str, Any] = rule_add_result_0["error"]
        self.assertEqual(456, rule_error["error_code"])
        self.assertEqual("rule error", rule_error["error_message"])
        self.assertTrue("warnings" in rule_add_result_0)
        rule0_warnings: list[dict[str, Any]] = rule_add_result_0["warnings"]
        self.assertEqual(1, len(rule0_warnings))
        rule_warning: dict[str, Any] = rule0_warnings[0]
        self.assertEqual(789, rule_warning["error_code"])
        self.assertEqual("rule warning", rule_warning["error_message"])
        rule_add_result_1: dict[str, Any] = rule_add_results[1]
        self.assertTrue("name" in rule_add_result_1)
        self.assertEqual("rule1", rule_add_result_1["name"])
        self.assertFalse("error" in rule_add_result_1)
        self.assertTrue("warnings" in rule_add_result_1)
        rule1_warnings: list[dict[str, Any]] = rule_add_result_1["warnings"]
        self.assertEqual(0, len(rule1_warnings))

    def test_constraint_rule_updates(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = UpdateConstraintRulesRequest_pb2.GraphConstraintRuleUpdatesRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual(1, len(pbf_request.constraint_rule_updates))
            self.assertEqual("rule", pbf_request.constraint_rule_updates[0].rule_name)
            self.assertTrue(pbf_request.constraint_rule_updates[0].mask.update_name)
            self.assertTrue(pbf_request.constraint_rule_updates[0].mask.update_alias)
            self.assertTrue(pbf_request.constraint_rule_updates[0].mask.update_disabled)
            self.assertEqual(
                "rule", pbf_request.constraint_rule_updates[0].constraint_rule.name
            )
            self.assertEqual(DataModelTypes_pb2.ConstraintRuleRole.ConstraintRuleRole_Regular, pbf_request.constraint_rule_updates[0].constraint_rule.role)  # type: ignore
            self.assertEqual(
                1,
                len(
                    pbf_request.constraint_rule_updates[
                        0
                    ].relationship_exclusion_rule_update.update_origin_entity_types.add_named_types
                ),
            )
            self.assertEqual(
                "Person",
                pbf_request.constraint_rule_updates[
                    0
                ].relationship_exclusion_rule_update.update_origin_entity_types.add_named_types[
                    0
                ],
            )
            self.assertEqual(
                0,
                len(
                    pbf_request.constraint_rule_updates[
                        0
                    ].relationship_exclusion_rule_update.update_origin_entity_types.remove_named_types
                ),
            )
            self.assertEqual(
                0,
                len(
                    pbf_request.constraint_rule_updates[
                        0
                    ].relationship_exclusion_rule_update.update_relationship_types.add_named_types
                ),
            )
            self.assertEqual(
                1,
                len(
                    pbf_request.constraint_rule_updates[
                        0
                    ].relationship_exclusion_rule_update.update_relationship_types.remove_named_types
                ),
            )
            self.assertEqual(
                "Owns",
                pbf_request.constraint_rule_updates[
                    0
                ].relationship_exclusion_rule_update.update_relationship_types.remove_named_types[
                    0
                ],
            )
            self.assertEqual(
                0,
                len(
                    pbf_request.constraint_rule_updates[
                        0
                    ].relationship_exclusion_rule_update.update_destination_entity_types.add_named_types
                ),
            )
            self.assertEqual(
                0,
                len(
                    pbf_request.constraint_rule_updates[
                        0
                    ].relationship_exclusion_rule_update.update_destination_entity_types.remove_named_types
                ),
            )
            pbf_response = UpdateConstraintRulesResponse_pb2.GraphConstraintRuleUpdatesResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            pbf_result_0 = pbf_response.constraint_rule_update_results.add()
            pbf_result_0.name = "rule0"
            pbf_result_0.error.error_code = 456
            pbf_result_0.error.error_message = "rule error"
            pbf_warning = pbf_result_0.warnings.add()
            pbf_warning.error_code = 789
            pbf_warning.error_message = "rule warning"
            pbf_result_1 = pbf_response.constraint_rule_update_results.add()
            pbf_result_1.name = "rule1"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE_ADMIN_URL}/dataModel/constraintRules/update": mock_service_func,
                },
            ),
        )
        response: Union[dict, ConstraintRuleUpdatesResponse] = (
            graph.constraint_rule_updates(
                rules=[
                    RelationshipExclusionRuleUpdate(
                        rule_name="rule",
                        mask=ConstraintRuleMask(
                            update_name=True,
                            update_alias=True,
                            update_disabled=True,
                        ),
                        constraint_rule=ConstraintRule(
                            name="rule",
                        ),
                        update_origin_entity_types=UpdateSetOfNamedTypes(
                            add_named_types=["Person"],
                            remove_named_types=[],
                        ),
                        update_relationship_types=UpdateSetOfNamedTypes(
                            add_named_types=[],
                            remove_named_types=["Owns"],
                        ),
                        update_destination_entity_types=UpdateSetOfNamedTypes(
                            add_named_types=[],
                            remove_named_types=[],
                        ),
                    ),
                ],
                as_dict=False,
            )
        )
        if not isinstance(response, ConstraintRuleUpdatesResponse):
            self.fail(
                msg="Expected response to be an instance of ConstraintRuleUpdatesResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("constraint_rule_update_results" in results)
        rule_update_results: list[dict[str, Any]] = results[
            "constraint_rule_update_results"
        ]
        self.assertEqual(2, len(rule_update_results))
        rule_update_result_0: dict[str, Any] = rule_update_results[0]
        self.assertTrue("name" in rule_update_result_0)
        self.assertEqual("rule0", rule_update_result_0["name"])
        self.assertTrue("error" in rule_update_result_0)
        rule_error: dict[str, Any] = rule_update_result_0["error"]
        self.assertEqual(456, rule_error["error_code"])
        self.assertEqual("rule error", rule_error["error_message"])
        self.assertTrue("warnings" in rule_update_result_0)
        rule0_warnings: list[dict[str, Any]] = rule_update_result_0["warnings"]
        self.assertEqual(1, len(rule0_warnings))
        rule_warning: dict[str, Any] = rule0_warnings[0]
        self.assertEqual(789, rule_warning["error_code"])
        self.assertEqual("rule warning", rule_warning["error_message"])
        rule_update_result_1: dict[str, Any] = rule_update_results[1]
        self.assertTrue("name" in rule_update_result_1)
        self.assertEqual("rule1", rule_update_result_1["name"])
        self.assertFalse("error" in rule_update_result_1)
        self.assertTrue("warnings" in rule_update_result_1)
        rule1_warnings: list[dict[str, Any]] = rule_update_result_1["warnings"]
        self.assertEqual(0, len(rule1_warnings))

    def test_constraint_rule_deletes(self):
        def mock_service_func(data: Optional[bytes]) -> Response:
            self.assertIsNotNone(data)
            pbf_request = DeleteConstraintRulesRequest_pb2.GraphConstraintRuleDeleteRequest()  # type: ignore
            pbf_request.ParseFromString(data)
            self.assertEqual(1, len(pbf_request.constraint_rule_name_array))
            self.assertEqual("rule", pbf_request.constraint_rule_name_array[0])
            pbf_response = DeleteConstraintRulesResponse_pb2.GraphConstraintRuleDeleteResponse()  # type: ignore
            pbf_response.error.error_code = 123
            pbf_response.error.error_message = "something bad happened"
            pbf_result_0 = pbf_response.constraint_rule_delete_results.add()
            pbf_result_0.name = "rule0"
            pbf_result_0.error.error_code = 456
            pbf_result_0.error.error_message = "rule error"
            pbf_result_1 = pbf_response.constraint_rule_delete_results.add()
            pbf_result_1.name = "rule1"
            response_content: bytes = pbf_response.SerializeToString()
            return TestHelpers.construct_response(
                status_code=200, content=response_content
            )

        graph: KnowledgeGraph = KnowledgeGraph(
            url=TestConstants.FAKE_SERVICE,
            gis=TestHelpers.construct_gis(
                get_requests={},
                post_requests={
                    f"{TestConstants.FAKE_SERVICE_ADMIN_URL}/dataModel/constraintRules/delete": mock_service_func,
                },
            ),
        )
        response: Union[dict, ConstraintRuleDeletesResponse] = (
            graph.constraint_rule_deletes(rule_names=["rule"], as_dict=False)
        )
        if not isinstance(response, ConstraintRuleDeletesResponse):
            self.fail(
                msg="Expected response to be an instance of ConstraintRuleDeletesResponse."
            )
        results: dict[str, Any] = response.model_dump(by_alias=True)
        self.assertTrue("error" in results)
        error: dict[str, Any] = results["error"]
        self.assertTrue("error_message" in error)
        self.assertEqual("something bad happened", error["error_message"])
        self.assertTrue("error_code" in error)
        self.assertEqual(123, error["error_code"])
        self.assertTrue("constraint_rule_delete_results" in results)
        constraint_rule_delete_results: list[dict[str, Any]] = results[
            "constraint_rule_delete_results"
        ]
        self.assertEqual(2, len(constraint_rule_delete_results))
        constraint_rule_delete_result_0: dict[str, Any] = (
            constraint_rule_delete_results[0]
        )
        self.assertTrue("name" in constraint_rule_delete_result_0)
        self.assertEqual("rule0", constraint_rule_delete_result_0["name"])
        self.assertTrue("error" in constraint_rule_delete_result_0)
        rule_error: dict[str, Any] = constraint_rule_delete_result_0["error"]
        self.assertEqual(456, rule_error["error_code"])
        self.assertEqual("rule error", rule_error["error_message"])
        constraint_rule_delete_result_1: dict[str, Any] = (
            constraint_rule_delete_results[1]
        )
        self.assertTrue("name" in constraint_rule_delete_result_1)
        self.assertEqual("rule1", constraint_rule_delete_result_1["name"])
        self.assertFalse("error" in constraint_rule_delete_result_1)

    def test_convert_to_proper_representation_geometry(self):
        geom: Geometry = Geometry(
            {
                "x": 1.1,
                "y": 2.2,
            }
        )
        converted_geom = KnowledgeGraph._convert_to_proper_representation(
            python_value=geom
        )
        self.assertTrue(isinstance(converted_geom, dict))
        self.assertTrue("_objectType" in converted_geom)
        self.assertEqual("geometry", converted_geom["_objectType"])
        self.assertTrue("x" in converted_geom)
        self.assertEqual(1.1, converted_geom["x"])
        self.assertTrue("y" in converted_geom)
        self.assertEqual(2.2, converted_geom["y"])

    def test_convert_to_proper_representation_dict(self):
        dictionary: dict[str, Any] = {
            "name": "Cameron",
            "age": 27,
        }
        converted_dictionary = KnowledgeGraph._convert_to_proper_representation(
            python_value=dictionary
        )
        self.assertTrue(isinstance(converted_dictionary, dict))
        self.assertTrue("_objectType" in converted_dictionary)
        self.assertEqual("object", converted_dictionary["_objectType"])
        self.assertTrue("_properties" in converted_dictionary)
        self.assertTrue(isinstance(converted_dictionary["_properties"], dict))
        self.assertTrue("name" in converted_dictionary["_properties"])
        self.assertEqual("Cameron", converted_dictionary["_properties"]["name"])
        self.assertTrue("age" in converted_dictionary["_properties"])
        self.assertEqual(27, converted_dictionary["_properties"]["age"])

    def test_convert_to_proper_representation_list(self):
        original_list: list[Any] = [
            Geometry(
                {
                    "x": 1.1,
                    "y": 2.2,
                }
            ),
            {
                "name": "Cameron",
                "age": 27,
            },
        ]
        converted_list = KnowledgeGraph._convert_to_proper_representation(
            python_value=original_list
        )
        self.assertTrue(isinstance(converted_list, list))
        self.assertEqual(2, len(converted_list))
        converted_geom = converted_list[0]
        self.assertTrue(isinstance(converted_geom, dict))
        self.assertTrue("_objectType" in converted_geom)
        self.assertEqual("geometry", converted_geom["_objectType"])
        self.assertTrue("x" in converted_geom)
        self.assertEqual(1.1, converted_geom["x"])
        self.assertTrue("y" in converted_geom)
        self.assertEqual(2.2, converted_geom["y"])
        converted_dictionary = converted_list[1]
        self.assertTrue(isinstance(converted_dictionary, dict))
        self.assertTrue("_objectType" in converted_dictionary)
        self.assertEqual("object", converted_dictionary["_objectType"])
        self.assertTrue("_properties" in converted_dictionary)
        self.assertTrue(isinstance(converted_dictionary["_properties"], dict))
        self.assertTrue("name" in converted_dictionary["_properties"])
        self.assertEqual("Cameron", converted_dictionary["_properties"]["name"])
        self.assertTrue("age" in converted_dictionary["_properties"])
        self.assertEqual(27, converted_dictionary["_properties"]["age"])


if __name__ == "__main__":
    unittest.main()
