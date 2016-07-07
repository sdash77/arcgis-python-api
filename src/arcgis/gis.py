"""
The **gis** module provides an information model for GIS hosted
within ArcGIS Online or an ArcGIS Portal. This module provides functionality to manage
(create, read, update and delete) GIS users, groups, content and datastores. This module
is the most important and provides the entry point into the GIS.
"""
from __future__ import absolute_import
from arcgis.lyr import *
from arcgis.tools import *
import arcgis._impl.portalpy as portalpy
from ._impl._managers import UserManager, GroupManager
from ._impl._managers import ContentManager
from ._impl._object import Item
from ._impl._managers import  DatastoreManager
from ._impl._util import Error, _lazy_property, _tempinput
# pylint: disable=fixme, line-too-long

###########################################################################
class GIS(object):
    """
    .. _gis:

    **************
    The GIS object
    **************
    A GIS is representative of ArcGIS Online or an ArcGIS Portal
    site. The GIS object provides helper objects to manage (search, create, retrieve) GIS resources:
    * users
    * groups
    * content
    * datastore
    * tools - including geometry, geocoder, analysis, rasters, geoanalytics

    Additionally, the GIS object has properties and methods to query it's state:
    * properties
    * usage()
    """

    _version = '0.1'

    def __init__(self, url=None, username=None, password=None, key_file=None, cert_file=None):
        """
        Constructs a GIS object given a url and user credentials to ArcGIS Online
        or an ArcGIS Portal. User credentials can be passed in using username/password
        pair, or key_file/cert_file pair (in case of PKI). Supports built-in users, LDAP,
        PKI and Anonymous access.

        If no url is provided, ArcGIS Online is used. If username/password
        or key/cert files are not provided, anonymous access is used.
        """
        if url is None:
            url = "http://www.arcgis.com"

        self._url = url
        self._username = username
        self._password = password
        self._key_file = key_file
        self._cert_file = cert_file
        self._portal = None
        self.tools = Tools(self)
        self.__enter__()

    def __enter__(self):
        self._portal = portalpy.Portal(self._url, self._username,
                                       self._password, self._key_file, self._cert_file)

    @_lazy_property
    def users(self):
        """
        The resource manager for GIS users
        """
        return UserManager(self._portal)

    @_lazy_property
    def groups(self):
        """
        The resource manager for GIS groups
        """
        return GroupManager(self._portal)

    @_lazy_property
    def content(self):
        """
        The resource manager for GIS content
        """
        return ContentManager(self._portal)

    @_lazy_property
    def datastore(self):
        """
        The resource manager for the GIS data store
        """
        fedservers_url = self._url + "/portaladmin/federation/servers?f=json"
        #print(fedservers_url)
        res = self._portal.con.get(fedservers_url)
        servers = res['servers']

        admin_url = None

        for server in servers:
            if server['isHosted']:
                admin_url = server['adminUrl'] + '/admin'
                return DatastoreManager(self, admin_url)

        return None

    @_lazy_property
    def properties(self):
        """
        The properties of the GIS
        """
        return self._get_properties()

    def __exit__(self, typ, value, traceback):
        self._portal.logout()

    def __str__(self):
        return 'GIS @ ' + self._url

    def _repr_html_(self):
        """
        HTML Representation for IPython Notebook
        """
        return 'GIS @ <a href="' + self._url + '">' + self._url + '</a>'

    def _get_properties(self, force=False):
        """ Returns the portal properties (using cache unless force=True). """
        return self._portal.get_properties(force)

    #def usage(self, startTime, endTime, period, vars, etype, stype, groupby, appId=None):
    #    """Usage statistics for the GIS"""
    #    return self._portal.usage(startTime, endTime, period, vars, etype, stype, groupby, appId)

    def map(self, location=None, zoomlevel=None):
        """Creates a map widget centered at the location (Address or (lat, long) tuple) with the specified zoom-level(integer)"""
        from arcgis.viz import MapView
        mapwidget = MapView()
        if location is not None:
            if isinstance(location, str):
                mapwidget.center = self.tools.geocoder.find_best_match(location)
            elif isinstance(location, tuple):
                mapwidget.center = location
            else:
                print("location must be an address(string) or (lat, long) pair as a tuple")
        if zoomlevel is not None:
            mapwidget.zoom = zoomlevel

        return mapwidget
###########################################################################
class Tools(object):
    """
    Collection of GIS tools. This class holds references to the helper services and tools available
    in the GIS. This class is not created by users directly.
    An instance of this class, called 'tools', is available as a property of the GIS object.
    Users access the GIS tools, such as the geocoder, spatial analysis tools, geoanalytics, raster
    geoanalysis tools, etc through the gis.tools object
    """
    def __init__(self, gis):
        self._gis = gis
        self._geocoder = None
        self._geometry = None
        self._analysis = None
        self._raster_analysis = None
        self._geoanalytics = None

    @property
    def geocoder(self):
        """the geocoder, if available and configured"""
        if self._geocoder is not None:
            return self._geocoder
        try:
            geocodesvcurl = self._gis.properties['helperServices']['geocode'][0]['url']
            self._geocoder = Geocoder(None, geocodesvcurl, self._gis)
            return self._geocoder
        except KeyError:
            return None

    @property
    def geometry(self):
        """the portal's geometry  tools, if available and configured"""
        if self._geometry is not None:
            return self._geometry
        try:
            svcurl = self._gis.properties['helperServices']['geometry']['url']
            self._geometry = Geometry(None, svcurl, self._gis)
            return self._geometry
        except KeyError:
            return None

    @property
    def rasteranalytics(self):
        """the portal's raster analysis tools, if available and configured"""
        if self._raster_analysis is not None:
            return self._raster_analysis
        try:
            try:
                svcurl = self._gis.properties['helperServices']['rasterAnalytics']['url']
            except:
                svcurl = 'https://rdvmags01.esri.com/arcgis/rest/services/System/RasterAnalysisTools/GPServer'

            self._raster_analysis = RasterAnalysisTools(svcurl, self._gis)
            return self._raster_analysis
        except KeyError:
            return None

    @property
    def bigdata(self):
        """the portal's bigdata analytics tools, if available and configured"""
        if self._geoanalytics is not None:
            return self._geoanalytics
        try:
            try:
                svcurl = self._gis.properties['helperServices']['geoanalytics']['url']
            except:
                print("This GIS does not support geoanalytics")
                return None

            self._geoanalytics = GeoAnalyticsTools(svcurl, self._gis)
            return self._geoanalytics
        except KeyError:
            return None

    @property
    def analysis(self):
        """the portal's spatial analysis tools, if available and configured"""
        if self._analysis is not None:
            return self._analysis
        try:
            try:
                svcurl = self._gis.properties['helperServices']['analysis']['url']
            except:
                svcurl = 'https://analysis6.arcgis.com/arcgis/rest/services/tasks/GPServer'
            self._analysis = SpatialAnalysisTools(svcurl, self._gis)
            return self._analysis
        except KeyError:
            return None
