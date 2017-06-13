"""
This resource is a container for all the KMZ files created on the
server.s
"""
from __future__ import absolute_import
from __future__ import print_function
from .._common import BaseServer

########################################################################
class KML(BaseServer):
    """
       This resource is a container for all the KMZ files created on the
       server.
    """
    _con = None
    _url = None
    _json_dict = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
               initialize - boolean - if true, information loaded at object
                creation
        """
        super(KML, self).__init__(connection=connection,
                                  url=url)
        self._con = connection
        self._url = url
        if initialize:
            self._init(connection)
    #----------------------------------------------------------------------
    def create_KMZ(self, kmz_as_json):
        """
           Creates a KMZ file from json.
           See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Create_Kmz/02r3000001tm000000/
           for more information.
        """
        url = self._url + "/createKmz"
        params = {
            "f" : "json",
            "kml" : kmz_as_json
        }
        return self._con.post(path=url,
                              postdata=params)
