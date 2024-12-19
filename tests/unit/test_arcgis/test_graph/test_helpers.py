from typing import Optional, Callable, Union, Any, Sequence
from requests import Response
from uuid import UUID

import gzip
import unittest

from google.protobuf.internal.encoder import _EncodeVarint  # type: ignore

from esriPBuffer import EsriTypes_pb2
from esriPBuffer.EsriExtendedTypes import EsriExtendedTypes_pb2
from esriPBuffer.graph import (
    DataModelTypes_pb2,
    QueryDataModelResponse_pb2,
    QueryResponse_pb2,
)

from arcgis.gis import GIS
from arcgis.graph import (
    GraphObject,
    Entity,
    Relationship,
    Path,
)


class TestConstants:
    FAKE_TOKEN: str = "fakeToken"
    FAKE_SERVICE: str = (
        "https://fakeServer.com/server/rest/services/Hosted/FakeService/KnowledgeGraphServer"
    )
    FAKE_SERVICE_ADMIN_URL: str = (
        "https://fakeServer.com/server/rest/admin/services/Hosted/FakeService/KnowledgeGraphServer"
    )


class MockEsriSession:
    def __init__(self, post_requests: dict[str, Callable[[Optional[bytes]], Response]]):
        self._post_requests = post_requests

    def post(self, url: str, data: Optional[bytes] = None, **kwargs) -> Response:
        assert kwargs["stream"]
        assert kwargs["headers"]["Content-Type"] == "application/octet-stream"
        assert kwargs["params"]["f"] == "pbf"
        # assert kwargs["params"]["token"] == TestConstants.FAKE_TOKEN
        return self._post_requests[url](data)


class MockConnection:
    def __init__(
        self,
        get_requests: dict[str, Callable[[], Union[Response, dict[str, Any]]]],
        post_requests: dict[str, Callable[[Optional[bytes]], Response]],
    ):
        self._session = MockEsriSession(post_requests=post_requests)
        self._get_requests = get_requests
        self.token = TestConstants.FAKE_TOKEN

    def get(
        self, path: str, params: dict[str, str], **kwargs
    ) -> Union[Response, dict[str, Any]]:
        match params["f"]:
            case "pbf":
                assert kwargs["return_raw_response"]
                assert not kwargs["try_json"]
            case "json":
                pass
            case _:
                raise Exception("Unsupported format requested!")
        return self._get_requests[path]()


class MockGIS:
    def __init__(self, con: MockConnection):
        self._con = con
        self._portal = None
        self._validate_item_url = False
        self._use_private_url_only = False


class TestHelpers:
    @staticmethod
    def construct_gis(
        get_requests: dict[str, Callable[[], Union[Response, dict[str, Any]]]],
        post_requests: dict[str, Callable[[Optional[bytes]], Response]],
    ) -> GIS:
        return MockGIS(
            con=MockConnection(get_requests=get_requests, post_requests=post_requests)
        )  # type: ignore

    @staticmethod
    def construct_response(status_code: int, content: bytes) -> Response:
        response: Response = Response()
        response._content = content
        response._content_consumed = True  # type: ignore
        response.status_code = status_code
        response.headers["Content-Type"] = "application/x-protobuf"
        return response

    @staticmethod
    def construct_query_response(header, frames) -> bytes:
        list_of_byte_strings: list[bytes] = []

        def write(data: bytes) -> None:
            list_of_byte_strings.append(data)

        header_bytes: bytes = header.SerializeToString()
        _EncodeVarint(write, len(header_bytes))
        list_of_byte_strings.append(header_bytes)
        for frame in frames:
            frame_bytes: bytes = frame.SerializeToString()
            frame_compressed_bytes: bytes = gzip.compress(data=frame_bytes)
            _EncodeVarint(write, len(frame_compressed_bytes))
            list_of_byte_strings.append(frame_compressed_bytes)
        return b"".join(list_of_byte_strings)

    @staticmethod
    def mock_properties() -> dict[str, Any]:
        return {
            "maxRecordCount": 1000,
        }

    @staticmethod
    def mock_query_response() -> Response:
        pbf_response_header = QueryResponse_pb2.GraphQueryResultHeader()  # type: ignore
        pbf_response_header.transform.scale.xScale = 1.1
        pbf_response_header.transform.scale.yScale = 1.2
        pbf_response_header.transform.scale.mScale = 1.3
        pbf_response_header.transform.scale.zScale = 1.4
        pbf_response_header.transform.translate.xTranslate = 2.1
        pbf_response_header.transform.translate.yTranslate = 2.2
        pbf_response_header.transform.translate.mTranslate = 2.3
        pbf_response_header.transform.translate.zTranslate = 2.4
        pbf_response_header.field_names.append("string_value")
        pbf_response_header.field_names.append("float_value")
        pbf_response_header.field_names.append("float_compressed_as_int32")
        pbf_response_header.field_names.append("double_value")
        pbf_response_header.field_names.append("double_compressed_as_float")
        pbf_response_header.field_names.append("double_compressed_as_int64")
        pbf_response_header.field_names.append("sint64_value")
        pbf_response_header.field_names.append("bool_value")
        pbf_response_header.field_names.append("uuid_value")
        pbf_response_header.field_names.append("blob_value")
        pbf_response_header.field_names.append("geometry_value")
        pbf_response_header.field_names.append("null_tag")
        pbf_response_header.field_names.append("datetime_value")
        pbf_response_header.field_names.append("timestamp_offset_value")
        pbf_response_header.field_names.append("date_only_value")
        pbf_response_header.field_names.append("time_only_value")
        pbf_response_header.field_names.append("duration_value")
        pbf_response_header.field_names.append("any_value_array")
        pbf_response_header.field_names.append("float_array")
        pbf_response_header.field_names.append("uuid_array")
        pbf_response_header.field_names.append("object_value")
        pbf_response_header.field_names.append("entity_value")
        pbf_response_header.field_names.append("relationship_value")
        pbf_response_header.field_names.append("path_value")
        pbf_response_header.field_names.append("unknown_string_value")
        pbf_response_header.compressed_frames = True
        pbf_response_frame = QueryResponse_pb2.GraphQueryResultFrame()  # type: ignore
        pbf_row = pbf_response_frame.rows.add()
        string_value = pbf_row.values.add()
        string_value.primitive_value.string_value = "pbf_string_value"
        float_value = pbf_row.values.add()
        float_value.primitive_value.float_value = 1.23
        float_compressed_as_int32 = pbf_row.values.add()
        float_compressed_as_int32.primitive_value.float_compressed_as_int32 = 123
        double_value = pbf_row.values.add()
        double_value.primitive_value.double_value = 1.23
        double_compressed_as_float = pbf_row.values.add()
        double_compressed_as_float.primitive_value.double_compressed_as_float = 1.23
        double_compressed_as_int64 = pbf_row.values.add()
        double_compressed_as_int64.primitive_value.double_compressed_as_int64 = 123
        sint64_value = pbf_row.values.add()
        sint64_value.primitive_value.sint64_value = 123
        bool_value = pbf_row.values.add()
        bool_value.primitive_value.bool_value = True
        uuid_value = pbf_row.values.add()
        uuid_value.primitive_value.uuid_value = b"\x12\x34\x56\x78" * 4
        blob_value = pbf_row.values.add()
        blob_value.primitive_value.blob_value = b"123"
        geometry_value = pbf_row.values.add()
        geometry_value.primitive_value.geometry_value.geometryType = EsriTypes_pb2.EsriTypes.GeometryType.esriGeometryTypePoint  # type: ignore
        geometry_value.primitive_value.geometry_value.geometry.lengths.append(1)
        geometry_value.primitive_value.geometry_value.geometry.coords.append(5)
        geometry_value.primitive_value.geometry_value.geometry.coords.append(6)
        null_tag = pbf_row.values.add()
        null_tag.primitive_value.null_tag = False
        datetime_value = pbf_row.values.add()
        datetime_value.primitive_value.datetime_value = 123
        timestamp_offset_value = pbf_row.values.add()
        timestamp_offset_value.primitive_value.timestamp_offset_value.date_time_offset.local_epoch_ms = (
            123
        )
        date_only_value = pbf_row.values.add()
        date_only_value.primitive_value.date_only_value.epoch_days = 123
        time_only_value = pbf_row.values.add()
        time_only_value.primitive_value.time_only_value.milliseconds_of_day = 123
        duration_value = pbf_row.values.add()
        duration_value.primitive_value.duration_value.duration_components.months = 5
        any_value_array = pbf_row.values.add()
        any_value_array_value = any_value_array.array_value.any_value_array.values.add()
        any_value_array_value.primitive_value.string_value = "any_value_array_value"
        float_array = pbf_row.values.add()
        float_array.array_value.float_array.value.append(1.23)
        uuid_array = pbf_row.values.add()
        uuid_array.array_value.uuid_array = b"\x12\x34\x56\x78" * 8
        object_value = pbf_row.values.add()
        object_value_property = object_value.object_value.properties.add()
        object_value_property.key = "name"
        object_value_property.value.primitive_value.string_value = "Cameron"
        entity_value = pbf_row.values.add()
        entity_value.entity_value.label = "Person"
        entity_value.entity_value.id.primitive_value.string_value = "abc123"
        relationship_value = pbf_row.values.add()
        relationship_value.relationship_value.type = "Owns"
        relationship_value.relationship_value.id.primitive_value.string_value = "def456"
        relationship_value.relationship_value.origin_id.primitive_value.string_value = (
            "ghi789"
        )
        relationship_value.relationship_value.dest_id.primitive_value.string_value = (
            "jkl123"
        )
        path_value = pbf_row.values.add()
        entity_path_value = path_value.path_value.entities.add()
        entity_path_value.label = "Person"
        entity_path_value.id.primitive_value.string_value = "xyz789"
        unknown_string_value = pbf_row.values.add()
        unknown_string_value.unknown_value.primitive_value.string_value = (
            "unknown_string_value"
        )
        response_content: bytes = TestHelpers.construct_query_response(
            header=pbf_response_header,
            frames=[pbf_response_frame],
        )
        return TestHelpers.construct_response(status_code=200, content=response_content)

    @staticmethod
    def validate_query_response(
        test_case: unittest.TestCase, result: Sequence[Any]
    ) -> None:
        test_case.assertEqual("pbf_string_value", result[0])
        test_case.assertEqual(1.2300000190734863, result[1])
        test_case.assertEqual(123.0, result[2])
        test_case.assertEqual(1.23, result[3])
        test_case.assertEqual(1.2300000190734863, result[4])
        test_case.assertEqual(123.0, result[5])
        test_case.assertEqual(123, result[6])
        test_case.assertTrue(result[7])
        test_case.assertEqual(
            UUID("12345678-1234-5678-1234-567812345678").bytes, result[8].bytes
        )
        test_case.assertEqual(b"123", result[9])
        test_case.assertEqual(7.6, result[10]["x"])
        test_case.assertEqual(9.399999999999999, result[10]["y"])
        test_case.assertIsNone(result[11])
        test_case.assertEqual(123, result[12])
        test_case.assertIsNone(
            result[13]
        )  # TODO this should be a timestamp offset value!
        test_case.assertEqual("1970-05-04", result[14])
        test_case.assertEqual("00:00:00.123", result[15])
        test_case.assertEqual("P5M", result[16])
        test_case.assertEqual(1, len(result[17]))
        test_case.assertEqual("any_value_array_value", result[17][0])
        test_case.assertEqual(1, len(result[18]))
        test_case.assertEqual(1.2300000190734863, result[18][0])
        test_case.assertEqual(2, len(result[19]))
        test_case.assertEqual(
            UUID("12345678-1234-5678-1234-567812345678").bytes, result[19][0].bytes
        )
        test_case.assertEqual(
            UUID("12345678-1234-5678-1234-567812345678").bytes, result[19][1].bytes
        )
        test_case.assertTrue(isinstance(result[20], GraphObject))
        test_case.assertEqual("Cameron", result[20].properties["name"])
        test_case.assertTrue(isinstance(result[21], Entity))
        test_case.assertEqual("Person", result[21].type_name)
        test_case.assertEqual("abc123", result[21].id)
        test_case.assertTrue(isinstance(result[22], Relationship))
        test_case.assertEqual("Owns", result[22].type_name)
        test_case.assertEqual("def456", result[22].id)
        test_case.assertEqual("ghi789", result[22].origin_entity_id)
        test_case.assertEqual("jkl123", result[22].destination_entity_id)
        test_case.assertTrue(isinstance(result[23], Path))
        test_case.assertEqual(1, len(result[23].path))
        test_case.assertTrue(isinstance(result[23].path[0], Entity))
        test_case.assertEqual("Person", result[23].path[0].type_name)
        test_case.assertEqual("xyz789", result[23].path[0].id)
        test_case.assertEqual("unknown_string_value", result[24])

    @staticmethod
    def mock_query_data_model() -> Response:
        pbf_graph_data_model = QueryDataModelResponse_pb2.GraphDataModel()  # type: ignore
        pbf_graph_data_model.data_model_timestamp = 123
        pbf_graph_data_model.spatial_reference.wkid = 4326
        pbf_entity_type = pbf_graph_data_model.entity_types.add()
        pbf_entity_type.entity.name = "Person"
        pbf_entity_type.entity.role = DataModelTypes_pb2.esriGraphNamedObjectRole.esriGraphNamedObjectRegular  # type: ignore
        pbf_property = pbf_entity_type.entity.properties.add()
        pbf_property.name = "name"
        pbf_property.fieldType = EsriExtendedTypes_pb2.FieldType.esriFieldTypeString  # type: ignore
        pbf_property.role = DataModelTypes_pb2.GraphPropertyRole.Regular  # type: ignore
        pbf_property_editor_tracking = pbf_entity_type.entity.properties.add()
        pbf_property_editor_tracking.name = "creator"
        pbf_property_editor_tracking.fieldType = EsriExtendedTypes_pb2.FieldType.esriFieldTypeString  # type: ignore
        pbf_property_editor_tracking.role = DataModelTypes_pb2.GraphPropertyRole.EditorTracking_Creator  # type: ignore
        pbf_field_index = pbf_entity_type.entity.field_indexes.add()
        pbf_field_index.name = "idx"
        pbf_field_index.fields = "a,b"
        pbf_relationship_type = pbf_graph_data_model.relationship_types.add()
        pbf_relationship_type.relationship.name = "Owns"
        pbf_relationship_type.relationship.role = DataModelTypes_pb2.esriGraphNamedObjectRole.esriGraphNamedObjectRegular  # type: ignore
        pbf_end_point = pbf_relationship_type.observed_end_points.add()
        pbf_end_point.origin_entity_type = "Person"
        pbf_end_point.destination_entity_type = "Vehicle"
        pbf_search_index = pbf_graph_data_model.search_indexes.add()
        pbf_search_index.name = "searchIdx"
        pbf_analyzer = pbf_search_index.analyzers.add()
        pbf_analyzer.name = "en"
        pbf_search_index.search_properties["Person"].property_names.append("name")
        pbf_graph_data_model.identifier_info.mapping_info.uniform_property.identifier_property_name = (
            "globalid"
        )
        pbf_graph_data_model.identifier_info.generation_info.uuid_method_hint = DataModelTypes_pb2.UUIDMethodHint.UUID_ESRI  # type: ignore
        pbf_source_type_value_behavior = (
            pbf_graph_data_model.provenance_source_type_values.value_behavior_array.add()
        )
        pbf_source_type_value_behavior.behavior = "String"
        pbf_source_type_value_behavior.value = "abc123"
        pbf_rel_rule = pbf_graph_data_model.constraint_rules.add()
        pbf_rel_rule.name = "rule"
        pbf_rel_rule.relationship_exclusion_rule.origin_entity_types.set.value.append(
            "Person"
        )
        pbf_rule = pbf_graph_data_model.constraint_rules.add()
        pbf_rule.name = "notRelRule"
        pbf_rule.role = DataModelTypes_pb2.ConstraintRuleRole.RelationshipExclusion_HasDocument  # type: ignore
        response_content: bytes = pbf_graph_data_model.SerializeToString()
        return TestHelpers.construct_response(status_code=200, content=response_content)
