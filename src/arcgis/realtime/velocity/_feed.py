from arcgis._impl.common._mixins import PropertyMap

from ._task import Task


class Feed(Task):
    """
    Feed class implements Task and provides public facing methods to access Feeds API endpoints
    """

    _id = ""
    _gis = None
    _url = None
    _util = None
    _feed_item = None
    _serialized_object = None

    def __init__(self, url, gis, util, feed_item=None):
        self._gis = gis
        self._util = util
        self._feed_item = feed_item
        self._id = feed_item["id"]
        self._serialized_object = PropertyMap(self._feed_item)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "<%s id:%s label:%s>" % (
            type(self).__name__,
            self._id,
            self._feed_item["label"],
        )

    # ----------------------------------------------------------------------
    def start(self):
        """
        Start the Feed for the given id
        :return: response of feed start
        """
        return self._util._start("feed", self._id)

    # ----------------------------------------------------------------------
    def stop(self):
        """
        Stop the Feed for the given id
        Return True if the Feed was successfully stopped.
        :return: boolean
        """
        return self._util._stop("feed", self._id)

    # ----------------------------------------------------------------------
    def status(self):
        """
        Get the status of the running Feed for the given id
        :return: response of Feed status
        """
        return self._util._status("feed", self._id)

    # ----------------------------------------------------------------------
    def metrics(self):
        """
        Get the metrics of the running Feed for the given id
        :return: response of Feed metrics
        """
        return self._util._metrics("feed/metrics", self._id)

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Deletes an existing feed instance
        :return: A boolean containing True (for success) or
         False (for failure) a dictionary with details is returned.
        """
        return self._util._delete("feed", self._id)

    # ----------------------------------------------------------------------
    def serialized_object(self):
        """
        Feed items in form property names and values
        :return: A serialized object of feed item
        """
        return self._serialized_object
