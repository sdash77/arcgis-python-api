from typing import Union, Optional, ClassVar
from dataclasses import field, dataclass

from arcgis.realtime import Velocity
from arcgis.realtime.velocity.feeds._feed_template import _FeedTemplate
from arcgis.realtime.velocity.feeds.geometry import (
    _HasGeometry,
    SingleFieldGeometry,
    XYZGeometry,
)
from arcgis.realtime.velocity.feeds.time import _HasTime, TimeInstant, TimeInterval
from arcgis.realtime.velocity.input.format import (
    DelimitedFormat,
    _format_from_config,
)


@dataclass
class HttpSimulator(_FeedTemplate, _HasTime, _HasGeometry):
    """
    ==================              ====================================================================
    **Argument**                    **Description**
    ------------------              --------------------------------------------------------------------
    label                           str. Unique label for this feed instance.
    ------------------              --------------------------------------------------------------------
    description                     str. Feed description.
    ------------------              --------------------------------------------------------------------
    url                             str. Address of the HTTP endpoint providing data.
    ------------------              --------------------------------------------------------------------
    field_separator                 str. Delimited field separator
                                    default value - ","
    ------------------              --------------------------------------------------------------------
    features_per_execution          int.
                                    default value - 1
    ------------------              --------------------------------------------------------------------
    interval_for_sending_events     int. Time in milliseconds
                                    default value - 1000
    ------------------              --------------------------------------------------------------------
    repeat_simulation               bool.
                                    default value - True
    ------------------              --------------------------------------------------------------------
    time_field_index                int.
                                    default value - 0
    ------------------              --------------------------------------------------------------------
    convert_to_current_time         bool.
                                    default value - True
    ------------------              --------------------------------------------------------------------

    **Optional Argument**           **Description**
    ------------------              --------------------------------------------------------------------
    data_format                     Union[DelimitedFormat].
                                    An instance that contains the data-format
                                    configuration for this feed. Configure only allowed formats.
                                    If this is not set right during initialization, a format will be
                                    auto-detected and set from a sample of the incoming data. This sample
                                    will be fetched from the configuration provided so far in the init.
    ------------------              --------------------------------------------------------------------
    track_id_field                  str. name of the field from the incoming data that should be set as
                                    track_id.
    ------------------              --------------------------------------------------------------------
    geometry                        Union[XYZGeometry, SingleFieldGeometry]. An instance of geometry configuration
                                    that will be used to create geometry objects from the incoming data.
    ------------------              --------------------------------------------------------------------
    time                            Union[TimeInstant, TimeInterval]. An instance of time configuration that
                                    will be used to create time info from the incoming data.
    ==================              ====================================================================
    """

    # fields that the user sets during init
    # HTTP Simulator specific properties
    url: str
    field_separator: str = field(default=",")
    features_per_execution: int = field(default=1)
    interval_for_sending_events: int = field(default=1000)
    repeat_simulation: bool = field(default=True)
    time_field_index: int = field(default=0)
    convert_to_current_time: bool = field(default=True)

    # user can define these properties even after initialization
    data_format: Optional[Union[DelimitedFormat]] = None
    # FeedTemplate properties
    track_id_field: Optional[str] = None
    # HasGeometry properties
    geometry: Optional[Union[XYZGeometry, SingleFieldGeometry]] = None
    # HasTime properties
    time: Optional[Union[TimeInstant, TimeInterval]] = None

    # FeedTemplate properties
    _name: ClassVar[str] = "simulator"

    def __post_init__(self):
        if Velocity is None:
            return
        self._util = Velocity._util

        # validation of fields
        if self._util.is_valid(self.label) == False:
            raise ValueError(
                "Label should only contain alpha numeric, _ and space only"
            )

        # generate dictionary of this feed object's properties that will be used to query test-connection and
        # sample-messages Rest endpoint
        feed_properties = self._generate_feed_properties()

        test_connection = self._util.test_connection(
            input_type="feed", payload=feed_properties
        )
        # Test connection to make sure feed can fetch schema
        if test_connection is True:
            # test connection succeeded. Now try getting sample messages
            sample_payload = {
                "properties": {
                    "maxSamplesToCollect": 5,
                    "timeoutInMillis": 5000,
                }
            }
            self._dict_deep_merge(sample_payload, feed_properties)
            # Sample messages to fetch schema/fields
            sample_messages = self._util.sample_messages(
                input_type="feed", payload=sample_payload
            )

            if sample_messages["featureSchema"] is not None:
                # sample messages succeeded. Get Feature Schema from it
                self._set_fields(sample_messages["featureSchema"])

            # if Format was not specified by user, use the auto-detected format from the sample messages response as this feed object's format.
            if self.data_format is None:
                self.data_format = _format_from_config(sample_messages)

            print(
                "Feature Schema retrieved from the Feed:",
                sample_messages["featureSchema"],
            )

            # initiate actions for each of the following properties if it was set at init
            if self.track_id_field is not None:
                self.set_track_id(self.track_id_field)
            if self.geometry is not None:
                self.set_geometry_config(self.geometry)
            if self.time is not None:
                self.set_time_config(self.time)

    def _build(self) -> dict:
        feed_configuration = {
            "id": "",
            "label": self.label,
            "description": self.description,
            "feed": {**self._generate_schema_transformation()},
            "properties": {"executable": True},
        }

        feed_properties = self._generate_feed_properties()
        self._dict_deep_merge(feed_configuration["feed"], feed_properties)
        print(feed_configuration)
        return feed_configuration

    def _generate_feed_properties(self) -> dict:
        feed_properties = {
            "name": self._name,
            "properties": {
                f"{self._name}.url": self.url,
                f"{self._name}.fieldSeparator": self.field_separator,
                f"{self._name}.featuresPerTime": self.features_per_execution,
                f"{self._name}.repeat": self.repeat_simulation,
                f"{self._name}.intervalInMillis": self.interval_for_sending_events,
                f"{self._name}.timeFieldIndex": self.time_field_index,
                f"{self._name}.setToCurrentTime": self.convert_to_current_time,
            },
        }

        if self.data_format is not None:
            format_dict = self.data_format._build()
            self._dict_deep_merge(feed_properties, format_dict)

        return feed_properties
