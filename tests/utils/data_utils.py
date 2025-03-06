from enum import Enum
from typing import Optional

from arcgis.gis._impl._dataclasses._contentds import ItemTypeEnum
from arcgis import GIS, features
from arcgis.gis import ItemProperties, Item
from integration.config import INTEGRATION_TEST_ITEM_TAG


def publish_test_item(
    gis: GIS,
    layer_name: str,
    source_data_path: str,
    item_type: ItemTypeEnum,
    prep_for_editing: bool = True,
    override_capabilities: Optional[dict] = None,
    source_item: Optional[Item] = None,
) -> Item:
    """

    :param gis: GIS: The target GIS instance
    :param layer_name: str: The name of the target feature service
    :param source_data_path: str: The path to the file to upload and publish
    :param item_type: ItemTypeEnum: The enum value for the data type
        e.g. SERVICE_DEFINITION, SHAPEFILE, etc.
    :param prep_for_editing: bool: Should the published service be given editing capabilities:
    :param override_capabilities: dict(str): Provide custom feature service capabilities
    :param source_item: Item: (Optional) The source file item to publish
    :return:
    """
    try:
        # Add the item to the portal
        source_item = add_source_item(gis, layer_name, item_type, source_data_path)

        # Source item is good, try publishing
        feature_layer_item = source_item.publish(
            {"name": layer_name, "tags": INTEGRATION_TEST_ITEM_TAG}
        )
        if not feature_layer_item:
            raise Exception(f"Could not update publish {layer_name}")
        if prep_for_editing:
            is_prepped_for_editing = prep_test_item(
                feature_layer_item, override_capabilities
            )
            if not is_prepped_for_editing:
                raise Exception("Could not update editing capabilities")
        return feature_layer_item

    except Exception as ex:
        # If publishing fails, don't leave the source item behind
        if source_item:
            source_item.delete(permanent=True)
        raise Exception("Failed to add necessary item file to portal.", ex)


def add_source_item(gis: GIS, layer_name: str, item_type: ItemTypeEnum, source_data_path: str):
    source_item = None
    try:
        ip = ItemProperties(
            title=layer_name,
            item_type=item_type.value,
            tags=["ntgrtn-tst"],
            snippet="Item for Feature Layer integration testing",
        )
        root_folder = gis.content.folders.get()
        source_item = root_folder.add(
            item_properties=ip,
            file=source_data_path,
        ).result()
        return source_item
    except Exception as ex:
        raise Exception("Failed to add necessary item file to portal.")


def prep_test_item(feature_layer, capabilities):
    """
    Ensure feature layer has necessary capabilities enabled
    :param feature_layer: FeatureLayer: The target feature layer
    :param capabilities: dict: (Optional) Custom capabilities to add to the Feature Layer
    :return:
    """
    flc = features.FeatureLayerCollection.fromitem(feature_layer)
    if flc is not None:
        if "Editing" in flc.properties.capabilities:
            return True
        else:
            if not capabilities:
                capabilities = {
                    "capabilities": "Create,Delete,Query,Update,Editing,Extract,Sync",
                }
            result = flc.manager.update_definition(capabilities)
            return result


def cleanup_published_items(items: list[Item]) -> None:
    """
    Delete source item and related items by name.

    :param items: list(arcgis.gis.Item): A list of Items to delete
    :return: void
    """
    for item in items:
        try:
            source_item = item.related_items("Service2Data", "forward")[0]
            if source_item:
                source_item.delete(permanent=True)
                item.delete(permanent=True)
        except IndexError as ie:
            item.delete(permanent=True)
        except Exception as ex:
            print("Failed to delete item:", item, ex)


class ServerTypeEnum(Enum):
    FEATURE = "FeatureServer"
    TOPOGRAPHIC = "TopographicProductionServer"
    MAP_SERVER = "MapServer"
    VERSION_MANAGER = "VersionManagementServer"
    PARCEL_FABRIC = "ParcelFabricServer"
    VALIDATION = "ValidationServer"
    RASTER = "RasterAnalytics"
    WORKFLOW_MANAGER = "WorkflowManager"
    KNOWLEDGE = "KnowledgeServer"
    MISSION = "MissionServer"
    NOTEBOOK = "NotebookServer"


def get_feature_layer_url(
    gis: GIS,
    service_name: str,
    server_type: ServerTypeEnum | str,
    server_role: str = "HOSTING",
    layer_id: int | str = None,
    folder_name: str = None,
):
    """
    Build a URL string to a feature service from GIS
    Example: ``https://pythonapitestnb.dev.geocloud.com/server/rest/services/TMS_ntgrtn_tst/FeatureServer``

    :param gis: GIS The GIS
    :param service_name: str The name of the feature service
    :param server_type: ServerTypeEnum or str The server type (FeatureServer, MapServer, ValidationServer, etc.)
    :param server_role: str: The server role of the target instance.
                "HOSTING" - Access to hosted endpoints (FeatureServer, MapServer, ValidationServer, etc.)
                "FEDERATED" - Access to federated server types (MissionServer, NotebookServer, RasterAnalytics, etc.)
    :param layer_id: (Optional) The target layer ID of a specific feature layer
    :param folder_name: (Optional) The name of the folder containing the target service
    :return: The URL string of the feature service
    """
    service_type_str = server_type if type(server_type) is str else server_type.value
    server_manager = gis.admin.servers

    if folder_name:
        service_name = f"{folder_name}/{service_name}"

    if gis._is_agol:
        # return the first feature server url for agol
        return server_manager.properties.get("feature")[0]

    if server_role.lower() == "hosting":
        hosting_server = server_manager.get(role="HOSTING_SERVER")[0]
        base_server_url = hosting_server.content.url
        result_url = f"{base_server_url}/{service_name}/{service_type_str}"
        if not isinstance(layer_id, (type(False), type(None))):
            result_url = f"{result_url}/{layer_id}"
        return result_url
    if server_role.lower() == "federated":
        for item in server_manager.properties.get("servers"):
            if item.get("serverFunction", None) == server_type.value:
                server = [
                    s for s in server_manager.list() if item.get("adminUrl") in s.url
                ][0]
                base_server_url = server.content.url
                result_url = f"{base_server_url}/{service_name}"
                if not isinstance(layer_id, (type(False), type(None))):
                    result_url = f"{result_url}/{layer_id}"
                return result_url
    return None


def create_group(gis: GIS, group_name: str):
    """
    Create a test group in GIS

    :param gis: GIS: The GIS instance
    :param group_name: str: The name of the group
    :return: The created group
    """
    try:
        group = gis.groups.create(
            title=group_name,
            tags=INTEGRATION_TEST_ITEM_TAG,
            access="org",
        )
        return group
    except Exception as ex:
        raise Exception("Failed to create necessary group in portal.", ex)


def cleanup_groups(groups: list):
    """
    Delete groups

    :param groups: list: The groups to delete
    :return: void
    """
    for group in groups:
        try:
            group.delete()
        except Exception as ex:
            print("Failed to delete group.", group, ex)
