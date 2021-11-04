from dataclasses import dataclass, asdict, field
from typing import Dict, Union, Optional, Any, ClassVar
import pytz


@dataclass(frozen=True)
class RunInterval:
    """
    Set the run interval for the feed.
    :param cron_expression: Cron Expression that specifies the run interval. Please use the following link to generate the cron expression: FIXME: <cron_expression_generator_url>
                            Default value - if nothing is specified following expresion will be used to configure the feed:
                                            "0 * * ? * * *" - Runs every minute
    :param timezone: run interval timezone to use. refer: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for strings
                    Default value - "America/Los_Angeles"
    """

    cron_expression: str
    timezone: str = field(default="America/Los_Angeles")

    def __post_init__(self):
        if self.cron_expression in (None, ""):
            raise ValueError("Cron expression cannot be empty or None")
        elif self.timezone not in pytz.all_timezones:
            raise ValueError("Invalid time zone string")

    def _build(self):
        return {
            "recurrence": {
                "expression": self.cron_expression,
                "timeZone": self.timezone,
            }
        }
