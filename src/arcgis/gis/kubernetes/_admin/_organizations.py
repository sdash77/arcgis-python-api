from arcgis.gis.kubernetes._admin._base import _BaseKube

class KubeOrgSecurity(_BaseKube):
    """"""
    def users(self):
        pass
    def groups(self):
        pass
class KubeOrgLicense(_BaseKube):
    """"""
    ...
class KubeOrgFederation(_BaseKube):
    """"""
    ...
class KubeOrganization(_BaseKube):
    """A Single Kubernetes Organization"""
    _security = None
    _federation = None
    _license = None


    @property
    def security(self):
        if self._security is None:
            self._security = KubeOrgSecurity(url=f"{self._url}/security",
                                             gis=self._gis, initialize=False)
        pass

    @property
    def license(self):
        pass

    @property
    def federation(self):
        pass

class KubeOrganizations(_BaseKube):
    """
    """
    _url = None
    _gis = None
    _properties = None

    def __init__(self, url, gis):
        initialize = False
        super()
        self._url = url
        self._gis = gis

    @property
    def orgs(self) -> tuple:
        """
        Returns a list of registerd organizations with the Kubernetes deployment

        :returns: tuple
        """
        return (KubeOrganization(url=f"{self._url}/{org}",
                                 gis=self._gis)\
                for org in self.properties['organizations'])
