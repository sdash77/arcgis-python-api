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
    def list(self, itemid: str) -> dict:
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
    def unlist(self, itemid: str) -> dict:
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
    ) -> dict:
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

    # ----------------------------------------------------------------------
    def listing(self, itemid: str) -> dict:
        """
        A listing in the marketplace. The listing and its corresponding item share the same ID.

        =====================       ========================================
        **Argument**                **Description**
        ---------------------       ----------------------------------------
        itemid                      Required String. The item id.
        =====================       ========================================

        :return:
            A dictionary of the listed item with properties.
        """
        params = {"f": "json"}
        url = f"{self._url}/listings/{itemid}"
        return self._gis._portal.con.get(url, params)

    # ----------------------------------------------------------------------
    def listing(self, itemid: str) -> dict:
        """
        A listing in the marketplace. The listing and its corresponding item share the same ID.

        =====================       ========================================
        **Argument**                **Description**
        ---------------------       ----------------------------------------
        itemid                      Required String. The item id.
        =====================       ========================================

        :return:
            A dictionary of the listed item with properties.
        """
        params = {"f": "json"}
        url = f"{self._url}/listings/{itemid}"
        return self._gis._portal.con.post(url, params)

    # ----------------------------------------------------------------------
    def delete_provision(self, itemid: str) -> dict:
        """
        This operation deletes all provisions to this item for
        the specified purchaser.

        This operation cannot be invoked if the item has not been provisioned
        to the specified purchaser.

        .. note::
            Only vendor org admins can invoke this operation.

        =====================       ========================================
        **Argument**                **Description**
        ---------------------       ----------------------------------------
        itemid                      Required String. The item id.
        =====================       ========================================

        :return:
            A dictionary with syntax:
            {
                "success": <true | false>,
                "itemId": "<itemId>",
                "purchaserOrgId": "<purchaserOrgId>"
            }
        """
        params = {"f": "json"}
        url = f"{self._url}/listings/{itemid}/deleteProvision"
        return self._gis._portal.con.post(url, params)

    # ----------------------------------------------------------------------
    def express_interest(self, itemid: str) -> dict:
        """
        A purchaser can express interest in a marketplace listing by
        invoking this operation.

        This operation cannot be invoked if the item has already been
        purchased or if the purchaser has previously expressed interest.

        Only administrators and members with request purchase information
        privilege of purchasing orgs can invoke this operation.

        Note that interests cannot be expressed for free listings, because
        they can be directly purchased by purchasing org admins or members
        with request purchase information privilege.

        =====================       ========================================
        **Argument**                **Description**
        ---------------------       ----------------------------------------
        itemid                      Required String. The item id.
        =====================       ========================================

        :return:
            A dictionary of the listed item with properties.
        """
        params = {"f": "json"}
        url = f"{self._url}/listings/{itemid}/interest"
        return self._gis._portal.con.post(url, params)

    # ----------------------------------------------------------------------
    def provision_user_entitlements(self, itemid: str, user_entitlements: dict) -> bool:
        """
        For a license-by-user listing, purchasing organization administrator
        can use this operation to provision entitlements to org
        members. It can only be made if the item has already been purchased,
        or is being tried by the purchasing org. A maximum of 25 users can
        be provisioned in one request.

        =====================       ==================================================================================
        **Argument**                **Description**
        ---------------------       ----------------------------------------------------------------------------------
        itemid                      Required String. The item id.
        ---------------------       ----------------------------------------------------------------------------------
        user_entitlements           Required Dictionary. A JSON object representing the set of entitlements
                                    assigned to the specified set of users.

                                    Example:
                                        {
                                        "users": ["username1", "username2"],
                                        "entitlements": ["standard", "networkAnalyst"] //"standard" is an entitlement string that uniquely identifies entitlement, listing itemId is used typically for provider apps
                                        }

                                    Only members of the purchasing org can be specified in the request.

                                    Specified entitlements are assigned to all specified users. If different sets of
                                    entitlements are to be assigned to different users, multiple requests
                                    with this operation are required.

                                    When there is no entitlements specified, it will revoke access to
                                    the item completely for the specified users.

                                    The total number of currently provisioned users plus users specified in requests
                                    should be no larger than the maximum number of users allowed for the purchasing org.
        =====================       ==================================================================================

        :return:
            A boolean indicating success (True) or failure (False).
        """
        params = {"f": "json", "userEntitlements": user_entitlements}
        url = f"{self._url}/listings/{itemid}"
        res = self._gis._portal.con.post(url, params)
        return res["success"]

    # ----------------------------------------------------------------------
    def purchase(
        self,
        itemid: str,
        purchase_org_id: str | None = None,
        provisioned_itemid: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        """
        =====================       ==================================================================================
        **Argument**                **Description**
        ---------------------       ----------------------------------------------------------------------------------
        itemid                      Required String. The item id.
        ---------------------       ----------------------------------------------------------------------------------
        purchase_org_id             Required String. The org ID of the purchaser organization. This parameter is required
                                    only when the call is made by the vendor. It is ignored otherwise.
        ---------------------       ----------------------------------------------------------------------------------
        provisioned_itemid          Required String. The ID of the item to be provisioned if different from the one listed.

                                    Note that the listed item and the provisioned item must be related by the
                                    "Listed2Provisioned" relationship otherwise it will result in an error.

                                    This parameter is allowed only when the call is made by the vendor. It is ignored otherwise.
        ---------------------       ----------------------------------------------------------------------------------
        end_date                    Required String. The end/expiry date of this purchase if any. If this parameter is
                                    not specified, it implies an unexpiring purchase. The end date specified
                                    should be in milliseconds from epoch.
        =====================       ==================================================================================

        :return: A dictionary of the provision item.
        """

        params = {
            "f": "json",
            "purchaseOrgId": purchase_org_id,
            "provisionedItemId": provisioned_itemid,
            "endDate": end_date,
        }
        url = f"{self._url}/listings/{itemid}/purchase"
        return self._gis._portal.con.post(url, params)

    # ----------------------------------------------------------------------
    def trial(self, itemid) -> dict:
        """
        A purchaser can start a trial for a marketplace listing by invoking this operation.

        This operation is only supported for listings that support trials
        (whose trialSupported property is true). Once started, the trial will be valid
        for the duration of the trial specified on the listing (the trialDuration property).

        This operation cannot be invoked if the item has already been purchased or
        if the purchaser has started a trial previously.

        Only admins or members with request purchase information privilege of
        purchasing orgs can invoke this operation.

        =====================       ==================================================================================
        **Argument**                **Description**
        ---------------------       ----------------------------------------------------------------------------------
        itemid                      Required String. The item id.
        =====================       ==================================================================================

        :return: A dictionary of the provision item.
        """
        params = {"f": "json"}
        url = f"{self._url}/listings/{itemid}/trial"
        return self._gis._portal.con.post(url, params)
