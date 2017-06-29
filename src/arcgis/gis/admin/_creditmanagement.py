########################################################################
class CreditManager(object):
    """
    Manages an AGOL Site's Credits for users and sites
    """
    _gis = None
    _con = None
    _portal = None
    #----------------------------------------------------------------------
    def __init__(self, gis):
        """Constructor"""
        self._gis = gis
        self._portal = gis._portal
        self._con = self._portal.con
    #----------------------------------------------------------------------
    @property
    def credits(self):
        """returns the current number of credits on the GIS"""
        try:
            return self._gis.properties.availableCredits
        except:
            return 0
    #----------------------------------------------------------------------
    @property
    def is_enabled(self):
        """
        boolean that show is credit credit assignment
        """
        return self._gis.properties.creditAssignments == 'enabled'
    #----------------------------------------------------------------------
    def enable(self):
        """
        enables credit allocation on AGOL
        """
        return self._gis.update_properties(
            {"creditAssignments" : 'enabled'})
    #----------------------------------------------------------------------
    def disable(self):
        """
        disables credit allocation on AGOL
        """
        return self._gis.update_properties(
            {"creditAssignments" : 'disabled'})
    #----------------------------------------------------------------------
    @property
    def default_limit(self):
        """
        Gets/Sets the default credit allocation for AGOL
        """
        return self._gis.properties.defaultUserCreditAssignment
    #----------------------------------------------------------------------
    @default_limit.setter
    def default_limit(self, value):
        """
        Gets/Sets the default credit allocation for AGOL
        """
        params = {"defaultUserCreditAssignment" : value}
        self._gis.update_properties(params)
    #----------------------------------------------------------------------
    def allocate(self, username, credits=None):
        """
        Allows organization administrators to allocate credits for
        organizational users in ArcGIS Online

        Parameters:
        :param username: name of the user to assign credits to
        :param credits: number of credits to assign to a user. If None is
        provided, it sets user to unlimited credits.
        """
        if credits:
            params = {
                "f" : "json",
                "userAssignments" : [{"username" : username, "credits" : credits}]
            }
            path = "portals/self/assignUserCredits"
            res =  self._con.post(path, params)
            if 'success' in res:
                return res['success']
            return res
        else:
            return self.deallocate(username=username)
    #----------------------------------------------------------------------
    def deallocate(self, username):
        """
        Allows organization administrators to remove credit allocation for
        organizational users in ArcGIS Online

        Parameters:
        :param username: name whose credit allocation to be removed

        """
        params = {"usernames" : [username],
                  "f" : 'json'}
        path = "portals/self/unassignUserCredits"
        res = self._con.post(path, params)
        if 'success' in res:
            return res['success']
        return res
