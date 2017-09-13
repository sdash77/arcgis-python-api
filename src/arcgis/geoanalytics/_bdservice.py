from ..gis import _GISResource

class BigDataCatalog(_GISResource):
    """
    Big data catalog services are a new service type introduced in ArcGIS
    Enterprise 10.5. Web clients can browse this service to find
    information about datasets registered as a big data file share and
    use it as input to GeoAnalytics tasks.

    The response returns an array containing each dataset's name, type, and
    geometryType, when applicable. It also returns the dataStoreID
    property, which corresponds to the id of big data file share item.
    """
    _con = None
    _portal = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis):
        super(BigDataCatalog, self).__init__(url=url,
                                             gis=gis)
        self._url = url
        if hasattr(gis, '_con'):
            self._con = gis._con
        elif hasattr(gis, 'portal'):
            self._con = gis.portal.con
        elif hasattr(gis,'get'):
            self._con = gis
        else:
            raise Exception("A GIS connection is required")
        self._hydrate()
    #----------------------------------------------------------------------
    def list(self):
        """returns a list children associated with the Big Data Catalog service"""
        return [child['name'] for child in self.properties.children]
    #----------------------------------------------------------------------
    def get(self, name):
        """returns information about a specific child item in the big data catalog"""
        k = {child.lower() : child for child in self.list()}
        if name.lower() in k.keys():
            name = k[name.lower()]
            params = {'f': 'json'}
            url = "%s/%s" % (self._url, name)
            return self._con.post(path=url, postdata=params)
        else:
            raise ValueError("Invalid child name: %s" % name)
        return None
    #----------------------------------------------------------------------
    @property
    def manifest(self):
        """
        Manifest resource provides the schema for a big data file share. A
        manifest will be auto-generated for each big data file share that
        is registered with server.
        """
        return self._con.get(path="%s/manifest" % self._url,
                             params={'f':'json'})
