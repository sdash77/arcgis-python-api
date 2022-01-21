"""
The ``arcgis.geoenrichment`` module enables data driven Human Geography workflows through access to Esri’s rich
demographic data, standard geographies and reporting capabilities. Access to thousands of demographic variables
available for most countries worldwide enables data driven exploration of questions about how people interact with
their surroundings. While these questions frequently involve commercial applications, increasingly they are starting to
include public policy questions as well.

Commercial questions commonly include site selection and store forecasting. When selecting a new site for a retail
store or even a distribution center, it is necessary to understand who lives in the surrounding area. If a retail
store, knowing who lives in the area surrounding the store, especially knowing detailed quantitative demographic
details, enables forecasting the revenue the potential location will generate. This enables much more informed decision
making to select the best locations for a new store.

If the site selection is for a new distribution center, just as important as who the location will serve is knowing
who is available to work in the distribution center. If the area already has a large population of skilled workers,
finding labor to work in the distribution center will be significantly easier. Similarly, once stores are in place,
knowing detailed information about the people in the surrounding area enables forecasting revenue for these existing
store locations. This is especially important as markets evolve due to demographic shifts and competitive pressures.

Far from being the only applications, site selection and forecasting are two very common examples of how the
``arcgis.geoenrichment`` module is used. Since such a powerful Human Geography tool, increasingly this module is being
used to answer public policy questions such as understanding social equity.

Understanding how areas where people are similar enables understanding where people are different. The
``arcgis.geoenrichment`` module, by providing access to rich demographic data, enables data driven workflows to group
people based on their demographic characteristics (clustering). Defining characteristics for each area can then be
identified (feature selection) to better understand the challenges people are facing and meet the needs of a community.
While far from the only application, this is just one example of how ``arcgis.geoenrichent`` can be used to understand
and answer Human Geography public policy questions.
"""

__all__ = [
    "BufferStudyArea",
    "Country",
    "get_countries",
    "create_report",
    "enrich",
    "standard_geography_query",
    "service_limits",
]

from .enrichment import (
    BufferStudyArea,
    Country,
    get_countries,
    create_report,
    enrich,
    standard_geography_query,
    service_limits,
)
