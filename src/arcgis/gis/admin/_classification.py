from __future__ import annotations
from arcgis.auth.tools import LazyLoader
from arcgis.auth import EsriSession
from arcgis.gis import GIS

from typing import Any
import requests

json = LazyLoader("json")

__all__ = ["ClassificationManager"]


class ClassificationManager:
    url: str
    gis: GIS
    session: EsriSession
    _properties: dict | None = None

    # ---------------------------------------------------------------------
    def __init__(self, url: str, gis: GIS) -> None:
        if url.endswith("/classification") == False:
            url += "/classification"
        self.url = url
        self.gis = gis
        self.session = gis.session

    # ---------------------------------------------------------------------
    @property
    def properties(self) -> dict[str, Any]:
        if self._properties is None:
            params = {
                "f": "json",
            }
            self._properties = self.session.get(self.url, params=params).json()
        return self._properties

    # ---------------------------------------------------------------------
    @property
    def schema(self) -> dict | None:
        url: str = f"{self.url}/classificationSchema"
        params: dict = {
            "f": "json",
        }
        resp: requests.Response = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    # ---------------------------------------------------------------------
    def delete(self) -> bool:
        """Deletes the current schema defined on the organization"""
        if self.schema == {
            "classificationSchema": []
        }:  #  no schema set, so nothing to clear out
            return True
        url: str = f"{self.url}/deleteClassificationSchema"
        params: dict = {
            "f": "json",
        }
        resp: requests.Response = self.session.post(url, data=params)
        resp.raise_for_status()
        data: dict = resp.json()
        if "error" in data:
            raise Exception(data)
        self._properties = None
        return data.get("success", False)

    # ---------------------------------------------------------------------
    def add(self, schema_file: str) -> bool:
        """
        Adds a schema definition from a file to the current enterprise
        """
        url: str = f"{self.url}/assignClassificationSchema"
        params: dict = {
            "f": "json",
        }

        with open(schema_file, "rb") as f:
            resp: requests.Response = self.session.post(
                url,
                data=params,
                files={"classificationSchemaFile": f},
            )

            resp.raise_for_status()
            data: dict = resp.json()
            if "error" in data:
                raise Exception(data)
            self._properties = None
            return data.get("success", False)
        self._properties = None
        return False

    # ---------------------------------------------------------------------
    def validate_schema_file(self, schema_file: str) -> bool:
        """Validates the schema file to be set on the enterprise system."""
        url: str = f"{self.url}/validateClassificationSchema"
        params: dict = {
            "f": "json",
        }
        data: dict = {}
        with open(schema_file, "rb") as f:
            resp: requests.Response = self.session.post(
                url,
                data=params,
                files={"classificationSchemaFile": f},
            )

            resp.raise_for_status()
            data: dict = resp.json()
        if "error" in data:
            raise Exception(data)
        return data.get("success", False)

    # ---------------------------------------------------------------------
    def validate_item_schema(
        self,
        classification: dict[str, Any] | None = None,
        classification_schema: str | None = None,
    ) -> bool:
        """
        Validates a classification that would be given to an Item

        =======================    =============================================================
        **Parameter**               **Description**
        -----------------------    -------------------------------------------------------------
        classification             Optional dict. The classification paylaod for a given item as a dictionary.
        -----------------------    -------------------------------------------------------------
        classification_schema      Optional str. The classification paylaod represented as a file.
        =======================    =============================================================

        """
        url: str = f"{self.url}/validateClassification"
        params = {
            "f": "json",
        }
        files: dict = {}
        if classification is None and classification_schema is None:
            raise ValueError(
                "A `classification` string or `classification_schema` file path must be provided."
            )
        if isinstance(classification, dict):
            classification: str = json.dumps(classification)
            files["classificationValue"] = (None, classification)
        elif isinstance(classification, str):
            files["classificationValue"] = (None, classification)
        else:
            files["classificationValue"] = (None, "")

        if classification_schema:
            with open(classification_schema, "rb") as f:
                files["classificationValueFile"] = f
                resp: requests.Response = self.session.post(
                    url, data=params, files=files
                )

        else:
            resp: requests.Response = self.session.post(
                url,
                params=params,
                files=files,
            )
        resp.raise_for_status()
        data: dict = resp.json()
        if "error" in data:
            raise Exception(data)
        return data.get("success", False)
