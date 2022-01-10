from arcgis.auth.tools import LazyLoader

try:
    import _arcgisknowledge as _kgparser

    HAS_KG = True
except ImportError as e:
    HAS_KG = False
_gis = LazyLoader("arcgis.gis")
_isd = LazyLoader("arcgis._impl.common._isd")


class KnowledgeGraph:
    _gis = None
    _url = None
    _properties = None

    def __init__(self, url: str, *, gis=None):
        """initializer"""
        self._url = url
        self._gis = gis

    def _validate_import(self):
        if HAS_KG == False:
            raise ImportError("Missing _arcgisknowledge library.")

    @property
    def properties(self) -> _isd.InsensitiveDict:
        """returns the properties of the service"""
        if self._properties is None:
            resp = self._gis._con.get(self._url, {"f": "json"})
            self._properties = _isd.InsensitiveDict(resp)
        return self._properties

    def query(self, query: str) -> dict:
        """
        Queries the Knowledge Graph
        """
        self._validate_import()
        url = f"{self._url}'/graph/query"
        params = {
            'f': 'pbf',
            'token': self._gis._con.token,
            'openCypherQuery': query,
        }
        if stream:
            return self._gis._con.post(url, params)
        else:
            return self._gis._con.get(url, params)
        return

    def _obj_2_dict(self, obj) -> dict:
        """ """
        import datetime as _dt

        data = {}
        keys = [key for key in dir(obj) if key.find("__") == -1 or key.find("_") == -1]
        common_dtypes = (str, int, _dt.datetime, float)  # dict, list, tuple
        if (
            isinstance(
                obj,
                (_kgparser.esriFieldType,),
            )
            or obj.__name__.lower().find("esriFieldType") > -1
        ):
            keys = ['name', 'value']
        for key in keys:
            d = getattr(obj, key)
            if isinstance(d, common_dtypes) and callable(d) == False:
                data[key] = getattr(obj, key)
            elif isinstance(d, (list, tuple, set)):
                # data[key] = d  # issue here
                res = []
                for o in d:
                    res.append(self._obj_2_dict(o))
                data[key] = res
            elif isinstance(d, dict):
                d[key] = {}
                for k, v in d.items():
                    d[key][k] = self._obj_2_dict(v)

            elif callable(d) == False and isinstance(d, common_dtypes) == False:
                data[key] = self._obj_2_dict(d)
        return data

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
        result = self._obj_2_dict(dm)

        return result


if __name__ == "__main__":
    gis = _gis.GIS('https://dev0018783.esri.com/portal/', 'admin', 'esri.agp')
    print("Logged in as: " + gis.properties.user.username)

    token = gis._con.token

    url = r'https://dev0018783.esri.com/server/rest/services/Hosted/KGS_PanamaPapers/KnowledgeGraphServer'
    kg = KnowledgeGraph(url, gis=gis)
    print(kg.datamodel)
    print('stop')
