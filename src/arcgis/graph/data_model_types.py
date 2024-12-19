from typing import Literal, Any, Annotated, Union
from enum import Enum
from pydantic import BaseModel, model_serializer, model_validator, Discriminator
from pydantic.alias_generators import to_camel

from arcgis.graph.search_types import SearchIndex


esriGraphNamedObjectRole = Literal[
    "esriGraphNamedObjectRegular",
    "esriGraphNamedObjectProvenance",
    "esriGraphNamedObjectDocument",
]


esriGraphPropertyRole = Literal[
    "esriGraphPropertyUNSPECIFIED",
    "esriGraphPropertyRegular",
    "esriGraphPropertyDocumentName",
    "esriGraphPropertyDocumentTitle",
    "esriGraphPropertyDocumentUrl",
    "esriGraphPropertyDocumentText",
    "esriGraphPropertyDocumentKeywords",
    "esriGraphPropertyDocumentContentType",
    "esriGraphPropertyDocumentMetadata",
    "esriGraphPropertyDocumentFileExtension",
    "esriGraphPropertyProvenanceInstanceId",
    "esriGraphPropertyProvenanceSourceType",
    "esriGraphPropertyProvenanceSourceName",
    "esriGraphPropertyProvenanceSource",
    "esriGraphPropertyProvenanceComment",
    "esriGraphPropertyProvenanceTypeName",
    "esriGraphPropertyProvenancePropertyName",
]


esriFieldType = Literal[
    "esriFieldTypeSmallInteger",
    "esriFieldTypeInteger",
    "esriFieldTypeSingle",
    "esriFieldTypeDouble",
    "esriFieldTypeString",
    "esriFieldTypeDate",
    "esriFieldTypeDateOnly",
    "esriFieldTypeTimeOnly",
    "esriFieldTypeTimestampOffset",
    "esriFieldTypeOID",
    "esriFieldTypeGeometry",
    "esriFieldTypeBlob",
    "esriFieldTypeRaster",
    "esriFieldTypeGUID",
    "esriFieldTypeGlobalID",
    "esriFieldTypeXML",
    "esriFieldTypeBigInteger",
]


esriGeometryType = Literal[
    "esriGeometryPoint",
    "esriGeometryMultipoint",
    "esriGeometryPolyline",
    "esriGeometryPolygon",
    "esriGeometryEnvelope",
]


class GraphProperty(BaseModel):
    name: str
    alias: str = ""
    domain: str = ""
    field_type: esriFieldType
    geometry_type: esriGeometryType = "esriGeometryPoint"
    has_z: bool = False
    has_m: bool = False
    default_value: Any = None
    nullable: bool = True
    visible: bool = True
    editable: bool = True
    required: bool = False
    is_system_maintained: bool = False
    role: esriGraphPropertyRole = "esriGraphPropertyRegular"

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class GraphPropertyMask(BaseModel):
    update_name: bool = False
    update_alias: bool = False
    update_field_type: bool = False
    update_geometry_type: bool = False
    update_has_m: bool = False
    update_has_z: bool = False
    update_default_value: bool = False
    update_nullable: bool = False
    update_editable: bool = False
    update_visible: bool = False
    update_required: bool = False
    update_domain: bool = False


class FieldIndex(BaseModel):
    name: str
    is_ascending: bool
    is_unique: bool
    fields: list[str]

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class NamedObjectType(BaseModel):
    name: str
    alias: str = ""
    role: esriGraphNamedObjectRole = "esriGraphNamedObjectRegular"
    strict: bool = False
    properties: dict[str, GraphProperty] = {}
    field_indexes: dict[str, FieldIndex] = {}


class EntityType(NamedObjectType): ...


class EndPoint(BaseModel):
    origin_entity_type: str
    destination_entity_type: str

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "origin_entity_type": self.origin_entity_type,
            "dest_entity_type": self.destination_entity_type,
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "dest_entity_type" in data:
                data["destination_entity_type"] = data.pop("dest_entity_type")
        return data


class RelationshipType(NamedObjectType):
    observed_end_points: list[EndPoint] = []

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "alias": self.alias,
            "role": self.role,
            "strict": self.strict,
            "properties": self.properties,
            "field_indexes": self.field_indexes,
            "end_points": self.observed_end_points,
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "end_points" in data:
                data["observed_end_points"] = data.pop("end_points")
        return data


class NamedObjectTypeMask(BaseModel):
    update_name: bool = False
    update_alias: bool = False
    update_role: bool = False
    update_strict: bool = False


esriGraphConstraintRuleRole = Literal[
    "esriGraphConstraintRuleRoleUNSPECIFIED",
    "esriGraphConstraintRuleRoleRegular",
    "esriGraphConstraintRuleRoleHasDocument",
    "esriGraphConstraintRuleRoleNoProvenanceOrigin",
    "esriGraphConstraintRuleRoleNoProvenanceDestination",
]


class ConstraintRule(BaseModel):
    name: str
    alias: str = ""
    disabled: bool = False
    role: esriGraphConstraintRuleRole = "esriGraphConstraintRuleRoleRegular"
    type: Literal["esriGraphConstraintRuleTypeUNSPECIFIED"] = (
        "esriGraphConstraintRuleTypeUNSPECIFIED"
    )


class TypeOfSet(Enum):
    SET = 0
    SET_COMPLEMENT = 1


class SetOfNamedTypes(BaseModel):
    set: list[str] = []
    set_complement: list[str] = []

    def type_of_set(self) -> TypeOfSet:
        if self.set and not self.set_complement:
            return TypeOfSet.SET
        else:
            return TypeOfSet.SET_COMPLEMENT

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        match self.type_of_set():
            case TypeOfSet.SET:
                return {
                    "set": self.set,
                }
            case TypeOfSet.SET_COMPLEMENT:
                return {
                    "set_complement": self.set_complement,
                }
            case _:
                return {}


class RelationshipExclusionRule(ConstraintRule):
    type: Literal["esriGraphRelationshipExclusionRuleType"] = "esriGraphRelationshipExclusionRuleType"  # type: ignore
    origin_entity_types: SetOfNamedTypes
    relationship_types: SetOfNamedTypes
    destination_entity_types: SetOfNamedTypes

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "alias": self.alias,
            "disabled": self.disabled,
            "role": self.role,
            "type": self.type,
            "relationship_exclusion_rule": {
                "origin_entity_types": self.origin_entity_types.model_dump(),
                "relationship_types": self.relationship_types.model_dump(),
                "destination_entity_types": self.destination_entity_types.model_dump(),
            },
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "relationship_exclusion_rule" in data:
                data["origin_entity_types"] = data["relationship_exclusion_rule"][
                    "origin_entity_types"
                ]
                data["relationship_types"] = data["relationship_exclusion_rule"][
                    "relationship_types"
                ]
                data["destination_entity_types"] = data["relationship_exclusion_rule"][
                    "destination_entity_types"
                ]
                data.pop("relationship_exclusion_rule")
        return data


class ConstraintRuleMask(BaseModel):
    update_name: bool = False
    update_alias: bool = False
    update_disabled: bool = False


class ConstraintRuleUpdate(BaseModel):
    rule_name: str
    mask: ConstraintRuleMask
    constraint_rule: ConstraintRule


class UpdateSetOfNamedTypes(BaseModel):
    add_named_types: list[str]
    remove_named_types: list[str]


class RelationshipExclusionRuleUpdate(ConstraintRuleUpdate):
    update_origin_entity_types: UpdateSetOfNamedTypes
    update_relationship_types: UpdateSetOfNamedTypes
    update_destination_entity_types: UpdateSetOfNamedTypes

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "mask": self.mask,
            "constraint_rule": self.constraint_rule.model_dump(),
            "relationship_exclusion_rule_update": {
                "update_origin_entity_types": self.update_origin_entity_types.model_dump(),
                "update_relationship_types": self.update_relationship_types.model_dump(),
                "update_destination_entity_types": self.update_destination_entity_types.model_dump(),
            },
        }


class IdentifierMappingInfo(BaseModel):
    identifier_info_type: Literal["esriIdentifierInfoTypeUNSPECIFIED"] = (
        "esriIdentifierInfoTypeUNSPECIFIED"
    )


class DatabaseNativeIdentifier(IdentifierMappingInfo):
    identifier_info_type: Literal["esriIdentifierInfoTypeDatabaseNative"] = "esriIdentifierInfoTypeDatabaseNative"  # type: ignore

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if isinstance(self, UniformPropertyIdentifier):
            return self.ser_model()
        return {
            "identifier_info_type": self.identifier_info_type,
            "native_identifier": "",
        }


class UniformPropertyIdentifier(IdentifierMappingInfo):
    identifier_info_type: Literal["esriIdentifierInfoTypeUniformProperty"] = "esriIdentifierInfoTypeUniformProperty"  # type: ignore
    identifier_property_name: str

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if isinstance(self, DatabaseNativeIdentifier):
            return self.ser_model()
        return {
            "identifier_info_type": self.identifier_info_type,
            "uniform_property": {
                "identifier_property_name": self.identifier_property_name
            },
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "uniform_property" in data:
                data["identifier_property_name"] = data["uniform_property"][
                    "identifier_property_name"
                ]
                data.pop("uniform_property")
        return data


esriUUIDMethodHint = Literal[
    "esriMethodHintUNSPECIFIED",
    "esriUUIDESRI",
    "esriUUIDRFC4122",
]


class IdentifierGenerationInfo(BaseModel):
    uuid_method_hint: esriUUIDMethodHint


class IdentifierInfo(BaseModel):
    identifier_mapping_info: Annotated[
        Union[
            IdentifierMappingInfo, DatabaseNativeIdentifier, UniformPropertyIdentifier
        ],
        Discriminator(discriminator="identifier_info_type"),
    ]
    identifier_generation_info: IdentifierGenerationInfo

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "identifier_mapping_info" in data:
                if isinstance(data["identifier_mapping_info"], dict):
                    if "native_identifier" in data["identifier_mapping_info"]:
                        data["identifier_mapping_info"] = (
                            DatabaseNativeIdentifier.model_validate(
                                data["identifier_mapping_info"]
                            )
                        )
                    elif "uniform_property" in data["identifier_mapping_info"]:
                        data["identifier_mapping_info"] = (
                            UniformPropertyIdentifier.model_validate(
                                data["identifier_mapping_info"]
                            )
                        )
        return data


class SourceTypeValueBehavior(BaseModel):
    behavior: str
    value: str


class ProvenanceSourceTypeValues(BaseModel):
    value_behavior_array: list[SourceTypeValueBehavior] = []


class GraphDataModel(BaseModel):
    data_model_timestamp: int
    spatial_reference: dict[str, Any]
    entity_types: dict[str, EntityType] = {}
    relationship_types: dict[str, RelationshipType] = {}
    meta_entity_types: dict[str, EntityType] = {}
    strict: bool
    objectid_property: str
    globalid_property: str
    arcgis_managed: bool
    identifier_info: IdentifierInfo
    search_indexes: dict[str, SearchIndex] = {}
    provenance_source_type_values: ProvenanceSourceTypeValues = (
        ProvenanceSourceTypeValues()
    )
    constraint_rules: dict[
        str,
        Annotated[
            Union[ConstraintRule, RelationshipExclusionRule],
            Discriminator(discriminator="type"),
        ],
    ] = {}

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "constraint_rules" in data:
                if isinstance(data["constraint_rules"], dict):
                    for value in data["constraint_rules"].values():
                        if "relationship_exclusion_rule" in value:
                            value = RelationshipExclusionRule.model_validate(value)
        return data
