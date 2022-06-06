from __future__ import annotations
from arcgis.gis import GIS


class MarketPlaceManager:
    """Provides the ability for Manager to list and unlist marketplace items"""

    _gis: GIS = None
    _url: str = None

    def __init__(self, gis: GIS):
        self._gis = gis
        self._url = f"{gis._portal.resturl}content"

    # ----------------------------------------------------------------------
    def list(self, itemid: str):
        """
        The `list_item` operation lists the item in the marketplace.

        This operation is only available to organizations that have permissions
        to list items in the marketplace. The permissions are returned with the
        Portal Self response.

        The listing properties must be specified for the item before
        calling this operation. This operation will fail if listing
        properties have not already been specified.

        Listing an item will set its listed property to true.

        This operation is available to the user and to the administrator
        of the organization to which the user belongs.

        :return: A dictionary indicating success or failure and the item id of the listed item.
        """
        params = {"f": "json"}
        url = f"{self._url}/users/{self._gis.users.me.username}/items/{itemid}/list"
        return self._gis._portal.con.post(url, params)

    # ----------------------------------------------------------------------
    def unlist(self, itemid: str):
        """
        The `unlist` operation unlists a previously listed item from the marketplace.

        Unlisting an item will reset its listed property to false.

        This operation is available to the user and the administrator of
        the organization to which the user belongs.

        :return: A dictionary indicating success or failure and the item id of the listed item.
        """
        params = {"f": "json"}
        url = f"{self._url}/users/{self._gis.users.me.username}/items/{itemid}/unlist"
        return self._gis._portal.con.post(url, params)

    # ----------------------------------------------------------------------
    def listings(
        self,
        query: str = "*",
        my_listings: bool = False,
        start: int = 1,
        num: int = 10,
        sort_field: str | None = None,
        sort_order: str = "asc",
    ):
        """
        This operation searches for marketplace listings. The searches are performed
        against a high performance index that indexes the most popular fields of a listing.

        By default, this search spans all public listings in the marketplace. However,
        if you're logged in as a vendor org admin and you specify the my_listings=true parameter,
        it then searches all public and private listings in your organization.


        ======================      =======================================================
        **Argument**                **Description**
        ----------------------      -------------------------------------------------------
        query                       Optional string. The query string to use to search.
        ----------------------      -------------------------------------------------------
        my_listings                 Optional boolean.  If True and you're logged in as
                                    a vendor org admin, it searches all public and private
                                    listings in your organization. Note that if my_listings=True,
                                    the query parameter is optional. Default is False.
        ----------------------      -------------------------------------------------------
        start                       Optional integer. The number of the first entry in the
                                    result set response. The index number is 1-based.

                                    The default value of start is 1. (i.e., the first search result).

                                    The start parameter, along with the num parameter,
                                    can be used to paginate the search results.
        ----------------------      -------------------------------------------------------
        num                         Optional integer. The maximum number of results to be
                                    included in the result set response.

                                    The default value is 10, and the maximum allowed value is 100.

                                    The start parameter, along with the num parameter,
                                    can be used to paginate the search results.

                                    Note that the actual number of returned results may be
                                    less than num. This happens when the number of results
                                    remaining after start is less than num.
        ----------------------      -------------------------------------------------------
        sort_field                  Optional string. The field to sort by. You can also sort
                                    by multiple fields (comma separated) for listings, sort
                                    field names are case-insensitive.

                                    Supported sort field names are:
                                    "title", "created", "listingpublisheddate", "type", "owner",
                                    "avgrating", "numratings", "numcomments", and "numviews".
        ----------------------      -------------------------------------------------------
        sort_order                  Optional string. Describes whether the order returns
                                    in ascending(asc) or descending(desc) order. Default is asc.
        ======================      =======================================================

        :return:
            A dictionary with response syntax of:
            {
                "query": "<query string>",
                "total": <total number of results>,
                "start": <results in first set>,
                "num": <number of results per page>,
                "nextStart": <result number of next page>,
                "listings": [
                    {<listing1>},
                    {<listing2>}
                ]
            }
        """
        url = f"{self._url}/listings"
        params = {
            "f": "json",
            "q": query,
            "mylistings": my_listings,
            "start": start,
            "num": num,
            "sortField": sort_field,
            "sortOrder": sort_order,
        }
        return self._gis._portal.con.get(url, params)
