from arcgis._impl.common._mixins import PropertyMap

from ._task import Task


class BigDataAnalytics(Task):
    """
     BigDataAnalytics class implements Task and provides public facing methods to
     access BigDataAnalytics API endpoints
    """
    _id = ""
    _gis = None
    _url = None
    _util = None
    _bigdata_analytics_item = None
    _serialized_object = None

    def __init__(self, gis, util, bigdata_analytics_item=None):
        self._gis = gis
        self._util = util

        if bigdata_analytics_item:
            self._bigdata_analytics_item = bigdata_analytics_item
            self._id = bigdata_analytics_item['id']
            self._serialized_object = PropertyMap(self._bigdata_analytics_item)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "<%s id:%s label:%s>" % (type(self).__name__, self._id, self._bigdata_analytics_item['label'])

    # ----------------------------------------------------------------------
    def start(self):
        """
       Start the Big Data Analytics for the given id
       :return: response of bigdata_analytics start
       """
        return self._util._start("analytics/bigdata", self._id)

    # ----------------------------------------------------------------------
    def stop(self):
        """
       Stop the Big Data Analytics for the given id
       :return: response of bigdata_analytics stop
       """
        return self._util._stop("analytics/bigdata", self._id)

    # ----------------------------------------------------------------------
    def status(self):
        """
        Get the status of the running Big Data Analytics for the given id
        :return: response of Big Data Analytics status
        """
        return self._util._status("analytics/bigdata", self._id)

    # ----------------------------------------------------------------------
    def metrics(self):
        """
        Get the metrics of the running Big Data Analytics for the given id
        :return: response of Big Data Analytics metrics
        """
        return self._util._metrics("analytics/bigdata/metrics", self._id)

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Deletes an existing Big Data Analytics instance
        :return: response for Big Data Analytics item deleted
        """
        return self._util._delete("analytics/bigdata", self._id)

    # ----------------------------------------------------------------------
    def serialized_object(self):
        """
        Big Data Analytics items in form property names and values
        :return: A serialized object of bigdata_analytics item
        """
        return self._serialized_object
