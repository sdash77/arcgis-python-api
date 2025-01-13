from typing import Optional, Any, Union
from pydantic import BaseModel, model_serializer, model_validator
from pydantic.alias_generators import to_camel

from arcgis.geometry import Geometry


def _client_core_to_python_value(client_core_value: Any) -> Any:
    if isinstance(client_core_value, list):
        transformed_list: list[Any] = []
        for val in client_core_value:
            transformed_list.append(_client_core_to_python_value(client_core_value=val))
        return transformed_list
    if isinstance(client_core_value, dict):
        if "_objectType" not in client_core_value:
            return None
        match client_core_value["_objectType"]:
            case "geometry":
                client_core_value.pop("_objectType")
                return Geometry(client_core_value)
            case "object":
                return GraphObject.model_validate(client_core_value)
            case "entity":
                return Entity.model_validate(client_core_value)
            case "relationship":
                return Relationship.model_validate(client_core_value)
            case "path":
                return Path.model_validate(client_core_value)
            case _:
                return None
    return client_core_value


def _python_to_client_core_value(python_value: Any) -> Any:
    if isinstance(python_value, Geometry):
        copy_dict: dict[str, Any] = python_value.copy()
        copy_dict["_objectType"] = "geometry"
        return copy_dict
    if isinstance(python_value, BaseModel):
        return python_value.model_dump(by_alias=True)
    if isinstance(python_value, list):
        return [_python_to_client_core_value(val) for val in python_value]
    return python_value


class GraphObject(BaseModel):
    properties: dict[str, Any] = {}

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "_objectType": "object",
            "_properties": {
                key: _python_to_client_core_value(value)
                for key, value in self.properties.items()
            },
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "_objectType" not in data:
            return data
        assert data["_objectType"] == "object"
        data.pop("_objectType")
        assert isinstance(data["_properties"], dict)
        for value in data["_properties"].values():
            value = _client_core_to_python_value(client_core_value=value)
        data["properties"] = data.pop("_properties")
        return data


class NamedObject(GraphObject):
    type_name: str
    id: Optional[Any] = None


class Entity(NamedObject):
    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        model_dict: dict[str, Any] = {
            "_objectType": "entity",
            "_typeName": self.type_name,
            "_properties": {
                key: _python_to_client_core_value(value)
                for key, value in self.properties.items()
            },
        }
        if self.id is not None:
            model_dict["_id"] = self.id
        return model_dict

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "_objectType" not in data:
            return data
        assert data["_objectType"] == "entity"
        data.pop("_objectType")
        data["type_name"] = data.pop("_typeName")
        assert isinstance(data["_properties"], dict)
        for value in data["_properties"].values():
            value = _client_core_to_python_value(client_core_value=value)
        data["properties"] = data.pop("_properties")
        if "_id" in data:
            data["id"] = data.pop("_id")
        return data


class Relationship(NamedObject):
    origin_entity_id: Any
    destination_entity_id: Any

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        model_dict: dict[str, Any] = {
            "_objectType": "relationship",
            "_typeName": self.type_name,
            "_properties": {
                key: _python_to_client_core_value(value)
                for key, value in self.properties.items()
            },
            "_originEntityId": self.origin_entity_id,
            "_destinationEntityId": self.destination_entity_id,
        }
        if self.id is not None:
            model_dict["_id"] = self.id
        return model_dict

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "_objectType" not in data:
            return data
        assert data["_objectType"] == "relationship"
        data.pop("_objectType")
        data["type_name"] = data.pop("_typeName")
        assert isinstance(data["_properties"], dict)
        for value in data["_properties"].values():
            value = _client_core_to_python_value(client_core_value=value)
        data["properties"] = data.pop("_properties")
        data["origin_entity_id"] = data.pop("_originEntityId")
        data["destination_entity_id"] = data.pop("_destinationEntityId")
        if "_id" in data:
            data["id"] = data.pop("_id")
        return data


class Path(BaseModel):
    path: list[Union[Entity, Relationship]]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "_objectType": "path",
            "_path": [named_object.model_dump() for named_object in self.path],
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "_objectType" not in data:
            return data
        assert data["_objectType"] == "path"
        data.pop("_objectType")
        path: Any = data.pop("_path")
        if isinstance(path, list):
            new_path: list[Union[Entity, Relationship]] = []
            for named_object in path:
                if isinstance(named_object, dict):
                    match named_object["_objectType"]:
                        case "entity":
                            new_path.append(Entity.model_validate(named_object))
                        case "relationship":
                            new_path.append(Relationship.model_validate(named_object))
                        case _:
                            raise ValueError(
                                "Path must contain only entities or relationships!"
                            )
                elif isinstance(named_object, Entity) or isinstance(
                    named_object, Relationship
                ):
                    new_path.append(named_object)
                else:
                    raise ValueError(
                        "Path must contain only entities or relationships!"
                    )
            path = new_path
        data["path"] = path
        return data


class NamedObjectDelete(BaseModel):
    type_name: str
    ids: list[Any]


class EntityDelete(NamedObjectDelete):
    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "_objectType": "entity",
            "_typeName": self.type_name,
            "_ids": self.ids,
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "_objectType" not in data:
            return data
        assert data["_objectType"] == "entity"
        data.pop("_objectType")
        data["type_name"] = data.pop("_typeName")
        data["ids"] = data.pop("_ids")
        return data


class RelationshipDelete(NamedObjectDelete):
    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "_objectType": "relationship",
            "_typeName": self.type_name,
            "_ids": self.ids,
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "_objectType" not in data:
            return data
        assert data["_objectType"] == "relationship"
        data.pop("_objectType")
        data["type_name"] = data.pop("_typeName")
        data["ids"] = data.pop("_ids")
        return data


class Transform(BaseModel):
    xy_resolution: float
    x_false_origin: float
    y_false_origin: float
    z_resolution: float
    z_false_origin: float
    m_resolution: float
    m_false_origin: float

    class Config:
        alias_generator = to_camel
        populate_by_name = True
