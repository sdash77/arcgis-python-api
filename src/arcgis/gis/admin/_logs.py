"""
Allows access to the Portal Logs
"""
from ..gis import GIS
from ._base import BasePortalAdmin
########################################################################
class Logs(BasePortalAdmin):
    """
    Logs are records written by various components of the portal. You can
    query the logs, clean the logs, and edit log settings.
    """
    _gis = None
    _url = None
    _con = None
    _portal = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis):
        """Constructor"""
        if isinstance(gis, GIS):
            self._url = url
            self._gis = gis
            self._portal = gis._portal
            self._con = gis._con
        else:
            raise ValueError("gis object must be of type GIS")
    #----------------------------------------------------------------------
    def clean(self):
        """
        Deletes all the log files on the machine hosting Portal for ArcGIS.
        This operation allows you to free up disk space. The logs cannot be
        recovered after executing this operation.
        """
        url = "%s/clean" % self._url
        params = {"f" : "json"}
        res = self._con.post(path=url, postdata=params)
        if isinstance(res, dict) and \
           'status' in res:
            return res['status'] == "success"
        return False
    #----------------------------------------------------------------------
    @property
    def settings(self):
        """
        Reads/writes the current log settings for the portal.
        """
        url = "%s/settings" % self._url
        params = {'f' : 'json'}
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @settings.setter
    def settings(self, value):
        """
        Reads/writes the current log settings for the portal.
        """
        url = "%s/settings/edit" % self._url
        params = {'f' : 'json'}
        if isinstance(value, dict):
            for k,v in value.items():
                params[k] = v
        else:
            raise ValueError("Value must be a dictionary")
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def query(self, start_time, end_time=None,
              level="WARNING", query_filter="*",
              page_size=1000):
        """
        The query operation allows you to aggregate, filter, and page
        through logs written by the portal.

        Parameters:
         :start_time: The most recent time to query. If the hasMore member
          of the response object is true, then to get the next set of
          records, pass the endTime member as the startTime parameter for
          the next request. This parameter is optional.
          Time can be specified as a portal timestamp (format in
          yyyy-mm-ddThh:mm:ss) or in milliseconds since UNIX epoch. For
          example:
          Timestamp: { "startTime": "2015-08-01T15:17:20,123", ... }
          Milliseconds: { "startTime": 1312237040123, ... }
          Default: now
         :end_time: The oldest time to include in the result set. You can
          use this to limit the query to the last number of minutes, hours,
          days, months, and years as needed. If since PortalStart is true,
          then the default is all logs since the portal was started. This
          parameter is optional.
         :level: Can be one of [OFF, SEVERE, WARNING, INFO, FINE, VERBOSE,
          DEBUG]. Returns only records with a log level at or more severe
          than the level specified. This parameter is required.
          Default: WARNING
         :query_filter: Filtering is allowed by any combination of codes,
          users, and source components. The filter accepts a comma
          delimited list of filter definitions. If any definition is
          omitted, it defaults to all. This parameter is required.
          Example:
          {"codes":[204000-205999,212015,219114], "users":["admin","jcho"],
           "source": ["PORTAL ADMIN"]}
          The source of logged events are generated from the sharing,
          administrative, and portal components of the software.
          For example:
           - Events related to publishing and users are categorized under
             SHARING.
           - Events related to security and indexing are categorized under
             PORTAL ADMIN.
           - Events related to installing the software are categorized
             under PORTAL.
         :page_size: The maximum number of log records to be returned by
          this query. This parameter is optional.
          Default: 1000
        :Returns:
         JSON response of the log messages
        """
        from datetime import datetime
        from six import integer_types
        url = "%s/query" % self._url
        if isinstance(start_time, datetime):
            start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        elif not isinstance(end_time, integer_types):
            raise ValueError("Invalid datetime, must be integer or datetime object")
        if end_time is None:
            end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        elif isinstance(end_time, datetime):
            end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")
        elif not isinstance(end_time, integer_types):
            raise ValueError("Invalid datetime, must be integer or datetime object")
        if query_filter == "*":
            query_filter = {"codes":[], "users":[], "source": "*"}
        params = {
            "startTime" : start_time,
            "endTime" : end_time,
            "level" : level,
            "f" : "json",
            "filterType" : "json",
            "pageSize" : page_size

        }
        if query_filter:
            params['filter'] = query_filter
        return self._con.get(path=url, params=params)
