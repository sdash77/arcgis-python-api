"""
This resource represents a collection of all the server machines that
have been registered with the site. It other words, it represents
the total computing power of your site. A site will continue to run
as long as there is one server machine online.
For a server machine to start hosting GIS services, it must be
grouped (or clustered). When you create a new site, a cluster called
'default' is created for you.
The list of server machines in your site can be dynamic. You can
register additional server machines when you need to increase the
computing power of your site or unregister them if you no longer
need them.
"""
from __future__ import absolute_import
from __future__ import print_function
import json
from .._common import BaseServer

########################################################################
class Machines(BaseServer):
    """
       This resource represents a collection of all the server machines that
       have been registered with the site. It other words, it represents
       the total computing power of your site. A site will continue to run
       as long as there is one server machine online.
       For a server machine to start hosting GIS services, it must be
       grouped (or clustered). When you create a new site, a cluster called
       'default' is created for you.
       The list of server machines in your site can be dynamic. You can
       register additional server machines when you need to increase the
       computing power of your site or unregister them if you no longer
       need them.
    """
    _machines = None
    _json_dict = None
    _con = None
    _url = None
    _json = None
    _DatastoreMachines = None
    _Protocal = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
               initialize - loads the machine information
        """
        super(Machines, self).__init__(connection=connection,
                                       url=url)
        self._url = url
        self._con = connection
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """ populates server admin information """
        params = {
            "f" : "json"
        }
        if connection:
            json_dict = connection.get(path=self._url,
                                       params=params)
        else:
            json_dict = self._con.get(path=self._url,
                                      params=params)
        self._json_dict = json_dict
        self._json = json.dumps(json_dict)
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        for k, v in json_dict.items():
            if k == "machines":
                self._machines = []
                for m in v:
                    self._machines.append(
                        Machine(url=self._url +"/%s" % m['machineName'],
                                connection=self._con)
                    )
            elif k in attributes:
                setattr(self, "_"+ k, json_dict[k])
            else:
                setattr(self, k, v)
            del k, v
    #----------------------------------------------------------------------
    @property
    def datastore_machines(self):
        """returns the datastore machine list"""
        if self._DatastoreMachines is None:
            self.init()
        return self._DatastoreMachines
    #----------------------------------------------------------------------
    @property
    def protocol(self):
        """returns the protocal"""
        if self._Protocal is None:
            self.init()
        return self._Protocal
    #----------------------------------------------------------------------
    @property
    def machines(self):
        """  returns the list of machines in the cluster """
        if self._machines is None:
            self.init()
        return self._machines
    #----------------------------------------------------------------------
    def get_machine(self, machine_name):
        """returns a machine object for a given machine
           Input:
              machine_name - name of the box ex: SERVER.DOMAIN.COM
        """
        url = self._url + "/%s" % machine_name
        return Machine(url=url,
                       connection=self._con)
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
        params = {
            "f" : "json",
            "machineName" : name,
            "adminURL" : admin_url
        }
        url = "%s/register" % self._url
        return self._con.post(path=url, postdata=params)
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
        params = {
            "f" : "json",
            "machineName" : name,
            "newMachineName" : new_name
        }
        url = self._url + "/rename"
        return self._con.post(path=url, postdata=params)
########################################################################
class Machine(BaseServer):
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
    _appServerMaxHeapSize = None
    _webServerSSLEnabled = None
    _webServerMaxHeapSize = None
    _platform = None
    _adminURL = None
    _machineName = None
    _ServerStartTime = None
    _webServerCertificateAlias = None
    _socMaxHeapSize = None
    _synchronize = None
    _configuredState = None
    _ports = None
    _json = None
    _json_dict = None
    _con = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
               initialize - boolean - loads properties at creation of object
        """
        super(Machine, self).__init__(connection=connection,
                                      url=url)
        self._url = url
        self._con = connection
        self._currentURL = url
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    @property
    def status(self):
        """ returns the state """
        uURL = self._url + "/status"
        params = {
            "f" : "json",
        }
        return self._con.get(path=uURL, params=params)
    #----------------------------------------------------------------------
    def start(self):
        """ Starts the server machine """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/start"
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def stop(self):
        """ Stops the server machine """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/stop"
        return self._con.post(path=uURL, postdata=params)
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
        params = {
            "f" : "json"
        }
        uURL = self._url + "/unregister"
        return self._con.post(path=uURL, postdata=params)
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
        params = {"f" : "json"}
        url = self._url + "/sslcertificates"
        return self._con.get(path=url,
                             params=params)
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
        params = {"f": "json"}
        url = self._url + "/sslcertificates/{cert}".format(cert=certificate)
        return self._con.get(path=url, params=params)
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
        params = {"f": "json"}
        url = self._url + "/sslcertificates/%s/export" % certificate
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def generate_CSR(self, certificate):
        """
        This operation generates a certificate signing request (CSR) for a
        self-signed certificate. A CSR is required by a CA to create a
        digitally signed version of your certificate.
        Parameters:
         :certificate: name of the certificate to grab information for
        """
        params = {"f" : "json"}
        url = self._url + "/sslcertificates/{cert}/generateCSR".format(cert=certificate)
        return self._con.post(path=url, postdata=params)
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
        params = {"f" : "json"}
        url = self._url + "/sslcertificates/{cert}/importCASignedCertificate".format(
            cert=certificate)
        files = {"caSignedCertificate" : ca_signed_certificate}
        return self._con.post(path=url, postdata=params, files=files)
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
        url = self._url + "/sslcertificates/importExistingServerCertificate"
        params = {
            "f" : "json",
            "alias" : alias,
            "certPassword" : cert_password
        }
        files = {
            "certFile" : cert_file}
        return self._con.post(path=url,
                              postdata=params,
                              files=files)
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
        url = self._url + "/sslcertificates/importRootOrIntermediate"
        params = {
            "f" : "json",
            "alias" : alias
        }
        files = {
            'rootCACertificate' : root_CA_certificate
        }
        return self._con.post(path=url,
                              postdata=params,
                              files=files)
