"""
   Front end controls to the server.
"""
from .catalog import Server
from .admin.administration import SiteManager
########################################################################
class ServerManager(object):
    """
    Gains Access to the ArcGIS REST API
    """
    _url = None
    _con =  None
    _adminUrl = None
    _server = None
    _sm = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url=None, tokenurl=None,
                 username=None, password=None,
                 key_file=None, cert_file=None,
                 expiration=60, all_ssl=True,
                 referer=None, proxy_host=None,
                 proxy_port=None, portal_connection=None,
                 initialize=True):
        """Constructor"""
        self._server = Server(url, tokenurl,
                              username, password,
                              key_file, cert_file,
                              expiration, all_ssl,
                              referer, proxy_host,
                              proxy_port, portal_connection,
                              initialize)
        self._sm = self._server.site_manager
        self._info = self._server.info
    #----------------------------------------------------------------------
    @property
    def users(self):
        """returns operations to work with users"""
        return self._sm.security
    #----------------------------------------------------------------------
    @property
    def datastore(self):
        return self._sm.data
    #----------------------------------------------------------------------
    @property
    def usage(self):
        """"""
        return self._sm.usagereports
    #----------------------------------------------------------------------
    @property
    def content(self):
        """"""
        return self._server
    #----------------------------------------------------------------------
    @property
    def config(self):
        """"""
        return
    #----------------------------------------------------------------------
    @property
    def logs(self):
        """"""
        return self._sm.logs
    #----------------------------------------------------------------------
    @property
    def kml(self):
        """"""
        return self._sm.kml
    #----------------------------------------------------------------------
    @property
    def info(self):
        """"""
        return self._sm.info









