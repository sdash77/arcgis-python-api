from typing import ClassVar

from arcgis.realtime.velocity.feeds.mqtt import MQTT


class CiscoEdgeIntelligence(MQTT):
    # FeedTemplate properties
    _name: ClassVar[str] = "kinetic"
