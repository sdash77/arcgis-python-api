from .bigdata_analytics_manager import BigDataAnalyticsManager
from .feeds_manager import FeedsManager
from .realtime_analytics_manager import RealTimeAnalyticsManager


class Velocity:
    _gis = None
    _url = None
    _subinfo = None
    _velocity = None
    # manager instances
    _feeds_manager = None
    _realtime_manager = None
    _bigdata_manager = None

    def __init__(self, url, gis):
        self._gis = gis
        self._url = url

    @property
    def feeds_manager(self):
        """
        Provides access to managing configured Feeds with ArcGIS Velocity

        :return: FeedsManager
        """
        if self._feeds_manager is None:
            self._feeds_manager = FeedsManager(url=self._url, gis=self._gis)
        return self._feeds_manager

    @property
    def realtime_analytics_manager(self):
        """
        Provides access to managing configured Real-time analytics tasks with ArcGIS Velocity

       :return: RealTimeAnalyticsManager
       """
        if self._realtime_manager is None:
            self._realtime_manager = RealTimeAnalyticsManager(url=self._url, gis=self._gis)
        return self._realtime_manager

    @property
    def bigdata_analytics_manager(self):
        """
         Provides access to managing configured Big data analytics tasks with ArcGIS Velocity

        :return: BigDataAnalyticsManager
        """
        if self._bigdata_manager is None:
            self._bigdata_manager = BigDataAnalyticsManager(url=self._url, gis=self._gis)
        return self._bigdata_manager
