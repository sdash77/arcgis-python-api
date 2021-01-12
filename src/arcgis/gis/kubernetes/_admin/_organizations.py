import json
from collections import OrderedDict
from urllib.request import HTTPError
from arcgis.gis._impl._con import Connection
from arcgis.gis import GIS
from arcgis._impl.common._mixins import PropertyMap
###########################################################################
class KubeOrgSecurity(object):
    """
    Allows the for the management of the security of the settings.
    """
    _con = None
    _gis = None
    _url = None
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url:str,
                 gis:"GIS"
                 ) -> "KubeOrgSecurity":
        self._url = url
        self._gis = gis
        self._con = gis._con
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self) -> dict:
        """
        returns the properties for the Organization

        :return: dict
        """
        if self._properties is None:
            self._properties = self._con.get(self._url, {'f' : 'json'})
        return self._properties
###########################################################################
class KubeOrganization():
    """
    A single organization within your deployment, allowing you to manage
    and update it's licensing and security information, as well as manage
    it's federated servers.
    """
    _con = None
    _gis = None
    _url = None
    _properties = None
    _security = None
    _federation = None
    _license = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis:"GIS", **kwargs):
        """class initializer"""
        self._gis = gis
        self._url = url
        self._con = gis._con
        self._properties = None
        self._json_dict = None
    #----------------------------------------------------------------------
    def _init(self):
        """loads the properties into the class"""
        params = {"f":"json"}
        try:
            result = self._con.get(path=self._url,
                                    params=params)
            if isinstance(result, dict):
                self._json_dict = result
                self._properties = PropertyMap(result)
            else:
                self._json_dict = {}
                self._properties = PropertyMap({})
        except HTTPError as err:
            raise RuntimeError(err)
        except:
            self._json_dict = {}
            self._properties = PropertyMap({})
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the object properties
        """
        if self._properties is None:
            self._init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def url(self):
        """gets/sets the service url"""
        return self._url
    #----------------------------------------------------------------------
    def _refresh(self):
        """reloads all the properties of a given service"""
        self._init()
    #----------------------------------------------------------------------
    @property
    def security(self):
        if self._security is None:
            self._security = KubeOrgSecurity(url=f"{self._url}/security",
                                             gis=self._gis)
        return self._security
    #----------------------------------------------------------------------
    @property
    def license(self) -> "KubeOrgLicense":
        """
        The Licenses resource returns high-level licensing details.

        :return: KubeOrgLicense
        """
        if self._license is None:
            url = url=f"{self._url}/license"
            self._license = KubeOrgLicense(url, self._gis)
        return self._license
    #----------------------------------------------------------------------
    @property
    def federation(self) -> "KubeOrgFederations":
        """
        Returns manager to work with server federation.

        :returns: KubeOrgFederations
        """
        if self._federation is None:
            url = self._url + "/federation"
            self._federation = KubeOrgFederations(url, self._gis)
        return self._federation
###########################################################################
class KubeOrgFederations():
    """
    Provides access to the federation of ArcGIS Server and the ability to
    federate them with the organization.
    """
    _con = None
    _gis = None
    _url = None
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url:str,
                 gis:"GIS"
                 ) -> "KuberOrgFederations":
        self._url = url
        self._gis = gis
        self._con = gis._con
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self) -> dict:
        """
        returns the properties for the Kubernetes License Organization

        :return: dict
        """
        if self._properties is None:
            self._properties = self._con.get(self._url, {'f' : 'json'})
        return self._properties


###########################################################################
class KubeOrgLicense():
    """
    The Licenses resource returns high-level licensing details, such as the
    total number of registered members that can be added, the current
    number of members in the organization, the Enterprise portal version,
    and license manager information. This API endpoint also provides access
    to various operations that allow you to manage your portal licenses for
    your organization.

    """
    _con = None
    _gis = None
    _url = None
    _properties = None
    # ---------------------------------------------------------------------
    def __init__(self, url:str, gis:"GIS") -> "KubeOrgLicense":
        """
        initializer
        """
        self._url = url
        self._gis = gis
        self._con = gis._con
        self._properties = None
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self) -> dict:
        """
        returns the properties for the Kubernetes License Organization

        :return: dict
        """
        if self._properties is None:
            self._properties = self._con.get(self._url, {'f' : 'json'})
        return self._properties
    #----------------------------------------------------------------------
    def update_license_manager(self, config:dict) -> bool:
        """
        This operation allows you to change the license server connection
        information for your portal, as well as register a backup license
        manager for high availability. After changing the license manager
        properties, Portal for ArcGIS automatically restarts to register
        changes and set up connections with the backup license manager.

        ===========================     ====================================================================
        **Argument**                    **Description**
        ---------------------------     --------------------------------------------------------------------
        config                          Required Dict. The JSON representation of the license server
                                        connection information.
        ===========================     ====================================================================

        :return: Boolean

        """

        url = self._url + "/updateLicenseManager"
        params = {
            "f" : "json",
            "licenseManagerInfo" : json.dumps(config)
        }
        res = self._con.post(url, params)
        if "status" in res:
            return res["status"] == "success"
        return res
    #----------------------------------------------------------------------
    def import_license(self, license_file:str):
        """
        Applies a new license file to a specific organization, which contains the portal's user type and add-on licenses.

        ===========================     ====================================================================
        **Argument**                    **Description**
        ---------------------------     --------------------------------------------------------------------
        license_file                    Required String. The kubernetes license file.
        ===========================     ====================================================================

        :return: Boolean

        """
        url = self._url + "/importLicense"
        file = {'file' : file}
        res = self._con.post(url, params, files=file)
        if "status" in res:
            return res["status"] == "success"
        return res
    #----------------------------------------------------------------------
    def validate(self, file, list_ut=False):
        """
        The `validate` operation is used to validate an input license file.
        Only valid license files can be imported into the Enterprise
        portal. If the provided file is valid, the operation will return
        user type, app bundle, and app information from the license file.
        If the file is invalid, the operation will fail and return an error
        message.


        ===========================     ====================================================================
        **Argument**                    **Description**
        ---------------------------     --------------------------------------------------------------------
        file                            Required String. The kubernetes license file.
        ---------------------------     --------------------------------------------------------------------
        list_ut                         Optional Boolean. Returns a list of user types that are compatible
                                        with the Administrator role. This identifies the user type(s) that
                                        can be assigned to the Initial Administrator Account when creating
                                        a portal.
        ===========================     ====================================================================

        :returns: Dict

        """
        file = {'file' : file}
        params = {'f' : "json",
                  'listAdministratorUserTypes' : list_ut}
        url = "%s/validateLicense" % self._url
        res = self._con.post(url, params, files=file)
        return res
###########################################################################
class KubeOrganizations():
    """
    Allows for the management of organizations within the ArcGIS Enterprise
    on Kubernetes deployment.
    """
    _con = None
    _gis = None
    _url = None
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self,
                url:str,
                gis:"GIS",
                initialize:bool=True
                ) -> "KuberOrganizations":
        """
        Kubernetes Organization
        """
        self._url = url
        self._gis = gis
        self._con = gis._con

        if initialize:
            self._init(gis)
    #----------------------------------------------------------------------
    def _init(self, connection=None):
        """loads the properties into the class"""

        params = {"f":"json"}
        try:
            result = self._con.get(self._url, {'f' :'json'})
            if isinstance(result, dict):
                self._json_dict = result
                self._properties = PropertyMap(result)
            else:
                self._json_dict = {}
                self._properties = PropertyMap({})
        except HTTPError as err:
            raise RuntimeError(err)
        except:
            self._json_dict = {}
            self._properties = PropertyMap({})
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the object properties
        """
        if self._properties is None:
            self._init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def url(self):
        """gets/sets the service url"""
        return self._url
    #----------------------------------------------------------------------
    def _refresh(self):
        """reloads all the properties of a given service"""
        self._init()
    #----------------------------------------------------------------------
    @property
    def orgs(self) -> tuple:
        """
        Returns a list of registerd organizations with the Kubernetes deployment

        :returns: tuple
        """
        return tuple([KubeOrganization(url=f"{self._url}/{org}",
                                 gis=self._gis)\
                for org in self.properties['organizations']])
