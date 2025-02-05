from ._item_graph import ItemGraph, ItemNode, load_from_file
from ._get_dependencies import _get_related_item_dict
from arcgis.gis import GIS
from arcgis.gis._impl._content_manager.folder import Folder
from arcgis._impl.common._utils import _text_replace
import os
import shutil
import tempfile
import tarfile
import ujson as json
import re
import uuid
import random
import string
import warnings

JSON_BASED_TYPES = [
    "Application",
    "Dashboard",
    "Feature Collection",
    "Map Service",
    "Scene Service",
    "Site Application",
    "Site Page",
    "StoryMap",
    "Vector Tile Service",
    "Web Experience",
    "Web Map",
    "Web Mapping Application",
    "Web Scene",
    "WMS",
]

JSON_BASED_WITH_DATA_TYPES = [
    "Feature Service",
    "Image Service",
]

SERVICE_BASED_TYPES = [
    "Map Service",
]


OTHER_BASED_TYPES = [
    "Geoprocessing Service",
]


FILE_BASED_TYPES = [
    "Administrative report",
    "AppBuilder Extension",
    "AppBuilder Widget Package",
    "ArcGIS Pro Add In",
    "ArcPad Package",
    "CAD Drawing",
    "Code Attachment",
    "Code Sample",
    "Compact Tile Package",
    "CSV",
    "CSV Collection",
    "Dashboards Add In",
    "Dashboards Extension",
    "Desktop Add-In",
    "Desktop Application",
    "Desktop Application Template",
    "Desktop Style",
    "Export Package",
    "File Geodatabase",
    "Form",
    "GeoJSON",
    "GeoPackage",
    "Geoprocessing Package",
    "Globe Document",
    "Image",
    "Image Collection",
    "iWork Keynote",
    "iWork Numbers",
    "iWork Pages",
    "KML",
    "Layer Package",
    "Layout",
    "Map Document",
    "Map Package",
    "Map Template",
    "Microsoft Excel",
    "Microsoft Powerpoint",
    "Microsoft Word",
    "Mobile Application",
    "Mobile Map Package",
    "Mobile Scene Package",
    "Native Application",
    "Native Application Installer",
    "Native Application Template",
    "Notebook",
    "PDF",
    "Pro Report",
    "Project Package",
    "Report Template",
    "Scene Package",
    "Service Definition",
    "Shapefile",
    "SQLite Geodatabase",
    "Statistical Data Collection",
    "Survey123 Add In",
    "Task File",
    "Tile Package",
    "Vector Tile Package",
    "Visio Document",
    "Workflow Manager (Classic) Package",
]


def _export_content(
    # item_list : list = None,
    graph: ItemGraph,
    output_folder: str = None,
    package_name: str = None,
    service_format: str = "File Geodatabase",
):

    if output_folder is None:
        output_folder = tempfile.mkdtemp()
    if package_name is None:
        package_name = "exported_content"

    # Create the main directory
    main_dir = os.path.join(output_folder, package_name)
    os.makedirs(main_dir, exist_ok=True)

    # Helper function to create item folder and export item data
    def create_item_folder(item, parent_dir):
        item_dir = os.path.join(parent_dir, item.id)
        os.makedirs(item_dir, exist_ok=True)
        # Call helper function to export item data
        _export_item_data(item, item_dir, service_format)

    manifest = {}
    # Iterate over all items in the graph and create their folders
    node_list = graph.all_items()
    for node in node_list:
        # if it's a hosted FS with no data file, must export data
        item = node.item
        if item is None:
            continue
        create_item_folder(node, main_dir)
        manifest[item.id] = {
            "title": item.title,
            "type": item.type,
            "created": item.created,
            "org_source": item._gis.url,
        }

    # Create a metadata file at the top directory
    manifest_file = os.path.join(main_dir, "manifest.json")
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)

    # create the graph structure file
    graph_file = os.path.join(main_dir, "graph.gml")
    graph.write_to_file(graph_file)

    # Create a static binary file containing the entire directory
    binary_file_path = os.path.join(output_folder, f"{package_name}.contentexport")
    with tarfile.open(binary_file_path, "w:gz") as tar:
        tar.add(main_dir, arcname=os.path.basename(main_dir))

    # Clean up the temporary main directory
    shutil.rmtree(main_dir)

    return binary_file_path


def _export_item_data(node: ItemNode, output_folder: str, service_format: str):
    item = node.item
    if item is None:
        return
    # Create a folder for the item
    os.makedirs(output_folder, exist_ok=True)

    # create all the proper folders
    for header in ["files", "resources", "data", "proxies"]:
        os.makedirs(os.path.join(output_folder, header), exist_ok=True)

    # download json of item properties based
    item_dict = dict(item)

    # download thumbnail
    files_folder = os.path.join(output_folder, "files")
    item.download_thumbnail(files_folder)

    # download metadata
    if "Metadata" in item_dict["typeKeywords"]:
        item.download_metadata(files_folder)

    # resources
    res_folder = os.path.join(output_folder, "resources")
    # rm = item.resources
    rm = item.resources
    resources_list = rm.list()
    res_manifest = {}
    for resource in resources_list:
        # get the info and then download
        res_manifest[resource["resource"]] = resource
        res_download = rm.get(
            file=resource["resource"], out_folder=res_folder, try_json=False
        )
    with open(os.path.join(res_folder, "resources.json"), "w") as res_list:
        json.dump(res_manifest, res_list, indent=4)

    # relationships
    relationships = {}
    relationships["contains"] = node.contains("id")
    relationships["requires"] = node.requires("id")
    relationships["contained_by"] = node.contained_by("id")
    relationships["required_by"] = node.required_by("id")
    relationships["related_items"] = _get_related_item_dict(
        item, forward=True, reverse=False
    )["forward"]
    rel_file_path = os.path.join(output_folder, "relationships.json")
    with open(rel_file_path, "w") as rel_file:
        json.dump(relationships, rel_file, indent=4)

    # data
    data_folder = os.path.join(output_folder, "data")
    download_path = None
    if item.type in JSON_BASED_TYPES:
        path_name = "structure.json"
        download_path = item.download(data_folder, path_name)
    elif item.type in JSON_BASED_WITH_DATA_TYPES:
        # views are annoying
        if "View Service" in item.typeKeywords:
            # add check for proxy services like below (hosted elsewhere)
            view_props = dict(item.layers[0].container.manager.properties)
            view_props_file_path = os.path.join(data_folder, "view_props.json")
            with open(view_props_file_path, "w") as view_props_file:
                json.dump(view_props, view_props_file, indent=4, ensure_ascii=False)
            fl_layers = item.layers
            for i in range(len(fl_layers)):
                layer_props = dict(fl_layers[i].manager.properties)
                layer_props_file_path = os.path.join(
                    data_folder, f"layer_{i}_props.json"
                )
                with open(layer_props_file_path, "w") as layer_props_file:
                    json.dump(
                        layer_props, layer_props_file, indent=4, ensure_ascii=False
                    )

        else:
            reqs = node.requires("item")
            needs_export = True
            # go through and check if there's already a data file
            for req in reqs:
                if req.type in FILE_BASED_TYPES:
                    needs_export = False
                    break
            # if no data file associated, export data to specified format
            if needs_export:
                try:
                    fc_item = item.export(item.title, service_format)
                    download_path = fc_item.download(data_folder)
                    fc_item.delete()
                    item_dict["data_item_type"] = service_format
                except:
                    # this means that this references data hosted elsewhere
                    # will have to recreate as new flc referencing og service
                    pass

        # fc_zip = zipfile.ZipFile(download_path)
    else:
        download_path = item.download(data_folder)

    json_file_path = os.path.join(output_folder, "properties.json")
    with open(json_file_path, "w") as json_file:
        json.dump(item_dict, json_file, indent=4, ensure_ascii=False)

    if download_path and os.stat(download_path).st_size == 0:
        os.remove(download_path)

    return output_folder


class ImportPackage:
    def __init__(self, package_path: str, gis: GIS):
        self.package_path = package_path
        self.gis = gis
        basename = os.path.splitext(os.path.basename(package_path))[0]
        self._temp_dir = self._unpack_package()
        self._temp_package = os.path.join(self._temp_dir.name, basename)
        temp_graph_path = os.path.join(self._temp_package, "graph.gml")
        self.graph = load_from_file(temp_graph_path, gis, include_items=False)
        self.created_item_mapping = {}
        self._name_mapping = {}
        self._service_mapping = {}
        manifest_file_path = os.path.join(self._temp_package, "manifest.json")
        with open(manifest_file_path, "r") as manifest_file:
            self.items = json.load(manifest_file)
        self._item_relationships = {}

    def _unpack_package(self):
        temp_dir = tempfile.TemporaryDirectory()
        with tarfile.open(self.package_path, "r:gz") as tar:
            tar.extractall(temp_dir.name)
        return temp_dir

    def _import_item(
        self,
        item_folder,
        preserve_id: bool = False,
        folder: Folder | str = None,
    ):
        # read the properties.json file
        with open(os.path.join(item_folder, "properties.json"), "r") as prop_file:
            item_properties = json.load(prop_file)

        # read the relationships.json file
        with open(os.path.join(item_folder, "relationships.json"), "r") as rel_file:
            relationships = json.load(rel_file)

        # read the resources.json file
        with open(
            os.path.join(item_folder, "resources/resources.json"), "r"
        ) as res_file:
            resources = json.load(res_file)

        # read the data folder
        data_folder = os.path.join(item_folder, "data")
        res_folder_path = os.path.join(item_folder, "resources")

        # import the item
        if isinstance(folder, str):
            folder = self.gis.content.folders.get(folder)
        if folder is None:
            folder = self.gis.content.folders.get()
        # clean props for item creation
        # if held item id, specify that
        # determine what file type is and create accordingly
        # for feature services: if data file, create and publish there,
        # otherwise, publish one that should have already been created based on relationships
        props = {}
        _property_names = [
            "title",
            "type",
            "description",
            "snippet",
            "tags",
            "culture",
            "accessInformation",
            "licenseInfo",
            "typeKeywords",
            "extent",
            "url",
            "properties",
        ]
        for prop_name in _property_names:
            if prop_name in item_properties:
                props[prop_name] = item_properties[prop_name]
        if item_properties["thumbnail"] is not None:
            thumbnail_name = item_properties["thumbnail"].split("/")[1]
            props["thumbnail"] = os.path.join(item_folder, "files", thumbnail_name)
        if "Metadata" in item_properties["typeKeywords"]:
            props["metadata"] = os.path.join(item_folder, "files/metadata.xml")
        item_id = item_properties["id"]
        new_item_id = None
        if (
            preserve_id
            and self.gis._portal.is_arcgisonline == False
            and self.gis.content.get(item_id) is None
        ):
            new_item_id = item_id

        def _add_data_item(fp, item_type, props=None):
            if props is None:
                data_props = {
                    "type": item_type,
                    "title": item_properties["title"],
                }
            else:
                data_props = props
                data_props["type"] = item_type
            try:
                job = folder.add(
                    **{
                        "item_properties": data_props,
                        "file": fp,
                        "stream": True,
                    }
                )
            except:
                rand_name = "_" + "".join(random.choices(string.ascii_letters, k=5))
                # switch this to removing extension and then re-adding
                new_fp = fp[:-4] + rand_name + ".zip"
                os.rename(fp, new_fp)
                job = folder.add(
                    **{
                        "item_properties": data_props,
                        "file": new_fp,
                        "stream": True,
                    }
                )
            return job.result()

        remap_dict = {}

        def _remap_json(json_text, remap_dict):
            if len(remap_dict) > 0:
                json_text = json_text.replace("\\/", "/")
                json_text = _text_replace(json_text, remap_dict)
            if self.items[item_id]["org_source"] != self.gis.url:
                secondary_remap = {self.items[item_id]["org_source"]: self.gis.url}
                json_text = _text_replace(json_text, secondary_remap)
            return json_text

        if (
            item_properties["type"] == "Feature Service"
            and "View Service" in item_properties["typeKeywords"]
        ):
            # completely different process for views. they're such a pain
            return None
            # this stuff below doesn't quite work yet but leaving it there to come back to
            # view_props_path = os.path.join(data_folder, "view_props.json")
            # with open(view_props_path, "r") as view_props_file:
            #     view_props = json.load(view_props_file)

            # reqs = self.graph.get_item(item_id).requires("id")
            # if len(reqs) == 0:
            #     raise RuntimeError("View Service does not have a valid data item")
            # elif len(reqs) == 1:
            #     flc_item = self.gis.content.get(self.created_item_mapping[reqs[0]])
            #     flc = flc_item.layers[0].container
            #     flc_props = flc.manager.properties
            #     v_layers = []
            #     v_tables = []
            #     if "layers" in view_props:
            #         v_layers = view_props["layers"]
            #     if "tables" in view_props:
            #         v_tables = view_props["tables"]
            #     vds = []
            #     for layer in v_layers:
            #         if "viewLayerDefinition" in layer["adminLayerInfo"]:
            #             vds.append(layer["adminLayerInfo"]["viewLayerDefinition"])
            #     for table in v_tables:
            #         if "viewLayerDefinition" in table["adminLayerInfo"]:
            #             vds.append(table["adminLayerInfo"]["viewLayerDefinition"])
            #     new_item = flc.manager.create_view(
            #         name = item_properties["title"],
            #         view_def = vds,
            #     )

        elif item_properties["type"] in JSON_BASED_WITH_DATA_TYPES:
            # check if dependent file already was uploaded
            reqs = self.graph.get_item(item_id).requires("id")
            service_item = None
            if len(reqs) > 0:
                # find the dependent file
                for req in reqs:
                    if (
                        req in self.created_item_mapping
                        and self.items[req]["type"] in FILE_BASED_TYPES
                    ):
                        service_id = self.created_item_mapping[req]
                        service_item = self.gis.content.get(service_id)
                        break

            if service_item is None and len(os.listdir(data_folder)) > 0:
                # this is case where data was newly exported into package
                for file in os.listdir(data_folder):
                    if file.endswith(".zip"):
                        fp = os.path.join(data_folder, file)
                        dt = item_properties.get("data_item_type", None)
                        if dt is None:
                            raise RuntimeError(
                                "Feature Service does not have a valid data item"
                            )
                        service_item = _add_data_item(fp, dt)
                        break

                # publish the service
                pub_params = props
                try:
                    new_item = service_item.publish(
                        publish_parameters=pub_params, item_id=new_item_id
                    )
                except:
                    new_name = _get_unique_name(
                        self.gis, item_properties["title"], True
                    )
                    new_name = new_name.replace("/", "_")
                    pub_params["name"] = new_name
                    new_item = service_item.publish(
                        publish_parameters=pub_params, item_id=new_item_id
                    )
            else:
                # this is case of referencing service from outside server
                # just have to republish assuming service is public
                service_url = props.pop("url")
                job = folder.add(
                    **{
                        "item_properties": props,
                        "item_id": new_item_id,
                        "url": service_url,
                        "stream": False,
                    }
                )
                new_item = job.result()

            if new_item:
                self._service_mapping[item_id] = (item_properties["url"], new_item.url)

        elif item_properties["type"] in FILE_BASED_TYPES:
            for file in os.listdir(data_folder):
                # if file.endswith(".zip"):
                #     fp = os.path.join(data_folder, file)
                #     new_item = _add_data_item(fp, item_properties["type"], props)
                #     break
                fp = os.path.join(data_folder, file)
                new_item = _add_data_item(fp, item_properties["type"], props)

        elif item_properties["type"] in JSON_BASED_TYPES:
            reqs = self.graph.get_item(item_id).requires("node")
            for req in reqs:
                if (
                    req.id in self.created_item_mapping
                    and self.created_item_mapping[req.id] != req.id
                ):
                    remap_dict[req.id] = self.created_item_mapping[req.id]
                if req.id in self._name_mapping:
                    orig_title, new_title = self._name_mapping[req.id]
                    remap_dict[orig_title] = new_title
                if req.id in self._service_mapping:
                    orig_url, new_url = self._service_mapping[req.id]
                    remap_dict[orig_url] = new_url

            structure_file_path = os.path.join(data_folder, "structure.json")
            if os.path.exists(structure_file_path):
                with open(structure_file_path, "r") as structure_file:
                    structure_data = json.load(structure_file)
                    structure_text = json.dumps(structure_data, ensure_ascii=False)
                    props["text"] = _remap_json(structure_text, remap_dict)
            else:
                # unpublished storymap draft case
                props["text"] = None

            job = folder.add(
                **{
                    "item_properties": props,
                    "item_id": new_item_id,
                    "stream": False,
                }
            )
            new_item = job.result()

        else:
            # if not a covered type, then skip
            warnings.warn(
                f"Item type '{item_properties['type']}' is not eligible to be created."
            )
            return None

        self.created_item_mapping[item_id] = new_item.id
        if item_properties["title"] != new_item.title:
            self._name_mapping[item_id] = (item_properties["title"], new_item.title)

        # import the resources
        for res_name in resources.keys():
            res_split = res_name.split("/")
            if len(res_split) > 1:
                res_folder = res_split[-2]
                res_basename = res_split[-1]
            else:
                res_folder = None
                res_basename = res_split[0]
            res_path = os.path.join(res_folder_path, res_basename)
            if res_basename.endswith(".json"):
                with open(res_path, "r") as res_file:
                    res_data = json.load(res_file)
                    res_text = json.dumps(res_data, ensure_ascii=False)
                    res_text = _remap_json(res_text, remap_dict)
                    new_item.resources.add(
                        folder_name=res_folder, file_name=res_basename, text=res_text
                    )
            else:
                new_item.resources.add(file=res_path, folder_name=res_folder)
            # new_item.resources.add(res_path)

        # add the related_items relationships to dict for reconstruction
        self._item_relationships[item_id] = relationships["related_items"]
        # return the item
        return new_item

    def import_items(
        self,
        items: list[str] = [],
        deep: bool = True,
        preserve_ids: bool = False,
        item_mapping: dict = {},
        folder: Folder | str = None,
    ):
        if len(items) == 0:
            nodes = set(self.graph.all_items())
        else:
            items = set(items)
            nodes = set()
            for itemid in items:
                if not itemid in self.items:
                    raise ValueError(f"Item with id {itemid} not found in the package")

                # if deep, make sure required items are also getting cloned
                node = self.graph.get_item(itemid)
                nodes.add(node)
                if deep:
                    for req in node.requires():
                        nodes.add(req)

        # then sort id's by the number of required relationships
        # this ensures that items are created in the correct order
        # and we only have to iterate through the item list once
        def count_reqs(node):
            return len(node.requires("id"))

        sorted_nodes = sorted(nodes, key=count_reqs)
        created_items = []
        for node in sorted_nodes:
            # maybe just take it out of the set beforehand?
            itemid = node.id
            item_folder = os.path.join(self._temp_package, itemid)
            if itemid in item_mapping or not os.path.exists(item_folder):
                continue
            new_item = self._import_item(
                item_folder, preserve_id=preserve_ids, folder=folder
            )
            if new_item:
                created_items.append(new_item)
        # have to wait until all items are created to restore related items
        # due to possible presence of reverse relationships
        self._restore_related_items()
        return created_items

    def _restore_related_items(self):
        for itemid, rel_dict in self._item_relationships.items():
            if rel_dict == {}:
                continue
            try:
                new_id = self.created_item_mapping[itemid]
                new_item = self.gis.content.get(new_id)
                for rel_type, rel_list in rel_dict.items():
                    for rel_id in rel_list:
                        new_rel_item = self.gis.content.get(
                            self.created_item_mapping[rel_id]
                        )
                        new_item.add_relationship(new_rel_item, rel_type)
            except:
                continue


def _get_unique_name(target, name, force_add_guid_suffix=False):
    """Create a new unique name for the service.
    Keyword arguments:
    target - The instance of arcgis.gis.GIS (the portal) to clone the feature service to.
    name - The original name.
    force_add_guid_suffix - Indicates if a guid suffix should automatically be added to the end of the service name
    """

    if name[0].isdigit():
        name = "_" + name
    name = name.replace(" ", "_")

    if not force_add_guid_suffix:
        guids = re.findall("[0-9A-F]{32}", name, re.IGNORECASE)
        for guid in guids:
            new_guid = uuid.uuid4().hex[0:5]
            name = name.replace(guid, new_guid)

        while True:
            if target.content.is_service_name_available(name, "featureService"):
                break

            guid = uuid.uuid4().hex[0:5]
            ends_with_guid = re.findall("_[0-9A-F]{32}$", name, re.IGNORECASE)
            if len(ends_with_guid) > 0:
                name = name[: len(name) - 32] + guid
            else:
                name = "{0}_{1}".format(name, guid)

    else:
        guid = uuid.uuid4().hex[0:5]
        ends_with_guid = re.findall("_[0-9A-F]{32}$", name, re.IGNORECASE)
        if len(ends_with_guid) > 0:
            name = name[: len(name) - 32] + guid
        else:
            name = "{0}_{1}".format(name, guid)

    return name
