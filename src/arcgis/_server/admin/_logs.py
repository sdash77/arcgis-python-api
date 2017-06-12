"""
Logs are the records written by the various components of ArcGIS Server.
You can query the logs and change various log settings.
"""
from __future__ import absolute_import
from __future__ import print_function
import csv
from datetime import datetime
from .._common import BaseServer


########################################################################
class Log(BaseServer):
    """ Log of a server """
    _url = None
    _con = None
    _json_dict = None
    _operations = None
    _resources = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection class
        """
        super(Log, self).__init__(connection=connection,
                                  url=url)
        self._url = url
        self._con = connection
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    @property
    def operations(self):
        """ returns the operations """
        if self._operations is None:
            self.init()
        return self._operations
    #----------------------------------------------------------------------
    @property
    def resources(self):
        """ returns the log resources """
        if self._resources is None:
            self.init()
        return self._resources
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
        params = {
            "f": "json",
            "machine" : machine
        }
        url = self._url + "/countErrorReports"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def clean(self):
        """ Deletes all the log files on all server machines in the site.  """
        params = {
            "f" : "json",
        }
        url = "{}/clean".format(self._url)
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    @property
    def settings(self):
        """ returns the current log settings """
        params = {
            "f" : "json"
        }
        url = self._url + "/settings"
        try:
            return self._con.post(path=url,
                                  postdata=params)['settings']
        except:
            return ""
    #----------------------------------------------------------------------
    def edit_settings(self,
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
        url = self._url + "/settings/edit"
        allowed_levels = ("OFF", "SEVERE", "WARNING", "INFO", "FINE", "VERBOSE", "DEBUG")
        current_settings = self.settings
        current_settings["f"] = "json"

        if level.upper() in allowed_levels:
            current_settings['logLevel'] = level.upper()
        if log_dir is not None:
            current_settings['logDir'] = log_dir
        if max_age is not None and \
           isinstance(max_age, int):
            current_settings['maxLogFileAge'] = max_age
        if max_report_count is not None and \
           isinstance(max_report_count, int) and\
           max_report_count > 0:
            current_settings['maxErrorReportsCount'] = max_report_count
        return self._con.post(path=url,
                              postdata=current_settings)
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
        if codes is None:
            codes = []
        if process_IDs is None:
            process_IDs = []
        allowed_levels = ("SEVERE", "WARNING", "INFO",
                          "FINE", "VERBOSE", "DEBUG")
        qFilter = {
            "services": "*",
            "machines": "*",
            "server" : "*"
        }
        if len(process_IDs) > 0:
            qFilter['processIds'] = process_IDs
        if len(codes) > 0:
            qFilter['codes'] = codes
        params = {
            "f" : "json",
            "sinceServerStart" : since_server_start,
            "pageSize" : 10000
        }
        url = "{url}/query".format(url=self._url)
        if start_time is not None and \
           isinstance(start_time, datetime):
            params['startTime'] = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        if end_time is not None and \
           isinstance(end_time, datetime):
            params['endTime'] = end_time.strftime("%Y-%m-%dT%H:%M:%S")
        if level.upper() in allowed_levels:
            params['level'] = level
        if server != "*":
            qFilter['server'] = server.split(',')
        if services != "*":
            qFilter['services'] = services.split(',')
        if machines != "*":
            qFilter['machines'] = machines.split(",")
        params['filter'] = qFilter
        if export is True and \
           out_path is not None:

            messages = self._con.post(path=url,
                                      postdata=params)
            with open(name=out_path, mode='wb') as f:
                hasKeys = False
                if export_type == "TAB":
                    csvwriter = csv.writer(f, delimiter='\t')
                else:
                    csvwriter = csv.writer(f)
                for message in messages['logMessages']:
                    if hasKeys == False:
                        csvwriter.writerow(message.keys())
                        hasKeys = True
                    csvwriter.writerow(message.values())
                    del message
            del messages
            return out_path
        else:
            return self._con.post(path=url,
                                  postdata=params)
