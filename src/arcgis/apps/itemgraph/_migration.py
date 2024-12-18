from ._item_graph import ItemGraph, ItemNode, load_from_file
from arcgis.gis import GIS, Item, ContentManager
from arcgis.gis._impl._content_manager.folder import Folder
import os
import shutil
import tempfile
import tarfile
import ujson as json
import zipfile
import re
import uuid

JSON_BASED_TYPES = [
    "Application",
    "Dashboard",
    "Feature Collection",
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
        # if item.type in JSON_BASED_WITH_DATA_TYPES and node.requires("id") == []:
        #     fc_item = item.export(item.title, service_format)
        #     graph.add_relationship(item.id, fc_item.id)
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
        json.dump(manifest, f, indent=4)
    
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
    json_file_path = os.path.join(output_folder, "properties.json")
    with open(json_file_path, "w") as json_file:
        json.dump(item_dict, json_file, indent=4)

    # download thumbnail
    files_folder = os.path.join(output_folder, "files")
    item.download_thumbnail(files_folder)

    # download metadata
    item.download_metadata(files_folder)

    # resources
    res_folder = os.path.join(output_folder, "resources")
    # rm = item.resources
    # rm.export(res_folder, "archive.zip")
    rm = item.resources
    resources_list = rm.list()
    res_manifest = {}
    for resource in resources_list:
        # get the info and then download
        res_manifest[resource["resource"]] = resource
        res_download = rm.get(
            file = resource["resource"], out_folder=res_folder, try_json=False
        )
    with open(os.path.join(res_folder, "resources.json"), "w") as res_list:
        json.dump(res_manifest, res_list, indent=4)

    # relationships
    relationships = {}
    relationships["contains"] = node.contains("id")
    relationships["requires"] = node.requires("id")
    relationships["contained_by"] = node.contained_by("id")
    relationships["required_by"] = node.required_by("id")
    rel_file_path = os.path.join(output_folder, "relationships.json")
    with open(rel_file_path, "w") as rel_file:
        json.dump(relationships, rel_file, indent=4)

    # data
    data_folder = os.path.join(output_folder, "data")
    if item.type in JSON_BASED_TYPES:
        path_name = "structure.json"
        download_path = item.download(data_folder, path_name)
    elif item.type in JSON_BASED_WITH_DATA_TYPES and node.requires("id") == []:
        # if no associated data file, export the data
        fc_item = item.export(item.title, service_format)
        download_path = fc_item.download(data_folder)
        fc_item.delete()
        # fc_zip = zipfile.ZipFile(download_path)
    else:
        download_path = item.download(data_folder)
    
    if os.stat(download_path).st_size == 0:
        os.remove(download_path)

    return output_folder
    
class ImportPackage():
    def __init__(self, package_path: str, gis: GIS):
        self.package_path = package_path
        self.gis = gis
        basename = os.path.splitext(os.path.basename(package_path))[0]
        self._temp_dir = self._unpack_package()
        self._temp_package = os.path.join(self._temp_dir.name, basename)
        temp_graph_path = os.path.join(self._temp_package, "graph.gml")
        self.graph = load_from_file(temp_graph_path, gis, include_items=False)
        self.created_item_mapping = {}
        manifest_file_path = os.path.join(self._temp_package, "manifest.json")
        with open(manifest_file_path, "r") as manifest_file:
            self.items = json.load(manifest_file)
    
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
        with open(os.path.join(item_folder, "resources/resources.json"), "r") as res_file:
            resources = json.load(res_file)
        
        # read the data folder
        data_folder = os.path.join(item_folder, "data")
        if item_properties["type"] in JSON_BASED_TYPES:
            path_name = "structure.json"
            data_path = os.path.join(data_folder, path_name)
        else:
            data_path = None
        
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
        props = item_properties.copy()
        item_id = props["id"]
        new_item_id = None
        if (
            preserve_id
            and self.gis._portal.is_arcgisonline == False
        ):
            new_item_id = item_id
        
        if item_properties["type"] == "Feature Service":
            # check if dependent file already was uploaded
            reqs = self.graph.get_item(item_id).requires("id")
            service_item = None
            if len(reqs) > 0:
                # find the dependent file
                for req in reqs:
                    if req in self.created_item_mapping and self.items[req]["type"] in FILE_BASED_TYPES:
                        service_id = self.created_item_mapping[req]
                        service_item = self.gis.content.get(service_id)
                        break
            else:
                # check if data file exists
                for file in os.listdir(data_folder):
                    if file.endswith(".zip"):
                        fp = os.path.join(data_folder, file)
                        data_props = {
                            "type": "File Geodatabase",
                            "title": item_properties["title"],
                        }
                        try:
                            job = folder.add(
                                **{
                                    "item_properties": data_props,
                                    "file": fp,
                                }
                            )
                            service_item = job.result()
                        except:
                            data_props["title"] = _get_unique_name(self.gis, item_properties["title"])
                            job = folder.add(
                                **{
                                    "item_properties": data_props,
                                    "file": fp,
                                }
                            )
                            service_item = job.result()
                        break
            
            # publish the service
            if service_item:
                pub_params = {"name": item_properties["title"]}
                new_item = service_item.publish(publish_parameters = pub_params, item_id = item_id)
                self.created_item_mapping[item_id] = new_item.id

        for file in os.listdir(data_folder):
            if file.endswith(".zip"):
                fp = os.path.join(data_folder, file)
                data_props = {
                    "type": item_properties["type"],
                    "title": item_properties["title"],
                }
                try:
                    job = folder.add(
                        **{
                            "item_properties": data_props,
                            "file": fp,
                        }
                    )
                    new_item = job.result()
                except:
                    data_props["title"] = _get_unique_name(self.gis, item_properties["title"])
                    job = folder.add(
                        **{
                            "item_properties": data_props,
                            "file": fp,
                        }
                    )
                    new_item = job.result()
                self.created_item_mapping[item_id] = new_item.id
                break
        
        # import the resources
        # for res in resources:
        #     res_path = os.path.join(data_folder, res)
        #     new_item.resources.add(res_path)
        
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
            if itemid in item_mapping:
                continue
            item_folder = os.path.join(self._temp_package, itemid)
            new_item = self._import_item(item_folder, preserve_id = preserve_ids, folder=folder)
            created_items.append(new_item)
            # if we changed the item id, update mapping so other items adjust
            if itemid != new_item.id:
                item_mapping[itemid] = new_item.id
            reqs = node.requires("id")
            # Check if any item in the reqs is a key in the mapping
            # maybe put this in the _import_item part instead?
            if any(req in item_mapping for req in reqs):
                try:
                    new_item.remap_data(item_mapping)
                except:
                    pass

        return created_items
    
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