import os
from concurrent.futures import Future
import logging
_log = logging.getLogger(__name__)
class GPJob(object):
    """
    Represents a Single Geoprocessing Job.  The `GPJob` class allows for the asynchronous operation
    of any geoprocessing task.  To request a GPJob task, the code must be called with `future=True`
    or else the operation will occur synchronously.  This class is not intended for users to call
    directly.


    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    future            Required ccurrent.futures.Future.  The async object created by
                      the geoprocessing (GP) task.
    ----------------  ---------------------------------------------------------------
    gptool            Required Layer. The Geoprocessing Service
    ----------------  ---------------------------------------------------------------
    jobid             Required String. The unique ID of the GP Job.
    ----------------  ---------------------------------------------------------------
    task_url          Required String. The URL to the GP Task.
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
    #----------------------------------------------------------------------
    def __init__(self, future, gptool, jobid, task_url, gis, notify=False):
        """
        initializer
        """
        assert isinstance(future, Future)
        self._future = future
        if notify:
            self._future.add_done_callback(self._notify)
        self._gptool = gptool
        self._jobid = jobid
        self._url = task_url
        self._gis = gis
    #----------------------------------------------------------------------
    def _notify(self, future):
        """prints finished method"""
        jobid = str(self).replace("<", "").replace(">", "")
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
        return "<%s GP Job: %s>" % (self.task, self._jobid)
    #----------------------------------------------------------------------
    def __repr__(self):
        return "<%s GP Job: %s>" % (self.task, self._jobid)
    #----------------------------------------------------------------------
    @property
    def task(self):
        """Returns the task name.
        :returns: string
        """
        if self._task_name is None:
            self._task_name = os.path.basename(self._url)
        return self._task_name
    #----------------------------------------------------------------------
    @property
    def status(self):
        """
        returns the GP status

        :returns: String
        """
        url = self._url + "/jobs/%s" % self._jobid
        params = {'f' : 'json',
                  'returnMessages': True}


        res = self._gis._con.post(url, params)
        if 'jobStatus' in res:
            return res['jobStatus']
        return res
    #----------------------------------------------------------------------
    def cancel(self):
        """
        Attempt to cancel the call. If the call is currently being executed
        or finished running and cannot be cancelled then the method will
        return False, otherwise the call will be cancelled and the method
        will return True.

        :returns: boolean
        """
        if self.done():
            return False
        if self.cancelled():
            return False
        try:
            url = self._url + "/jobs/%s/cancel" % self._jobid
            params = {'f' : 'json'}
            res = self._gis._con.post(url, params)
            if 'jobStatus' in res:
                self._future.set_result({'jobStatus' : 'esriJobCancelled'})
                self._future.cancel()
                return True
            self._future.set_result({'jobStatus' : 'esriJobCancelled'})
            self._future.cancel()
            #self._future.set_result({'jobStatus' : 'esriJobCancelled'})
            return res
        except:
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
        if self.cancelled():
            return None
        if self._is_fa:
            return self._process_fa(self._future.result())
        elif self._is_ra:
            return self._process_fa(self._future.result())
        return self._future.result()

    def _process_fa(self, result):
        import arcgis
        if hasattr(result, '_fields'):
            r = {}
            iids = []
            for key in result._fields:
                value = getattr(result, key)
                if isinstance(value, dict) and 'featureSet' in value:
                    r[key] = arcgis.features.FeatureCollection(value)
                elif isinstance(value, dict) and 'itemId' in value and len(value['itemId']) > 0:
                    if not value['itemId'] in iids:
                        r[key] = arcgis.gis.Item(self._gis, value['itemId'])
                        iids.append(value['itemId'])
                elif len(str(value)) > 0 and value:
                    r[key] = value
            if len(r) == 1:
                return r[list(r.keys())[0]]

            return r
        else:
            value = result
            if len(value['itemId']) > 0:
                itemid = value['itemId']
                return arcgis.gis.Item(gis=self._gis, itemid=itemid)
            elif isinstance(value, dict) and 'featureSet' in value:
                return arcgis.features.FeatureCollection(value)
            return value
        return result

