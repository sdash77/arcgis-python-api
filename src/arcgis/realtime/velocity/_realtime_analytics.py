from ._task import Task


class RealTimeAnalytics(Task):
    """
    RealTimeAnalytics class implements Task and provides public facing methods to
    access RealTimeAnalytics API endpoints
    """

    _id = ""
    _gis = None
    _util = None
    _item = None

    def __init__(self, gis, util, item=None):
        self._gis = gis
        self._util = util

        if item:
            self._item = item
            self._id = item["id"]

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "<%s id:%s label:%s>" % (
            type(self).__name__,
            self._id,
            self._item["label"],
        )

    # ----------------------------------------------------------------------
    def start(self):
        """
        Start the Real-Time Analytics for the given id

        :return: response of realtime_analytics start

        .. code-block:: python

            # Start real-time analytics

            # Method: <item>.start()
            
            sample_realtime_task.start()

        """
        return self._util._start("analytics/realtime", self._id)

    # ----------------------------------------------------------------------
    def stop(self):
        """
        Stop the Real-Time Analytics for the given id
        Return True if the the Real-Time Analytics was successfully stopped.

        :return: boolean

        .. code-block:: python

            # Stop real-time analytics

            # Method: <item>.stop()
            
            sample_realtime_task.stop()

        """
        return self._util._stop("analytics/realtime", self._id)

    # ----------------------------------------------------------------------
    @property
    def status(self):
        """
        Get the status of the running Real-Time Analytics for the given id

        :return: response of Real-Time Analytics status

        .. code-block:: python

            # Retrieve status of real-time analytics task

            # Property: <item>.status()
            
            status = sample_realtime_task.status
            status

        """
        return self._util._status("analytics/realtime", self._id)

    # ----------------------------------------------------------------------
    @property
    def metrics(self):
        """
        Get the metrics of the running Real-Time Analytics for the given id

        :return: response of Real-Time Analytics metrics

        .. code-block:: python

            # Retrieve metrics of real-time analytics task

            # Property: <item>.metrics()
            
            metrics = sample_realtime_task.metrics
            metrics

        """
        return self._util._metrics("analytics/realtime/metrics", self._id)

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Deletes an existing Real-Time Analytics task instance

        :return: A boolean containing True (for success) or False (for failure) a dictionary with details is returned.

        .. code-block:: python

            # Delete a real-time analytics 

            # Method: <item>.delete()
            
            sample_realtime_task.delete

        """
        return self._util._delete("analytics/realtime", self._id)
