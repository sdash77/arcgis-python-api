import sys
sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_issue_5552\src")
from arcgis.gis._impl._con import Connection
from arcgis._impl.common._mixins import PropertyMap
from arcgis.gis import Item
from arcgis.gis.server._service import Service
from arcgis._impl.backport import cached_property
from functools import lru_cache
###########################################################################
class MissionJob(object):
    _properties = None
    _url = None
    _con = None
    _gis = None
    # ---------------------------------------------------------------------
    def __init__(self, url:str, gis:"GIS", **kwargs) -> "MissionJob":
        self._url = url
        self._gis = gis
        self._con = gis._con
    # ---------------------------------------------------------------------
    def __str__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    def __repr__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    @cached_property
    def properties(self):
        if self._properties is None:
            try:
                self._properties = PropertyMap(self._con.get(self._url, {'f' : 'json'}))
            except:
                self._properties = PropertyMap(self._con.post(self._url, {'f' : 'json'}))
        return self._properties
    # ---------------------------------------------------------------------
    @property
    def status(self) -> object:

        """
        Returns the status

        :returns: string when not finished, else a `Mission`
        """
        resp = self._con.get(self._url, {'f' : 'json'})
        if resp['status'] != "COMPLETED":

            return resp['status']
        else:
            url = f"{self._url.split('/jobs/')[0]}/missions/{resp['customAttributes']['missionId']}"
            return Mission(url=url, gis=self._gis)

###########################################################################
class MissionReport(object):
    _properties = None
    _url = None
    _con = None
    _gis = None
    _status = None
    _item = None
    # ---------------------------------------------------------------------
    def __init__(self, url:str, gis:"GIS", status:str, item_id:str, **kwargs) -> "MissionReport":
        self._url = url
        self._gis = gis
        self._con = gis._con
        self._status = status
        self._itemid = item_id
    # ---------------------------------------------------------------------
    def __str__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    def __repr__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    @cached_property
    def properties(self):
        if self._properties is None:
            try:
                self._properties = PropertyMap(self._con.get(self._url, {'f' : 'json'}))
            except:
                self._properties = PropertyMap(self._con.post(self._url, {'f' : 'json'}))
        return self._properties
    # ---------------------------------------------------------------------
    @property
    def status(self) -> str:
        """
        returns the report status

        :return: str
        """
        return self._status
    # ---------------------------------------------------------------------
    @cached_property
    def item(self) -> str:
        """
        returns the report status

        :return: str
        """
        return Item(self._gis, self.properties['itemId'])


###########################################################################
class Mission(object):
    """
    A single registered `Mission` on the Enterprise.
    """
    _properties = None
    _url = None
    _con = None
    _gis = None
    # ---------------------------------------------------------------------
    def __init__(self, url:str, gis:"GIS", **kwargs) -> "Mission":
        self._url = url
        self._gis = gis
        self._con = gis._con
    # ---------------------------------------------------------------------
    def _dictionary_check(self, i):
        """
        First prints the final entry in the dictionary (most nested) and its key
        Then prints the keys leading into this
        * could be reversed to be more useful, I guess
        """
        for key,value in i.items():
            if isinstance(value, dict):
                self._dictionary_check(value)
            else:
                if isinstance(value, str) and \
                   value.lower().find('/featureserver/'):
                    i[key] = Service(url=value, server=self._gis)
    # ---------------------------------------------------------------------
    @cached_property
    def properties(self):
        if self._properties is None:
            try:
                r = self._con.get(self._url, {'f' : 'json'})
                self._dictionary_check(r)
                self._properties = r
            except:
                r = self._con.post(self._url, {'f' : 'json'})
                self._dictionary_check(r)
                self._properties = r
        return self._properties
    # ---------------------------------------------------------------------
    def __str__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    def __repr__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    def delete(self) -> bool:
        """
        Deletes a `Mission` from the server.

        :return: Boolean
        """
        params = {
            'f' : 'json',
            'async' : False
        }
        url = f"{self._url}/delete"
        return self._con.post(url, params)

###########################################################################
class MissionCatalog():
    """
    The ArcGIS Mission Server catalog.

    """
    _con = None
    _gis = None
    _url = None
    _properties = None
    # ---------------------------------------------------------------------
    def __init__(self, gis:"GIS") -> "MissionCatalog":
        url = None
        urls = {
            'admin' : None,
            'url' : None
        }
        for rs in gis._registered_servers()['servers']:
            if rs['serverType'] == "ARCGIS_MISSION_SERVER":
                url = f"{rs['url']}/rest"
                urls['url'] = url
                urls['admin'] = f"{rs['adminUrl']}/admin"


        if url is None:
            raise Exception("No registered mission server found.")

        self._url = url
        self._gis = gis
        self._con = gis._con
        try:
            from arcgis.gis.mission import MissionServer
            self.admin = MissionServer(url=urls['admin'], gis=gis)
        except:
            pass
    # ---------------------------------------------------------------------
    def __str__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    def __repr__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"
    # ---------------------------------------------------------------------
    @cached_property
    def properties(self):
        if self._properties is None:
            try:
                self._properties = PropertyMap(self._con.get(self._url, {'f' : 'json'}))
            except:
                self._properties = PropertyMap(self._con.post(self._url, {'f' : 'json'}))
        return self._properties
    # ---------------------------------------------------------------------
    def create_mission(self,
                       title:str,
                       snippet:str=None,
                       description:str=None,
                       license_info:str=None,
                       tags:str=None,
                       extent:list=None,
                       template_item:"Item"=None,
                       locale:str='en') -> MissionJob:
        """

        Creates a new `Mission` on the enterprise.

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        title	               Required String. The title of the mission. This is the name that's displayed to users and by which they refer to the mission. Every mission must have a title.
        ------------------     --------------------------------------------------------------------
        snippet	               Optional String. A short summary description of the item.
        ------------------     --------------------------------------------------------------------
        description	       Optional String. Mission description.
        ------------------     --------------------------------------------------------------------
        license_info	       Optional String. Any license information or restrictions.
        ------------------     --------------------------------------------------------------------
        tags	               Optional String. Comma-separated list of user defined tags that
                               describe the mission.
        ------------------     --------------------------------------------------------------------
        extent	               Optional String. Comma-separated list that defines the bounding
                               rectangle of the mission. Should always be in WGS84. The
                               default is -180, -90, 180, 90.

                               **Format: <xmin>, <ymin>, <xmax>, <ymax>**

        ------------------     --------------------------------------------------------------------
        templateWebMapId	Optional. String. The ID of the web map to use as a template for the mission.
        ------------------     --------------------------------------------------------------------
        locale	               Optional String. Default = 'en', must be a valid IETF BCP 47 language tag.
        ==================     ====================================================================


        :returns: `MissionJob`


        """

        url = f"{self._url}/missions/add"
        params = {
            'title' : title,
            'snippet' : snippet or "",
            'description' : description or "",
            "licenseInfo" : license_info or "",
            "async" : True,
            "tags" : tags or "",
            "extent" : extent or "-180,-90,180,90",
            "locale" : locale or "en",
            "f" : "json"
        }
        resp = self._con.post(url, params)
        return MissionJob(url=f"{self._url}/jobs/{resp.get('jobId')}", gis=self._gis)
    # ---------------------------------------------------------------------
    @property
    def jobs(self) -> list:
        """returns a list of jobs on the server"""
        url = f"{self._url}/jobs"
        params = {'f' : 'json'}
        resp = self._con.get(url, params)
        return [MissionJob(url=f"{url}/{j}", gis=self._gis) for j in resp["asyncJobs"]]
    # ---------------------------------------------------------------------
    @property
    def missions(self) -> list:
        """
        returns a list of missions on the server

        :returns: List
        """
        url = f"{self._url}/missions"
        params = {'f' : 'json'}
        resp = self._con.get(url, params)
        return [Mission(url=f"{url}/{j['id']}", gis=self._gis) for j in resp["results"]]


if __name__ == "__main__":
    from arcgis.gis import GIS
    gis = GIS(url="https://wdctyint0000399.esri.com/portal",
              username="achapadmin",
              password="Password.1234",
              verify_cert=False,
              trust_env=True)
    mc = MissionCatalog(gis=gis)
    print(mc.missions)
    print(mc.missions[0].properties)
    print(mc.jobs)
    print(mc.properties)
    import uuid
    job = mc.create_mission(title=f'test_ms_{uuid.uuid4().hex[:3]}')
    print(job.status)
    print(job.status)
    import time
    while not isinstance(job.status, Mission) and job.status not in ['FAILED']:
        print(job.status)
        time.sleep(2)
    print(job.status)
    print(job.properties)
    print()