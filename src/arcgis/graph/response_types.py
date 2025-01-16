from typing import Optional, Any
from pydantic import BaseModel, model_serializer, model_validator, Field
from pydantic.alias_generators import to_camel

from arcgis.graph.data_model_types import EndPoint


class Error(BaseModel):
    error_code: int = Field(..., description="The error code.")
    error_message: str = Field(..., description="The error message.")


class UpdateSearchIndexResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class SyncDataModelResult(BaseModel):
    type_name: str = Field(..., description="The type name that was synced.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    warnings: list[Error] = Field(
        default=[], description="The list of warnings returned for the named type."
    )

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
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    warnings: list[Error] = Field(
        default=[], description="The list of warnings returned for the operation."
    )
    named_type_sync_results: list[SyncDataModelResult] = Field(
        default=[], description="The list of results for each named type."
    )

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
    name: str = Field(..., description="The type name that was added.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class NamedObjectTypeAddsResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    entity_add_results: list[NamedObjectTypeAddResult] = Field(
        ..., description="The list of results for added entity types."
    )
    relationship_add_results: list[NamedObjectTypeAddResult] = Field(
        ..., description="The list of results for added relationship types."
    )

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
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class NamedObjectTypeDeleteResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class PropertyAddResult(BaseModel):
    name: str = Field(..., description="The name of the property that was added.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class PropertyAddsResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    property_add_results: list[PropertyAddResult] = Field(
        ..., description="The list of results for the added properties."
    )

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
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


class PropertyDeleteResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {}
        return {"error": self.error}


def _to_camel_plus_extra_space(snake: str) -> str:
    return to_camel(snake=snake).strip() + " "


class IndexAddResult(BaseModel):
    name: str = Field(..., description="The name of the added index.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class IndexAddsResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    index_add_results: list[IndexAddResult] = Field(
        ..., description="The list of results for the added indexes."
    )

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
    name: str = Field(..., description="The name of the deleted index.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class IndexDeletesResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    index_delete_results: list[IndexDeleteResult] = Field(
        ..., description="The list of results for the deleted indexes."
    )

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
    name: str = Field(..., description="The name of the added constraint rule.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    warnings: list[Error] = Field(
        ..., description="The list of warnings from adding the constraint rule."
    )

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
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    constraint_rule_add_results: list[ConstraintRuleAddResult] = Field(
        ..., description="The list of results for the added constraint rules."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"constraint_rule_add_results": self.constraint_rule_add_results}
        return {
            "error": self.error,
            "constraint_rule_add_results": self.constraint_rule_add_results,
        }


class ConstraintRuleUpdateResult(BaseModel):
    name: str = Field(..., description="The name of the updated constraint rule.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    warnings: list[Error] = Field(
        ..., description="The list of warnings for the updated constraint rules."
    )

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
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    constraint_rule_update_results: list[ConstraintRuleUpdateResult] = Field(
        ..., description="The list of results from updating the constraint rule."
    )

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
    name: str = Field(..., description="The name of the deleted constraint rule.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"name": self.name}
        return {
            "name": self.name,
            "error": self.error,
        }


class ConstraintRuleDeletesResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    constraint_rule_delete_results: list[ConstraintRuleDeleteResult] = Field(
        ..., description="The list of results from deleting the constraint rules."
    )

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
    id: Any = Field(..., description="The ID of the edited entity or relationship.")
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        if self.error is None:
            return {"id": self.id}
        return {
            "error": self.error,
            "id": self.id,
        }


class EditResults(BaseModel):
    add_results: list[EditResult] = Field(
        default=[], description="The results from adding entities and relationships."
    )
    update_results: list[EditResult] = Field(
        default=[], description="The results from updating entities and relationships."
    )
    delete_results: list[EditResult] = Field(
        default=[], description="The results from deleting entities and relationships."
    )

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class CascadingRelationshipDelete(BaseModel):
    id: Any = Field(
        ..., description="The ID of the relationship that was cascade deleted."
    )
    origin_id: Any = Field(
        ...,
        description="The origin entity ID for the relationship that was cascade deleted.",
    )
    destination_id: Any = Field(
        ...,
        description="The destination entity ID for the relationship that was cascade deleted.",
    )

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
        if not isinstance(data, dict):
            return data
        if "destId" in data:
            data["destinationId"] = data.pop("destId")
        return data

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class RelationshipTypeSchemaChanges(BaseModel):
    new_end_points: list[EndPoint] = Field(
        ..., description="The new end points in the database as a result of the edits."
    )


class CascadingProvenanceDelete(BaseModel):
    id: Any = Field(
        ..., description="The ID of the Provenance entity that was cascade deleted."
    )


class ApplyEditsResponse(BaseModel):
    error: Optional[Error] = Field(
        default=None, description="The error, or None if the operation was successful."
    )
    edits_result: dict[str, EditResults] = Field(
        ..., description="The edit results, grouped by type name."
    )
    cascaded_deletes: dict[str, list[CascadingRelationshipDelete]] = Field(
        ..., description="The cascade deleted relationships, grouped by type name."
    )
    relationship_schema_changes: dict[str, RelationshipTypeSchemaChanges] = Field(
        ..., description="The relationship type schema changes, grouped by type name."
    )
    cascaded_provenance_deletes: list[CascadingProvenanceDelete] = Field(
        default=[], description="The cascade deleted Provenance entities."
    )

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
