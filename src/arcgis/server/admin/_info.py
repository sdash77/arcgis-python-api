from __future__ import absolute_import
from __future__ import print_function
import json
from .._common import BaseServer

########################################################################
class Info(BaseServer):
    """
       A read-only resource that returns meta information about the server.
    """
    _con = None
    _json_dict = None
    _url = None
    _securityHandler = None
    _timezone = None
    _loggedInUser = None
    _loggedInUserPrivilege = None
    _currentBuild = None
    _currentVersion = None
    _fullVersion = None
    _proxy_port = None
    _proxy_url = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
               initialize - loads the object's properties on runtime
        """
        super(Info, self).__init__(connection=connection,
                                      url=url)
        self._con = connection
        self._url = url
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    def available_time_zones(self):
        """
           Returns an enumeration of all the time zones of which the server
           is aware. This is used by the GIS service publishing tools
        """
        url = self._url + "/getAvailableTimeZones"
        params = {
            "f" : "json"
        }
        return self._con.get(path=url, params=params)
