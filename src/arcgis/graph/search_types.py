from typing import Literal, Any
from pydantic import BaseModel, model_validator, model_serializer


esriNamedTypeCategory = Literal[
    "unspecified",
    "both",
    "both_entity_relationship",
    "relationships",
    "entities",
    "meta_entity_provenance",
]


class SearchAnalyzer(BaseModel):
    name: str


class SearchIndexProperties(BaseModel):
    property_names: list[str]


class SearchIndex(BaseModel):
    name: str
    supported_category: esriNamedTypeCategory
    analyzers: list[SearchAnalyzer]
    search_properties: dict[str, SearchIndexProperties]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        supported_category: str = "UNSPECIFIED"
        match self.supported_category:
            case "entities":
                supported_category = "Entity"
            case "relationships":
                supported_category = "Relationship"
            case "both":
                supported_category = "Both"
            case "both_entity_relationship":
                supported_category = "Both"
            case "meta_entity_provenance":
                supported_category = "MetaEntityProvenance"
            case _:
                pass
        return {
            "name": self.name,
            "supported_category": supported_category,
            "analyzers": [
                analyzer.model_dump(by_alias=True) for analyzer in self.analyzers
            ],
            "search_properties": {
                key: value.model_dump() for key, value in self.search_properties.items()
            },
        }

    @model_validator(mode="before")  # type: ignore
    @classmethod
    def validate_model(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "supported_category" in data:
                match data["supported_category"]:
                    case "UNSPECIFIED":
                        data["supported_category"] = "unspecified"
                    case "Entity":
                        data["supported_category"] = "entities"
                    case "Relationship":
                        data["supported_category"] = "relationships"
                    case "Both":
                        data["supported_category"] = "both_entity_relationship"
                    case "MetaEntityProvenance":
                        data["supported_category"] = "meta_entity_provenance"
                    case _:
                        pass
        return data
