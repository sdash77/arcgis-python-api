from arcgis.gis import GIS
from arcgis import env as _env
from arcgis._impl.common._isd import InsensitiveDict
from functools import lru_cache
class OGCFeatureService:
    """
    Represents the Hosted OGC Feature Server
    """
    _gis = None
    _url = None
    _properties = None
    
    def __init__(self, url, gis=None):
        """Constructor"""
        assert str(url).lower().endswith("ogcfeatureserver")
        if gis is None:            
            gis = _env.active_gis or GIS()
        self._gis = gis
        self._url = url
        
    @property
    def properties(self):
        """returns the service properties"""
        params = {'f' : 'json'}
        try:
            res = self._gis._con.get(self._url, params)
            return InsensitiveDict(res)
        except:
            res = self._gis._con.post(self._url, params)
            return InsensitiveDict(res)
    
    
    @property
    @lru_cache(maxsize=100)
    def conformance(self) -> dict:
        """
        Provides the API conformance with the OGC standard.
        
        :returns: dict
        """
        url = f"{self._url}/conformance" 
        params = {'f' : 'json'}
        return self._con.get(url, params)
    
    @property
    def collections(self):
        """
        returns the OGC feature service layers within the collection
        
        :returns: List[OGCCollection]
        """
        ...
    
class OGCCollection:
    """
    """
    _gis = None
    _url = None
    _properties = None
    def __init__(self, url, gis=None):
        """Constructor"""
        assert str(url).lower().endswith("ogcfeatureserver")
        if gis is None:            
            gis = _env.active_gis or GIS()
        self._gis = gis
        self._url = url
        
    @property
    def properties(self):
        """returns the service properties"""
        params = {'f' : 'json'}
        try:
            res = self._gis._con.get(self._url, params)
            return InsensitiveDict(res)
        except:
            res = self._gis._con.post(self._url, params)
            return InsensitiveDict(res)        
        
    def query(self, **kwargs):
        """"""
        ...
    
    def get(self, feature_id:int) -> dict:
        """
        Gets an individual feature on the service
        """
        ...
    

if __name__ == "__main__":
    url = "https://servicesdev.arcgis.com/01ClFLufh9nZafWR/ArcGIS/rest/services/TRAN_Alaska_State_Shape/OGCFeatureServer"
    ogc = OGCFeatureService(url=url)
    print(ogc.properties)
    #https://servicesdev.arcgis.com/01ClFLufh9nZafWR/ArcGIS/rest/services/TRAN_Alaska_State_Shape/OGCFeatureServer/api?f=html#/Features/getFeature
    # query
    # 