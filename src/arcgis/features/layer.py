"""
Feature Layers and Tables provide the primary interface for working with features in a GIS.

Users create, import, export, analyze, edit, and visualize features, i.e. “entities in space” as feature layers.

A FeatureDataset is a collection of feature layers and tables, with the associated relationships among the entities.
"""
import json
import os
from re import search

import six
from arcgis._impl.common import _utils
from arcgis._impl.common._filters import StatisticFilter, TimeFilter, GeometryFilter
from arcgis._impl.common._mixins import PropertyMap
from arcgis._impl.common._spatial import scratchGDB, scratchFolder, json_to_featureclass
from arcgis._impl.common._utils import _date_handler

from .managers import AttachmentManager, ReplicaManager, FeatureDatasetManager, FeatureLayerManager
from .feature import Feature, FeatureSet
from arcgis.geom import SpatialReference
from arcgis.lyr import Layer, GISService


class FeatureLayer(Layer):
    """
    The feature layer is the primary concept for working with features in a GIS.

    Users create, import, export, analyze, edit, and visualize features, i.e. “entities in space” as feature layers.

    Feature layers can be added to and visualized using maps. They act as inputs to and outputs from feature analysis
    tools.

    Feature layers are created by publishing feature data to a GIS, and are exposed as a broader resource (Item) in the
    GIS. Feature layer objects can be obtained through the layers attribute on feature layer Items in the GIS.
    """
    def __init__(self, url, gis=None, storage=None):
        """
        Constructs a feature layer given a feature layer URL
        :param url: feature layer url
        :param gis: optional, the GIS that this layer belongs to. Required for secure feature layers.
        :param storage: optional, the feature dataset to which this layer belongs
        """
        super(FeatureLayer, self).__init__(url, gis)
        self.storage = storage
        self.attachments = AttachmentManager(self)

    @property
    def manager(self):
        """
        Helper object to manage the feature layer, update it's definition, etc
        """
        url = self._url
        res = search("/rest/", url).span()
        add_text = "admin/"
        part1 = url[:res[1]]
        part2 = url[res[1]:]
        admin_url = "%s%s%s" % (part1, add_text, part2)

        res = FeatureLayerManager(admin_url, self._gis)
        return res

    def _add_attachment(self, oid, file_path):
        """ Adds an attachment to a feature service
            Input:
              oid - string - OBJECTID value to add attachment to
              file_path - string - path to file
            Output:
              JSON Repsonse
        """
        attach_url = self._url + "/%s/addAttachment" % oid
        params = {'f': 'json'}

        files = {'attachment': file_path}
        res = self._con.post(path=attach_url,
                             postdata=params,
                             files=files, token=self._token)
        return res

    # ----------------------------------------------------------------------
    def _delete_attachment(self, oid, attachment_id):
        """ removes an attachment from a feature service feature
            Input:
              oid - integer or string - id of feature
              attachment_id - integer - id of attachment to erase
            Output:
               JSON response
        """
        url = self._url + "/%s/deleteAttachments" % oid
        params = {
            "f": "json",
            "attachmentIds": "%s" % attachment_id
        }
        return self._con.post(url, params, token=self._token)

    # ----------------------------------------------------------------------
    def _update_attachment(self, oid, attachment_id, file_path):
        """ updates an existing attachment with a new file
            Inputs:
               oid - string/integer - Unique record ID
               attachment_id - integer - Unique attachment identifier
               file_path - string - path to new attachment
            Output:
               JSON response
        """
        url = self._url + "/%s/updateAttachment" % oid
        params = {
            "f": "json",
            "attachmentId": "%s" % attachment_id
        }
        files = {'attachment': file_path}
        res = self._con.post(path=url,
                             postdata=params,
                             files=files, token=self._token)
        return res

    # ----------------------------------------------------------------------
    def _list_attachments(self, oid):
        """ list attachements for a given OBJECT ID """
        url = self._url + "/%s/attachments" % oid
        params = {
            "f": "json"
        }
        return self._con.get(path=url, params=params, token=self._token)

    # ----------------------------------------------------------------------
    def query(self,
              where="1=1",
              out_fields="*",
              time_filter=None,
              geometry_filter=None,
              return_geometry=True,
              return_count_only=False,
              return_ids_only=False,
              return_feature_class=False,
              return_distinct_values=False,
              return_extent_only=False,
              group_by_fields_for_statistics=None,
              statistic_filter=None,
              result_offset=None,
              result_record_count=None,
              out_fc=None,
              object_ids=None,
              distance=None,
              units=None,
              max_allowable_offset=None,
              out_sr=None,
              geometry_precision=None,
              gdb_version=None,
              order_by_fields=None,
              out_statistics=None,
              return_z=False,
              return_m=False,
              multipatch_option=None,
              quanitization_parameters=None,
              return_centroid=False,
              as_obj=False,
              as_dict=False,
              **kwargs):
        """ queries a feature service based on a sql statement
            Inputs:
                where - the selection sql statement
                out_fields - the attribute fields to return
                objectIds -  The object IDs of this layer or table to be
                            queried.
                distance - The buffer distance for the input geometries.
                          The distance unit is specified by units. For
                          example, if the distance is 100, the query
                          geometry is a point, units is set to meters, and
                          all points within 100 meters of the point are
                          returned.
                units - The unit for calculating the buffer distance. If
                        unit is not specified, the unit is derived from the
                        geometry spatial reference. If the geometry spatial
                        reference is not specified, the unit is derived
                        from the feature service data spatial reference.
                        This parameter only applies if
                        supportsQueryWithDistance is true.
                        Values: esriSRUnit_Meter | esriSRUnit_StatuteMile |
                        esriSRUnit_Foot | esriSRUnit_Kilometer |
                        esriSRUnit_NauticalMile | esriSRUnit_USNauticalMile
                timeFilter - a TimeFilter object where either the start time
                            or start and end time are defined to limit the
                            search results for a given time.  The values in
                            the timeFilter should be as UTC timestampes in
                            milliseconds.  No checking occurs to see if they
                            are in the right format.
                geometryFilter - a GeometryFilter object to parse down a given
                               query by another spatial dataset.
                maxAllowableOffset - This option can be used to specify the
                                     maxAllowableOffset to be used for
                                     generalizing geometries returned by
                                     the query operation.
                                     The maxAllowableOffset is in the units
                                     of outSR. If outSR is not specified,
                                     maxAllowableOffset is assumed to be in
                                     the unit of the spatial reference of
                                     the map.
                outSR - The spatial reference of the returned geometry.
                geometryPrecision -  This option can be used to specify the
                                     number of decimal places in the
                                     response geometries returned by the
                                     Query operation.
                gdbVersion - Geodatabase version to query
                returnDistinctValues -  If true, it returns distinct values
                                        based on the fields specified in
                                        outFields. This parameter applies
                                        only if the
                                        supportsAdvancedQueries property of
                                        the layer is true.
                returnIdsOnly -  If true, the response only includes an
                                 array of object IDs. Otherwise, the
                                 response is a feature set. The default is
                                 false.
                returnCountOnly -  If true, the response only includes the
                                   count (number of features/records) that
                                   would be returned by a query. Otherwise,
                                   the response is a feature set. The
                                   default is false. This option supersedes
                                   the returnIdsOnly parameter. If
                                   returnCountOnly = true, the response will
                                   return both the count and the extent.
                returnExtentOnly -  If true, the response only includes the
                                    extent of the features that would be
                                    returned by the query. If
                                    returnCountOnly=true, the response will
                                    return both the count and the extent.
                                    The default is false. This parameter
                                    applies only if the
                                    supportsReturningQueryExtent property
                                    of the layer is true.
                orderByFields - One or more field names on which the
                                features/records need to be ordered. Use
                                ASC or DESC for ascending or descending,
                                respectively, following every field to
                                control the ordering.
                groupByFieldsForStatistics - One or more field names on
                                             which the values need to be
                                             grouped for calculating the
                                             statistics.
                outStatistics - The definitions for one or more field-based
                                statistics to be calculated.
                returnZ -  If true, Z values are included in the results if
                           the features have Z values. Otherwise, Z values
                           are not returned. The default is false.
                returnM - If true, M values are included in the results if
                          the features have M values. Otherwise, M values
                          are not returned. The default is false.
                multipatchOption - This option dictates how the geometry of
                                   a multipatch feature will be returned.
                resultOffset -  This option can be used for fetching query
                                results by skipping the specified number of
                                records and starting from the next record
                                (that is, resultOffset + 1th).
                resultRecordCount - This option can be used for fetching
                                    query results up to the
                                    resultRecordCount specified. When
                                    resultOffset is specified but this
                                    parameter is not, the map service
                                    defaults it to maxRecordCount. The
                                    maximum value for this parameter is the
                                    value of the layer's maxRecordCount
                                    property.
                quanitizationParameters - Used to project the geometry onto
                                          a virtual grid, likely
                                          representing pixels on the screen.
                returnCentroid - Used to return the geometry centroid
                                 associated with each feature returned. If
                                 true, the result includes the geometry
                                 centroid. The default is false.
                as_obj - If true, the query will return the results as a
                         collections.mapping object that provides attribute-style access.
                         This object can be converted to a dict using dict(obj)
                          The default is False.
                as_dict - If true, the query will return the results as a dict.
                          The default is False
                returnFeatureClass - If true and arcpy is installed, the
                                     script will attempt to save the result
                                     of the query to a feature class.
                out_fc - only valid if returnFeatureClass is set to True.
                         Output location of query. If out_fc is set to None,
                         then the feature class will be saved to the scratch
                         File Geodatabase with a random name.
               kwargs - optional parameters that can be passed to the Query
                 function.  This will allow users to pass additional
                 parameters not explicitly implemented on the function. A
                 complete list of functions available is documented on the
                 Query REST API.
            Output:
               A list of Feature Objects (default) or a path to the output featureclass if
               returnFeatureClass is set to True.
         """
        url = self._url + "/query"
        params = {"f": "json"}
        params['where'] = where
        params['outFields'] = out_fields
        params['returnGeometry'] = return_geometry
        params['returnDistinctValues'] = return_distinct_values
        params['returnCentroid'] = return_centroid
        params['returnCountOnly'] = return_count_only
        params['returnExtentOnly'] = return_extent_only
        params['returnIdsOnly'] = return_ids_only
        params['returnZ'] = return_z
        params['returnM'] = return_m
        if result_record_count:
            params['resultRecordCount'] = result_record_count
        if result_offset:
            params['resultOffset'] = result_offset
        if quanitization_parameters:
            params['quanitizationParameters'] = quanitization_parameters
        if multipatch_option:
            params['multipatchOption'] = multipatch_option
        if order_by_fields:
            params['orderByFields'] = order_by_fields
        if group_by_fields_for_statistics:
            params['groupByFieldsForStatistics'] = group_by_fields_for_statistics
        if statistic_filter and \
                isinstance(statistic_filter, StatisticFilter):
            params['outStatistics'] = statistic_filter.filter
        if out_statistics:
            params['outStatistics'] = out_statistics
        if out_sr:
            params['outSR'] = out_sr
        if max_allowable_offset:
            params['maxAllowableOffset'] = max_allowable_offset
        if gdb_version:
            params['gdbVersion'] = gdb_version
        if geometry_precision:
            params['geometryPrecision'] = geometry_precision
        if object_ids:
            params['objectIds'] = object_ids
        if distance:
            params['distance'] = distance
        if units:
            params['units'] = units
        if time_filter and \
                isinstance(time_filter, TimeFilter):
            for key, val in time_filter.filter:
                params[key] = val
        elif isinstance(time_filter, dict):
            for key, val in time_filter.items():
                params[key] = val
        if geometry_filter and \
                isinstance(geometry_filter, GeometryFilter):
            for key, val in geometry_filter.filter:
                params[key] = val
        elif geometry_filter and \
                isinstance(geometry_filter, dict):
            for key, val in geometry_filter.items():
                params[key] = val
        if len(kwargs) > 0:
            for key, val in kwargs.items():
                params[key] = val
                del key, val

        result = self._con.post(path=url,
                                postdata=params, token=self._token)
        if 'error' in result:
            raise ValueError(result)

        if return_count_only:
            return result['count']
        elif as_obj:
            return PropertyMap(result)
        elif return_ids_only or as_dict:
            return result
        elif return_feature_class and \
                not return_count_only and \
                not return_ids_only:
            uid = _utils.create_uid()
            if out_fc is None:
                out_fc = os.path.join(scratchGDB(),
                                      "a{fid}".format(fid=uid))
            text = json.dumps(result)
            temp = scratchFolder() + os.sep + uid + ".json"
            with open(temp, 'wb') as writer:
                if six.PY3:
                    text = bytes(text, 'UTF-8')
                writer.write(text)
                writer.flush()
                del writer
            feat_cls = json_to_featureclass(json_file=temp,
                                            out_fc=out_fc)
            os.remove(temp)
            return feat_cls
        else:
            return result['features']
            # df = json_normalize(result['features'])
            # df.columns = df.columns.str.replace('attributes.', '')
            # return df
            # return FeatureSet.fromJSON(jsonValue=json.dumps(result))

    # ----------------------------------------------------------------------
    def query_related_records(self,
                              object_ids,
                              relationship_id,
                              out_fields="*",
                              definition_expression=None,
                              return_geometry=True,
                              max_allowable_offset=None,
                              geometry_precision=None,
                              out_wkid=None,
                              gdb_version=None,
                              return_z=False,
                              return_m=False):
        """
           The Query operation is performed on a feature service layer
           resource. The result of this operation are feature sets grouped
           by source layer/table object IDs. Each feature set contains
           Feature objects including the values for the fields requested by
           the user. For related layers, if you request geometry
           information, the geometry of each feature is also returned in
           the feature set. For related tables, the feature set does not
           include geometries.
           Inputs:
              objectIds - the object IDs of the table/layer to be queried
              relationshipId - The ID of the relationship to be queried.
              outFields - the list of fields from the related table/layer
                          to be included in the returned feature set. This
                          list is a comma delimited list of field names. If
                          you specify the shape field in the list of return
                          fields, it is ignored. To request geometry, set
                          returnGeometry to true.
                          You can also specify the wildcard "*" as the
                          value of this parameter. In this case, the result
                          s will include all the field values.
              definitionExpression - The definition expression to be
                                     applied to the related table/layer.
                                     From the list of objectIds, only those
                                     records that conform to this
                                     expression are queried for related
                                     records.
              returnGeometry - If true, the feature set includes the
                               geometry associated with each feature. The
                               default is true.
              maxAllowableOffset - This option can be used to specify the
                                   maxAllowableOffset to be used for
                                   generalizing geometries returned by the
                                   query operation. The maxAllowableOffset
                                   is in the units of the outSR. If outSR
                                   is not specified, then
                                   maxAllowableOffset is assumed to be in
                                   the unit of the spatial reference of the
                                   map.
              geometryPrecision - This option can be used to specify the
                                  number of decimal places in the response
                                  geometries.
              outWKID - The spatial reference of the returned geometry.
              gdbVersion - The geodatabase version to query. This parameter
                           applies only if the isDataVersioned property of
                           the layer queried is true.
              returnZ - If true, Z values are included in the results if
                        the features have Z values. Otherwise, Z values are
                        not returned. The default is false.
              returnM - If true, M values are included in the results if
                        the features have M values. Otherwise, M values are
                        not returned. The default is false.
        """
        params = {
            "f": "json",
            "objectIds": object_ids,
            "relationshipId": relationship_id,
            "outFields": out_fields,
            "returnGeometry": return_geometry,
            "returnM": return_m,
            "returnZ": return_z
        }
        if gdb_version is not None:
            params['gdbVersion'] = gdb_version
        if definition_expression is not None:
            params['definitionExpression'] = definition_expression
        if out_wkid is not None and \
                isinstance(out_wkid, SpatialReference):
            params['outSR'] = out_wkid
        elif out_wkid is not None and \
                isinstance(out_wkid, dict):
            params['outSR'] = out_wkid
        if max_allowable_offset is not None:
            params['maxAllowableOffset'] = max_allowable_offset
        if geometry_precision is not None:
            params['geometryPrecision'] = geometry_precision
        qrr_url = self._url + "/queryRelatedRecords"
        return self._con.get(path=qrr_url, params=params, token=self._token)

    # ----------------------------------------------------------------------
    def get_html_popup(self, oid):
        """
           The htmlPopup resource provides details about the HTML pop-up
           authored by the user using ArcGIS for Desktop.
           Input:
              oid - object id of the feature where the HTML pop-up
           Output:

        """
        if self.properties.htmlPopupType != "esriServerHTMLPopupTypeNone":
            pop_url = self._url + "/%s/htmlPopup" % oid
            params = {
                'f': "json"
            }

            return self._con.get(path=pop_url, params=params, token=self._token)
        return ""

    # ----------------------------------------------------------------------
    def edit_features(self,
                      adds=None,
                      updates=None,
                      deletes=None,
                      gdb_version=None,
                      use_global_ids=False,
                      rollback_on_failure=True):
        """
           This operation adds, updates, and deletes features to the
           associated feature layer or table in a single call.
           Inputs:
              adds - The array of features to be added.
              updates - The array of features to be updateded.
              deletes - string of OIDs to remove from service
              gdbVersion - Geodatabase version to apply the edits.
              useGlobalIds - instead of referencing the default Object ID
                              field, the service will look at a GUID field
                              to track changes.  This means the GUIDs will
                              be passed instead of OIDs for delete,
                              update or add features.
              rollbackOnFailure - Optional parameter to specify if the
                                  edits should be applied only if all
                                  submitted edits succeed. If false, the
                                  server will apply the edits that succeed
                                  even if some of the submitted edits fail.
                                  If true, the server will apply the edits
                                  only if all edits succeed. The default
                                  value is true.
           Output:
              dictionary of messages
        """
        if adds is None:
            adds = []
        if updates is None:
            updates = []
        edit_url = self._url + "/applyEdits"
        params = {
            "f": "json",
            "useGlobalIds": use_global_ids,
            "rollbackOnFailure": rollback_on_failure
        }
        if gdb_version is not None:
            params['gdbVersion'] = gdb_version
        if isinstance(adds, FeatureSet):
            params['adds'] = json.dumps([f.as_dict for f in adds.features],
                                        default=_date_handler)
        elif len(adds) > 0:
            if isinstance(adds[0], dict):
                params['adds'] = json.dumps([f for f in adds],
                                            default=_date_handler)
            elif isinstance(adds[0], PropertyMap):
                params['adds'] = json.dumps([dict(f) for f in adds],
                                            default=_date_handler)
            else:
                print('pass in features as dict or PropertyMap')
        if isinstance(updates, FeatureSet):
            params['updates'] = json.dumps([f.as_dict for f in updates.features],
                                           default=_date_handler)
        elif len(updates) > 0:
            if isinstance(updates[0], dict):
                params['updates'] = json.dumps([f for f in updates],
                                               default=_date_handler)
            elif isinstance(updates[0], PropertyMap):
                params['updates'] = json.dumps([dict(f) for f in updates],
                                               default=_date_handler)
            elif isinstance(updates[0], Feature):
                params['updates'] = json.dumps([f.as_dict for f in updates],
                                               default=_date_handler)
            else:
                print('pass in features as dict or PropertyMap')
        if deletes is not None and \
                isinstance(deletes, str):
            params['deletes'] = deletes
        elif deletes is not None and \
                isinstance(deletes, PropertyMap):
            print('pass in delete, unable to convert PropertyMap to string list of OIDs')

        elif deletes is not None and \
                isinstance(deletes, FeatureSet):
            params['deletes'] = ",".join(
                [str(feat.get_value(field_name=deletes.object_id_field_name)) for feat in deletes.features])

        if 'deletes' not in params and 'updates' not in params and 'adds' not in params:
            print("Parameters not valid for edit_features")
            return None
        return self._con.post(path=edit_url, postdata=params, token=self._token)

    # ----------------------------------------------------------------------
    def calculate(self, where, calc_expression, sql_format="standard"):
        """
        The calculate operation is performed on a feature layer
        resource. It updates the values of one or more fields in an
        existing feature service layer based on SQL expressions or scalar
        values. The calculate operation can only be used if the
        supportsCalculate property of the layer is true.
        Neither the Shape field nor system fields can be updated using
        calculate. System fields include ObjectId and GlobalId.
        See Calculate a field for more information on supported expressions

        Inputs:
           where - A where clause can be used to limit the updated records.
                   Any legal SQL where clause operating on the fields in
                   the layer is allowed.
           calcExpression - The array of field/value info objects that
                            contain the field or fields to update and their
                            scalar values or SQL expression.  Allowed types
                            are dictionary and list.  List must be a list
                            of dictionary objects.
                            Calculation Format is as follows:
                               {"field" : "<field name>",
                               "value" : "<value>"}
           sqlFormat - The SQL format for the calcExpression. It can be
                       either standard SQL92 (standard) or native SQL
                       (native). The default is standard.
                       Values: standard, native
        Output:
           JSON as string
        Usage:
        >>>print(fl.calculate(where="OBJECTID < 2",
                              calcExpression={"field": "ZONE",
                                              "value" : "R1"}))
        {'updatedFeatureCount': 1, 'success': True}
        """
        url = self._url + "/calculate"
        params = {
            "f": "json",
            "where": where,

        }
        if isinstance(calc_expression, dict):
            params["calcExpression"] = json.dumps([calc_expression],
                                                  default=_date_handler)
        elif isinstance(calc_expression, list):
            params["calcExpression"] = json.dumps(calc_expression,
                                                  default=_date_handler)
        if sql_format.lower() in ['native', 'standard']:
            params['sqlFormat'] = sql_format.lower()
        else:
            params['sqlFormat'] = "standard"
        return self._con.post(path=url,
                              postdata=params, token=self._token)


class Table(FeatureLayer):
    """
    Tables represent entity classes with uniform properties. In addition to working with “entities with location” as
    features, the GIS can also work with non-spatial entities as rows in tables.

    Working with tables is similar to working with feature layers, except that the rows (Features) in a table do not
    have a geometry, and tables ignore any geometry related operation.
    """
    pass


class FeatureDataset(GISService):
    """
    A FeatureDataset is a collection of feature layers and tables, with the associated relationships among the entities.

    This class allows use and administration (if access permits) of a feature dataset.

    In a web GIS, a feature dataset is exposed as a feature service with multiple feature layers.

    Instances of FeatureDatasets can be obtained from feature service Items in the GIS using
    `FeatureDataset.fromitem(item)`, from feature service endpoints using the constructor, or by accessing the `storage`
    attribute of feature layer objects.

    FeatureDatasets can be configured and managed using their `manager` helper object.

    If the dataset supports the sync operation, the `replicas` helper object allows management and synchronization of
    replicas for disconnected editing of the feature dataset.
    """

    def __init__(self, url, gis=None):
        super(FeatureDataset, self).__init__(url, gis)

        try:
            if self.properties.syncEnabled:
                self.replicas = ReplicaManager(self)
        except AttributeError:
            pass

        self._populate_layers()
        self._admin = None

    def _populate_layers(self):
        """
        populates the layers and tables for this feature service
        """
        layers = []
        tables = []

        for lyr in self.properties.layers:
            lyr = FeatureLayer(self.url + '/' + str(lyr.id), self._gis, self)
            layers.append(lyr)

        for lyr in self.properties.tables:
            lyr = Table(self.url + '/' + str(lyr.id), self._gis, self)
            tables.append(lyr)

        # fsurl = self.url + '/layers'
        # params = { "f" : "json" }
        # allayers = self._con.post(fsurl, params, token=self._token)

        # for layer in allayers['layers']:
        #    layers.append(FeatureLayer(self.url + '/' + str(layer['id']), self._gis))

        # for table in allayers['tables']:
        #    tables.append(FeatureLayer(self.url + '/' + str(table['id']), self._gis))

        self.layers = layers
        self.tables = tables

    @property
    def manager(self):
        """ helper object to manage the feature dataset, update it's definition, etc """
        if self._admin is None:
            url = self._url
            res = search("/rest/", url).span()
            add_text = "admin/"
            part1 = url[:res[1]]
            part2 = url[res[1]:]
            admin_url = "%s%s%s" % (part1, add_text, part2)

            self._admin = FeatureDatasetManager(admin_url, self._gis, self)
        return self._admin

    def query(self,
              layer_defs_filter=None,
              geometry_filter=None,
              time_filter=None,
              return_geometry=True,
              return_ids_only=False,
              return_count_only=False,
              return_z=False,
              return_m=False,
              out_sr=None):
        """
           The Query operation is performed on a feature service resource
        """
        qurl = self._url + "/query"
        params = {"f": "json",
                  "returnGeometry": return_geometry,
                  "returnIdsOnly": return_ids_only,
                  "returnCountOnly": return_count_only,
                  "returnZ": return_z,
                  "returnM": return_m}
        if layer_defs_filter is not None and \
                isinstance(layer_defs_filter, dict):
            params['layerDefs'] = layer_defs_filter
        elif layer_defs_filter is not None and \
                isinstance(layer_defs_filter, dict):
            pass
        if geometry_filter is not None and \
                isinstance(geometry_filter, dict):
            params['geometryType'] = geometry_filter['geometryType']
            params['spatialRel'] = geometry_filter['spatialRel']
            params['geometry'] = geometry_filter['geometry']
            params['inSR'] = geometry_filter['inSR']
        if out_sr is not None and \
                isinstance(out_sr, SpatialReference):
            params['outSR'] = out_sr
        elif out_sr is not None and \
                isinstance(out_sr, dict):
            params['outSR'] = out_sr
        if time_filter is not None and \
                isinstance(time_filter, dict):
            params['time'] = time_filter
        results = self._con.get(path=qurl,
                                params=params, token=self._token)
        if 'error' in results:
            raise ValueError(results)
        if not return_count_only and not return_ids_only:
            return results
            # if returnFeatureClass == True:
            # json_text = json.dumps(results)
            # return results
            # df = json_normalize(results['features'])
            # df.columns = df.columns.str.replace('attributes.', '')
            # return df
            # else:
            #    return results
            # df = json_normalize(results['features'])
            # df.columns = df.columns.str.replace('attributes.', '')
            # return df
        else:
            return results

    # ----------------------------------------------------------------------
    def query_related_records(self,
                              object_ids,
                              relationship_id,
                              out_fields="*",
                              definition_expression=None,
                              return_geometry=True,
                              max_allowable_offset=None,
                              geometry_precision=None,
                              out_wkid=None,
                              gdb_version=None,
                              return_z=False,
                              return_m=False):
        """
           The Query operation is performed on a feature service layer
           resource. The result of this operation are feature sets grouped
           by source layer/table object IDs. Each feature set contains
           Feature objects including the values for the fields requested by
           the user. For related layers, if you request geometry
           information, the geometry of each feature is also returned in
           the feature set. For related tables, the feature set does not
           include geometries.
           Inputs:
              objectIds - the object IDs of the table/layer to be queried
              relationshipId - The ID of the relationship to be queried.
              outFields - the list of fields from the related table/layer
                          to be included in the returned feature set. This
                          list is a comma delimited list of field names. If
                          you specify the shape field in the list of return
                          fields, it is ignored. To request geometry, set
                          returnGeometry to true.
                          You can also specify the wildcard "*" as the
                          value of this parameter. In this case, the result
                          s will include all the field values.
              definitionExpression - The definition expression to be
                                     applied to the related table/layer.
                                     From the list of objectIds, only those
                                     records that conform to this
                                     expression are queried for related
                                     records.
              returnGeometry - If true, the feature set includes the
                               geometry associated with each feature. The
                               default is true.
              maxAllowableOffset - This option can be used to specify the
                                   maxAllowableOffset to be used for
                                   generalizing geometries returned by the
                                   query operation. The maxAllowableOffset
                                   is in the units of the outSR. If outSR
                                   is not specified, then
                                   maxAllowableOffset is assumed to be in
                                   the unit of the spatial reference of the
                                   map.
              geometryPrecision - This option can be used to specify the
                                  number of decimal places in the response
                                  geometries.
              outWKID - The spatial reference of the returned geometry.
              gdbVersion - The geodatabase version to query. This parameter
                           applies only if the isDataVersioned property of
                           the layer queried is true.
              returnZ - If true, Z values are included in the results if
                        the features have Z values. Otherwise, Z values are
                        not returned. The default is false.
              returnM - If true, M values are included in the results if
                        the features have M values. Otherwise, M values are
                        not returned. The default is false.
        """
        params = {
            "f": "json",
            "objectIds": object_ids,
            "relationshipId": relationship_id,
            "outFields": out_fields,
            "returnGeometry": return_geometry,
            "returnM": return_m,
            "returnZ": return_z
        }
        if gdb_version is not None:
            params['gdbVersion'] = gdb_version
        if definition_expression is not None:
            params['definitionExpression'] = definition_expression
        if out_wkid is not None and \
                isinstance(out_wkid, SpatialReference):
            params['outSR'] = out_wkid
        elif out_wkid is not None and \
                isinstance(out_wkid, dict):
            params['outSR'] = out_wkid
        if max_allowable_offset is not None:
            params['maxAllowableOffset'] = max_allowable_offset
        if geometry_precision is not None:
            params['geometryPrecision'] = geometry_precision
        qrr_url = self._url + "/queryRelatedRecords"
        res = self._con.get(path=qrr_url, params=params, token=self._token)
        return res

    # ----------------------------------------------------------------------
    @property
    def _replicas(self):
        """ returns all the replicas for a feature service """
        params = {
            "f": "json",

        }
        url = self._url + "/replicas"
        return self._con.get(path=url, params=params, token=self._token)

    # ----------------------------------------------------------------------
    def _unregister_replica(self, replica_id):
        """
           removes a replica from a feature service
           Inputs:
             replica_id - The replicaID returned by the feature service
                          when the replica was created.
        """
        params = {
            "f": "json",
            "replicaID": replica_id
        }
        url = self._url + "/unRegisterReplica"
        return self._con.post(path=url, postdata=params, token=self._token)

    # ----------------------------------------------------------------------
    def _replica_info(self, replica_id):
        """
           The replica info resources lists replica metadata for a specific
           replica.
           Inputs:
              replica_id - The replicaID returned by the feature service
                           when the replica was created.
        """
        params = {
            "f": "json"
        }
        url = self._url + "/replicas/" + replica_id
        return self._con.get(path=url, params=params, token=self._token)

    # ----------------------------------------------------------------------
    def _create_replica(self,
                        replica_name,
                        layers,
                        layer_queries=None,
                        geometry_filter=None,
                        replica_sr=None,
                        transport_type="esriTransportTypeUrl",
                        return_attachments=False,
                        return_attachments_data_by_url=False,
                        async=False,
                        attachments_sync_direction="none",
                        sync_model="none",
                        data_format="json",
                        replica_options=None,
                        wait=False,
                        out_path=None):
        """
        The createReplica operation is performed on a feature service
        resource. This operation creates the replica between the feature
        service and a client based on a client-supplied replica definition.
        It requires the Sync capability. See Sync overview for more
        information on sync. The response for createReplica includes
        replicaID, server generation number, and data similar to the
        response from the feature service query operation.
        The createReplica operation returns a response of type
        esriReplicaResponseTypeData, as the response has data for the
        layers in the replica. If the operation is called to register
        existing data by using replicaOptions, the response type will be
        esriReplicaResponseTypeInfo, and the response will not contain data
        for the layers in the replica.

        Inputs:
           replicaName - name of the replica
           layers - layers to export
           layerQueries - In addition to the layers and geometry parameters, the layerQueries
            parameter can be used to further define what is replicated. This
            parameter allows you to set properties on a per layer or per table
            basis. Only the properties for the layers and tables that you want
            changed from the default are required.
            Example:
             layerQueries = {"0":{"queryOption": "useFilter", "useGeometry": true,
             "where": "requires_inspection = Yes"}}
           geometryFilter - Geospatial filter applied to the replica to
            parse down data output.
           returnAttachments - If true, attachments are added to the replica and returned in the
            response. Otherwise, attachments are not included.
           returnAttachmentDatabyURL -  If true, a reference to a URL will be provided for each
            attachment returned from createReplica. Otherwise,
            attachments are embedded in the response.
           replicaSR - the spatial reference of the replica geometry.
           transportType -  The transportType represents the response format. If the
            transportType is esriTransportTypeUrl, the JSON response is contained in a file,
            and the URL link to the file is returned. Otherwise, the JSON object is returned
            directly. The default is esriTransportTypeUrl.
            If async is true, the results will always be returned as if transportType is
            esriTransportTypeUrl. If dataFormat is sqlite, the transportFormat will always be
            esriTransportTypeUrl regardless of how the parameter is set.
            Values: esriTransportTypeUrl | esriTransportTypeEmbedded
           returnAttachments - If true, attachments are added to the replica and returned in
            the response. Otherwise, attachments are not included. The default is false. This
            parameter is only applicable if the feature service has attachments.
           returnAttachmentsDatabyURL -  If true, a reference to a URL will be provided for
            each attachment returned from createReplica. Otherwise, attachments are embedded
            in the response. The default is true. This parameter is only applicable if the
            feature service has attachments and if returnAttachments is true.
           attachmentsSyncDirection - Client can specify the attachmentsSyncDirection when
            creating a replica. AttachmentsSyncDirection is currently a createReplica property
            and cannot be overridden during sync.
            Values: none, upload, bidirectional
           async - If true, the request is processed as an asynchronous job, and a URL is
            returned that a client can visit to check the status of the job. See the topic on
            asynchronous usage for more information. The default is false.
           syncModel - Client can specify the attachmentsSyncDirection when creating a replica.
            AttachmentsSyncDirection is currently a createReplica property and cannot be
            overridden during sync.
           dataFormat - The format of the replica geodatabase returned in the response. The
            default is json.
            Values: filegdb, json, sqlite, shapefile
           replicaOptions - This parameter instructs the createReplica operation to create a
            new replica based on an existing replica definition (refReplicaId). It can be used
            to specify parameters for registration of existing data for sync. The operation
            will create a replica but will not return data. The responseType returned in the
            createReplica response will be esriReplicaResponseTypeInfo.
           wait - if async, wait to pause the process until the async operation is completed.
           out_path - folder path to save the file
        """
        if not self.properties.syncEnabled and "Extract" not in self.properties.capabilities:
            return None
        url = self._url + "/createReplica"
        dataformat = ["filegdb", "json", "sqlite", "shapefile"]
        params = {
            "f": "json",
            "replicaName": replica_name,
            "returnAttachments": return_attachments,
            "returnAttachmentsDatabyURL": return_attachments_data_by_url,
            "attachmentsSyncDirection": attachments_sync_direction,
            "async": async,
            "syncModel": sync_model,
            "layers": layers
        }
        if data_format.lower() in dataformat:
            params['dataFormat'] = data_format.lower()
        else:
            raise Exception("Invalid dataFormat")
        if layer_queries is not None:
            params['layerQueries'] = layer_queries
        if geometry_filter is not None and \
                isinstance(geometry_filter, dict):
            params.update(geometry_filter)
        if replica_sr is not None:
            params['replicaSR'] = replica_sr
        if replica_options is not None:
            params['replicaOptions'] = replica_options
        if transport_type is not None:
            params['transportType'] = transport_type

        if async:
            if wait:
                export_job = self._con.post(path=url, postdata=params, token=self._token)
                status = self._replica_status(url=export_job['statusUrl'])
                while status['status'].lower() != "completed":
                    status = self._replica_status(url=export_job['statusUrl'])
                    if status['status'].lower() == "failed":
                        return status

                res = status

            else:
                res = self._con.post(path=url, postdata=params, token=self._token)
        else:
            res = self._con.post(path=url, postdata=params, token=self._token)

        if out_path is not None and \
                os.path.isdir(out_path):
            dl_url = None
            if 'resultUrl' in res:

                dl_url = res["resultUrl"]
            elif 'responseUrl' in res:
                dl_url = res["responseUrl"]
            if dl_url is not None:
                return self._con.get(path=dl_url,
                                     out_folder=out_path, token=self._token)
            else:
                return res
        elif res is not None:
            return res
        return None

    # ----------------------------------------------------------------------
    def _synchronize_replica(self,
                             replica_id,
                             transport_type="esriTransportTypeUrl",
                             replica_server_gen=None,
                             return_ids_for_adds=False,
                             edits=None,
                             return_attachment_databy_url=False,
                             async=False,
                             sync_direction="snapshot",
                             sync_layers="perReplica",
                             edits_upload_id=None,
                             edits_upload_format=None,
                             data_format="json",
                             rollback_on_failure=True):
        """
        TODO: implement synchronize replica
        http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000vv000000
        """
        url = "{url}/synchronizeReplica".format(url=self._url)
        params = {
            "f": "json",
            "replicaID": replica_id,
        }
        if transport_type is not None:
            params['transportType'] = transport_type
        if edits is not None:
            params['edits'] = edits
        if replica_server_gen is not None:
            params['replicaServerGen'] = replica_server_gen
        if return_ids_for_adds is not None:
            params['returnIdsForAdds'] = return_ids_for_adds
        if return_attachment_databy_url is not None:
            params['returnAttachmentDatabyURL'] = return_attachment_databy_url
        if async is not None:
            params['async'] = async
        if sync_direction is not None:
            params['syncDirection'] = sync_direction
        if sync_layers is not None:
            params['syncLayers'] = sync_layers
        if edits_upload_format is not None:
            params['editsUploadFormat'] = edits_upload_format
        if edits_upload_id is not None:
            params['editsUploadID'] = edits_upload_id
        if data_format is not None:
            params['dataFormat'] = data_format
        if rollback_on_failure is not None:
            params['rollbackOnFailure'] = rollback_on_failure
        return self._con.post(path=url, postdata=params, token=self._token)

    # ----------------------------------------------------------------------
    def _replica_status(self, url):
        """gets the replica status when exported async set to True"""
        params = {"f": "json"}
        url += "/status"
        return self._con.get(path=url,
                             params=params, token=self._token)
