from ..connection import _ArcGISConnection
from ...gis import GIS
from ._base import BasePortalAdmin

class PortalAdminManager(BasePortalAdmin):
    """
    This is the root resource for administering your portal. Starting from
    this root, all of the portal's environment is organized into a
    hierarchy of resources and operations. A version number is returned as
    a part of this resource. After installation, the portal can be
    configured using the Create Site operation. Once initialized, the
    portal environment is available through System and Security resources.


    """
    _logs = None
    _federation = None
    _system = None
    _security = None
    _url = None
    _gis = None
    def __init__(self, url, gis=None, **kwargs):
        """initializer"""
        super(PortalAdminManager, self).__init__(url=url,
                                                 gis=gis,
                                                 **kwargs)
        initialize = kwargs.pop("initialize", False)
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self._init(self._gis)
    #----------------------------------------------------------------------
    #def __str__(self):
    #    return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    #def __repr__(self):
    #    return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def machines(self):
        """
        This resource lists all the portal machines in a site. Each portal
        machine has a status that indicates whether the machine is ready
        to accept requests.
        """
        params = {'f' : 'json'}
        url = "%s/%s" % (self._url, "machines")
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def security(self):
        """
        accesses the controls for the security of a local portal site
        """

        if self._security is None:
            from ._security import Security
            url = "%s/security" % self._url
            self._security = Security(url=url, gis=self._gis)
        return self._security
    #----------------------------------------------------------------------
    @property
    def logs(self):
        """
        returns a class to work with the portal logs
        """
        if self._logs is None:
            from ._logs import Logs
            url = "%s/logs" % self._url
            self._logs = Logs(url=url, gis=self._gis)
        return self._logs
    #----------------------------------------------------------------------
    @property
    def federation(self):
        """
        provides access into the federation settings of a server.
        """
        if self._federation is None:
            from ._federation import Federation
            url = "%s/federation" % self._url
            self._federation = Federation(url=url, gis=self._gis)
        return self._federation
    #----------------------------------------------------------------------
    @property
    def system(self):
        """
        The importSite operation lets you restore your site from a backup
        site configuration file that you created using the exportSite
        operation. It imports the site configuration file into the
        currently running portal site.
        The importSite operation will replace all site configurations with
        information included in the backup site configuration file. See the
        exportSite operation documentation for details on what the backup
        file includes. The importSite operation also updates the portal
        content index.
        """
        if self._system is None:
            from ._system import System
            url = "%s/system" % self._url
            self._system = System(url=url, gis=self._gis)
        return self._system
    #----------------------------------------------------------------------
    def machine_status(self, machine_name):
        """
        This operation checks whether a portal machine is ready to receive
        requests.
        """
        url = "%s/machines/status/%s" % (self._url, machine_name)
        params = {"f": "json"}
        res = self._con.get(path=url,
                            params=params)
        if 'status' in res:
            return res['status'] == 'success'
        return False
    #----------------------------------------------------------------------
    def create(self,
               username,
               password,
               full_name,
               email,
               content_store,
               description="",
               question_idx=None,
               question_ans=None):
        """
        The create site operation initializes and configures Portal for
        ArcGIS for use. It must be the first operation invoked after
        installation. Creating a new site involves:
          - Creating the initial administrator account
          - Creating a new database administrator account (which is same as
            the initial administrator account)
          - Creating token shared keys
          - Registering directories
        This operation is time consuming, as the database is initialized
        and populated with default templates and content. If the database
        directory is not empty, this operation attempts to migrate the
        database to the current version while keeping its data intact. At
        the end of this operation, the web server that hosts the API is
        restarted.

        Parameters:
         :username: initial admin account name
         :password: password for initial admin account
         :full_name: full name of the admin account
         :email: account email address
         :content_store: JSON string including the path to the location of
          the site's content.
         :description: optional descript for the account
         :question_idx: index of the secret question to retrieve a
          forgotten password
         :question_ans: answer to the secret question
        """
        url = "%s/createNewSite" % self._url
        params = {"f": "json",
                  "username" : username,
                  "password" : password,
                  "fullName" : full_name,
                  "email" : email,
                  "description" : description,
                  "contentStore" : content_store}
        if question_idx and question_ans:
            params['securityQuestionIdx'] = question_idx
            params['securityQuestionAns'] = question_ans
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def export_site(self, location):
        """
        This operation exports the portal site configuration to a location
        you specify. The exported file includes the following information:
          Content directory - the content directory contains the data
           associated with every item in the portal
          Database dump file - a plain-text file that contains the SQL
           commands required to reconstruct the portal database
          Configuration store connection file - a JSON file that contains
           the database connection information

        Parameters:
         :location: path to the folder accessible to the portal where the
          exported site configuration will be written.
        """
        url = "%s/exportSite" % self._url
        params = {'f' : 'json',
                  'location' : location}
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def import_site(self, location):
        """
        The importSite operation lets you restore your site from a backup
        site configuration file that you created using the exportSite
        operation. It imports the site configuration file into the
        currently running portal site.
        The importSite operation will replace all site configurations with
        information included in the backup site configuration file. See the
        export_site operation documentation for details on what the backup
        file includes. The importSite operation also updates the portal
        content index.

        Parameters:
         :location: A file path to an exported configuration.

        """
        url = "%s/importSite" % self._url
        if url.find(":7443") == -1:
            raise ValueError(
                "You must access portal not using the web adaptor (port 7443)"
            )
        params = {'f' : 'json',
                      'location' : location}
        res =  self._con.post(path=url,
                              postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return False
    #----------------------------------------------------------------------
    def join(self, admin_url, username, password):
        """
        The joinSite operation connects a portal machine to an existing
        site. You must provide an account with administrative privileges to
        the site for the operation to be successful.
        When an attempt is made to join a site, the site validates the
        administrative credentials, then returns connection information
        about its configuration store back to the portal machine. The portal
        machine then uses the connection information to work with the
        configuration store.
        If this is the first portal machine in your site, use the Create
        Site operation instead.
        The joinSite operation:
         - Registers a machine to an existing site (active machine)
         - Creates a snapshot of the database of the active machine
         - Updates the token shared key
         - Updates Web Adaptor configurations
        Sets up replication to keep the database of both machines in sync
        The operation is time-consuming as the database is configured on
        the machine and all configurations are applied from the active
        machine. After the operation is complete, the web server that hosts
        the API will be restarted.

        Parameters:
         :admin_url: The admin URL of the existing portal site to which a
          machine will be joined
         :username: username for the initial administrator account of the
          existing portal site.
         :password:  password for the initial administrator account of the
          existing portal site.

        """
        url = "%s/joinSite" % self._url
        params = {'f' : 'json',
                  'machineAdminUrl' : admin_url,
                  'username' : username,
                  'password' : password}
        return self._con.post(path=url,
                                  postdata=params)
    #----------------------------------------------------------------------
    def unregister_machine(self, machine_name):
        """
        This operation unregisters a portal machine from a portal site. The
        operation can only performed when there are two machines
        participating in a portal site.

        Parameters:
         :machine_name: name of the machine to be unregistered
        """
        params = {"f" : "json",
                  "machineName" : machine_name}
        url = "%s/machines/unregister" % self._url
        return self._con.post(path=url, postdata=params)
