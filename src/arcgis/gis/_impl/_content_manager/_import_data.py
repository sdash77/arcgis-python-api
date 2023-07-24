import random
from uuid import uuid4
import string
import os
import warnings
import pandas as pd
import tempfile
import shutil

from arcgis.auth.tools import LazyLoader

_tool_utils = LazyLoader("arcgis.features.geo._tools._utils")
_common_utils = LazyLoader("arcgis._impl.common._utils")
gis = LazyLoader("arcgis.gis")
features = LazyLoader("arcgis.features")

try:
    from arcgis.features.geo import _is_geoenabled
except:

    def _is_geoenabled(o):
        return False


try:
    import arcpy

    has_arcpy = True
except ImportError:
    has_arcpy = False
except RuntimeError:
    has_arcpy = False
try:
    import shapefile

    has_pyshp = True
except ImportError:
    has_pyshp = False


"""
This file is to have methods that can be utilized in the import_data method of the ContentManager as well as in the insert_layer from the Feature Layer Collection Manager.

Steps to achieve to import data that will drive the methods created:
1. Establish if the df is geoenabled
2. If geoenabled, Establish if arcpy or shapely is available
3. Create the necessary file out of the dataframe: fgdb, shp, or csv (csv if not geoenabled)
4. Get the correct publish parameters for the file type
5. Publish the file
6. If insert or overwrite has been indicated in the import_data method then perform correct method. (includes adding dependencies)
"""

def _import_as_item(gis, df, **kwargs):

    if item_id and gis.version <= [7, 1]:
        item_id = None

        warnings.warn(
            "`item_id` is not allowed at this version of Portal, please use Enterprise 10.8.1+"
        )

    overwrite = kwargs.pop("overwrite", False)
    insert = kwargs.pop("append", False)

    if isinstance(df, features.FeatureSet):
        df = df.sdf

    # Check that a layer can be created
    if _is_geoenabled(df):
        if has_arcpy == False and has_pyshp == False:
            raise Exception(
                "Spatially enabled DataFrame's must have either pyshp or"
                + " arcpy available to use import_data"
            )
        if has_arcpy:
            file_type = "File Geodatabase"
        elif has_pyshp:
            file_type = "Shapefile"
    else:
        file_type = "CSV"

    # Create the file item
    file_item, new_item, publish_parameters = _create_file_item(df, file_type, **kwargs)

    if not(overwrite or insert):
        return new_item
    else:
        # Get user defined parameters
            fs_dict = kwargs.pop("service", None)
            if fs_dict is None:
                raise ValueError(
                    "If overwite or append is True, then the feature service id needs to be specified in the `service` parameter."
                )
            fs_id = fs_dict["featureServiceId"]
            if isinstance(fs_id, gis.Item):
                fs_id = fs_id.itemid

            index = fs_dict["layer"]

            # Create the feature layer manager for the existing feature service
            if fs_id is None:
                raise ValueError(
                    "The provided feature service id cannot be found. Please check it is correct and try again."
                )
            fs_item = gis.content.get(fs_id)

            flc = features.FeatureLayerCollection.fromitem(fs_item)
            flc_manager = flc.manager
    
    if overwrite:
        # overwrite workflow
        _perform_overwrite(index, flc_manager, publish_parameters)
    else:
        # insert workflow
        _perform_insert(index, flc_manager, publish_parameters)
    
    _add_item_dependency(file_type, index, file_item, fs_item, new_item, gis)

def _create_file_item(gis, df, file_type, **kwargs):
    # File Type Dictionary
    ftypes = {
        "File Geodatabase": "gdb",
        "Shapefile": "shp",
        "CSV": "csv"
    }

    # Pop out kwargs, establish params to be used throughout
    service_name = kwargs.pop("service_name", None)
    if service_name is None:
        service_name = "a" + uuid4().hex[:7]
    temp_dir = os.path.join(tempfile.gettempdir(), service_name)
    title = kwargs.pop("title", uuid4().hex)
    capabilities = kwargs.pop("capabilities", "Query")
    item_id = kwargs.pop("item_id", None)
    tags = kwargs.pop("tags", file_type)
    folder = kwargs.pop("folder", None)
    name = "%s%s.%s" % (
        random.choice(string.ascii_lowercase),
        uuid4().hex[:5],
        ftypes[file_type],
    )
    
    # Create the file to be added as an item
    if file_type in ["File Geodatabase", "Shapefile"]:
        # Working with feature layers
        # set up temporary zip to be used in directory
        os.makedirs(temp_dir)
        temp_zip = os.path.join(temp_dir, "%s.zip" % ("a" + uuid4().hex[:5]))

        # Create filegdb or shapefile
        if file_type == "File Geodatabase":
            # create empty filegdb
            emtpy_fgdb = _tool_utils.run_and_hide(
                fn=arcpy.CreateFileGDB_management,
                **{"out_folder_path": temp_dir, "out_name": name},
            )
            fgdb = emtpy_fgdb[0]
            location = os.path.join(fgdb, os.path.basename(temp_dir))
            zip_loc = os.path.join(temp_dir, name)
        else:
            location = os.path.join(temp_dir, name)
            zip_loc = temp_dir

        # Writes the df to file as features
        sanitize_columns = kwargs.pop("sanitize_columns", False)
        df.spatial.to_featureclass(location=location, sanitize_columns=sanitize_columns)

        # zip it
        file = _common_utils.zipws(path=zip_loc, outfile=temp_zip, keep=True)

    elif file_type == "CSV":
        # Table Workflow
        file = tempfile.gettempdir() + "\\%s%s.csv" % (
            random.choice(string.ascii_lowercase),
            uuid4().hex[:5],
        )
        with open(file, "w") as my_csv:
            df.to_csv(my_csv)
            my_csv.close()
    
    # add item to portal
    file_item = gis.content.add(
        item_properties={
            "title": title,
            "type": file_type,
            "tags": tags,
        },
        data=file,
        folder=folder,
    )
    shutil.rmtree(temp_dir, ignore_errors=True)

    if file_type == "CSV":
        # analyze the csv for publish params
        publish_parameters = gis.content.analyze(item=file_item, file_type="csv")
        publish_parameters["name"] = service_name
        publish_parameters["locationType"] = None
    else:
        # start creating publish params from new file item
        publish_parameters = {
            "hasStaticData": True,
            "name": os.path.splitext(file_item["name"])[0],
            "maxRecordCount": 2000,
            "layerInfo": {"capabilities": capabilities},
            "targetSR": kwargs.pop("target_sr", 102100)
        }
    
    new_item = file_item.publish(
                    publish_parameters=publish_parameters, item_id=item_id
                )
    return file_item, new_item, publish_parameters

def _perform_overwrite(fl_index, flc_manager, publish_parameters):
    # update the name and id to represent correct values
    publish_parameters["id"] = fl_index
    publish_parameters["name"] = flc_manager.properties.layers[fl_index]["name"]

    # Perform edit on the flc
    # Step 1: Preserve layer ids
    revert = False
    if (
        "preserveLayerIds" not in flc_manager.properties
        or flc_manager.properties["preserveLayerIds"] is not True
    ):
        flc_manager.update_definition({"preserveLayerIds": True})
        revert = True
    # Step 2: Delete layer from definition
    flc_manager.delete_from_definition({"layers": [{"id": fl_index}]})
    # Step 3: Add new layer to definition
    flc_manager.add_to_definition({"layers": [dict(publish_parameters)]})
    # Step 4: Cleanup
    if revert:
        flc_manager.update_definition({"preserveLayerIds": False})

def _perform_insert(flc_manager, publish_parameters):
    # Add new layer to definition
    flc_manager.add_to_definition({"layers": [dict(publish_parameters)]})
    # Find the index at which the layer was added
    for layer in flc_manager.properties.layers:
        if layer["name"] == publish_parameters["name"]:
            fl_index = layer["id"]
    return fl_index

def _add_item_dependency(
    file_type, fl_index, file_item, fs_item, new_item=None, gis=None
):
    if file_type == "csv":
        source_info = gis.content.analyze(item=file_item)["publishParameters"]
        gis.ItemDependency(fs_item).add("itemid", file_item.id)
        fs_item.tables[fl_index].append(
            item_id=file_item.id,
            upload_format=file_type,
            source_info=source_info,
        )
    elif (
        file_type == "shapefile"
        or "filegdb"
        in fs_item.layers[fl_index].properties.supportedAppendFormats
    ):
        gis.ItemDependency(fs_item).add("itemid", file_item.id)
        fs_item.layers[fl_index].append(
            item_id=file_item.id, upload_format=file_type
        )
    else:
        # When filegdb not supported through append, use featureCollection
        features = new_item.layers[0].query().features
        fs_item.layers[fl_index].edit_features(adds=features)
    fs_item.add_relationship(rel_item=file_item, rel_type="Service2Data")