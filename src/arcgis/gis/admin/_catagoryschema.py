
########################################################################
class CategorySchemaManager(object):
    """
    This class allows for the addition, removal and viewing of category
    schema.

    """
    _url = None
    _gis = None
    _con = None

    #----------------------------------------------------------------------
    def __init__(self, gis):
        """Constructor"""
        self._gis = gis
        self._con = gis._con
        baseurl = gis._portal.resturl
        portal_id = None
        if portal_id is None:
            res = self._con.get("%s/portals/self" % baseurl,
                                params={'f': 'json'})
            if 'id' in res:
                pid = res['id']
            else:
                raise Exception("Could not find the portal's ID")
        self._url = "%sportals/%s" % (baseurl, pid)
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def schema(self):
        """
        Get/Sets the catagory schema for a GIS.

        When schema is used as a getter, then operation returns the GIS'
        defined category schema is any.

        When schema is used as a setter, the parameter:

        =======================    =============================================================
        **Argument**               **Description**
        -----------------------    -------------------------------------------------------------
        value                      optional list. The schema list.
                                   Syntax Example:
                                   [
                                    {
                                      "title": "Themes",
                                      "categories": [
                                        {
                                          "title": "Basemaps",
                                          "categories": [
                                            {"title": "Partner Basemap"},
                                            {
                                              "title": "Esri Basemaps",
                                              "categories": [
                                                {"title": "Esri Redlands Basemap"},
                                                {"title": "Esri Highland Basemap"}
                                              ]
                                            }
                                          ]
                                        },
                                    {
                                      "title": "Region",
                                      "categories": [
                                        {"title": "US"},
                                        {"title": "World"}
                                      ]
                                    }]}]
        =======================    =============================================================

        """
        url = "%s/categorySchema" % self._url
        params = {'f' : 'json'}
        return self._con.get(url, params)
    #----------------------------------------------------------------------
    @schema.setter
    def schema(self, value):
        """
        Get/Sets the catagory schema for a GIS.

        When schema is used as a getter, then operation returns the GIS'
        defined category schema is any.

        When schema is used as a setter, the parameter:

        =======================    =============================================================
        **Argument**               **Description**
        -----------------------    -------------------------------------------------------------
        value                      optional list. The schema list.
                                   Syntax Example:
                                   [
                                    {
                                      "title": "Themes",
                                      "categories": [
                                        {
                                          "title": "Basemaps",
                                          "categories": [
                                            {"title": "Partner Basemap"},
                                            {
                                              "title": "Esri Basemaps",
                                              "categories": [
                                                {"title": "Esri Redlands Basemap"},
                                                {"title": "Esri Highland Basemap"}
                                              ]
                                            }
                                          ]
                                        },
                                    {
                                      "title": "Region",
                                      "categories": [
                                        {"title": "US"},
                                        {"title": "World"}
                                      ]
                                    }]}]
        =======================    =============================================================

        """
        params = {'f' : 'json'}
        if value is not None:
            params['categorySchema'] = {"categorySchema": value}
            url = "%s/assignCategorySchema" % self._url

            self._con.post(path=url, postdata=params)
        elif value is None:
            url = "%s/deleteCategorySchema" % self._url
            self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def categorize(self, items, categories):
        """
        Assigns a category to a given set of items.
        """
        from arcgis.gis import Item
        res = []
        #if isinstance(categories)
        if isinstance(items, list):
            for item in items:
                res.append(item.update(item_properties={'categories' : ",".join(categories)}))
                del item
        elif isinstance(items, Item):
            res.append(item.update(item_properties={'categories' : ",".join(categories)}))
        #elif isinstance()
        return all(res)

