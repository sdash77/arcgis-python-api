"""
The arcgis.lyr module is used for accessing layers exposed from ArcGIS Online
or Portal.
"""
from __future__ import absolute_import
import arcgis.gis
import json
from pandas.io.json import json_normalize
import collections
from ._impl import *

class ImageLayer(collections.OrderedDict):
    "represents an image service layer"
    def __init__(self, item):
        """
        Constructs an Image Service Layer given it's item from ArcGIS Online or Portal.
        """
        if item.type.lower() != 'image service':
            raise TypeError("item type must be image service")
        self.url = item.url
        self.item = item
        self._portal = item._portal
        params = {
            "f" : "json"
        }
        properties = {}
        add_token = False
        if self.item['access'] != 'public':
            add_token = True

        properties = self.item._portal.con.post(self.url, params, add_token=add_token)

        #try:
        #    properties = self.item._portal.con.post(self.url, params)
        #except:
        #    pass
            #TODO - why does token not work for public access?
        #if self.item['access'] != 'public':
        #properties.update({"url" : self.url + "?token=" + self.item._portal.con.token })
        #else:
        properties.update({"url" : self.url})

        collections.OrderedDict.__init__(self, properties)

    def __str__(self):
        return json.dumps(self)

class FeatureService(object):
    "represents a feature service"
    def __init__(self, item):
        """
        Constructs a Feature Service object given it's item from ArcGIS Online or Portal.
        """
        if item.type.lower() != 'feature service':
            raise TypeError("item type must be feature service")
        self.url = item.url
        self.item = item


        layers = []

        #print("URL of Feature Service: " + self.url)
        import re
        m = re.search(r'\d+$', self.url)
        # if the string ends in digits m will be a Match object, or None otherwise.
        if m is not None:
            layers.append(Layer(self.url, None, self.item))
        else:
            fsurl = self.url + '/layers'
            params = {
                "f" : "json"
            }

            allayers = self.item._portal.con.post(fsurl, params)
            try:
                for layer in allayers['layers']:
                    layers.append(Layer(self.url, layer, self.item))
                    #print("***" + str(layer))
                    #lyr_type = layer['type']
                    #lyr_url = self.url + '/' + str(layer['id'])
                    #layers.append({"type": lyr_type, "url" : lyr_url.replace(' ', '%20')})
            except:
                layers.append(Layer(self.url, allayers, self.item))

        #print(str(layers))
        self.layers = layers

    def __str__(self):
        return "Feature service at " + self.url

class Layer(collections.OrderedDict):
    """
    """
    def __init__(self, svcurl, dictdata, item=None, gis=None):
        """
        Constructs a layer given it's data
        """
        if dictdata is None:
            dictdata = {}
            lyr_url = svcurl
        else:
            lyr_url = svcurl + '/' + str(dictdata['id'])

        self.url = lyr_url #.replace(' ', '%20')

        if item is not None:
            self._portal = item._portal
        elif gis is not None:
            self._portal = gis._portal
        else:
            print("Item or GIS must be passed")

        data = dictdata
        data.update({ "url" : self.url })
        #print(self.url)
        collections.OrderedDict.__init__(self, data)

    def __str__(self):
        return json.dumps(self)

    def query(self,
              where="1=1",
              out_fields="*",
              timeFilter=None,
              geometryFilter=None,
              returnGeometry=True,
              returnIDsOnly=False,
              returnCountOnly=False,
              returnFeatureClass=False,
              returnDistinctValues=False,
              returnExtentOnly=False,
              groupByFieldsForStatistics=None,
              statisticFilter=None,
              out_fc=None,
              objectIds="",
              **kwargs):
        """ queries a feature service based on a sql statement
            Inputs:
               where - the selection sql statement
               out_fields - the attribute fields to return
               timeFilter - a TimeFilter object where either the start time
                            or start and end time are defined to limit the
                            search results for a given time.  The values in
                            the timeFilter should be as UTC timestampes in
                            milliseconds.  No checking occurs to see if they
                            are in the right format.
               geometryFilter - a GeometryFilter object to parse down a given
                               query by another spatial dataset.
               returnGeometry - true means a geometry will be returned,
                                else just the attributes
               returnIDsOnly - false is default.  True means only OBJECTIDs
                               will be returned
               returnCountOnly - if True, then an integer is returned only
                                 based on the sql statement
               returnFeatureClass - Default False. If true, query will be
                                    returned as feature class
               groupByFieldsForStatistics - One or more field names on
                                    which the values need to be grouped for
                                    calculating the statistics.
               statisticFilter - object that performs statistic queries
               out_fc - only valid if returnFeatureClass is set to True.
                        Output location of query.
               kwargs - optional parameters that can be passed to the Query
                 function.  This will allow users to pass additional
                 parameters not explicitly implemented on the function. A
                 complete list of functions available is documented on the
                 Query REST API.
            Output:
               A list of Feature Objects (default) or a path to the output featureclass if
               returnFeatureClass is set to True.
         """
        params = {"f": "json",
                  "where": where,
                  "outFields": out_fields,
                  "returnGeometry" : returnGeometry,
                  "returnIdsOnly" : returnIDsOnly,
                  "returnCountOnly" : returnCountOnly,
                  "returnDistinctValues" : returnDistinctValues,
                  "returnExtentOnly" : returnExtentOnly
                  }
        for key, value in kwargs.items():
            params[key] = value
        if not timeFilter is None and \
           isinstance(timeFilter, filters.TimeFilter):
            params['time'] = timeFilter.filter
        if not geometryFilter is None and \
           isinstance(geometryFilter, filters.GeometryFilter):
            gf = geometryFilter.filter
            params['geometry'] = gf['geometry']
            params['geometryType'] = gf['geometryType']
            params['spatialRelationship'] = gf['spatialRel']
            params['inSR'] = gf['inSR']
        if objectIds is not None and objectIds != "":
            params['objectIds'] = objectIds
        if not groupByFieldsForStatistics is None:
            params['groupByFieldsForStatistics'] = groupByFieldsForStatistics
        if not statisticFilter is None and \
           isinstance(statisticFilter, filters.StatisticFilter):
            params['outStatistics'] = statisticFilter.filter
        fURL = self.url + "/query"
        #print(fURL)
        results = self._portal.con.post(fURL, params)

        if 'error' in results:
            raise ValueError (results)
        if not returnCountOnly and not returnIDsOnly:
            if returnFeatureClass == True:
                #json_text = json.dumps(results)
                #return results
                df = json_normalize(results['features'])
                df.columns = df.columns.str.replace('attributes.', '')
                return df
            else:
                #return results #FeatureSet.fromJSON(json.dumps(results))
                #print(results)
                df = json_normalize(results['features'])
                df.columns = df.columns.str.replace('attributes.', '')
                return df
        else:
            return results
        return

class FeatureCollection(collections.OrderedDict):
    """
    """
    def __init__(self, dictdata):
        """
        Constructs a feature collection given it's data
        """
        if isinstance(dictdata, arcgis.gis.Item):
            fcdict = dictdata.get_data()
            collections.OrderedDict.__init__(self, fcdict)
        else:
            fcdict = dictdata
            collections.OrderedDict.__init__(self, fcdict)

    def __str__(self):
        return json.dumps(self)

    def to_df(self): #TODO
        if 'layers' in self:
            df = json_normalize(self['layers'][0]['featureSet']['features'])
        else:
            df = json_normalize(self['featureSet']['features'])

        df.columns = df.columns.str.replace('attributes.', '')
        return df
