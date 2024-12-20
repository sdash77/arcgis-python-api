from typing import Optional, Any
from pydantic import BaseModel, model_serializer, model_validator
from pydantic.alias_generators import to_camel

from arcgis.graph.data_model_types import EndPoint


class Error(BaseModel):
    error_code: int
    error_message: str


class UpdateSearchIndexResponse(BaseModel):
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class SyncDataModelResult(BaseModel):
    type_name: str
    error: Optional[Error] = None
    warnings: list[Error] = []

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None and not self.warnings:
            return {"typeName": self.type_name}
        elif not self.warnings:
            return {
                "typeName": self.type_name,
                "error": self.error,
            }
        elif self.error is None:
            return {
                "typeName": self.type_name,
                "warnings": self.warnings,
            }
        return {
            "typeName": self.type_name,
            "error": self.error,
            "warnings": self.warnings,
        }

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class SyncDataModelResponse(BaseModel):
    error: Optional[Error] = None
    warnings: list[Error] = []
    named_type_sync_results: list[SyncDataModelResult] = []

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if (
            self.error is None
            and not self.warnings
            and not self.named_type_sync_results
        ):
            return {}
        elif not self.warnings and not self.named_type_sync_results:
            return {"error": self.error}
        elif self.error is None and not self.named_type_sync_results:
            return {"warnings": self.warnings}
        elif self.error is None and not self.warnings:
            return {"named_type_sync_results": self.named_type_sync_results}
        elif not self.named_type_sync_results:
            return {
                "error": self.error,
                "warnings": self.warnings,
            }
        elif not self.warnings:
            return {
                "error": self.error,
                "named_type_sync_results": self.named_type_sync_results,
            }
        elif self.error is None:
            return {
                "warnings": self.warnings,
                "named_type_sync_results": self.named_type_sync_results,
            }
        return {
            "error": self.error,
            "warnings": self.warnings,
            "named_type_sync_results": self.named_type_sync_results,
        }


class NamedObjectTypeAddResult(BaseModel):
    name: str
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class NamedObjectTypeAddsResponse(BaseModel):
    error: Optional[Error] = None
    entity_add_results: list[NamedObjectTypeAddResult]
    relationship_add_results: list[NamedObjectTypeAddResult]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {
                "entityAddResults": self.entity_add_results,
                "relationshipAddResults": self.relationship_add_results,
            }
        return {
            "error": self.error,
            "entityAddResults": self.entity_add_results,
            "relationshipAddResults": self.relationship_add_results,
        }

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class NamedObjectTypeUpdateResponse(BaseModel):
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class NamedObjectTypeDeleteResponse(BaseModel):
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class PropertyAddResult(BaseModel):
    name: str
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class PropertyAddsResponse(BaseModel):
    error: Optional[Error] = None
    property_add_results: list[PropertyAddResult]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"propertyAddResults": self.property_add_results}
        return {
            "error": self.error,
            "propertyAddResults": self.property_add_results,
        }

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class PropertyUpdateResponse(BaseModel):
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class PropertyDeleteResponse(BaseModel):
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


def _to_camel_plus_extra_space(snake: str) -> str:
    return to_camel(snake=snake).strip() + " "


class IndexAddResult(BaseModel):
    name: str
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class IndexAddsResponse(BaseModel):
    error: Optional[Error] = None
    index_add_results: list[IndexAddResult]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"indexAddResults ": self.index_add_results}
        return {
            "error": self.error,
            "indexAddResults ": self.index_add_results,
        }

    class Config:
        alias_generator = _to_camel_plus_extra_space
        populate_by_name = True


class IndexDeleteResult(BaseModel):
    name: str
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class IndexDeletesResponse(BaseModel):
    error: Optional[Error] = None
    index_delete_results: list[IndexDeleteResult]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"indexDeleteResults ": self.index_delete_results}
        return {
            "error": self.error,
            "indexDeleteResults ": self.index_delete_results,
        }

    class Config:
        alias_generator = _to_camel_plus_extra_space
        populate_by_name = True


class ConstraintRuleAddResult(BaseModel):
    name: str
    error: Optional[Error] = None
    warnings: list[Error]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {
                "name": self.name,
                "warnings": self.warnings,
            }
        return {
            "name": self.name,
            "error": self.error,
            "warnings": self.warnings,
        }


class ConstraintRuleAddsResponse(BaseModel):
    error: Optional[Error] = None
    constraint_rule_add_results: list[ConstraintRuleAddResult]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"constraint_rule_add_results": self.constraint_rule_add_results}
        return {
            "error": self.error,
            "constraint_rule_add_results": self.constraint_rule_add_results,
        }


class ConstraintRuleUpdateResult(BaseModel):
    name: str
    error: Optional[Error] = None
    warnings: list[Error]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {
                "name": self.name,
                "warnings": self.warnings,
            }
        return {
            "name": self.name,
            "error": self.error,
            "warnings": self.warnings,
        }


class ConstraintRuleUpdatesResponse(BaseModel):
    error: Optional[Error] = None
    constraint_rule_update_results: list[ConstraintRuleUpdateResult]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {
                "constraint_rule_update_results": self.constraint_rule_update_results
            }
        return {
            "error": self.error,
            "constraint_rule_update_results": self.constraint_rule_update_results,
        }


class ConstraintRuleDeleteResult(BaseModel):
    name: str
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class ConstraintRuleDeletesResponse(BaseModel):
    error: Optional[Error] = None
    constraint_rule_delete_results: list[ConstraintRuleDeleteResult]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {
                "constraint_rule_delete_results": self.constraint_rule_delete_results
            }
        return {
            "error": self.error,
            "constraint_rule_delete_results": self.constraint_rule_delete_results,
        }


class EditResult(BaseModel):
    id: Any
    error: Optional[Error] = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"id": self.id}
        return {
            "error": self.error,
            "id": self.id,
        }


class EditResults(BaseModel):
    add_results: list[EditResult] = []
    update_results: list[EditResult] = []
    delete_results: list[EditResult] = []

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class CascadingRelationshipDelete(BaseModel):
    id: Any
    origin_id: Any
    destination_id: Any

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "originId": self.origin_id,
            "destId": self.destination_id,
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "destId" in data:
                data["destinationId"] = data.pop("destId")
        return data

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class RelationshipTypeSchemaChanges(BaseModel):
    new_end_points: list[EndPoint]


class CascadingProvenanceDelete(BaseModel):
    id: Any


class ApplyEditsResponse(BaseModel):
    error: Optional[Error] = None
    edits_result: dict[str, EditResults]
    cascaded_deletes: dict[str, list[CascadingRelationshipDelete]]
    relationship_schema_changes: dict[str, RelationshipTypeSchemaChanges]
    cascaded_provenance_deletes: list[CascadingProvenanceDelete] = []

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {
                "editsResult": self.edits_result,
                "cascadedDeletes": self.cascaded_deletes,
                "relationshipSchemaChanges": self.relationship_schema_changes,
                "cascadedProvenanceDeletes": self.cascaded_provenance_deletes,
            }
        return {
            "error": self.error,
            "editsResult": self.edits_result,
            "cascadedDeletes": self.cascaded_deletes,
            "relationshipSchemaChanges": self.relationship_schema_changes,
            "cascadedProvenanceDeletes": self.cascaded_provenance_deletes,
        }

    class Config:
        alias_generator = to_camel
        populate_by_name = True
