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
            i = 0
            while gqd.get_value(i):
                v = gqd.get_value(i)
                rows.append(_kgparser.to_value_object(v))
                i += 1
                del v
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
