from arcgis._impl.common._mixins import PropertyMap

from ._task import Task


class RealTimeAnalytics(Task):
    """
     RealTimeAnalytics class implements Task and provides public facing methods to
     access RealTimeAnalytics API endpoints
    """
    _id = ""
    _gis = None
    _url = None
    _util = None
    _realtime_analytics_item = None
    _serialized_object = None

    def __init__(self, gis, util, realtime_analytics_item=None):
        self._gis = gis
        self._util = util

        if realtime_analytics_item:
            self._realtime_analytics_item = realtime_analytics_item
            self._id = realtime_analytics_item['id']
            self._serialized_object = PropertyMap(self._realtime_analytics_item)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "<%s id:%s label:%s>" % (type(self).__name__, self._id, self._realtime_analytics_item['label'])

    # ----------------------------------------------------------------------
    def start(self):
        """
       Start the Real-Time Analytics for the given id
       :return: response of realtime_analytics start
       """
        return self._util._start("analytics/realtime", self._id)

    # ----------------------------------------------------------------------
    def stop(self):
        """
       Stop the Real-Time Analytics for the given id
       :return: response of realtime_analytics stop
       """
        return self._util._stop("analytics/realtime", self._id)

    # ----------------------------------------------------------------------
    def status(self):
        """
        Get the status of the running Real-Time Analytics for the given id
        :return: response of Real-Time Analytics status
        """
        return self._util._status("analytics/realtime", self._id)

    # ----------------------------------------------------------------------
    def metrics(self):
        """
        Get the metrics of the running Real-Time Analytics for the given id
        :return: response of Real-Time Analytics metrics
        """
        return self._util._metrics("analytics/realtime/metrics", self._id)

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Deletes an existing Real-Time Analytics task instance
        :return: response for Real-Time Analytics item deleted
        """
        return self._util._delete("analytics/realtime", self._id)

    # ----------------------------------------------------------------------
    def serialized_object(self):
        """
        Real-Time Analytics items in form property names and values
        :return: A serialized object of realtime_analytics item
        """
        return self._serialized_object
