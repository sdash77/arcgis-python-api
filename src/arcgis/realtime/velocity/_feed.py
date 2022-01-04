from ._task import Task


class Feed(Task):
    """
    Feed class implements Task and provides public facing methods to access Feeds API endpoints
    """

    _id = ""
    _gis = None
    _util = None
    _item = None

    def __init__(self, gis, util, item=None):
        self._gis = gis
        self._util = util
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
        Start the Feed for the given id

        :return: response of feed start

        .. code-block:: python

            # start feed
            
            # Method: <item>.start

            sample_feed.start()

        """
        return self._util._start("feed", self._id)

    # ----------------------------------------------------------------------
    def stop(self):
        """
        Stop the Feed for the given id
        Return True if the Feed was successfully stopped.

        :return: boolean

        .. code-block:: python

            # stop feed

            # Method: <item>.stop

            sample_feed.stop()

        """
        return self._util._stop("feed", self._id)

    # ----------------------------------------------------------------------
    @property
    def status(self):
        """
        Get the status of the running Feed for the given id
        :return: response of Feed status

        .. code-block:: python

            # Retrieve status of sample_feed

            # Method: <item>.status

            Sample_feed = feeds.get("id")
            status = sample_feed.status
            status
        """
        return self._util._status("feed", self._id)

    # ----------------------------------------------------------------------
    @property
    def metrics(self):
        """
        Get the metrics of the running Feed for the given id

        :return: response of feed metrics

        .. code-block:: python

            # Method: <item>.metrics
            
            # Retrieve metrics of sample_feed
            
            metrics = sample_feed.metrics
            metrics
        """
        return self._util._metrics("feed/metrics", self._id)

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Deletes an existing feed instance

        :return: A boolean containing True (for success) or
         False (for failure) a dictionary with details is returned.

        .. code-block:: python
            
            # Delete a feed
            
            # Method: <item>.delete()
                
            sample_feed.delete()
        """
        return self._util._delete("feed", self._id)
