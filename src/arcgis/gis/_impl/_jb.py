
import os
import datetime
import concurrent.futures
from concurrent.futures import Future
import logging
import json
_log = logging.getLogger(__name__)

class StatusJob(object):
    """
    Represents a Single Geoprocessing Job.  The `GPJob` class allows for the asynchronous operation
    of any geoprocessing task.  To request a GPJob task, the code must be called with `future=True`
    or else the operation will occur synchronously.  This class is not intended for users to call
    directly.


    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    future            Required current.futures.Future.  The async object.
    ----------------  ---------------------------------------------------------------
    op                Required String. The name of the operation performed.
    ----------------  ---------------------------------------------------------------
    jobid             Required String. The unique ID of the job.
    ----------------  ---------------------------------------------------------------
    gis               Required GIS. The GIS connection object
    ----------------  ---------------------------------------------------------------
    notify            Optional Boolean.  When set to True, a message will inform the
                      user that the geoprocessing task has completed. The default is
                      False.
    ================  ===============================================================

    """
    _future = None
    _jobid = None
    _url = None
    _gis = None
    _task_name = None
    _is_fa = False
    _is_ra = False
    _is_ortho = False
    _start_time = None
    _end_time = None
    _item_properties = None
    #----------------------------------------------------------------------
    def __init__(self, future, op, jobid, gis, notify=False):
        """
        initializer
        """
        assert isinstance(future, Future)
        self._future = future
        self._start_time = datetime.datetime.now()
        if notify:
            self._future.add_done_callback(self._notify)
        self._future.add_done_callback(self._set_end_time)
        self._op = op
        self._jobid = jobid
        self._gis = gis
    #----------------------------------------------------------------------
    @property
    def ellapse_time(self):
        """
        Returns the Ellapse Time for the Job
        """
        if self._end_time:
            return self._end_time - self._start_time
        else:
            return datetime.datetime.now() - self._start_time
    #----------------------------------------------------------------------
    @property
    def definition(self):
        """
        Returns information about the job

        :return: Dict
        """
        url = f"{self._gis._portal.resturl}portals/self/jobs/%s" % self._jobid
        params = {'f' : 'json'}
        res = self._gis._con.post(url, params)
        if "definition" in res:
            return res["definition"]
        return res

    #----------------------------------------------------------------------
    def _set_end_time(self, future):
        """sets the finish time"""
        self._end_time = datetime.datetime.now()
    #----------------------------------------------------------------------
    def _notify(self, future):
        """prints finished method"""
        jobid = self._jobid
        try:
            res = future.result()
            infomsg = '{jobid} finished successfully.'.format(jobid=jobid)
            _log.info(infomsg)
            print(infomsg)
        except Exception as e:
            msg = str(e)
            msg = '{jobid} failed: {msg}'.format(jobid=jobid, msg=msg)
            _log.info(msg)
            print(msg)
    #----------------------------------------------------------------------
    def __str__(self):
        return "<%s Group Job: %s>" % (self.task, self._jobid)
    #----------------------------------------------------------------------
    def __repr__(self):
        return "<%s Group Job: %s>" % (self.task, self._jobid)
    #----------------------------------------------------------------------
    @property
    def task(self):
        """Returns the task name.
        :returns: string
        """

        return self._op
    #----------------------------------------------------------------------
    @property
    def status(self):
        """
        returns the GP status

        :returns: String
        """

        url = f"{self._gis._portal.resturl}portals/self/jobs/%s" % self._jobid
        params = {'f' : 'json'}
        res = self._gis._con.post(url, params)
        if "status" in res:
            return res["status"]
        return res
    #----------------------------------------------------------------------
    @property
    def messages(self):
        """
        returns the jobs message

        :returns: String
        """

        url = f"{self._gis._portal.resturl}portals/self/jobs/%s" % self._jobid
        params = {'f' : 'json'}
        res = self._gis._con.post(url, params)
        if "messages" in res:
            return res["messages"]
        return res
    #----------------------------------------------------------------------
    def cancel(self):
        """
        Cancels the `Future` process to end the job locally.
        Import/Export jobs cannot be terminiated on server.

        :returns: boolean
        """
        if self.done():
            return False
        if self.cancelled():
            return False
        self._future.cancel()
        return True
    #----------------------------------------------------------------------
    def cancelled(self):
        """
        Return True if the call was successfully cancelled.

        :returns: boolean
        """
        return self._future.cancelled()
    #----------------------------------------------------------------------
    def running(self):
        """
        Return True if the call is currently being executed and cannot be cancelled.

        :returns: boolean
        """
        return self._future.running()
    #----------------------------------------------------------------------
    def done(self):
        """
        Return True if the call was successfully cancelled or finished running.

        :returns: boolean
        """
        return self._future.done()
    #----------------------------------------------------------------------
    def result(self):
        """
        Return the value returned by the call. If the call hasn't yet completed
        then this method will wait.

        :returns: object
        """
        from arcgis.gis import Item
        if self.cancelled():
            return None
        res = self._future.result()
        if 'result' in res:
            if 'itemId' in res['result']:
                from arcgis.gis import Item
                return Item(gis=self._gis, itemid=res['result']['itemId'])
            if 'itemsImported' in res['result']:
                return_result = {}
                return_result['itemsImported'] = [Item(itemid=i['itemId'], gis=self._gis) for i in res['result']['itemsImported'] if 'itemId' in i]
                return_result['itemsSkipped'] = [Item(i['itemId'], gis=self._gis) for i in res['result']['itemsSkipped'] if 'itemId' in i]
                return_result['itemsFailedImport'] = [Item(i['itemId'], gis=self._gis) for i in res['result']['itemsFailedImport'] if 'itemId' in i]
                return return_result
            else:
                return res
            
        return res
