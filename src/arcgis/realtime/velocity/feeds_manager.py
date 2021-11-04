from ._feed import Feed
from ._util import _Util
import logging

_LOGGER = logging.getLogger(__name__)


class FeedsManager:
    """
    Used to manage Feeds
    """

    _gis = None
    _util = None

    def __init__(self, url, gis):
        """
        :param url: Base url of Velocity.
        :param gis: An authenticated arcigs.gis.GIS object.
        """
        self._gis = gis
        self._util = _Util(gis, url)

    # ----------------------------------------------------------------------
    @property
    def items(self):
        """
        Get all Feeds
        :return: returns a collection of all configured Feed tasks
        """
        all_feeds_response = self._util._get_request("feeds")
        if all_feeds_response is not None and type(all_feeds_response) is list:
            feed_items = [
                Feed(self._gis, self._util, feed) for feed in all_feeds_response
            ]
            return feed_items
        elif all_feeds_response is None:
            _LOGGER.warning("No Feed items found for the user.")
            return []
        else:
            raise Exception(
                f"Error retrieving Feed items. Velocity response: ${all_feeds_response}"
            )

    # ----------------------------------------------------------------------
    def get(self, id):
        """
        Get Feed by id
        :param id: unique id of a Feed
        :return: endpoint response of Feed for the given id
        """
        feed_item = self._util._get("feed", id)
        return Feed(self._gis, self._util, feed_item)

    # ----------------------------------------------------------------------
    # TODO: need to decide what return type we want here Boolean or simple label and id of newly created feed
    def create(self, feed=None):
        """
        Creates a new feed configuration
        :param feed: an instance of Feed like RSS, HTTPoller etc.
        :return: Id and label of the newly created feed
        """
        if feed is None:
            raise "Feed not found"
        else:
            feed_configuration = feed._build()
            response = self._util._post_request(
                "feed", id=None, payload=feed_configuration
            )
            if response is not None:
                return self.get(response["id"])
