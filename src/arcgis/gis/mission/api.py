from arcgis.gis._impl._con import Connection
from arcgis._impl.common._mixins import PropertyMap
from arcgis.gis import Item
from arcgis.gis.server._service import Service
from arcgis._impl.backport import cached_property
from functools import lru_cache
###########################################################################
class MissionJob(object):
    """Represents a Single `Job` operation for Mission Server"""
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

        :returns: string
        """
        resp = self._con.get(self._url, {'f' : 'json'})
        try:
            return resp['status']
        except:
            return "UNKNOWN"
    # ---------------------------------------------------------------------
    def result(self) -> "Mission":
        """Returns the results of the process"""
        if self.status.upper() == 'COMPLETED':
            resp = self._con.get(self._url, {'f' : 'json'})
            if self.properties['type'] == "addMission":
                url = f"{self._url.split('/jobs/')[0]}/missions/{resp['customAttributes']['missionId']}"
                return Mission(url=url, gis=self._gis)
            else:
                return self.properties
        return None
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
                   value.lower().find('/featureserver/') > -1:
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
        res = self._con.post(url, params)
        if res.get('status') or res.get('success'):
            return res.get('status') or res.get('success')
        return res
    # ---------------------------------------------------------------------
    def add_message(self, message:dict):
        """
        Adds a message to the current `Mission`

        :return: bool
        """
        url = f"{self._url}/addMessages"
        params = {
            'f' : 'json',
            'features' : message
        }
        res = self._con.post(url, params)
        if res.get('status') or res.get('success'):
            return res.get('status') or res.get('success')
        return res
    # ---------------------------------------------------------------------
    def add_reports(self,
                    title:str,
                    description:str=None,
                    tags:str=None,
                    questions:dict=None,
                    display_field:str=None,
                    drawing_info:dict=None,
                    locale:str='en',
                    share_as_template:bool=False) -> dict:
        """
        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        title	               Required String. The name of the report.
        ------------------     --------------------------------------------------------------------
        description	       Optional String. Mission report description.
        ------------------     --------------------------------------------------------------------
        tags	               Optional String. Comma-separated list of user defined tags that
                               describe the mission report.
        ------------------     --------------------------------------------------------------------
        questions              Optional Dict. Dictionary containing questions and their fields.
                               Available question types: Single Line Text, Single Choice, Number,
                               Image, Multiline Text, Dropdown, Multiple Choice, and Date/Time.
                               See https://doc.arcgis.com/en/survey123/browser/create-surveys/quickreferencecreatesurveys.htm#GUID-2D96112F-85B1-4C41-9C6F-A85BB6026A51 for details.
        ------------------     --------------------------------------------------------------------
        display_field          Optional String. The name to display for the report
        ------------------     --------------------------------------------------------------------
        locale                 Optional String. A valid IETF BCP 47 language tag
        ------------------     --------------------------------------------------------------------
        share_as_template      Optional Boolean. Shares the report as a template.
        ==================     ====================================================================

        :returns: Dict
        """
        params = {
            "title" : title,
            "description" : description or "",
            "tags" : tags or "report",
            "questions" : questions or [],
            "displayField" : display_field or "",
            "drawingInfo" : drawing_info or "",
            "shareAsTemplate": share_as_template,
            "locale" : locale,
            'f' : 'json'
        }
        url = f"{self._url}/reports/add"
        return self._con.post(url, params)
    # ---------------------------------------------------------------------
    @property
    def reports(self) -> list:
        """
        Returns a List of Mission Report Items associated with the `Mission`

        :returns: List[Item]

        """
        url = f"{self._url}/reports"
        params = {'f' : 'json'}
        res = self._con.get(url, params)
        return [Item(gis=self._gis, itemid=r['itemId']) \
                for r in res['reports'] if r.get('itemId')]
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
                       locale:str='en',
                       base_map:dict=None,
                       wm_description:str=None) -> MissionJob:
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
        ------------------     --------------------------------------------------------------------
        base_map               Optional dict. The desired base map for the mission.
        ------------------     --------------------------------------------------------------------
        wm_description         Optional string. The description of the web map added to the mission.
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
            "baseMap" : base_map or "",
            "webMapDescription" : wm_description,
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


