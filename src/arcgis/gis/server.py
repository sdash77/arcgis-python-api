import ssl
import logging
import arcgis


from .._impl.common._mixins import PropertyMap
from .._impl.connection import _ArcGISConnection
from .._server._common import ServerConnection
from ..gis import GIS
from .._server._view import Catalog
from .._server.admin._logs import Log
_log = logging.getLogger(__name__)

class ServerManager(object):
    _gis = None

    def __init__(self, gis):
        self._gis = gis
        self._portal = gis._portal
        self._server_list = None

    def list(self):
        """gets all servers in a GIS"""
        if self._server_list is not None:
            return self._server_list

        self._server_list = []

        res = self._portal.con.post("portals/self/servers", {"f": "json"})
        servers = res['servers']
        admin_url = None
        for server in servers:
            try:
                admin_url = server['adminUrl']
                self._server_list.append(Server(url=admin_url, gis=self))
            except:
                _log.warn("Could not access the server at " + admin_url)

        return self._server_list
    #----------------------------------------------------------------------


    def federate(self):
        pass
    #----------------------------------------------------------------------

class Server(object):
    """
    An ArcGIS Enterprise server used for hosting services
    """
    _url = None
    _con =  None
    _admin_url = None
    _server = None
    _sm = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url=None,
                 tokenurl=None,
                 username=None,
                 password=None,
                 verify_cert=False,
                 gis=None,
                 **kwargs):
        """An ArcGIS Enterprise server"""
        ### TODO: write doc

        ### TODO: don't set unverified context
        if not verify_cert:
            ssl._create_default_https_context = ssl._create_unverified_context
        key_file = kwargs.pop('key_file', None)
        cert_file = kwargs.pop('cert_file', None)
        expiration = kwargs.pop('expiration', 60)
        all_ssl = kwargs.pop('all_ssl', None)
        is_agol = kwargs.pop('is_agol', False)
        if url.lower().find("arcgis.com") > -1:
            is_agol = True
        if all_ssl is None:
            from six.moves.urllib_parse import urlparse
            all_ssl = urlparse(url).scheme == "https"
        referer = kwargs.pop('referer', None)
        proxy_host = kwargs.pop('proxy_host', None)
        proxy_port= kwargs.pop('proxy_port', None)
        initialize = kwargs.pop('initialize', None)
        self._admin_url = url
        self._server = Catalog(url,
                               tokenurl,
                               username,
                               password,
                               key_file,
                               cert_file,
                               expiration,
                               all_ssl,
                               referer,
                               proxy_host,
                               proxy_port,
                               gis,
                               initialize,
                               is_agol=is_agol)
        self._con = self._server.connection
        if not is_agol:
            self._sm = self._server.site_manager
            # self._info = self._server.info

    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._admin_url)

    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._admin_url)
    # ----------------------------------------------------------------------

    #----------------------------------------------------------------------
    def _publish_sd(self,
                   sd_file,
                   folder=None):
        """
        publishes a service definition file to arcgis server
        """
        if sd_file.lower().endswith('.sd') == False:
            return False
        if self._sm:
            catalog = self.catalog
            isinstance(catalog, Catalog)
            if 'System' in catalog.folders:
                catalog.folder = 'System'
            else:
                return False
            service = catalog.find(service_name="PublishingTools",
                                   folder="System")
            if service is None:
                service = catalog.find(service_name="PublishingToolsEx",
                                       folder="System")
            if service is None:
                return False
            uploads = self._sm.uploads
            status, res = uploads.upload(path=sd_file, description="sd file")
            if status:
                uid = res['item']['itemID']
                res = service.publish_service_definition(in_sdp_id=uid)
                return True
            return False
        else:
            return False

    # #----------------------------------------------------------------------
    # @property
    # def connection(self):
    #     """gets _server the connection object"""
    #     return self._server.connection
    #----------------------------------------------------------------------
    @property
    def users(self):
        """returns operations to work with users"""
        if self._sm:
            from arcgis._server._server import UserManager
            return UserManager(self._sm)
    #----------------------------------------------------------------------
    @property
    def datastores(self):
        """
        This resource provides information about the data holdings of the
        _server. Data items are used by ArcGIS for Desktop and other clients
        to validate data paths referenced by GIS services.
        You can register new data items with the _server by using the
        Register Data Item operation. Use the Find Data Items operation to
        search through the hierarchy of data items.
        A relational data store type represents a database platform that
        has been registered for use on a portal's hosting _server by the
        ArcGIS Server administrator. Each relational data store type
        describes the properties ArcGIS Server requires in order to connect
        to an instance of a database for a particular platform. At least
        one registered relational data store type is required before client
        applications such as Insights for ArcGIS can create Relational
        Database Connection portal items.
        The Compute Ref Count operation counts and lists all references to
        a specific data item. This operation helps you determine if a
        particular data item can be safely deleted or refreshed."""
        if self._sm:
            return self._sm.data
    #----------------------------------------------------------------------
    @property
    def usage(self):
        """
        This resource is a collection of all the usage reports created
        within your site. The Create Usage Report operation lets you define
        a new usage report.
        """
        if self._sm:
            return ReportManager(self._sm)
    #----------------------------------------------------------------------
    @property
    def _catalog(self):
        """
        The content resource is the root node and initial entry point into
        an ArcGIS Server host. This resource represents a catalog of
        folders and services published on the host.
        """
        return self._server
    #----------------------------------------------------------------------
    @property
    def machines(self):
        """
        This resource represents a collection of all the _server machines that
        have been registered with the site. It other words, it represents
        the total computing power of your site. A site will continue to run
        as long as there is one _server machine online.
        For a _server machine to start hosting GIS services, it must be
        grouped (or clustered). When you create a new site, a cluster called
        'default' is created for you.
        The list of _server machines in your site can be dynamic. You can
        register additional _server machines when you need to increase the
        computing power of your site or unregister them if you no longer
        need them.
        """
        if self._sm:
            return MachineManager(self._sm)
        return

    #----------------------------------------------------------------------
    @property
    def _site(self):
        """
        The site maintains all its configuration and meta information on
        disk in a set of files that make up the Configuration Store.
        """
        if self._sm:
            return self._sm
    #----------------------------------------------------------------------
    @property
    def logs(self):
        """
        This allows users to access the  ArcGIS Server's logs and lets
        administrators query and find errors and/or problems related to
        the _server or a service.

        Logs are the records written by the various components of ArcGIS
        Server. You can query the logs and change various log settings.
        **Note**
        ArcGIS Server Only
        """
        if self._sm:
            return LogManager(logs=self._sm.logs)
    #----------------------------------------------------------------------
    @property
    def _kml(self):
        """
        This resource is a container for all the KMZ files created on the
        _server.
        """
        if self._sm:
            return self._sm.kml
    #----------------------------------------------------------------------
    @property
    def _me(self):
        """
        returns the current logged in username
        """
        if self._sm:
            from arcgis._server import User
            res = self.users.search(self._sm.info._loggedInUser)
            if len(res) > 0:
                return res[0]
            else:
                return self._sm.info._loggedInUser
        else:
            return self._con._username
    #----------------------------------------------------------------------
    @property
    def _info(self):
        """

        A read-only resource that returns meta information about the _server
        """
        if self._sm:
            return self._sm.info
    #----------------------------------------------------------------------
    @property
    def system(self):
        """
        provides access to common system configuration settings
        """
        if self._sm:
            from arcgis._server import SystemManager
            return SystemManager(self._sm)

    #----------------------------------------------------------------------
    @property
    def services(self):
        """
        Provides administrator access to the services on ArcGIS Server as a
        ServerManager Object.
        """
        if self._sm:
            return ServiceManager(self)

class ServiceManager(object):
    """
    Helper class for managing services. This class is not created by users directly. An instance of this class,
    called ‘services’, is available as a property of the Server object. Users call methods on this ‘services’ object to
    managing services.
    """
    def __init__(self, server):
        self._svcmgr = server._sm.services
        self._server = server

    @property
    def folders(self):
        """ returns a list of all folders """
        return self._svcmgr.folders

    def list(self, folder='/'):
        """ returns a list of services in the specified folder """
        self._svcmgr.folder = folder
        services =  self._svcmgr.services
        return [Service(None, None, service=svc, svcmgr=self._svcmgr) for svc in services]

    def create_folder(self, folder, description=""):
        """
           Creates a unique folder
           Inputs:
              folder_name - name of folder
              description - describes the folder
           Output:
              result as dictionary
        """
        return self._svcmgr.create_folder(self, folder, description)

    def delete_folder(self, folder):
        """
           Deletes a folder
           Inputs:
              folder - name of folder to remove
           Output:
              bool
        """
        return self._svcmgr.delete_folder(folder)

    def publish_sd(self, sd_file_path, folder=None):
        """
        Publishes a service definition file to the server
        :param sd_file_path: service defition file
        :param folder: optional folder name
        :return: True if published, False otherwise
        """
        return self._server._publish_sd(sd_file_path, folder)

    def create_service(self, service):
        """
        Creates a new GIS service in the folder. A service is created by
        submitting a JSON representation of the service to this operation.

        The JSON representation of a service contains the following four
        sections:
         - Service Description Properties-Common properties that are shared
          by all service types. Typically, they identify a specific service.
         - Service Framework Properties-Properties targeted towards the
          framework that hosts the GIS service. They define the life cycle
          and load balancing of the service.
         - Service Type Properties -Properties targeted towards the core
          service type as seen by the server administrator. Since these
          properties are associated with a server object, they vary across
          the service types. The Service Types section in the Help
          describes the supported properties for each service.
         - Extension Properties-Represent the extensions that are enabled
          on the service. The Extension Types section in the Help describes
          the supported out-of-the-box extensions for each service type.
        Output:
         dictionary status message
        """
        return self._svcmgr.create_service(service)

    def exists(self, folder_name, name=None, service_type=None):
        """
        This operation allows you to check whether a folder or a service
        exists. To test if a folder exists, supply only a folder_name. To
        test if a service exists in a root folder, supply both serviceName
        and service_type with folder_name=None. To test if a service exists
        in a folder, supply all three parameters.

        Inputs:
           folder_name - a folder name
           name - a service name
           service_type - a service type. Allowed values:
                GeometryServer | ImageServer | MapServer | GeocodeServer |
                GeoDataServer | GPServer | GlobeServer | SearchServer
        """
        return self._svcmgr.exists(folder_name, name, service_type)

class Service(object):
    """A GIS service"""
    _service = None
    _svcmgr = None

    def __init__(self, url, server, **kwargs):
        service = kwargs.pop('service', None)
        svcmgr = kwargs.pop('svcmgr', None)
        if service is not None:
            self._service = service
            self._svcmgr = svcmgr
        else:
            self._service = arcgis._server.admin._services.Service(url, server._con)

        self._properties = PropertyMap(self._service._json_dict)

    @classmethod
    def _from_service(cls, service):
        return cls(None, None, service=service)

    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._service.url)

    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._service.url)

    @property
    def properties(self):
        """
        The properties of the Service
        """
        return self._properties

    def start(self):
        """Starts the service"""
        return self._service.start()

    def stop(self):
        """Stops the service"""
        return self._service.stop()

    def delete(self):
        """Deletes the service and return True if successful, False otherwise"""
        return self._service.delete()

    def edit(self, service):
        """
        To edit a service, you need to submit the complete JSON
        representation of the service, which includes the updates to the
        service properties. Editing a service causes the service to be
        restarted with updated properties.
        """
        return self._service.edit(service)

    @property
    def status(self):
        """Returns the status of the service """
        return self._service.status

    @property
    def statistics(self):
        """Returns the stats for the service """
        return self._service.statistics

    def rename(self, new_name):
        """Renames this service to the new name"""
        params = {
            "f": "json",
            "serviceName": self.properties.serviceName,
            "serviceType": self.properties.type,
            "serviceNewName": new_name
        }

        u_url = self._service._url[:self._service._url.rfind('/')] + "/renameService"

        res = self._service._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
########################################################################
class MachineManager(object):
    """
    """
    _machines = None
    _pm = None
    _hydrated = None
    #----------------------------------------------------------------------
    def __init__(self, server, **kwargs):
        """Constructor"""
        hydrate = kwargs.pop('hydrate', False)
        self._sm = server
        self._machines = server.machines
        if hydrate:
            self._hydrate()
            self._hydrated = True
            self._properties = PropertyMap(self._machines._json_dict)
        else:
            self._hydrated = False

    def _hydrate(self):
        self._machines.init()
        self._properties = PropertyMap(self._machines._json_dict)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the machine's properties
        """
        if self._properties is None:
            self._hydrate()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def list(self):
        """
        returns the list of machines in the GIS
        """
        ms = []
        for m in self._machines.machines:
            ms.append(_Machine(machine=m))
        return ms
    #----------------------------------------------------------------------
    def get(self, name):
        """
        gets a single instance of a machine
        """
        return _Machine(
            self._machines.get_machine(
                machine_name=name)
        )
    #----------------------------------------------------------------------
    def register(self, name, admin_url):
        """
           For a server machine to participate in a site, it needs to be
           registered with the site. The server machine must have ArcGIS
           Server software installed and authorized.
           Registering machines this way is a "pull" approach to growing
           the site and is a convenient way when a large number of machines
           need to be added to a site. In contrast, a server machine can
           choose to join a site.
           Inputs:
              name - name of the server machine
              admin_url - URL wher ethe Administrator API is running on the
                         server machine.
                         Example: http://<machineName>:6080/arcgis/admin
           Output:
              JSON message as dictionary
        """
        res = self._machines.register(name, admin_url)
        self._machines.init()
        self._properties = PropertyMap(self._machines._json_dict)
        return res
    #----------------------------------------------------------------------
    def rename(self, name, new_name):
        """
           You must use this operation if one of the registered machines
           has undergone a name change. This operation updates any
           references to the former machine configuration.
           By default, when the server is restarted, it is capable of
           identifying a name change and repairing itself and all its
           references. This operation is a manual call to handle the
           machine name change.
           Input:
              name - The former name of the server machine that is
                            registered with the site.
              new_name - The new name of the server machine.
           Output:
              JSON messages as dictionary
        """
        res = self._machines.rename(name, new_name)
        self._machines.init()
        self._properties = PropertyMap(self._machines._json_dict)
        return res
########################################################################
class _Machine(object):
    """
       A server machine represents a machine on which ArcGIS Server
       software has been installed and licensed. A site is made up one or
       more of such machines that work together to host GIS services and
       data and provide administrative capabilities for the site. Each
       server machine is capable of performing all these tasks and hence a
       site can be thought of as a distributed peer-to-peer network of such
       machines.
       A server machine communicates with its peers over a range of TCP and
       UDP ports that can be configured using the edit operation. For a
       server machine to host GIS services, it needs to be added to a
       cluster. Starting and stopping the server machine enables and
       disables, respectively, its ability to host GIS services.
       The administrative capabilities of the server machine are available
       through the ArcGIS Server Administrator API that can be accessed
       over HTTP(S). For a server machine to participate in a site, it must
       be registered with the site. A machine can participate in only one
       site at a time. To remove a machine permanently from the site, you
       can use the unregister operation.
    """
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self, machine):
        """Constructor"""
        self._machine = machine
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        lists the machine's properties
        """
        if self._properties is None:
            self._machine.init()
            self._properties = PropertyMap(self._machine._json_dict)
        return self._properties
    #----------------------------------------------------------------------
    @property
    def status(self):
        """ returns the state """
        return self._machine.status
    #----------------------------------------------------------------------
    def start(self):
        """ Starts the server machine """
        return self._machine.start()
    #----------------------------------------------------------------------
    def stop(self):
        """ Stops the server machine """
        return self._machine.stop()
    #----------------------------------------------------------------------
    def unregister(self):
        """
           This operation causes the server machine to be deleted from the
           Site.
           The server machine will no longer participate in the site or run
           any of the GIS services. All resources that were acquired by the
           server machine (memory, files, and so forth) will be released.
           Typically, you should only invoke this operation if the machine
           is going to be shut down for extended periods of time or if it
           is being upgraded.
           Once a machine has been unregistered, you can create a new site
           or join an existing site.
        """
        return self._machine.unregister()
    #----------------------------------------------------------------------
    @property
    def ssl_certificates(self):
        """
        This resource lists all the certificates (self-signed and CA-signed)
        created for the server machine. The server securely stores these
        certificates inside a key store within the configuration store.
        Before you enable SSL on your server, you need to generate
        certificates and get them signed by a trusted certificate authority
        (CA). For your convenience, the server is capable of generating
        self-signed certificates that can be used during development or
        staging. However, it is critical that you get CA-signed
        certificates when standing up a production server.
        In order to get a certificate signed by a CA, you need to generate
        a CSR (certificate signing request) and then submit it to your CA.
        The CA will sign your certificate request which can then be
        imported into the server by using the import CA signed certificate
        operation.
        """
        return self._machine.ssl_certificates
    #----------------------------------------------------------------------
    def ssl_certificate(self, certificate):
        """
        A certificate represents a key pair that has been digitally signed
        and acknowledged by a Certifying Authority (CA). It is the most
        fundamental component in enabling SSL on your server.
        The Generate Certificate operation creates a new self-signed
        certificate and adds it to the keystore. In order for browsers and
        other HTTP client applications to trust the SSL connection on the
        server, this certificate must be digitally signed by a CA and then
        imported into the keystore. Even though a self-signed certificate
        can be used to enable SSL, it is recommended that you use a
        self-signed certificates only on staging or development servers.

        Parameters:
         :certificate: name of the certificate to grab information for
        """
        self._machine.ssl_certificate(certificate)
    #----------------------------------------------------------------------
    def export_certificate(self, certificate):
        """
        A certificate represents a key pair that has been digitally signed
        and acknowledged by a Certifying Authority (CA). It is the most
        fundamental component in enabling SSL on your server.
        The Generate Certificate operation creates a new self-signed
        certificate and adds it to the keystore. In order for browsers and
        other HTTP client applications to trust the SSL connection on the
        server, this certificate must be digitally signed by a CA and then
        imported into the keystore. Even though a self-signed certificate
        can be used to enable SSL, it is recommended that you use a
        self-signed certificates only on staging or development servers.

        Parameters:
         :certificate: name of the certificate to grab information for
        """
        return self._machine.export_certificate(certificate)
    #----------------------------------------------------------------------
    def generate_CSR(self, certificate):
        """
        This operation generates a certificate signing request (CSR) for a
        self-signed certificate. A CSR is required by a CA to create a
        digitally signed version of your certificate.
        Parameters:
         :certificate: name of the certificate to grab information for
        """
        return self._machine.generate_CSR(certificate)
    #----------------------------------------------------------------------
    def import_CA_signed_certificate(self,
                                     certificate,
                                     ca_signed_certificate):
        """
        Parameters:
         :certificate: name of the certificate to grab information for
         :ca_signed_certificate: The multi-part POST parameter containing the
          signed certificate file.
        """
        return self._machine.import_CA_signed_certificate(certificate,
                                                          ca_signed_certificate)
    #----------------------------------------------------------------------
    def import_existing_server_certificate(self,
                                           alias,
                                           cert_password,
                                           cert_file):
        """
        This operation imports an existing server certificate, stored in
        the PKCS #12 format, into the keystore.
        If the certificate is a CA signed certificate, you must first
        import the CA Root or Intermediate certificate using the
        importRootCertificate operation.

        Parameters:
         :alias: A unique name for the certificate that easily identifies
          it.
         :cert_password: password to unlock the file containing the
          certificate
         :cert_file: multi-part POST parameter containing the certificate
          file
        """
        return self._machine.import_existing_server_certificate(alias,
                                                                cert_password,
                                                                cert_file)
    #----------------------------------------------------------------------
    def import_root_certificate(self,
                                alias,
                                root_CA_certificate):
        """
        This operation imports a certificate authority (CA)'s root and
        intermediate certificates into the keystore.
        To create a production quality CA-signed certificate, you need to
        add the CA's certificates into the keystore that enables the SSL
        mechanism to trust the CA (and the certificates it has signed).
        While most of the popular CA's certificates are already available
        in the keystore, you can use this operation if you have a custom
        CA or specific intermediate certificates.

        Parameters:
         :alias: name of teh certificate
         :root_CA_certificate:multi-part POST parameter containing the
          certificate file.
        """
        return self._machine.import_root_certificate(
            alias,
            root_CA_certificate)
########################################################################
class LogManager(object):
    """
    Log Mangement of a server

    This resource is accessed through by administrators to check on error
    messages.

    Parameters:
     :param logs: log object
    """
    _url = None
    _con = None
    _json_dict = None
    _operations = None
    _resources = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, logs):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection class
        """
        self._logs = logs
    #----------------------------------------------------------------------
    def count_error_reports(self, machine="*"):
        """ This operation counts the number of error reports (crash
            reports) that have been generated on each machine.
            Input:
               machine - name of the machine in the cluster.  * means all
                         machines.  This is default
            Output:
               dictionary with report count and machine name
        """
        return self._logs.count_error_reports(machine=machine)
    #----------------------------------------------------------------------
    def clean(self):
        """ Deletes all the log files on all server machines in the site.  """
        return self._logs.clean()
    #----------------------------------------------------------------------
    @property
    def settings(self):
        """ returns the current log settings """
        return self._logs.settings
    #----------------------------------------------------------------------
    def edit(self,
             level="WARNING",
             log_dir=None,
             max_age=90,
             max_report_count=10):
        """
           The log settings are for the entire site.
           Inputs:
             level -  Can be one of [OFF, SEVERE, WARNING, INFO, FINE,
                         VERBOSE, DEBUG].
             log_dir - File path to the root of the log directory
             max_age - number of days that a server should save a log
                             file.
             ax_report_count - maximum number of error report files
                                    per machine
        """
        return self._logs.edit_settings(level=level,
                                        log_dir=log_dir,
                                        max_age=max_age,
                                        max_report_count=max_report_count)
    #----------------------------------------------------------------------
    def query(self,
              start_time=None,
              end_time=None,
              since_server_start=False,
              level="WARNING",
              services="*",
              machines="*",
              server="*",
              codes=None,
              process_IDs=None,
              export=False,
              export_type="CSV", #CSV or TAB
              out_path=None):
        """
           The query operation on the logs resource provides a way to
           aggregate, filter, and page through logs across the entire site.
           Inputs:

        """
        return self._logs.query(
            start_time=start_time,
            end_time=end_time,
            since_server_start=since_server_start,
            level=level,
            services=services,
            machines=machines,
            server=server,
            codes=codes,
            process_IDs=process_IDs,
            export=export,
            export_type=export_type,
            out_path=out_path
        )
########################################################################
class ReportManager:
    """
    Manages and modifies the usage reports for ArcGIS Server
    """
    _machines = None
    _pm = None
    _hydrated = None
    _reports = None
    #----------------------------------------------------------------------
    def __init__(self, server, **kwargs):
        """Constructor"""
        hydrate = kwargs.pop('hydrate', False)
        self._sm = server
        self._reports = self._sm.usagereports
        from .._server.admin._usagereports import UsageReports, UsageReport
        isinstance(self._reports, UsageReports)
        if hydrate:
            self._hydrate()
            self._hydrated = True
            self._reports.init()
            self._properties = PropertyMap(self._reports._json_dict)
        else:
            self._hydrated = False
    #----------------------------------------------------------------------
    def _hydrate(self):
        self._properties = None
        self._reports.init()
        self._properties = PropertyMap(self._reports._json_dict)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the machine's properties
        """
        if self._properties is None:
            self._reports.init()
            self._properties = PropertyMap(self._reports._json_dict)
        return self._properties
    #----------------------------------------------------------------------
    @property
    def list(self):
        """returns a list of reports on the server"""
        reports = []
        for report in self._reports.reports:
            reports.append(Report(report))
        return reports
    #----------------------------------------------------------------------
    @property
    def settings(self):
        """
        The usage reports settings are applied to the entire site. A GET
        request returns the current usage reports settings. When usage
        reports are enabled, service usage statistics are collected and
        persisted to a statistics database. When usage reports are
        disabled, the statistics are not collected. The interval
        parameter defines the duration (in minutes) during which the usage
        statistics are sampled or aggregated (in-memory) before being
        written out to the statistics database. Database entries are
        deleted after the interval specified in the max_history parameter (
        in days), unless the max_history parameter is 0, for which the
        statistics are persisted forever.
        """
        return self._reports.usage_settings
    #----------------------------------------------------------------------
    def edit(self,
             interval,
             enabled=True,
             max_history=0):
        """
        The usage reports settings are applied to the entire site. A POST
        request updates the usage reports settings.

        Inputs:
           interval - Defines the duration (in minutes) for which
             the usage statistics are aggregated or sampled, in-memory,
             before being written out to the statistics database.
           enabled - default True - Can be true or false. When usage
             reports are enabled, service usage statistics are collected
             and persisted to a statistics database. When usage reports are
             disabled, the statistics are not collected.
           max_history - default 0 - Represents the number of days after
             which usage statistics are deleted after the statistics
             database. If the max_history parameter is set to 0, the
             statistics are persisted forever.
        """
        return self._reports.edit_settings(interval,
                                           enabled,
                                           max_history)
    #----------------------------------------------------------------------
    def create(self,
               reportname,
               queries,
               metadata=None,
               since="LAST_DAY",
               from_value=None,
               to_value=None,
               aggregation_interval=None):
        """
        Creates a new usage report. A usage report is created by submitting
        a JSON representation of the usage report to this operation.

        Inputs:
           reportname - the unique name of the report
           since - the time duration of the report. The supported values
              are: LAST_DAY, LAST_WEEK, LAST_MONTH, LAST_YEAR, CUSTOM
              LAST_DAY represents a time range spanning the previous 24
                 hours.
              LAST_WEEK represents a time range spanning the previous 7
                 days.
              LAST_MONTH represents a time range spanning the previous 30
                 days.
              LAST_YEAR represents a time range spanning the previous 365
                 days.
              CUSTOM represents a time range that is specified using the
                 from and to parameters.
           from_value - optional value - The timestamp (milliseconds since
              UNIX epoch, namely January 1, 1970, 00:00:00 GMT) for the
              beginning period of the report. Only valid when since is
              CUSTOM
           to_value - optional value - The timestamp (milliseconds since
              UNIX epoch, namely January 1, 1970, 00:00:00 GMT) for the
              ending period of the report.Only valid when since is
              CUSTOM.
           aggregation_interval - Optional. Aggregation interval in minutes.
              Server metrics are aggregated and returned for time slices
              aggregated using the specified aggregation interval. The time
              range for the report, specified using the since parameter
              (and from and to when since is CUSTOM) is split into multiple
              slices, each covering an aggregation interval. Server metrics
              are then aggregated for each time slice and returned as data
              points in the report data.
              When the aggregation_interval is not specified, the following
              defaults are used:
                 LAST_DAY: 30 minutes
                 LAST_WEEK: 4 hours
                 LAST_MONTH: 24 hours
                 LAST_YEAR: 1 week
                 CUSTOM: 30 minutes up to 1 day, 4 hours up to 1 week, 1
                 day up to 30 days, and 1 week for longer periods.
             If the interval specified in Usage Reports Settings is
             more than the aggregationInterval, the interval is
             used instead.
           queries - A list of queries for which to generate the report.
              You need to specify the list as an array of JSON objects
              representing the queries. Each query specifies the list of
              metrics to be queries for a given set of resourceURIs.
              The queries parameter has the following sub-parameters:
                 resourceURIs - Comma separated list of resource URIs for
                 which to report metrics. Specifies services or folders
                 for which to gather metrics.
                    The resourceURI is formatted as below:
                       services/ - Entire Site
                       services/Folder/  - Folder within a Site. Reports
                         metrics aggregated across all services within that
                         Folder and Sub-Folders.
                       services/Folder/ServiceName.ServiceType - Service in
                         a specified folder, for example:
                         services/Map_bv_999.MapServer.
                       services/ServiceName.ServiceType - Service in the
                         root folder, for example: Map_bv_999.MapServer.
                 metrics - Comma separated list of metrics to be reported.
                   Supported metrics are:
                    RequestCount - the number of requests received
                    RequestsFailed - the number of requests that failed
                    RequestsTimedOut - the number of requests that timed out
                    RequestMaxResponseTime - the maximum response time
                    RequestAvgResponseTime - the average response time
                    ServiceActiveInstances - the maximum number of active
                      (running) service instances sampled at 1 minute
                      intervals, for a specified service
           metadata - Can be any JSON Object. Typically used for storing
              presentation tier data for the usage report, such as report
              title, colors, line-styles, etc. Also used to denote
              visibility in ArcGIS Server Manager for reports created with
              the Administrator Directory. To make any report created in
              the Administrator Directory visible to Manager, include
              "managerReport":true in the metadata JSON object. When this
              value is not set (default), reports are not visible in
              Manager. This behavior can be extended to any client that
              wants to interact with the Administrator Directory. Any
              user-created value will need to be processed by the client.

        Example:
        >>> queryObj = [{
           "resourceURIs": ["services/Map_bv_999.MapServer"],
           "metrics": ["RequestCount"]
        }]
        >>> obj.createReport(
           reportname="SampleReport",
           queries=queryObj,
           metadata="This could be any String or JSON Object.",
           since="LAST_DAY"
        )
        """
        res = self._reports.create_usage_report(reportname,
                                                queries,
                                                metadata,
                                                since,
                                                from_value,
                                                to_value,
                                                aggregation_interval)
        if isinstance(res, UsageReport):
            self._reports.init()
            return Report(res)
        return res
    #----------------------------------------------------------------------
    def quick_report(self,
                     since="LAST_WEEK",
                     queries="services/",
                     metrics="RequestsFailed"):
        """
        The operation quick_report generates an on the fly usage report for
        a service, services, or folder.

        :Parameters:
           since - the time duration of the report. The supported values
              are: LAST_DAY, LAST_WEEK, LAST_MONTH, LAST_YEAR, CUSTOM
              LAST_DAY represents a time range spanning the previous 24
                 hours.
              LAST_WEEK represents a time range spanning the previous 7
                 days.
              LAST_MONTH represents a time range spanning the previous 30
                 days.
              LAST_YEAR represents a time range spanning the previous 365
                 days.
              CUSTOM represents a time range that is specified using the
                 from and to parameters.
           queries - A list of queries for which to generate the report.
              You need to specify the list as an array of JSON objects
              representing the queries. Each query specifies the list of
              metrics to be queries for a given set of resourceURIs.
              The queries parameter has the following sub-parameters:
                 resourceURIs - Comma separated list of resource URIs for
                 which to report metrics. Specifies services or folders
                 for which to gather metrics.
                    The resourceURI is formatted as below:
                       services/ - Entire Site
                       services/Folder/  - Folder within a Site. Reports
                         metrics aggregated across all services within that
                         Folder and Sub-Folders.
                       services/Folder/ServiceName.ServiceType - Service in
                         a specified folder, for example:
                         services/Map_bv_999.MapServer.
                       services/ServiceName.ServiceType - Service in the
                         root folder, for example: Map_bv_999.MapServer.
           metrics - Comma separated list of metrics to be reported.
                   Supported metrics are:
                    RequestCount - the number of requests received
                    RequestsFailed - the number of requests that failed
                    RequestsTimedOut - the number of requests that timed out
                    RequestMaxResponseTime - the maximum response time
                    RequestAvgResponseTime - the average response time
                    ServiceActiveInstances - the maximum number of active
                    (running) service instances sampled at 1 minute
                    intervals, for a specified service
         :Output:
          Python dictionary of data on a successful query.
        """
        return self._reports.quick_report(since=since,
                                          queries=queries,
                                          metrics=metrics
                                        )
########################################################################
class Report(object):
    """
    A Single Usage Report returned by ArcGIS Server
    """
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self, report):
        """Constructor"""
        from .._server.admin._usagereports import UsageReport
        if isinstance(report, UsageReport):
            self._report = report
            self._properties = report._json_dict
        else:
            raise ValueError("Invalid Input, a UsageReport must be given.")
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the Report Properties
        """
        if self._properties is None:
            self._report.init()
            self._properties = PropertyMap(self._report._json_dict)
        return self._properties
    #----------------------------------------------------------------------
    def edit(self, report):
        """
        Edits the usage report. To edit a usage report, you need to submit
        the complete JSON representation of the usage report which
        includes updates to the usage report properties. The name of the
        report cannot be changed when editing the usage report.

        Values are changed in the class, to edit a property like
        metrics, pass in a new value.  Changed values to not take until the
        edit() is called.
        """
        import json
        params = {
            "f" : "json",
            "usagereport" : json.dumps(report)
        }
        url = self._report.url + "/edit"
        self._report.init()
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def delete(self):
        """deletes the current report"""
        return self._report.delete()
    #----------------------------------------------------------------------
    def query(self, query_filter=None):
        """
        Retrieves server usage data for the report. This operation
        aggregates and filters server usage statistics for the entire
        ArcGIS Server site. The report data is aggregated in a time slice,
        which is obtained by dividing up the time duration by the default
        (or specified) aggregationInterval parameter in the report. Each
        time slice is represented by a timestamp, which represents the
        ending period of that time slice.
        In the JSON response, the queried data is returned for each metric-
        resource URI combination in a query. In the report-data section,
        the queried data is represented as an array of numerical values. A
        response of null indicates that data is not available or requests
        were not logged for that metric in the corresponding time-slice.

        Inputs:
           query_filter - The report data can be filtered by the machine
             where the data is generated. The filter accepts a comma
             separated list of machine names; * represents all machines.

             Examples:
               # filters for the specified machines
               {"machines": ["WIN-85VQ4T2LR5N", "WIN-239486728937"]}
               # no filtering; all machines are accepted
               {"machines": "*"}
        """
        return self._report.query(query_filter=query_filter)
