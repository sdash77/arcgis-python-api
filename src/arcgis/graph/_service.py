import sys

sys.path.insert(0, r"\\burebista\crdata\Knowledge\client-core\Python")
import datetime as _dt
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

    def _gv_2_geom(self, g, sr=None):
        from arcgis._impl.common._utils import chunks

        geom = None
        if sr is None:
            sr = {'wkid': 4326}
        if isinstance(g, _kgparser.GeometryValue):
            geom = {'spatialReference': sr}
            if 'point' in g.geometry_type.name.lower():
                geom['x'] = g.coords[0]
                geom['y'] = g.coords[1]
                if g.has_m and g.has_z:
                    geom['z'] = g.coords[2]
                    geom['m'] = g.coords[3]
                elif g.has_m == False and g.has_z:
                    geom['z'] = g.coords[2]
                elif g.has_m and g.has_z == False:
                    geom['m'] = g.coords[2]
            elif 'polygon' in g.geometry_type.name.lower():
                geom['hasM'] = g.has_m
                geom['hasZ'] = g.has_z
                geom['rings'] = list(
                    chunks(g.coords, n=2 + int(g.has_m) + int(g.has_z))
                )
            elif 'polyline' in g.geometry_type.name.lower():
                geom['hasM'] = g.has_m
                geom['hasZ'] = g.has_z
                geom['paths'] = list(
                    chunks(g.coords, n=2 + int(g.has_m) + int(g.has_z))
                )
            elif 'multipoint' in g.geometry_type.name.lower():
                geom['hasM'] = g.has_m
                geom['hasZ'] = g.has_z
                geom['points'] = list(
                    chunks(g.coords, n=2 + int(g.has_m) + int(g.has_z))
                )
        return geom

    def query(self, query: str) -> dict:
        """
        Queries the Knowledge Graph
        """
        self._validate_import()
        url = f"{self._url}/graph/query"
        params = {
            "f": "pbf",
            "token": self._gis._con.token,
            "openCypherQuery": query,
        }
        stream = False
        if stream:
            data = self._gis._con.post(
                url, params, return_raw_response=True, try_json=False
            )
        else:
            data = self._gis._con.get(
                url, params, return_raw_response=True, try_json=False
            )
        buffer_dm = data.content
        gqd = _kgparser.GraphQueryDecoder()
        gqd.push_buffer(buffer_dm)
        rows = []
        while gqd.next_row():
            i = 0
            while gqd.get_value(i):
                v = gqd.get_value(i)
                row = dict(v.key_value_pairs)
                if 'geometry' in row:
                    row['geometry'] = self._gv_2_geom(row.get('geometry', None))
                rows.append(row)
                i += 1
                del v
        return rows

    def _o_2_dict(self, obj):
        import datetime as _dt

        d = {}
        keys = [
            class_key
            for class_key in obj.__dir__()
            if callable(getattr(obj, class_key)) == False
            and not class_key in ['__doc__', '__module__']
            and class_key.find("__") == -1
            and class_key.find("_") == -1
        ]
        list_keys = []
        for key in keys:
            o = getattr(obj, key, None)
            if isinstance(o, (tuple, list, set)):
                d[key] = o
                list_keys.append(o)
            else:
                d[key] = o
        return d

    def _obj_2_dict(self, obj) -> dict:
        """ """

        import datetime as _dt

        common_dtypes = (str, int, _dt.datetime, float)  # dict, list, tuple
        data = {}
        keys = [key for key in dir(obj) if key.find("__") == -1 or key.find("_") == -1]

        for k in keys:
            data[k] = getattr(obj, k)
            if isinstance(data[k], (tuple, list, set)):
                data[k] = [self._obj_2_dict(v) for v in data[k]]
            elif isinstance(data[k], common_dtypes):
                return data[k]
            elif isinstance(data[k], dict):
                data[k] = {k: self._obj_2_dict(v) for k, v in data[k].items()}
            else:
                data[k] = self._obj_2_dict(data[k])
        return data

        # if (
        # isinstance(
        # obj,
        # (_kgparser.esriFieldType, _kgparser.DataModel),
        # )
        # or obj.__name__.lower().find("esriFieldType") > -1
        # ):
        # keys = ["name", "value"]
        # for key in keys:
        # d = getattr(obj, key)
        # if isinstance(d, common_dtypes) and callable(d) == False:
        # data[key] = getattr(obj, key)
        # elif isinstance(d, (list, tuple, set)):
        ## data[key] = d  # issue here
        # res = []
        # for o in d:
        # res.append(self._obj_2_dict(o))
        # data[key] = res
        # elif isinstance(d, dict):
        # d[key] = {}
        # for k, v in d.items():
        # d[key][k] = self._obj_2_dict(v)

        # elif callable(d) == False and isinstance(d, common_dtypes) == False:
        # data[key] = self._obj_2_dict(d)
        # return data

    @property
    def datamodel(self) -> dict:
        """
        Returns the datamodel for the Knowledge Graph Service
        """
        import datetime as _dt

        result = {}
        common_dtypes = (str, int, _dt.datetime, float)  # dict, list, tuple
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
        keys = [key for key in dir(dm) if key.find("__") == -1 or key.find("_") == -1]
        for key in keys:
            v = getattr(dm, key, None)
            if isinstance(v, common_dtypes):
                result[key] = v
            elif isinstance(
                v, (_kgparser.SpatialReference, _kgparser.DocumentEntityTypeInfo)
            ):
                result[key] = self._obj_2_dict(v)
            elif key == 'entity_types':
                result[key] = self._obj_2_dict(v)
            elif callable(v):
                print(f"passing {key}, callable")
            elif key == 'relationship_types':
                result[key] = [self._o_2_dict(rt) for rt in v]
            else:
                print(v)

        print()
        # result = self._obj_2_dict(dm)

        return result


if __name__ == "__main__":
    gis = _gis.GIS("https://dev0018783.esri.com/portal/", "admin", "esri.agp")
    print("Logged in as: " + gis.properties.user.username)

    token = gis._con.token

    url = r"https://dev0018783.esri.com/server/rest/services/Hosted/KGS_PanamaPapers/KnowledgeGraphServer"
    kg = KnowledgeGraph(url, gis=gis)
    ##
    ##  Need to test with polygon, polygline and multipoint, but it works.
    # kg.query(query="MATCH (n) RETURN n LIMIT 10")
    dm = kg.datamodel
    print("stop")
