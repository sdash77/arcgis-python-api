from enum import Enum

from arcgis import GIS, features
from arcgis.gis import ItemProperties, Item


# Enum of potential ItemTypes
class ItemType(Enum):
    CSV = "CSV"
    EXCEL = "Microsoft Excel"
    FGDB = "File Geodatabase"
    SD = "Service Definition"
    SHP = "Shapefile"
    SQLITE = "SQLite Geodatabase"


def publish_test_item(
    gis: GIS,
    layer_name: str,
    source_data_path: str,
    item_type: str,
    prep_for_editing=True,
) -> Item:
    source_item = None
    try:
        ip = ItemProperties(
            title=layer_name,
            item_type=item_type,
            tags=["ntgrtn-tst"],
            snippet="Item for Feature Layer integration testing",
        )
        root_folder = gis.content.folders.get()
        source_item = root_folder.add(
            item_properties=ip,
            file=source_data_path,
        ).result()
        # publish the item
        if not source_item:
            raise Exception(f"Could not update publish {layer_name}")

        # Source item is good, try publishing
        feature_layer_item = source_item.publish(
            {"name": layer_name, "tags": "ntgrtn-tst"}
        )
        if not feature_layer_item:
            raise Exception(f"Could not update publish {layer_name}")
        if prep_for_editing:
            is_prepped_for_editing = prep_test_item(feature_layer_item)
            if not is_prepped_for_editing:
                raise Exception("Could not update editing capabilities")
        return feature_layer_item

    except Exception as ex:
        # If publishing fails, don't leave the source item behind
        if source_item:
            source_item.delete(permanent=True)
        raise Exception("Failed to add necessary item file to portal.", ex)


def prep_test_item(feature_layer):
    # ensure feature layer has necessary capabilities enabled
    flc = features.FeatureLayerCollection.fromitem(feature_layer)
    if flc is not None:
        if "Editing" in flc.properties.capabilities:
            return True
        else:
            result = flc.manager.update_definition(
                {
                    "capabilities": "Create,Delete,Query,Update,Editing,Extract,Sync",
                }
            )
            return result


def cleanup_published_items(items: list[Item]):
    for item in items:
        print(item)
        try:
            source_item = item.related_items("Service2Data", "forward")[0]
            if source_item:
                source_item.delete(permanent=True)
                item.delete(permanent=True)
        except IndexError as ie:
            item.delete(permanent=True)
