import datetime as _dt
from arcgis.auth.tools import LazyLoader

try:
    from arcgis.graph import _arcgisknowledge as _kgparser

    HAS_KG = True
except ImportError as e:
    HAS_KG = False
_gis = LazyLoader("arcgis.gis")
_isd = LazyLoader("arcgis._impl.common._isd")
from typing import List
import platform


class KnowledgeGraph:
    _gis = None
    _url = None
    _properties = None

    def __init__(self, url: str, *, gis=None):
        """initializer"""
        self._url = url
        self._gis = gis

    def _validate_import(self):
        p = platform.platform().lower().find("windows") > -1
        if HAS_KG == False and p:
            raise ImportError("Missing _arcgisknowledge library.")
        elif HAS_KG == False and p == False:
            raise ImportError("KnowledgeGraph is currently only supported on Windows.")

    @classmethod
    def fromitem(cls, item):
        """Returns the KnowledgeGraph Service from an Item"""
        if item.type != "Knowledge Graph":
            raise ValueError(
                "Invalid item type, please provide a 'Knowledge Graph' item."
            )
        return cls(url=item.url, gis=item._gis)

    @property
    def properties(self) -> _isd.InsensitiveDict:
        """returns the properties of the service"""
        if self._properties is None:
            resp = self._gis._con.get(self._url, {"f": "json"})
            self._properties = _isd.InsensitiveDict(resp)
        return self._properties

    def search(self, query: str, category: str = "both") -> List[dict]:
        """
        Allows for the searching of the properties of both entities and
        relationships in the graph using a full-text index.

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        query               Required String. Allows you to return the entities and
                            relationships in a graph, as well as the properties of those
                            entities and relationships, by providing an open cypher query.
        ----------------    ---------------------------------------------------------------
        category            Optional String.  The category is the location of the full
                            text search.  This can be isolated to either the `entities` or
                            the `relationships`.  The default is to look in `both`.

                            The allowed values are: both, entities, relationships
        ================    ===============================================================

        :return: List[dict]

        """
        url = self._url + "/graph/search"
        cat_lu = {
            "both": _kgparser.esriNamedTypeCategory.both,
            "relationships": _kgparser.esriNamedTypeCategory.relationship,
            "entities": _kgparser.esriNamedTypeCategory.entity,
        }
        assert str(category).lower() in cat_lu.keys()
        r_enc = _kgparser.GraphSearchRequestEncoder()
        r_enc.search_query = query
        r_enc.return_geometry = True
        r_enc.max_num_results = self.properties["maxRecordCount"]
        r_enc.type_category_filter = cat_lu[category.lower()]
        r_enc.encode()
        assert r_enc.get_encoding_result().error.error_code == 0
        query_dec = _kgparser.GraphQueryDecoder()
        count = 0

        session = self._gis._con._session
        response = session.post(
            url=url,
            params={"f": "pbf"},
            data=r_enc.get_encoding_result().byte_buffer,
            stream=True,
            headers={"Content-Type": "application/octet-stream"},
        )
        rows = []
        query_dec = _kgparser.GraphQueryDecoder()
        for chunk in response.iter_content(8192):
            did_push = query_dec.push_buffer(chunk)
            count = 0
            while query_dec.next_row():
                rows.extend(query_dec.get_current_row())
                count += 1
        return rows

    def query(self, query: str) -> List[dict]:
        """
        Queries the Knowledge Graph

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        query               Required String. Allows you to return the entities and
                            relationships in a graph, as well as the properties of those
                            entities and relationships, by providing an open cypher query.
        ================    ===============================================================

        :return: List[dict]

        """
        self._validate_import()
        url = f"{self._url}/graph/query"
        params = {
            "f": "pbf",
            "token": self._gis._con.token,
            "openCypherQuery": query,
        }

        data = self._gis._con.get(url, params, return_raw_response=True, try_json=False)
        buffer_dm = data.content
        gqd = _kgparser.GraphQueryDecoder()
        gqd.push_buffer(buffer_dm)
        rows = []
        while gqd.next_row():
            rows.append(gqd.get_current_row())
        return rows

    @property
    def datamodel(self) -> dict:
        """
        Returns the datamodel for the Knowledge Graph Service
        """
        self._validate_import()
        url = f"{self._url}/dataModel/queryDataModel"
        params = {
            "f": "pbf",
        }
        r_dm = self._gis._con.get(
            url, params=params, return_raw_response=True, try_json=False
        )
        buffer_dm = r_dm.content
        dm = _kgparser.decode_data_model_from_protocol_buffer(buffer_dm)
        return dm.to_value_object()
