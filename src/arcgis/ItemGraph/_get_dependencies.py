from arcgis.gis import GIS, Item
from arcgis.gis.clone import clone_registry
from arcgis.features import FeatureLayer
import itertools
import re
from collections import OrderedDict

# any item that can contain another item or require another to exist
_COMPLEX_ITEMS = [
    "Web Map",
    "Web Scene",
    "Web Mapping Application",
    "Operation View",
    "Dashboard",
    "Feature Service",
    "StoryMap",
    "Workforce Project",
    "Form",
    "QuickCapture Project",
    "Notebook",
    "Pro Map",
    "Project Package",
    "Feature Collection",
    "Web Experience",
    "Hub Site Application",
    "Hub Page",
]

# regular expression to find GUID
REGEX_GUID = r"[0-9a-f]{8}[0-9a-f]{4}[1-5][0-9a-f]{3}[89ab][0-9a-f]{3}[0-9a-f]{12}"

def _get_item_dependencies(itemid, gis):
    if isinstance(itemid, Item):
        item = itemid
    else:
        item = gis.content.get(itemid)
    
    if not item:
        return []

    # if getattr(item, "groupDesignations", None) == "livingatlas":
    #     return []

    if item["type"] not in _COMPLEX_ITEMS:
        return []
    
    dependent_items = []
    dependent_services = []
    item_type = item["type"]
    
    if item_type in ["Web Map", "Web Scene"]:
        return parse_webmap(item)
    elif item_type == "Dashboard":
        return parse_dashboard(item)
    elif item_type == "Experience Builder":
        return parse_exb(item)
    elif item_type == "Web Mapping Application":
        return parse_wma(item)
    elif item_type == "StoryMap":
        return parse_storymap(item)
    else:
        return []
    
def parse_webmap(item):
    items = []
    services = []
    webmap_json = item.get_data()

    def process_op_layer(layer):
        if layer.get("layerType") == "GroupLayer":
            for sublayer in layer.get("layers"):
                process_op_layer(sublayer)
        
        else:
            if "itemId" in layer:
                items.append(layer["itemId"])
            elif "url" in layer:
                try:
                    sid = FeatureLayer(layer["url"]).properties["serviceItemId"]
                    items.append(sid)
                except:
                    services.append(layer["url"])

    for op_layer in webmap_json.get("operationalLayers"):
        process_op_layer(op_layer)
    
    items.extend(services)
    return items

def parse_dashboard(item):
    # credit to Dan Yaw for this one
    data_ids = []
    map_ids = []

    widgets = item.get_data().get("widgets")

    if widgets is not None:
        for widget in widgets:
            if widget.get("type") == "mapWidget":
                map_ids.append(widget.get("itemId"))

            else:
                try:
                    for dataset in widget.get("datasets"):
                        if dataset.get("type") == "serviceDataset":
                            data_source = dataset.get("dataSource")

                            if data_source.get("type") == "itemDataSource":
                                data_ids.append(data_source.get("itemId"))

                            elif data_source.get("type") == "arcadeDataSource":
                                script = data_source.get("script")

                                for item_id in find_regex(script, REGEX_GUID, []):
                                    data_ids.append(item_id)
                except:
                    pass

    map_ids.extend(data_ids)
    return map_ids

def parse_exb(item):
    pub_data = item.get_data()
    draft_data = item.resources.get("config/config.json")

    itemids = []

    for data in [pub_data, draft_data]:
        data_sources = data.get("dataSources", [])
        for ds in data_sources:
            if "itemId" in ds and ds["itemId"] not in itemids:
                itemids.append(ds["itemId"])
    
    return itemids

def parse_wma(item):
    data = item.get_data()
    itemids = []

    if "map" in data:
        try:
            itemids.append(data["map"]["itemId"])
        except:
            pass

    if "dataSource" in data:
        data_sources = data["dataSource"].get("dataSources")

        for ds in data_sources.values():
            try:
                itemids.append(ds["itemId"])
            except:
                pass

    return itemids

def parse_storymap(item):
    itemids = []
    pub_data = item.get_data()
    for res in item.resources.list():
        if "draft" in res["resource"] and "express" not in res["resource"]:
            draft_name = res["resource"]
    
    draft_data = item.resources.get(draft_name)

    for draft in [pub_data, draft_data]:
        web_maps = set(
            [
                v["data"]["itemId"]
                for k, v in draft["resources"].items()
                if v["type"].lower().find("webmap") > -1
            ]
        )

        themes = set(
            [
                v["data"]["themeItemId"]
                for k, v in draft["resources"].items()
                if v["type"].lower().find("story-theme") > -1
                and "themeItemId" in v["data"].keys()
            ]
        )

        for ids in [web_maps, themes]:
            itemids.extend(ids)
    
    return itemids

def find_regex(i, regex, res=[]):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    if isinstance(i, dict):
        for v in i.values():
            find_regex(v, regex, res)
    elif isinstance(i, list):
        for v in i:
            find_regex(v, regex, res)
    elif isinstance(i, str):
        # print(i)
        matches = re.findall(regex, i, re.MULTILINE)
        if matches:
            res.append(matches)
    # Flattening list of lists
    results = list(itertools.chain(*res))
    # Removing duplicates
    results = list(OrderedDict.fromkeys(results))
    return results


    # def process_group(layer):
    #     services = []
    #     collections = []
    #     services += [
    #         sublayer
    #         for sublayer in layer["layers"]
    #         if "layerType" in sublayer
    #         and sublayer["layerType"] == "ArcGISFeatureLayer"
    #         and "url" in sublayer
    #         and sublayer["url"] is not None
    #         and (
    #             "type" not in sublayer
    #             or sublayer["type"] != "Feature Collection"
    #         )
    #     ]
    #     collections += [
    #         sublayer
    #         for sublayer in layer["layers"]
    #         if "layerType" in sublayer
    #         and sublayer["layerType"] == "ArcGISFeatureLayer"
    #         and "type" in sublayer
    #         and sublayer["type"] == "Feature Collection"
    #     ]
    #     for sublayer in layer["layers"]:
    #         if "layers" in sublayer:
    #             res = process_group(sublayer)
    #             services += res[0]
    #             collections += res[1]
    #     return
    



# def _get_item_dependencies(self, item):

#         item_definition = None
#         source = item._gis

#         # if the item is in the clone_registry then use the item definition.
#         if isinstance(item, gis.Item) and item["type"] in clone_registry():
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition
#         # if the item is a group find all the web maps that are shared with the group
#         elif isinstance(item, gis.Group):
#             item_definition = self._get_group_definition(item)
#             # add to graph
#             self._graph[item_definition.info["id"]] = item_definition
#             group_id = item["id"]

#             search_query = "group:{0}".format(group_id)
#             group_items = source.content.search(
#                 search_query, max_items=100, outside_org=True
#             )
#             for group_item in group_items:
#                 item_definition2 = self._get_item_definitions(group_item)
#                 if item_definition2 is not None:
#                     item_definition.add_parent(item_definition2)
#                     item_definition2.sharing["groups"].append(group_id)
#         elif item.type == "StoryMap":
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition
#         # If the item is an application or dashboard find the web map or group that the application referencing
#         elif item["type"] in [
#             "Web Mapping Application",
#             "Operation View",
#             "Dashboard",
#         ]:
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition

#             webmap_ids = []
#             layer_ids = []
#             app_json = item_definition.data
#             if app_json is not None:
#                 if (
#                     "Story Map" in item["typeKeywords"]
#                     or "Story Maps" in item["typeKeywords"]
#                 ):
#                     webmap_ids = []

#                 elif item["type"] == "Operation View":
#                     webmap_ids.extend(_OperationViewDefintion.get_webmap_ids(app_json))
#                     layer_ids.extend(_OperationViewDefintion.get_layer_ids(app_json))

#                 elif item["type"] == "Dashboard":
#                     webmap_ids.extend(_DashboardDefinition.get_webmap_ids(app_json))
#                     layer_ids.extend(_DashboardDefinition.get_layer_ids(app_json))

#                 elif "Web AppBuilder" in item["typeKeywords"]:  # Web AppBuilder
#                     if "map" in app_json:
#                         if "itemId" in app_json["map"]:
#                             webmap_ids.append(app_json["map"]["itemId"])

#                 else:  # Configurable Application Template
#                     if "values" in app_json:
#                         if "group" in app_json["values"]:
#                             group_id = app_json["values"]["group"]
#                             try:
#                                 group = source.groups.get(group_id)
#                             except RuntimeError:
#                                 raise
#                             item_definition.add_child(self._get_item_definitions(group))

#                         if "webmap" in app_json["values"]:
#                             if isinstance(app_json["values"]["webmap"], list):
#                                 webmap_ids.extend(app_json["values"]["webmap"])
#                             else:
#                                 webmap_ids.append(app_json["values"]["webmap"])

#             for webmap_id in webmap_ids:
#                 try:
#                     webmap = source.content.get(webmap_id)
#                 except RuntimeError:
#                     raise
#                 item_definition.add_child(self._get_item_definitions(webmap))
#             for layer_id in layer_ids:
#                 try:
#                     item = source.content.get(layer_id)
#                 except RuntimeError:
#                     raise
#                 item_definition.add_child(self._get_item_definitions(item))

#         # If the item is a web map find all the feature service layers and tables that make up the map
#         elif item["type"] in ["Web Map", "Web Scene"]:
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition

#             webmap_json = item_definition.data
#             featurelayer_services = []
#             feature_collections = []

#             def process_group(layer):
#                 services = []
#                 collections = []
#                 services += [
#                     sublayer
#                     for sublayer in layer["layers"]
#                     if "layerType" in sublayer
#                     and sublayer["layerType"] == "ArcGISFeatureLayer"
#                     and "url" in sublayer
#                     and sublayer["url"] is not None
#                     and (
#                         "type" not in sublayer
#                         or sublayer["type"] != "Feature Collection"
#                     )
#                 ]
#                 collections += [
#                     sublayer
#                     for sublayer in layer["layers"]
#                     if "layerType" in sublayer
#                     and sublayer["layerType"] == "ArcGISFeatureLayer"
#                     and "type" in sublayer
#                     and sublayer["type"] == "Feature Collection"
#                 ]
#                 for sublayer in layer["layers"]:
#                     if "layers" in sublayer:
#                         res = process_group(sublayer)
#                         services += res[0]
#                         collections += res[1]
#                 return [services, collections]

#             if "operationalLayers" in webmap_json:
#                 featurelayer_services += [
#                     layer
#                     for layer in webmap_json["operationalLayers"]
#                     if "layerType" in layer
#                     and layer["layerType"] == "ArcGISFeatureLayer"
#                     and "url" in layer
#                     and layer["url"] is not None
#                     and ("type" not in layer or layer["type"] != "Feature Collection")
#                 ]
#                 feature_collections += [
#                     layer
#                     for layer in webmap_json["operationalLayers"]
#                     if "layerType" in layer
#                     and layer["layerType"] == "ArcGISFeatureLayer"
#                     and "type" in layer
#                     and layer["type"] == "Feature Collection"
#                 ]
#                 # check for group layers
#                 for layer in webmap_json["operationalLayers"]:
#                     if "layers" in layer:
#                         res = process_group(layer)
#                         featurelayer_services += res[0]
#                         feature_collections += res[1]
#             if "tables" in webmap_json:
#                 featurelayer_services += [
#                     table for table in webmap_json["tables"] if "url" in table
#                 ]

#             for layer in featurelayer_services:
#                 try:
#                     lay_item = arcgis.gis.Item(item._gis, layer["itemId"])
#                 except:
#                     lay_item = {}
#                 if (
#                     getattr(lay_item, "groupDesignations", "notlivingatlas")
#                     != "livingatlas"
#                 ):
#                     service_url = os.path.dirname(layer["url"])
#                     feature_service = next(
#                         (
#                             definition
#                             for definition in self._graph.values()
#                             if "url" in definition.info
#                             and _compare_url(definition.info["url"], service_url)
#                         ),
#                         None,
#                     )
#                     if not feature_service:
#                         feature_service = _get_feature_service_related_item(
#                             service_url, source
#                         )
#                         if feature_service:
#                             item_definition.add_child(
#                                 self._get_item_definitions(feature_service)
#                             )
#                     else:
#                         item_definition.add_child(
#                             self._get_item_definitions(feature_service.portal_item)
#                         )

#             for feature_collection in feature_collections:
#                 if (
#                     "itemId" in feature_collection
#                     and feature_collection["itemId"] is not None
#                 ):
#                     feature_collection = source.content.get(
#                         feature_collection["itemId"]
#                     )
#                     item_definition.add_child(
#                         self._get_item_definitions(feature_collection)
#                     )

#             if not self._use_org_basemap:
#                 basemap_layers = _deep_get(webmap_json, "baseMap", "baseMapLayers")
#                 if basemap_layers is not None:
#                     for basemap_layer in basemap_layers:
#                         if (
#                             "layerType" in basemap_layer
#                             and basemap_layer["layerType"] == "VectorTileLayer"
#                             and "itemId" in basemap_layer
#                         ):
#                             vector_tile_item = source.content.get(
#                                 basemap_layer["itemId"]
#                             )
#                             if vector_tile_item is None:
#                                 continue
#                             if vector_tile_item["owner"] == item["owner"]:
#                                 item_definition.add_child(
#                                     self._get_item_definitions(vector_tile_item)
#                                 )

#         # If the item is a feature service determine if it is a view and if it is find all it's sources
#         elif item["type"] == "Feature Service":
#             svc = FeatureLayerCollection.fromitem(item)
#             service_definition = dict(svc.properties)
#             item_definition = None

#             is_view = False
#             if (
#                 "isView" in service_definition
#                 and service_definition["isView"] is not None
#             ):
#                 is_view = service_definition["isView"]
#             elif "View Service" in item.typeKeywords:
#                 is_view = True

#             # Get the item data, for example any popup definition associated with the item
#             try:
#                 data = item.get_data()
#             except:
#                 data = {}

#             # Get the definitions of the the layers and tables
#             layers_definition = {"layers": [], "tables": []}

#             # Process the feature service if it is a view
#             if is_view:
#                 try:
#                     source_fs_definitions = []
#                     source_item_ids = []
#                     view_sources = {}
#                     view_source_fields = {}

#                     for layer in svc.layers + svc.tables:
#                         _view_sources = []
#                         _view_source_fields = []
#                         _sources = []

#                         layer_sources = source._portal.con.get(
#                             svc.url + "/" + str(layer.properties["id"]) + "/sources"
#                         )

#                         if not source.properties.isPortal:
#                             if "layers" in layer_sources:
#                                 for layer_source in layer_sources["layers"]:
#                                     _sources.append(layer_source)
#                             elif "tables" in layer_sources:
#                                 for layer_source in layer_sources["tables"]:
#                                     _sources.append(layer_source)
#                         else:
#                             if "layers" in layer_sources:
#                                 for layer_source in layer_sources["layers"]:
#                                     if not os.path.exists(layer_source["url"]):
#                                         layer_flc = source.content.get(
#                                             layer_source["serviceItemId"]
#                                         )
#                                         layer_id = int(
#                                             urlparse(layer_source["url"]).path.split(
#                                                 "/"
#                                             )[-1]
#                                         )
#                                         try:
#                                             layer_url_dict = {
#                                                 "url": layer_flc.layers[layer_id].url
#                                             }
#                                         except IndexError:
#                                             # Layer could be a table
#                                             table_index = layer_id - (len(svc.layers))
#                                             layer_url_dict = {
#                                                 "url": layer_flc.tables[table_index].url
#                                             }
#                                         layer_source.update(layer_url_dict)
#                                         _sources.append(layer_source)
#                         properties = self._get_properties(
#                             layer, data, len(_sources) > 1, is_view
#                         )
#                         if "geometryType" in properties:
#                             layers_definition["layers"].append(properties)
#                         else:
#                             layers_definition["tables"].append(properties)

#                         for layer_source in _sources:
#                             self._cant_export.append(layer_source["serviceItemId"])
#                             if layer_source["serviceItemId"] not in source_item_ids:
#                                 source_item = source.content.get(
#                                     layer_source["serviceItemId"]
#                                 )
#                                 source_fs_definition = self._get_item_definitions(
#                                     source_item
#                                 )
#                                 if source_fs_definition is not None:
#                                     source_fs_definitions.append(source_fs_definition)
#                                 source_item_ids.append(layer_source["serviceItemId"])
#                             _view_sources.append(layer_source["url"])
#                             feature_layer = FeatureLayer(layer_source["url"], source)
#                             _view_source_fields.append(feature_layer.properties.fields)

#                         view_sources[layer.properties["id"]] = _view_sources
#                         view_source_fields[layer.properties["id"]] = _view_source_fields
#                         if len(_sources) > 1:
#                             # multi-source views will have necessary source field info as a part of the admin_layer_info
#                             view_source_fields[layer.properties["id"]] = {}

#                     item_definition = _FeatureServiceDefinition(
#                         self.target,
#                         self._clone_mapping,
#                         dict(item),
#                         service_definition,
#                         layers_definition,
#                         is_view,
#                         view_sources,
#                         view_source_fields,
#                         features=None,
#                         data=data,
#                         folder=self.folder,
#                         thumbnail=None,
#                         portal_item=item,
#                         copy_data=self._copy_data,
#                         copy_global_ids=self._copy_global_ids,
#                         item_extent=self._item_extent,
#                         service_extent=self._service_extent,
#                         search_existing=self._search_existing_items,
#                         owner=self.owner,
#                         preserve_item_id=self._preserve_item_id,
#                         export_service=self._export_service,
#                         track_edits=self._track_edits,
#                         cant_export=self._cant_export,
#                     )

#                     for source_fs_definition in source_fs_definitions:
#                         item_definition.add_child(source_fs_definition)
#                 except RuntimeError:
#                     raise
#             else:
#                 for layer in svc.layers:
#                     properties = self._get_properties(layer, data, False, is_view)
#                     layers_definition["layers"].append(properties)
#                 for table in svc.tables:
#                     properties = self._get_properties(table, data, False, is_view)
#                     layers_definition["tables"].append(properties)
#                 ref_def_keywords = {"Singlelayer", "Multilayer"}
#                 if (
#                     any([kw in ref_def_keywords for kw in item.typeKeywords])
#                     and self._copy_data == False
#                 ):
#                     item_definition = _FeatureServiceRefDef(
#                         self.target,
#                         self._clone_mapping,
#                         dict(item),
#                         service_definition,
#                         layers_definition,
#                         features=None,
#                         data=data,
#                         thumbnail=None,
#                         portal_item=item,
#                         folder=self.folder,
#                         copy_data=self._copy_data,
#                         copy_global_ids=self._copy_global_ids,
#                         item_extent=self._item_extent,
#                         service_extent=self._service_extent,
#                         search_existing=self._search_existing_items,
#                         owner=self.owner,
#                         preserve_item_id=self._preserve_item_id,
#                     )

#                 else:
#                     item_definition = _FeatureServiceDefinition(
#                         self.target,
#                         self._clone_mapping,
#                         dict(item),
#                         service_definition,
#                         layers_definition,
#                         is_view,
#                         features=None,
#                         data=data,
#                         folder=self.folder,
#                         thumbnail=None,
#                         portal_item=item,
#                         copy_data=self._copy_data,
#                         copy_global_ids=self._copy_global_ids,
#                         item_extent=self._item_extent,
#                         service_extent=self._service_extent,
#                         search_existing=self._search_existing_items,
#                         owner=self.owner,
#                         preserve_item_id=self._preserve_item_id,
#                         export_service=self._export_service,
#                         track_edits=self._track_edits,
#                         cant_export=self._cant_export,
#                     )
#             self._graph[item.id] = item_definition
#             if "Workforce Project" in item.typeKeywords:
#                 # copying global ids is necessary for WF
#                 if self._copy_data:
#                     self._copy_global_ids = True

#                 # get Workforce group definition
#                 group_id = _deep_get(item.properties, "workforceProjectGroupId")
#                 group = source.groups.get(group_id)
#                 group_item_definition = self._get_group_definition(group)
#                 self._graph[group_id] = group_item_definition

#                 # add group to graph
#                 item_definition.sharing["groups"].append(group_id)
#                 self._graph[item.id] = item_definition
#                 item_definition.add_child(group_item_definition)

#                 # add webmaps to graph
#                 web_maps = [
#                     "workforceWorkerMapId",
#                     "workforceDispatcherMapId",
#                 ]
#                 for web_map in web_maps:
#                     item_id = _deep_get(item.properties, web_map)
#                     if item_id is not None:
#                         web_map_item = source.content.get(item_id)
#                         map_item_definition = self._get_item_definitions(web_map_item)
#                         if map_item_definition is not None:
#                             # WF layer is the parent of the maps, so remove it from the children
#                             for child in map_item_definition._children:
#                                 try:
#                                     if (
#                                         child._service_definition["serviceItemId"]
#                                         == item.id
#                                     ):
#                                         map_item_definition._children.remove(child)
#                                         break
#                                 except Exception:
#                                     # this is not the layer we want since it doesn't have a service definition
#                                     continue
#                             map_item_definition.sharing["groups"].append(group_id)
#                             item_definition.add_child(map_item_definition)
#                             map_item_definition.add_child(group_item_definition)

#                 # add integration as dependency
#                 integrations_fl = FeatureLayer(url=item.url + "/4", gis=item._gis)
#                 integrations_df = integrations_fl.query("1=1", as_df=True)
#                 for url_template in integrations_df.urltemplate.values:
#                     parsed = urlparse(url_template)
#                     try:
#                         item_id = urllib.parse.parse_qs(parsed.query)["itemID"][0]
#                         integration_item = source.content.get(item_id)
#                         if integration_item:
#                             integration_item_definition = self._get_item_definitions(
#                                 integration_item
#                             )
#                             if integration_item_definition is not None:
#                                 self._graph[item_id] = integration_item_definition
#                                 item_definition.add_child(integration_item_definition)
#                                 integration_item_definition.add_child(
#                                     group_item_definition
#                                 )
#                     except KeyError:
#                         # if item id doesn't exist, try at the next one
#                         continue

#         # If the item is a workforce find the group, maps and services that support the project
#         elif item["type"] == "Workforce Project":
#             workforce_json = item.get_data()

#             # Workforce group
#             group_id = _deep_get(workforce_json, "groupId")
#             group = source.groups.get(group_id)
#             group_item_definition = self._get_group_definition(group)
#             self._graph[group_id] = group_item_definition

#             item_definition = self._get_item_definition(item)
#             item_definition.sharing["groups"].append(group_id)
#             self._graph[item.id] = item_definition
#             item_definition.add_child(group_item_definition)

#             # Process the services
#             services = ["dispatchers", "assignments", "workers", "tracks"]
#             for service in services:
#                 item_id = _deep_get(workforce_json, service, "serviceItemId")
#                 if item_id is not None:
#                     service_item = source.content.get(item_id)
#                     layer_item_definition = self._get_item_definitions(service_item)
#                     if layer_item_definition is not None:
#                         self._graph[item_id] = layer_item_definition
#                         item_definition.add_child(layer_item_definition)
#                         layer_item_definition.sharing["groups"].append(group_id)
#                         layer_item_definition.add_child(group_item_definition)

#             # Process the web maps
#             web_maps = ["workerWebMapId", "dispatcherWebMapId"]
#             for web_map in web_maps:
#                 item_id = _deep_get(workforce_json, web_map)
#                 if item_id is not None:
#                     web_map_item = source.content.get(item_id)
#                     map_item_definition = self._get_item_definitions(web_map_item)
#                     if map_item_definition is not None:
#                         map_item_definition.sharing["groups"].append(group_id)
#                         item_definition.add_child(map_item_definition)
#                         map_item_definition.add_child(group_item_definition)

#             # Handle any app integrations
#             integrations = _deep_get(workforce_json, "assignmentIntegrations")
#             if integrations is not None:
#                 for integration in integrations:
#                     url_templates = []
#                     url_template = _deep_get(integration, "urlTemplate")
#                     if url_template is not None:
#                         url_templates.append(url_template)

#                     assignment_types = _deep_get(integration, "assignmentTypes")
#                     if assignment_types is not None:
#                         for key, value in assignment_types.items():
#                             url_template = _deep_get(value, "urlTemplate")
#                             if url_template is not None:
#                                 url_templates.append(url_template)

#                     for url_template in url_templates:
#                         item_ids = re.findall(
#                             "itemID=[0-9A-F]{32}",
#                             url_template,
#                             re.IGNORECASE,
#                         )
#                         for item_id in item_ids:
#                             integration_item = source.content.get(item_id[7:])
#                             integration_item_definition = self._get_item_definitions(
#                                 integration_item
#                             )
#                             if integration_item_definition is not None:
#                                 self._graph[item_id[7:]] = integration_item_definition
#                                 item_definition.add_child(integration_item_definition)

#         # If the item is a form find the feature service that supports it
#         elif item["type"] == "Form":
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition

#             for related_item in item_definition.related_items:
#                 item_def = self._get_item_definitions(
#                     source.content.get(related_item["id"])
#                 )
#                 if item_def is not None:
#                     item_definition.add_child(item_def)

#         # If the item is a quick capture project find the feature services that supports it
#         elif item["type"] == "QuickCapture Project":
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition

#             qc_json = item.resources.get("qc.project.json", try_json=True)
#             if "dataSources" in qc_json and qc_json["dataSources"] is not None:
#                 for datasource in qc_json["dataSources"]:
#                     if (
#                         "featureServiceItemId" in datasource
#                         and datasource["featureServiceItemId"] is not None
#                     ):
#                         feature_service = source.content.get(
#                             datasource["featureServiceItemId"]
#                         )
#                         if feature_service is not None:
#                             item_definition.add_child(
#                                 self._get_item_definitions(feature_service)
#                             )

#         # If the item is a python notebook find the referenced items from the same org
#         elif item["type"] == "Notebook":
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition

#             notebook = item_definition.data
#             with open(notebook, "r", encoding="utf8") as file:
#                 notebook_json = file.read()
#                 item_ids = set(re.findall("[0-9A-F]{32}", notebook_json, re.IGNORECASE))
#                 for id in item_ids:
#                     if id not in self._graph:
#                         notebook_item = source.content.get(id)
#                         if notebook_item is not None:
#                             item_definition.add_child(
#                                 self._get_item_definitions(notebook_item)
#                             )
#                     else:
#                         item_definition.add_child(self._graph[id])

#         # If the item is a pro map find the feature services that supports it
#         elif item["type"] == "Pro Map":
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition

#             map_json = None
#             with open(item_definition.data, "r", encoding="utf8") as file:
#                 map_json = json.loads(file.read())

#             data_connections = []
#             layer_definitions = _deep_get(map_json, "layerDefinitions")
#             if layer_definitions is not None:
#                 for layer_definition in layer_definitions:
#                     data_connection = _deep_get(
#                         layer_definition, "featureTable", "dataConnection"
#                     )
#                     if data_connection is not None:
#                         data_connections.append(data_connection)

#             table_definitions = _deep_get(map_json, "tableDefinitions")
#             if table_definitions is not None:
#                 for table_definition in table_definitions:
#                     data_connection = _deep_get(table_definition, "dataConnection")
#                     if data_connection is not None:
#                         data_connections.append(data_connection)

#             for data_connection in data_connections:
#                 if (
#                     "workspaceFactory" in data_connection
#                     and data_connection["workspaceFactory"] == "FeatureService"
#                 ):
#                     if (
#                         "workspaceConnectionString" in data_connection
#                         and data_connection["workspaceConnectionString"] is not None
#                     ):
#                         service_url = data_connection["workspaceConnectionString"][4:]
#                         feature_service = next(
#                             (
#                                 definition
#                                 for definition in self._graph.values()
#                                 if "url" in definition.info
#                                 and _compare_url(definition.info["url"], service_url)
#                             ),
#                             None,
#                         )
#                         if not feature_service:
#                             feature_service = _get_feature_service_related_item(
#                                 service_url, source
#                             )
#                             if feature_service:
#                                 fs_definition = self._get_item_definitions(
#                                     feature_service
#                                 )
#                                 if fs_definition is not None:
#                                     item_definition.add_child(fs_definition)

#         # If the item is a pro project find the feature services that supports it
#         elif item["type"] == "Project Package":
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition
#             if "copy-only" not in item["tags"]:
#                 try:
#                     import arcpy

#                     ppkx = item_definition.data
#                     extract_dir = os.path.join(os.path.dirname(ppkx), "extract")
#                     if not os.path.exists(extract_dir):
#                         os.makedirs(extract_dir)

#                     arcpy.ExtractPackage_management(ppkx, extract_dir, False)

#                     # 1.x versions of Pro use a different folder name
#                     project_folder = "p20"
#                     version = arcpy.GetInstallInfo()["Version"]
#                     if version.startswith("1"):
#                         project_folder = "p12"

#                     project_dir = os.path.join(extract_dir, project_folder)
#                     if os.path.exists(project_dir):
#                         aprx_files = [
#                             f for f in os.listdir(project_dir) if f.endswith(".aprx")
#                         ]
#                         if len(aprx_files) == 1:
#                             aprx_file = os.path.join(project_dir, aprx_files[0])
#                             aprx = arcpy.mp.ArcGISProject(aprx_file)
#                             maps = aprx.listMaps()
#                             for map in maps:
#                                 layers = [
#                                     l
#                                     for l in map.listLayers()
#                                     if l.supports("connectionProperties")
#                                 ]
#                                 layers.extend(map.listTables())
#                                 for lyr in layers:
#                                     connection_properties = lyr.connectionProperties
#                                     workspace_factory = _deep_get(
#                                         connection_properties,
#                                         "workspace_factory",
#                                     )
#                                     service_url = _deep_get(
#                                         connection_properties,
#                                         "connection_info",
#                                         "url",
#                                     )
#                                     if (
#                                         workspace_factory == "FeatureService"
#                                         and service_url is not None
#                                     ):
#                                         feature_service = next(
#                                             (
#                                                 definition
#                                                 for definition in self._graph.values()
#                                                 if "url" in definition.info
#                                                 and _compare_url(
#                                                     definition.info["url"],
#                                                     service_url,
#                                                 )
#                                             ),
#                                             None,
#                                         )
#                                         if not feature_service:
#                                             feature_service = (
#                                                 _get_feature_service_related_item(
#                                                     service_url, source
#                                                 )
#                                             )
#                                             if feature_service:
#                                                 fs_definition = (
#                                                     self._get_item_definitions(
#                                                         feature_service
#                                                     )
#                                                 )
#                                                 if fs_definition is not None:
#                                                     item_definition.add_child(
#                                                         fs_definition
#                                                     )

#                 except ImportError:
#                     pass

#         # If the item is a code attachment ignore it
#         elif item["type"] == "Code Attachment":
#             pass

#         # All other types we no longer need to recursively look for related items
#         else:
#             item_definition = self._get_item_definition(item)
#             self._graph[item.id] = item_definition

#         return item_definition