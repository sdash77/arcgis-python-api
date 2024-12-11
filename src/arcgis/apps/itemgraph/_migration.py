from ._item_graph import ItemGraph, ItemNode, load_from_file
from arcgis.gis import GIS, Item, ContentManager
import os
import shutil
import tempfile
import tarfile
import ujson as json

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
        service_format: str = "File GeoDatabase",
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
        export_item_data(item, item_dir)
    
    manifest = {}
    # Iterate over all items in the graph and create their folders
    for node in graph.all_items():
        create_item_folder(node, main_dir)
        item = node.item
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


def export_item_data(node: ItemNode, output_folder: str):
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
        self.temp_dir = self._unpack_package()
        self.temp_package = os.path.join(self.temp_dir.name, basename)
        temp_graph_path = os.path.join(self.temp_package, "graph.gml")
        self.graph = load_from_file(temp_graph_path, gis, include_items=False)
        manifest_file_path = os.path.join(self.temp_package, "manifest.json")
        with open(manifest_file_path, "r") as manifest_file:
            self.items = json.load(manifest_file)
    
    def _unpack_package(self):
        temp_dir = tempfile.TemporaryDirectory()
        with tarfile.open(self.package_path, "r:gz") as tar:
            tar.extractall(temp_dir.name)
        return temp_dir
    
    def _import_item(self, item_folder):
        # read the properties.json file
        with open(os.path.join(item_folder, "properties.json"), "r") as prop_file:
            item_properties = json.load(prop_file)
        
        # read the relationships.json file
        with open(os.path.join(item_folder, "relationships.json"), "r") as rel_file:
            relationships = json.load(rel_file)
        
        # read the resources.json file
        with open(os.path.join(item_folder, "resources.json"), "r") as res_file:
            resources = json.load(res_file)
        
        # read the data folder
        data_folder = os.path.join(item_folder, "data")
        if item_properties["type"] in JSON_BASED_TYPES:
            path_name = "structure.json"
            data_path = os.path.join(data_folder, path_name)
        else:
            data_path = data_folder
        
        # import the item
        item = self.gis.content.add(item_properties, data_path)
        
        # import the resources
        for res in resources:
            res_path = os.path.join(data_folder, res)
            item.resources.add(res_path)
        
        # return the item
        return item


    
    
