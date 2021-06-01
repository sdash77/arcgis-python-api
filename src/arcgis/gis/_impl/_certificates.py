from arcgis._impl.common._mixins import PropertyMap

###########################################################################
class CertificateManager(object):
    """
    The ``CertificateManager`` class provides the administor the ability to
    register and unregister certficates with the :class:`~arcgis.gis.GIS`.

    .. note::
        This resource is
        available via HTTPS only.
    """

    _gis = None
    _con = None
    _url = None
    _properties = None

    def __init__(self, gis):
        self._url = gis._portal.resturl + "portals/self/certificates"
        self._gis = gis
        self._con = gis._con

    # ----------------------------------------------------------------------
    def _init(self):
        result = self._con.get(self._url, {"f": "json"})
        self._properties = PropertyMap(result)

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        The ``properties`` method retrieves the properties of the certificate

        :returns:
            A list of the certificate properties
        """
        self._init()
        return self._properties

    # ----------------------------------------------------------------------
    def add(self, name, domain, certificate):
        """
        The ``add`` method allows allows administrators to
        register custom X.509 HTTPS certificates with their ArcGIS Online
        organizations. This will allow ArcGIS Online organization to trust
        the custom certificates used by a remote server when making HTTPS
        requests to it, i.e. store credentials required to access its
        resource and share with others.

        .. note::
            A maximum of 5 certificates can be registered with an organization.

        ================  ===============================================================================
        **Parameter**     **Description**
        ----------------  -------------------------------------------------------------------------------
        name              Required String. The certificate name.
        ----------------  -------------------------------------------------------------------------------
        domain            Required String. Server domain that the certificate is used for.
        ----------------  -------------------------------------------------------------------------------
        certificate	  Required String. Base64-encoded certificate text, enclosed between `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`.
        ================  ===============================================================================

        :returns:
            A boolean indicating success (True), or failure (False)

        """
        url = self._url + "/register"
        params = {
            "f": "json",
            "name": name,
            "domain": domain,
            "certificate": certificate,
        }
        import json

        res = self._con.post(url, params, try_json=False)
        res = res.replace(",}", "}")
        res = json.loads(res)
        if "success" in res:
            return res["success"]
        return res

    # ----------------------------------------------------------------------
    def get(self, cert_id):
        """
        A ``get`` method retrieves the certificate information for a single certificate

        ================  ===============================================================================
        **Parameter**     **Description**
        ----------------  -------------------------------------------------------------------------------
        cert_id           Required String.  The ID of the certificate to delete.
        ================  ===============================================================================


        The dictionary contains the following information:

        ================  ===============================================================================
        **Key**           **Value**
        ----------------  -------------------------------------------------------------------------------
        id                The ID of the registered certificate.
        ----------------  -------------------------------------------------------------------------------
        name              The certificate name.
        ----------------  -------------------------------------------------------------------------------
        domain            Server domain that the certificate is used for.
        ----------------  -------------------------------------------------------------------------------
        sslCertificate	  Base64-encoded certificate text, enclosed between `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`.
        ================  ===============================================================================

        :returns:
            A Dictionary (if found), else None

        """
        found_cert_id = None
        for cert in self.certificates:
            if cert_id.lower() == cert["id"].lower():
                found_cert_id = cert["id"]
                break
        if found_cert_id:
            url = self._url + "/{found_cert_id}".format(found_cert_id=found_cert_id)
            return self._con.get(url, {"f": "json"})
        return None

    # ----------------------------------------------------------------------
    def delete(self, cert_id):
        """
        The ``delete`` method unregisters the certificate from the organization.

        ================  ===============================================================================
        **Parameter**     **Description**
        ----------------  -------------------------------------------------------------------------------
        cert_id           Required String.  The ID of the certificate to delete.
        ================  ===============================================================================

        :returns:
            A boolean indicating success (True), or failure (False)

        """
        url = self._url + "/{cert_id}/unregister".format(cert_id=cert_id)
        params = {"f": "json"}
        res = self._con.post(url, params)
        if "success" in res:
            return res["success"]
        return res

    # ----------------------------------------------------------------------
    def update(self, cert_id, name=None, domain=None, certificate=None):
        """
        The ``update`` operation allows organization
        administrators to update a registered custom X.509 HTTPS
        certificate.

        ================  ===============================================================================
        **Parameter**     **Description**
        ----------------  -------------------------------------------------------------------------------
        cert_id           Required String.  The ID of the certificate to delete.
        ----------------  -------------------------------------------------------------------------------
        name              Optional String. The certificate name.
        ----------------  -------------------------------------------------------------------------------
        domain            Optional String. Server domain that the certificate is used for.
        ----------------  -------------------------------------------------------------------------------
        certificate	  Optional String. Base64-encoded certificate text, enclosed between `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`.
        ================  ===============================================================================

        :returns:
            A boolean indicating success (True), or failure (False)

        """
        url = self._url + "/{cert_id}/update".format(cert_id=cert_id)
        params = {"f": "json"}

        if not name is None:
            params["name"] = name
        if not domain is None:
            params["domain"] = domain
        if not certificate is None:
            params["certificate"] = certificate
        import json  # HANDLES BUG IN API

        res = self._con.post(url, params, try_json=False)
        res = json.loads(res.replace(",}", "}"))
        if "success" in res:
            return res["success"]
        return res

    # ----------------------------------------------------------------------
    @property
    def certificates(self):
        """
        The ``certificates`` method retrieves a list of certificates registered with the organization

        :returns:
            A List containing the information of registered certificates
        """
        return self.properties.certificates
