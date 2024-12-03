from ._item_graph import ItemGraph, ItemNode
from arcgis.gis import GIS, Item, ContentManager
import os
import shutil
import tempfile
import tarfile

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
    
    # Create a metadata file at the top directory
    metadata_file = os.path.join(main_dir, "metadata.txt")
    with open(metadata_file, "w") as f:
        f.write("Metadata for exported content\n")
        # Add more metadata information as needed
    
    # Helper function to create item folder and export item data
    def create_item_folder(item, parent_dir):
        item_dir = os.path.join(parent_dir, item.id)
        os.makedirs(item_dir, exist_ok=True)
        # Call helper function to export item data
        export_item_data(item, item_dir)
    
    # Iterate over all items in the graph and create their folders
    for item in graph.all_items():
        create_item_folder(item, main_dir)
    
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
    for header in ["files", "resources", "data", "relationships", "proxies"]:
        os.makedirs(os.path.join(output_folder, header), exist_ok=True)
    
    # download json of item properties based


    # download thumbnail
    files_folder = os.path.join(output_folder, "files")
    item.download_thumbnail(files_folder)

    # download metadata
    item.download_metadata(files_folder)

    # resources
    res_folder = os.path.join(output_folder, "resources")
    rm = item.resources
    rm.export(res_folder, "archive.zip")

    # data
    data_folder = os.path.join(output_folder, "data")
    if item.type in JSON_BASED_TYPES:
        path_name = "structure.json"
        item.download(data_folder, path_name)
    else:
        item.download(data_folder)

    return output_folder
    



    
    
