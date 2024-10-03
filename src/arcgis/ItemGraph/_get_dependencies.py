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
_REGEX_GUID = r"[0-9a-f]{8}[0-9a-f]{4}[1-5][0-9a-f]{3}[89ab][0-9a-f]{3}[0-9a-f]{12}"


def _get_item_dependencies(itemid, gis):
    if isinstance(itemid, Item):
        item = itemid
    else:
        item = gis.content.get(itemid)

    if not item:
        return []

    if item["type"] not in _COMPLEX_ITEMS:
        return []

    dependencies = []
    item_type = item["type"]

    if item_type in ["Web Map", "Web Scene"]:
        dependencies = _parse_webmap(item)
    elif item_type == "Dashboard":
        dependencies = _parse_dashboard(item)
    elif item_type == "Experience Builder":
        dependencies = _parse_exb(item)
    elif item_type == "Web Mapping Application":
        dependencies = _parse_wma(item)
    elif item_type == "StoryMap":
        dependencies = _parse_storymap(item)
    else:
        dependencies = []

    # add the dependent items property check from mtk

    return dependencies


def _parse_webmap(item):
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


def _parse_dashboard(item):
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

                                for item_id in _find_regex(script, _REGEX_GUID, []):
                                    data_ids.append(item_id)
                except:
                    pass

    map_ids.extend(data_ids)
    return map_ids


def _parse_exb(item):
    pub_data = item.get_data()
    draft_data = item.resources.get("config/config.json")

    itemids = []

    for data in [pub_data, draft_data]:
        data_sources = data.get("dataSources", [])
        for ds in data_sources:
            if "itemId" in ds and ds["itemId"] not in itemids:
                itemids.append(ds["itemId"])

    return itemids


def _parse_wma(item):
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


def _parse_storymap(item):
    itemids = []
    data_list = [item.get_data()]
    draft_name = None
    for res in item.resources.list():
        if "draft" in res["resource"] and "express" not in res["resource"]:
            draft_name = res["resource"]

    if draft_name:
        draft_data = item.resources.get(draft_name)
        data_list.append(draft_data)

    for draft in data_list:
        if "resources" not in draft:
            continue
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


def _find_regex(i, regex, res=[]):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    if isinstance(i, dict):
        for v in i.values():
            _find_regex(v, regex, res)
    elif isinstance(i, list):
        for v in i:
            _find_regex(v, regex, res)
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
